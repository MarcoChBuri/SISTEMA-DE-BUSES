package com.buses.rest.apis;

import java.util.HashMap;
import javax.ws.rs.Consumes;
import javax.ws.rs.DELETE;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.PUT;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import controlador.servicios.Controlador_pago;
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
    public Response guardarPago(Pago pago) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_pago cp = new Controlador_pago();
            cp.setPago(pago);
            response.put("mensaje", "Pago guardado");
            response.put("pago", pago);
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al guardar el pago");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response actualizarPago(Pago pago) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_pago cp = new Controlador_pago();
            cp.setPago(pago);
            response.put("mensaje", "Pago actualizado");
            response.put("pago", pago);
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al actualizar el pago");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/eliminar/{id}")
    @DELETE
    @Produces(MediaType.APPLICATION_JSON)
    public Response eliminarPago(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_pago cp = new Controlador_pago();
            cp.delete(id);
            response.put("mensaje", "Pago eliminado");
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al eliminar el pago");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

}
