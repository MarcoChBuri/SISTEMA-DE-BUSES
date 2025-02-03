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
import java.util.ArrayList;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import javax.ws.rs.POST;
import java.util.Arrays;
import javax.ws.rs.Path;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;
import modelo.Persona;
import java.util.List;
import modelo.Cuenta;

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
        try {
            if (!validarDatosCuenta(map)) {
                response.put("mensaje",
                        "Faltan datos requeridos: correo, contraseña, estado y tipo de cuenta");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            Controlador_cuenta cc = new Controlador_cuenta();
            Cuenta cuenta = new Cuenta();
            cuenta.setCorreo((String) map.get("correo"));
            cuenta.setContrasenia((String) map.get("contrasenia"));
            cuenta.setEstado_cuenta(Estado_cuenta.valueOf((String) map.get("estado_cuenta")));
            cuenta.setTipo_cuenta(Tipo_cuenta.valueOf((String) map.get("tipo_cuenta")));
            cc.setCuenta(cuenta);
            if (cc.save()) {
                response.put("mensaje", "Cuenta creada exitosamente");
                response.put("cuenta", cuenta);
                return Response.ok(response).build();
            }
            response.put("mensaje", "Error al guardar la cuenta");
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            if (!validarDatosCuenta(map) || map.get("id_cuenta") == null) {
                response.put("mensaje", "Faltan datos requeridos para actualizar la cuenta");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            Controlador_cuenta cc = new Controlador_cuenta();
            Controlador_persona cp = new Controlador_persona();
            Integer id = ((Number) map.get("id_cuenta")).intValue();
            Cuenta cuentaExistente = cc.get(id);
            if (cuentaExistente == null) {
                response.put("mensaje", "Cuenta no encontrada");
                return Response.status(Response.Status.NOT_FOUND).entity(response).build();
            }
            cuentaExistente.setCorreo((String) map.get("correo"));
            if (map.get("contrasenia") != null) {
                cuentaExistente.setContrasenia((String) map.get("contrasenia"));
            }
            cuentaExistente.setEstado_cuenta(Estado_cuenta.valueOf((String) map.get("estado_cuenta")));
            cuentaExistente.setTipo_cuenta(Tipo_cuenta.valueOf((String) map.get("tipo_cuenta")));
            cc.setCuenta(cuentaExistente);
            if (cc.update()) {
                LinkedList<Persona> personas = cp.Lista_personas();
                for (int i = 0; i < personas.getSize(); i++) {
                    Persona persona = personas.get(i);
                    if (persona.getCuenta() != null
                            && persona.getCuenta().getId_cuenta().equals(cuentaExistente.getId_cuenta())) {
                        persona.setCuenta(cuentaExistente);
                        cp.setPersona(persona);
                        cp.update();
                        break;
                    }
                }
                response.put("mensaje", "Cuenta actualizada exitosamente");
                response.put("cuenta", cuentaExistente);
                return Response.ok(response).build();
            }
            response.put("mensaje", "Error al actualizar la cuenta");
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error: " + e.getMessage());
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
            Controlador_persona cp = new Controlador_persona();
            Cuenta cuenta = cc.get(id);
            if (cuenta == null) {
                response.put("mensaje", "Cuenta no encontrada");
                return Response.status(Response.Status.NOT_FOUND).entity(response).build();
            }
            LinkedList<Persona> personas = cp.Lista_personas();
            for (int i = 0; i < personas.getSize(); i++) {
                Persona persona = personas.get(i);
                if (persona.getCuenta() != null && persona.getCuenta().getId_cuenta().equals(id)) {
                    response.put("mensaje",
                            "No se puede eliminar la cuenta porque está asociada a una persona");
                    return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
                }
            }
            if (cc.delete(id)) {
                response.put("mensaje", "Cuenta eliminada exitosamente");
                return Response.ok(response).build();
            }
            response.put("mensaje", "Error al eliminar la cuenta");
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error: " + e.getMessage());
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
                        if (cc.save()) {
                            cuentasSincronizadas++;
                        }
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

    @Path("/tipos")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getTiposCuenta() {
        HashMap<String, Object> response = new HashMap<>();
        try {
            List<String> tipos = new ArrayList<>();
            for (Tipo_cuenta tipo : Tipo_cuenta.values()) {
                tipos.add(tipo.name());
            }
            response.put("tipos_cuenta", tipos);
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al obtener tipos de cuenta");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/estados")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getEstadosCuenta() {
        HashMap<String, Object> response = new HashMap<>();
        try {
            List<String> estados = new ArrayList<>();
            for (Estado_cuenta estado : Estado_cuenta.values()) {
                estados.add(estado.name());
            }
            response.put("estados_cuenta", estados);
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al obtener estados de cuenta");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/ordenar/{atributo}/{orden}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response ordenarCuentas(@PathParam("atributo") String atributo, @PathParam("orden") String orden) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_cuenta cc = new Controlador_cuenta();
            LinkedList<Cuenta> lista = cc.Lista_cuentas();
            if (!Arrays.asList("correo", "tipo_cuenta", "estado_cuenta").contains(atributo)) {
                response.put("mensaje", "Atributo de ordenamiento no válido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            lista.quickSort(atributo, orden.equalsIgnoreCase("asc"));
            response.put("mensaje", "Lista ordenada correctamente");
            response.put("cuentas", lista.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al ordenar cuentas");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/buscar/{atributo}/{criterio}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarCuentas(@PathParam("atributo") String atributo,
            @PathParam("criterio") String criterio) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_cuenta cc = new Controlador_cuenta();
            LinkedList<Cuenta> lista = cc.Lista_cuentas();
            LinkedList<Cuenta> resultados = lista.binarySearch(criterio, atributo);
            response.put("mensaje", "Búsqueda realizada");
            response.put("cuentas", resultados.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error en la búsqueda");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }
}