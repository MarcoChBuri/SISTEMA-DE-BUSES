package com.buses.rest.apis;

import controlador.servicios.Controlador_persona;
import controlador.servicios.Controlador_cuenta;
import controlador.tda.lista.LinkedList;
import modelo.enums.Estado_cuenta;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import modelo.enums.Tipo_cuenta;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;
import modelo.Cuenta;
import modelo.Persona;

@Path("/cuenta")
public class Cuenta_api {

    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_cuenta() {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_cuenta cc = new Controlador_cuenta();
            response.put("mensaje", "Lista de cuentas");
            response.put("cuentas", cc.Lista_cuentas().toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al obtener la lista de cuentas");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getCuenta(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_cuenta cc = new Controlador_cuenta();
            Cuenta cuenta = cc.get(id);
            if (cuenta != null) {
                response.put("mensaje", "Cuenta encontrada");
                response.put("cuenta", cuenta);
                return Response.ok(response).build();
            }
            else {
                response.put("mensaje", "Cuenta no encontrada");
                return Response.status(Response.Status.NOT_FOUND).entity(response).build();
            }
        }
        catch (Exception e) {
            response.put("mensaje", "Error al obtener la cuenta");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/guardar")
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response save(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        if (!validarDatosCuenta(map)) {
            response.put("mensaje", "Faltan datos requeridos para la cuenta");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        try {
            Controlador_cuenta cc = new Controlador_cuenta();
            Cuenta cuenta = construirCuenta(map);
            cc.setCuenta(cuenta);
            if (cc.save()) {
                response.put("mensaje", "Cuenta guardada exitosamente");
                response.put("cuenta", cuenta);
                return Response.ok(response).build();
            }
            else {
                response.put("mensaje", "Error al guardar la cuenta");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
        }
        catch (Exception e) {
            response.put("mensaje", "Error al guardar la cuenta");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        if (!validarDatosCuenta(map) || map.get("id_cuenta") == null) {
            response.put("mensaje", "Faltan datos requeridos para actualizar la cuenta");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        try {
            Controlador_cuenta cc = new Controlador_cuenta();
            Cuenta cuenta = construirCuenta(map);
            cuenta.setId_cuenta(((Number) map.get("id_cuenta")).intValue());
            cc.setCuenta(cuenta);
            if (cc.update()) {
                response.put("mensaje", "Cuenta actualizada exitosamente");
                response.put("cuenta", cuenta);
                return Response.ok(response).build();
            }
            else {
                response.put("mensaje", "Error al actualizar la cuenta");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
        }
        catch (Exception e) {
            response.put("mensaje", "Error al actualizar la cuenta");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/eliminar/{id}")
    @DELETE
    @Produces(MediaType.APPLICATION_JSON)
    public Response delete(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_cuenta cc = new Controlador_cuenta();
            if (cc.delete(id)) {
                response.put("mensaje", "Cuenta eliminada exitosamente");
                return Response.ok(response).build();
            }
            else {
                response.put("mensaje", "No se encontró la cuenta para eliminar");
                return Response.status(Response.Status.NOT_FOUND).entity(response).build();
            }
        }
        catch (Exception e) {
            response.put("mensaje", "Error al eliminar la cuenta");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/sincronizar")
    @POST
    @Produces(MediaType.APPLICATION_JSON)
    public Response sincronizarCuentas() {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_cuenta cc = new Controlador_cuenta();
            Controlador_persona cp = new Controlador_persona();
            LinkedList<Persona> personas = cp.Lista_personas();
            int cuentasSincronizadas = 0;
            for (int i = 0; i < personas.getSize(); i++) {
                Persona persona = personas.get(i);
                if (persona.getCuenta() != null) {
                    boolean cuentaExiste = false;
                    for (int j = 0; j < cc.Lista_cuentas().getSize(); j++) {
                        if (cc.Lista_cuentas().get(j).getId_cuenta()
                                .equals(persona.getCuenta().getId_cuenta())) {
                            cuentaExiste = true;
                            break;
                        }
                    }
                    if (!cuentaExiste) {
                        cc.setCuenta(persona.getCuenta());
                        cc.save();
                        cuentasSincronizadas++;
                    }
                }
            }
            response.put("mensaje", "Sincronización completada");
            response.put("cuentas_sincronizadas", cuentasSincronizadas);
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al sincronizar cuentas");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    private boolean validarDatosCuenta(HashMap<String, Object> map) {
        return map.get("correo") != null && map.get("contrasenia") != null && map.get("estado_cuenta") != null
                && map.get("tipo_cuenta") != null;
    }

    private Cuenta construirCuenta(HashMap<String, Object> map) {
        Cuenta cuenta = new Cuenta();
        cuenta.setCorreo((String) map.get("correo"));
        cuenta.setContrasenia((String) map.get("contrasenia"));
        cuenta.setEstado_cuenta(Estado_cuenta.valueOf((String) map.get("estado_cuenta")));
        cuenta.setTipo_cuenta(Tipo_cuenta.valueOf((String) map.get("tipo_cuenta")));
        return cuenta;
    }
}