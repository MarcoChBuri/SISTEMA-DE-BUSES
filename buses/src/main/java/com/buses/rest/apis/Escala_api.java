package com.buses.rest.apis;

import controlador.servicios.Controlador_escala;
import controlador.tda.lista.LinkedList;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import java.util.Collections;
import javax.ws.rs.PathParam;
import javax.ws.rs.Consumes;
import javax.ws.rs.Produces;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import java.util.Arrays;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.GET;
import javax.ws.rs.PUT;
import modelo.Escala;

@Path("/escala")
public class Escala_api {

    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_escala() {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_escala ce = new Controlador_escala();
        response.put("msg", "Lista de escalas");
        response.put("escalas", ce.Lista_escala().toArray());
        if (ce.Lista_escala().isEmpty()) {
            response.put("escalas", new Object[] {});
        }
        return Response.ok(response).build();
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getEscala(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_escala ce = new Controlador_escala();
        try {
            ce.setEscala(ce.get(id));
            response.put("msg", "Escala encontrada");
            response.put("escala", ce.get(id));
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Escala no encontrada");
            return Response.status(Response.Status.NOT_FOUND).entity(response).build();
        }
    }

    @Path("/guardar")
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response save(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_escala ce = new Controlador_escala();
        try {
            if (map.get("id_escala") != null) {
                ce.getEscala().setId_escala((Integer) map.get("id_escala"));
            }
            ce.getEscala().setLugar_escala(map.get("lugar_escala").toString());
            ce.getEscala().setTiempo(map.get("tiempo").toString());
            if (ce.save()) {
                response.put("msg", "Escala guardada");
                response.put("escala", ce.getEscala());
                return Response.ok(response).build();
            }
            else {
                response.put("msg", "Error al guardar la escala");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
        }
        catch (Exception e) {
            response.put("msg", "Error al guardar la escala");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
    }

    @Path("/eliminar/{id}")
    @DELETE
    @Produces(MediaType.APPLICATION_JSON)
    public Response delete(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_escala ce = new Controlador_escala();
        try {
            if (ce.delete(id)) {
                response.put("msg", "Escala eliminada");
                return Response.ok(response).build();
            }
            else {
                response.put("msg", "Error al eliminar la escala");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
        }
        catch (Exception e) {
            response.put("msg", "Error al eliminar la escala");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
    }

    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_escala ce = new Controlador_escala();
        if (map.get("id_escala") == null || map.get("cantidad") == null || map.get("lugar_escala") == null
                || map.get("tiempo") == null) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Faltan datos requeridos")).build();
        }
        try {
            ce.getEscala().setId_escala(Integer.parseInt(map.get("id_escala").toString()));
            ce.getEscala().setLugar_escala(map.get("lugar_escala").toString());
            ce.getEscala().setTiempo(map.get("tiempo").toString());
            if (ce.update()) {
                response.put("msg", "Escala actualizada");
                response.put("escala", ce.getEscala());
                return Response.ok(response).build();
            }
            else {
                response.put("msg", "Error al actualizar la escala");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
        }
        catch (Exception e) {
            response.put("msg", "Error al actualizar la escala");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
    }

    @Path("/ordenar/{atributo}/{orden}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response ordenarEscalas(@PathParam("atributo") String atributo, @PathParam("orden") String orden) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_escala ce = new Controlador_escala();
            LinkedList<Escala> lista = ce.Lista_escala();
            if (!Arrays.asList("lugar_escala", "tiempo").contains(atributo)) {
                response.put("msg", "Atributo no válido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            lista.quickSort(atributo, orden.equalsIgnoreCase("asc"));
            response.put("msg", "Escalas ordenadas");
            response.put("escalas", lista.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Error al ordenar las escalas");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
    }

    @Path("/buscar/{atributo}/{criterio}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarEscala(@PathParam("atributo") String atributo,
            @PathParam("criterio") String criterio) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_escala ce = new Controlador_escala();
            LinkedList<Escala> lista = ce.Lista_escala();
            LinkedList<Escala> result = lista.binarySearch(atributo, criterio);
            response.put("msg", "Escalas encontradas");
            response.put("escalas", result.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Error al buscar las escalas");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
    }
}
