package com.buses.rest.apis;

import controlador.servicios.Controlador_horario;
import controlador.servicios.Controlador_ruta;
import controlador.dao.utiles.Sincronizar;
import modelo.enums.Estado_horario;
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
import modelo.Ruta;

@Path("/horario")
public class Horario_api {

    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_horario() {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_horario ch = new Controlador_horario();
        response.put("msg", "Lista de horarios");
        response.put("horarios", ch.Lista_horarios().toArray());
        if (ch.Lista_horarios().isEmpty()) {
            response.put("horarios", new Object[] {});
        }
        return Response.ok(response).build();
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getHorario(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_horario ch = new Controlador_horario();
        try {
            ch.setHorario(ch.get(id));
            response.put("msg", "Horario encontrado");
            response.put("horario", ch.get(id));
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Horario no encontrado");
            return Response.status(Response.Status.NOT_FOUND).entity(response).build();
        }
    }

    @SuppressWarnings("unchecked")
    @Path("/guardar")
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response save(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_horario ch = new Controlador_horario();
        Controlador_ruta cr = new Controlador_ruta();
        try {
            ch.getHorario().setHora_salida(map.get("hora_salida").toString());
            ch.getHorario().setHora_llegada(map.get("hora_llegada").toString());
            ch.getHorario().setEstado_horario(Estado_horario.valueOf(map.get("estado_horario").toString()));
            HashMap<String, Object> rutaMap = (HashMap<String, Object>) map.get("ruta");
            Integer rutaId = Integer.parseInt(rutaMap.get("id_ruta").toString());
            Ruta ruta = cr.get(rutaId);
            if (ruta == null) {
                response.put("msg", "Ruta no encontrada");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            ch.getHorario().setRuta(ruta);
            if (ch.save()) {
                response.put("msg", "Horario guardado exitosamente");
                response.put("horario", ch.getHorario());
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
        Controlador_horario ch = new Controlador_horario();
        try {
            if (ch.delete(id)) {
                response.put("msg", "Horario eliminado");
                return Response.ok(response).build();
            }
            else {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al eliminar el horario")).build();
            }
        }
        catch (Exception e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al eliminar el horario")).build();
        }
    }

    @SuppressWarnings("unchecked")
    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        System.out.println(map);
        HashMap<String, Object> response = new HashMap<>();
        Controlador_horario ch = new Controlador_horario();
        Controlador_ruta cr = new Controlador_ruta();
        if (map.get("id_horario") == null || map.get("hora_salida") == null
                || map.get("hora_llegada") == null || map.get("estado_horario") == null
                || map.get("ruta") == null) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Faltan datos requeridos")).build();
        }
        try {
            ch.getHorario().setId_horario(Integer.parseInt(map.get("id_horario").toString()));
            ch.getHorario().setHora_salida(map.get("hora_salida").toString());
            ch.getHorario().setHora_llegada(map.get("hora_llegada").toString());
            ch.getHorario().setEstado_horario(Estado_horario.valueOf(map.get("estado_horario").toString()));
            HashMap<String, Object> rutaMap = (HashMap<String, Object>) map.get("ruta");
            Integer rutaId = Integer.parseInt(rutaMap.get("id_ruta").toString());
            Ruta ruta = cr.get(rutaId);
            if (ruta == null) {
                response.put("msg", "Ruta no encontrada");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            ch.getHorario().setRuta(ruta);
            if (ch.update()) {
                Sincronizar.sincronizarHorario(ch.getHorario());
                response.put("msg", "Horario actualizado");
                response.put("horario", ch.getHorario());
                return Response.ok(response).build();
            }
            else {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al actualizar el horario")).build();
            }
        }
        catch (Exception e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al actualizar el horario")).build();
        }
    }
}