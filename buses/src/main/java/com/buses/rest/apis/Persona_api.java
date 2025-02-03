package com.buses.rest.apis;

import controlador.servicios.Controlador_persona;
import controlador.servicios.Controlador_pago;
import controlador.dao.modelo_dao.Pago_dao;
import controlador.tda.lista.LinkedList;
import controlador.dao.utiles.Fecha;
import modelo.enums.Identificacion;
import modelo.enums.Estado_cuenta;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import modelo.enums.Tipo_cuenta;
import modelo.enums.Tipo_tarifa;
import modelo.enums.Opcion_pago;
import javax.ws.rs.PathParam;
import java.util.Collections;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import modelo.enums.Genero;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import java.util.Arrays;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;
import modelo.Persona;
import modelo.Cuenta;
import modelo.Pago;

@Path("/persona")
public class Persona_api {

    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_persona() {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_persona cp = new Controlador_persona();
        response.put("msg", "Lista de personas");
        response.put("personas", cp.Lista_personas().toArray());
        if (cp.Lista_personas().isEmpty()) {
            response.put("personas", new Object[] {});
        }
        return Response.ok(response).build();
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getPersona(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_persona cp = new Controlador_persona();
        try {
            cp.setPersona(cp.get(id));
            response.put("msg", "Persona encontrada");
            response.put("persona", cp.get(id));
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Persona no encontrada");
            return Response.status(Response.Status.NOT_FOUND).entity(response).build();
        }
    }

    @Path("/guardar")
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response save(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_persona cp = new Controlador_persona();
        try {
            String fechaNacimiento = map.get("fecha_nacimiento").toString();
            String fechaNormalizada = Fecha.normalizarFecha(fechaNacimiento);
            cp.getPersona().setTipo_identificacion(
                    Identificacion.valueOf(map.get("tipo_identificacion").toString()));
            cp.getPersona().setNumero_identificacion(map.get("numero_identificacion").toString());
            cp.getPersona().setNombre(map.get("nombre").toString());
            cp.getPersona().setApellido(map.get("apellido").toString());
            cp.getPersona().setGenero(Genero.valueOf(map.get("genero").toString()));
            cp.getPersona().setCorreo(map.get("correo").toString());
            cp.getPersona().setTelefono(map.get("telefono").toString());
            cp.getPersona().setDireccion(map.get("direccion").toString());
            cp.getPersona().setFecha_nacimiento(fechaNormalizada);
            cp.getPersona().setTipo_tarifa(Tipo_tarifa.valueOf(map.get("tipo_tarifa").toString()));
            cp.getPersona().setSaldo_disponible(Float.parseFloat(map.get("saldo_disponible").toString()));
            Cuenta cuenta = new Cuenta();
            cuenta.setCorreo(map.get("usuario").toString());
            cuenta.setContrasenia(map.get("contrasenia").toString());
            if (cp.Lista_personas().isEmpty()) {
                cuenta.setTipo_cuenta(Tipo_cuenta.Administrador);
            }
            else {
                cuenta.setTipo_cuenta(Tipo_cuenta.valueOf(map.get("tipo_cuenta").toString()));
            }
            cuenta.setEstado_cuenta(Estado_cuenta.valueOf(map.get("estado_cuenta").toString()));
            cp.getPersona().setCuenta(cuenta);
            if (map.containsKey("metodo_pago")) {
                Pago pago = new Pago();
                pago.setOpcion_pago(Opcion_pago.valueOf(map.get("opcion_pago").toString()));
                pago.setNumero_tarjeta(map.get("numero_tarjeta").toString());
                pago.setTitular(map.get("titular").toString());
                pago.setFecha_vencimiento(map.get("fecha_vencimiento").toString());
                pago.setCodigo_seguridad(map.get("codigo_seguridad").toString());
                pago.setSaldo(Float.parseFloat(map.get("saldo").toString()));
                cp.getPersona().setMetodo_pago(pago);
            }
            if (cp.save()) {
                response.put("msg", "Persona y cuenta creadas exitosamente");
                response.put("persona", cp.getPersona());
                return Response.ok(response).build();
            }
            response.put("msg", "Error al guardar la persona");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Error: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/eliminar/{id}")
    @DELETE
    @Produces(MediaType.APPLICATION_JSON)
    public Response delete(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_persona cp = new Controlador_persona();
        try {
            if (cp.delete(id)) {
                response.put("msg", "Persona eliminada");
                return Response.ok(response).build();
            }
            else {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al eliminar la persona")).build();
            }
        }
        catch (Exception e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al eliminar la persona")).build();
        }
    }

    @Path("/eliminarpago/{id}")
    @PUT
    @Produces(MediaType.APPLICATION_JSON)
    public Response eliminarMetodoPago(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_persona cp = new Controlador_persona();
            Persona persona = cp.get(id);
            if (persona == null) {
                response.put("msg", "Persona no encontrada");
                return Response.status(Response.Status.NOT_FOUND).entity(response).build();
            }
            Integer idPago = null;
            if (persona.getMetodo_pago() != null) {
                idPago = persona.getMetodo_pago().getId_pago();
            }
            persona.setMetodo_pago(null);
            cp.setPersona(persona);
            if (cp.update()) {
                if (idPago != null) {
                    Controlador_pago controladorPago = new Controlador_pago();
                    controladorPago.delete(idPago);
                }
                response.put("msg", "Método de pago eliminado correctamente");
                return Response.ok(response).build();
            }
            response.put("msg", "Error al eliminar el método de pago");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Error: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @SuppressWarnings("unchecked")
    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            if (map == null || !map.containsKey("id_persona")) {
                response.put("msg", "Error: Datos de persona inválidos o faltantes");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            Controlador_persona cp = new Controlador_persona();
            Persona persona = cp.get(Integer.parseInt(map.get("id_persona").toString()));
            if (persona == null) {
                response.put("msg", "Error: Persona no encontrada");
                return Response.status(Response.Status.NOT_FOUND).entity(response).build();
            }
            String fechaNormalizada = Fecha.normalizarFecha(map.get("fecha_nacimiento").toString());
            persona.setTipo_identificacion(Identificacion.valueOf(
                    getStringValue(map, "tipo_identificacion", persona.getTipo_identificacion().toString())));
            persona.setNumero_identificacion(
                    getStringValue(map, "numero_identificacion", persona.getNumero_identificacion()));
            persona.setNombre(getStringValue(map, "nombre", persona.getNombre()));
            persona.setApellido(getStringValue(map, "apellido", persona.getApellido()));
            persona.setDireccion(getStringValue(map, "direccion", persona.getDireccion()));
            persona.setFecha_nacimiento(fechaNormalizada);
            persona.setTelefono(getStringValue(map, "telefono", persona.getTelefono()));
            persona.setCorreo(getStringValue(map, "correo", persona.getCorreo()));
            persona.setGenero(Genero.valueOf(getStringValue(map, "genero", persona.getGenero().toString())));
            persona.setTipo_tarifa(Tipo_tarifa
                    .valueOf(getStringValue(map, "tipo_tarifa", persona.getTipo_tarifa().toString())));
            persona.setSaldo_disponible(Float.parseFloat(getStringValue(map, "saldo_disponible", "0.0")));
            if (map.containsKey("cuenta")) {
                HashMap<String, Object> cuentaMap = (HashMap<String, Object>) map.get("cuenta");
                if (cuentaMap != null) {
                    Cuenta cuenta = persona.getCuenta();
                    if (cuenta == null) {
                        cuenta = new Cuenta();
                    }
                    if (cuentaMap.containsKey("correo")) {
                        cuenta.setCorreo(cuentaMap.get("correo").toString());
                    }
                    if (cuentaMap.containsKey("tipo_cuenta")) {
                        cuenta.setTipo_cuenta(Tipo_cuenta.valueOf(cuentaMap.get("tipo_cuenta").toString()));
                    }
                    if (cuentaMap.containsKey("estado_cuenta")) {
                        cuenta.setEstado_cuenta(
                                Estado_cuenta.valueOf(cuentaMap.get("estado_cuenta").toString()));
                    }
                    if (cuentaMap.containsKey("contrasenia") && cuentaMap.get("contrasenia") != null) {
                        cuenta.setContrasenia(cuentaMap.get("contrasenia").toString());
                    }
                    persona.setCuenta(cuenta);
                }
            }
            if (map.containsKey("metodo_pago")) {
                HashMap<String, Object> pagoMap = (HashMap<String, Object>) map.get("metodo_pago");
                if (pagoMap != null) {
                    Pago pago = persona.getMetodo_pago();
                    if (pago == null) {
                        pago = new Pago();
                        pago.setOpcion_pago(Opcion_pago.valueOf(pagoMap.get("opcion_pago").toString()));
                        pago.setTitular(pagoMap.get("titular").toString());
                        pago.setNumero_tarjeta(pagoMap.get("numero_tarjeta").toString());
                        pago.setFecha_vencimiento(pagoMap.get("fecha_vencimiento").toString());
                        pago.setCodigo_seguridad(pagoMap.get("codigo_seguridad").toString());
                        pago.setSaldo(Float.parseFloat(pagoMap.get("saldo").toString()));
                        Pago_dao pagoDao = new Pago_dao();
                        pagoDao.setPago(pago);
                        if (pagoDao.save()) {
                            persona.setMetodo_pago(pago);
                        }
                        else {
                            throw new Exception("Error al guardar el nuevo método de pago");
                        }
                    }
                    else {
                        Object pagoId = pagoMap.get("id_pago");
                        if (pagoId != null && !pagoId.toString().equals("0")) {
                            pago.setId_pago(Integer.valueOf(pagoId.toString()));
                        }
                        pago.setOpcion_pago(Opcion_pago.valueOf(
                                getStringValue(pagoMap, "opcion_pago", pago.getOpcion_pago().toString())));
                        pago.setNumero_tarjeta(getStringValue(pagoMap, "numero_tarjeta", ""));
                        pago.setTitular(getStringValue(pagoMap, "titular", ""));
                        pago.setFecha_vencimiento(getStringValue(pagoMap, "fecha_vencimiento", ""));
                        pago.setCodigo_seguridad(getStringValue(pagoMap, "codigo_seguridad", ""));
                        pago.setSaldo(Float.parseFloat(getStringValue(pagoMap, "saldo", "0.0")));
                        Pago_dao pagoDao = new Pago_dao();
                        pagoDao.setPago(pago);
                        pagoDao.update();
                        persona.setMetodo_pago(pago);
                    }
                }
            }
            cp.setPersona(persona);
            if (cp.update()) {
                response.put("msg", "Persona actualizada correctamente");
                response.put("persona", persona);
                return Response.ok(response).build();
            }
            else {
                response.put("msg", "Error al actualizar la persona");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
        }
        catch (Exception e) {
            e.printStackTrace();
            response.put("msg", "Error: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    private String getStringValue(HashMap<String, Object> map, String key, String defaultValue) {
        Object value = map.get(key);
        return value != null ? value.toString() : defaultValue;
    }

    @Path("/actualizar-pago")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response actualizarMetodoPago(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_persona cp = new Controlador_persona();
            Controlador_pago controladorPago = new Controlador_pago();
            cp.setPersona(cp.get(Integer.parseInt(map.get("id_persona").toString())));
            Pago pago = cp.getPersona().getMetodo_pago();
            if (pago == null) {
                pago = new Pago();
            }
            pago.setOpcion_pago(Opcion_pago.valueOf(map.get("opcion_pago").toString()));
            Integer idPago = pago.getId_pago();
            pago.setNumero_tarjeta(map.get("numero_tarjeta").toString());
            pago.setTitular(map.get("titular").toString());
            pago.setFecha_vencimiento(map.get("fecha_vencimiento").toString());
            pago.setCodigo_seguridad(map.get("codigo_seguridad").toString());
            if (map.get("saldo") != null) {
                if (map.get("saldo") instanceof Number) {
                    pago.setSaldo(((Number) map.get("saldo")).floatValue());
                }
                else {
                    pago.setSaldo(Float.parseFloat(map.get("saldo").toString()));
                }
            }
            if (idPago != null) {
                pago.setId_pago(idPago);
            }
            controladorPago.setPago(pago);
            if (controladorPago.update()) {
                cp.getPersona().setMetodo_pago(controladorPago.getPago());
                if (cp.update()) {
                    response.put("msg", "Método de pago actualizado correctamente");
                    response.put("persona", cp.getPersona());
                    return Response.ok(response).build();
                }
            }
            response.put("msg", "Error al actualizar el método de pago");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        catch (Exception e) {
            e.printStackTrace();
            response.put("msg", "Error: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/transferir-saldo")
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response transferirSaldo(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            if (!map.containsKey("id_persona")) {
                response.put("msg", "ID de persona requerido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            Integer idPersona = Integer.parseInt(map.get("id_persona").toString());
            Controlador_persona cp = new Controlador_persona();
            Persona persona = cp.get(idPersona);
            if (persona == null) {
                response.put("msg", "Persona no encontrada");
                return Response.status(Response.Status.NOT_FOUND).entity(response).build();
            }
            if (persona.getMetodo_pago() == null) {
                response.put("msg", "La persona no tiene método de pago");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            Float saldoTarjeta = persona.getMetodo_pago().getSaldo();
            Float saldoDisponible = persona.getSaldo_disponible();
            persona.setSaldo_disponible(saldoDisponible + saldoTarjeta);
            persona.getMetodo_pago().setSaldo(0.0f);
            cp.setPersona(persona);
            if (cp.update()) {
                response.put("msg", "Saldo transferido correctamente");
                response.put("persona", persona);
                return Response.ok(response).build();
            }
            response.put("msg", "Error al transferir el saldo");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Error: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/ordenar/{atributo}/{orden}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response ordenarPersonas(@PathParam("atributo") String atributo,
            @PathParam("orden") String orden) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_persona cp = new Controlador_persona();
            LinkedList<Persona> lista = cp.Lista_personas();
            if (!Arrays
                    .asList("tipo_identificacion", "numero_identificacion", "nombre", "apellido",
                            "fecha_nacimiento", "genero", "telefono", "correo", "metodo_pago.opcion_pago",
                            "cuenta.correo", "cuenta.tipo_cuenta", "cuenta.estado_cuenta")
                    .contains(atributo)) {
                response.put("mensaje", "Atributo de ordenamiento no válido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            lista.quickSort(atributo, orden.equalsIgnoreCase("asc"));
            response.put("mensaje", "Lista ordenada correctamente");
            response.put("personas", lista.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al ordenar personas: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/buscar/{atributo}/{criterio}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarPersona(@PathParam("atributo") String atributo,
            @PathParam("criterio") String criterio) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_persona cp = new Controlador_persona();
            LinkedList<Persona> lista = cp.Lista_personas();
            LinkedList<Persona> resultados = lista.binarySearch(criterio, atributo);
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