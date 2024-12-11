package com.buses.rest.apis;

import controlador.servicios.Controlador_cooperativa;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.PathParam;
import java.util.Collections;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;

@Path("/cooperativa")
public class Cooperativa_api {
    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_cooperativa() {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_cooperativa cc = new Controlador_cooperativa();
        response.put("msg", "Lista de cooperativas");
        response.put("cooperativas", cc.Lista_cooperativas().toArray());
        if (cc.Lista_cooperativas().isEmpty()) {
            response.put("cooperativas", new Object[] {});
        }
        return Response.ok(response).build();
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getCooperativa(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_cooperativa cc = new Controlador_cooperativa();
        try {
            cc.setCooperativa(cc.get(id));
            response.put("msg", "Cooperativa encontrada");
            response.put("cooperativa", cc.get(id));
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Cooperativa no encontrada");
        }
        if (cc.getCooperativa().getId_cooperativa() == null) {
            response.put("msg", "Cooperativa no encontrada");
            return Response.status(Response.Status.NOT_FOUND).entity(response).build();
        }
        return Response.ok(response).build();
    }

    @Path("/guardar")
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response save(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_cooperativa cc = new Controlador_cooperativa();
        try {
            cc.getCooperativa().setNombre(map.get("nombre").toString());
            cc.getCooperativa().setRuc(map.get("ruc").toString());
            cc.getCooperativa().setDireccion(map.get("direccion").toString());
            cc.getCooperativa().setTelefono(map.get("telefono").toString());
            cc.getCooperativa().setCorreo_empresarial(map.get("correo_empresarial").toString());
            if (cc.save()) {
                response.put("msg", "Cooperativa guardada exitosamente");
                response.put("cooperativa", cc.getCooperativa());
                return Response.ok(response).build();
            }
            response.put("msg", "Error al guardar");
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
        Controlador_cooperativa cc = new Controlador_cooperativa();
        try {
            if (cc.delete(id)) {
                response.put("msg", "Cooperativa eliminada");
                return Response.ok(response).build();
            }
            else {
                response.put("msg", "Error al eliminar la cooperativa");
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al eliminar la cooperativa"))
                        .build();
            }
        }
        catch (Exception e) {
            response.put("msg", "Error al eliminar la cooperativa");
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al eliminar la cooperativa")).build();
        }
    }

    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_cooperativa cc = new Controlador_cooperativa();
        if (map.get("id") == null || map.get("nombre") == null || map.get("ruc") == null
                || map.get("direccion") == null || map.get("telefono") == null
                || map.get("correo_empresarial") == null) {
            response.put("msg", "Faltan datos");
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Faltan datos requeridos")).build();
        }
        try {
            cc.getCooperativa().setId_cooperativa(Integer.parseInt(map.get("id").toString()));
            cc.getCooperativa().setNombre(map.get("nombre").toString());
            cc.getCooperativa().setRuc(map.get("ruc").toString());
            cc.getCooperativa().setDireccion(map.get("direccion").toString());
            cc.getCooperativa().setTelefono(map.get("telefono").toString());
            cc.getCooperativa().setCorreo_empresarial(map.get("correo_empresarial").toString());
            if (cc.update()) {
                response.put("msg", "Cooperativa actualizada");
                response.put("cooperativa", cc.getCooperativa());
                return Response.ok(response).build();
            }
            else {
                response.put("msg", "Error al actualizar la cooperativa");
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al actualizar la cooperativa"))
                        .build();
            }
        }
        catch (Exception e) {
            response.put("msg", "Error al actualizar la cooperativa");
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al actualizar la cooperativa")).build();
        }
    }
}