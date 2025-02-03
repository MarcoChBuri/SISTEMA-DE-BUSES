package com.buses.rest.apis;

import controlador.servicios.Controlador_pago;
import controlador.tda.lista.LinkedList;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import modelo.enums.Opcion_pago;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import java.util.ArrayList;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import javax.ws.rs.Path;
import java.util.Arrays;
import javax.ws.rs.POST;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;
import java.util.List;
import modelo.Pago;

@Path("/pago")
public class Pago_api {

    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_pago() {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_pago cp = new Controlador_pago();
            response.put("mensaje", "Lista de pagos");
            response.put("pagos", cp.Lista_pagos().toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al obtener la lista de pagos");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getPago(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_pago cp = new Controlador_pago();
            Pago pago = cp.get(id);
            if (pago != null) {
                response.put("mensaje", "Pago encontrado");
                response.put("pago", pago);
                return Response.ok(response).build();
            }
            else {
                response.put("mensaje", "Pago no encontrado");
                return Response.status(Response.Status.NOT_FOUND).entity(response).build();
            }
        }
        catch (Exception e) {
            response.put("mensaje", "Error al obtener el pago");
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
            if (!map.containsKey("saldo") || !map.containsKey("numero_tarjeta") || !map.containsKey("titular")
                    || !map.containsKey("fecha_vencimiento") || !map.containsKey("codigo_seguridad")
                    || !map.containsKey("opcion_pago")) {
                response.put("mensaje", "Faltan datos requeridos");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            Controlador_pago cp = new Controlador_pago();
            Pago pago = new Pago();
            pago.setOpcion_pago(Opcion_pago.valueOf(map.get("opcion_pago").toString()));
            pago.setTitular(map.get("titular").toString());
            pago.setNumero_tarjeta(map.get("numero_tarjeta").toString());
            pago.setFecha_vencimiento(map.get("fecha_vencimiento").toString());
            pago.setCodigo_seguridad(map.get("codigo_seguridad").toString());
            pago.setSaldo(Float.parseFloat(map.get("saldo").toString()));
            cp.setPago(pago);
            if (cp.save()) {
                response.put("mensaje", "Pago guardado exitosamente");
                response.put("pago", pago);
                return Response.ok(response).build();
            }
            response.put("mensaje", "Error al guardar el pago");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
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
            if (!validarDatosPago(map)) {
                response.put("mensaje", "Datos de pago incompletos o inválidos");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            Pago pago = new Pago();
            try {
                pago.setId_pago(Integer.parseInt(map.get("id_pago").toString()));
                pago.setOpcion_pago(Opcion_pago.valueOf(map.get("opcion_pago").toString()));
                pago.setTitular(map.get("titular").toString());
                pago.setNumero_tarjeta(map.get("numero_tarjeta").toString());
                pago.setFecha_vencimiento(map.get("fecha_vencimiento").toString());
                pago.setCodigo_seguridad(map.get("codigo_seguridad").toString());
                pago.setSaldo(Float.parseFloat(map.get("saldo").toString()));
            }
            catch (Exception e) {
                response.put("mensaje", "Error al procesar los datos: " + e.getMessage());
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            Controlador_pago cp = new Controlador_pago();
            cp.setPago(pago);
            if (cp.update()) {
                response.put("mensaje", "Pago actualizado exitosamente");
                response.put("pago", pago);
                return Response.ok(response).build();
            }
            response.put("mensaje", "Error al actualizar el pago");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        catch (Exception e) {
            e.printStackTrace();
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
            Controlador_pago cp = new Controlador_pago();
            if (cp.delete(id)) {
                response.put("mensaje", "Pago eliminado exitosamente");
                return Response.ok(response).build();
            }
            response.put("mensaje", "Error al eliminar el pago");
            return Response.status(Response.Status.NOT_FOUND).entity(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/opciones")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getOpcionesPago() {
        HashMap<String, Object> response = new HashMap<>();
        try {
            List<String> metodos = new ArrayList<>();
            for (Opcion_pago opcion : Opcion_pago.values()) {
                metodos.add(opcion.name());
            }
            response.put("metodos_pago", metodos);
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al obtener las opciones de pago");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    private boolean validarDatosPago(HashMap<String, Object> map) {
        boolean valid = map != null && map.containsKey("id_pago") && map.containsKey("saldo")
                && map.containsKey("numero_tarjeta") && map.containsKey("titular")
                && map.containsKey("fecha_vencimiento") && map.containsKey("codigo_seguridad")
                && map.containsKey("opcion_pago");
        return valid;
    }

    @Path("/ordenar/{atributo}/{orden}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response ordenarPagos(@PathParam("atributo") String atributo, @PathParam("orden") String orden) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_pago cp = new Controlador_pago();
            LinkedList<Pago> lista = cp.Lista_pagos();
            if (!Arrays.asList("opcion_pago", "titular", "numero_tarjeta", "fecha_vencimiento", "saldo")
                    .contains(atributo)) {
                response.put("mensaje", "Atributo de ordenamiento no válido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            lista.quickSort(atributo, orden.equalsIgnoreCase("asc"));
            response.put("mensaje", "Lista ordenada correctamente");
            response.put("pagos", lista.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al ordenar pagos: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/buscar/{atributo}/{criterio}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarPago(@PathParam("atributo") String atributo,
            @PathParam("criterio") String criterio) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_pago cp = new Controlador_pago();
            LinkedList<Pago> lista = cp.Lista_pagos();
            LinkedList<Pago> resultados = lista.binarySearch(criterio, atributo);
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
