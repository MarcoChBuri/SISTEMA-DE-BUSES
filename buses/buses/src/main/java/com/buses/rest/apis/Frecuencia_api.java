package com.buses.rest.apis;

import controlador.servicios.Controlador_frecuencia;
import controlador.servicios.Controlador_horario;
import controlador.tda.lista.LinkedList;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.PathParam;
import java.util.Collections;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import modelo.Frecuencia;
import java.util.Arrays;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;
import modelo.Horario;

@Path("/frecuencia")
public class Frecuencia_api {

    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_frecuencia() {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_frecuencia cf = new Controlador_frecuencia();
        response.put("msg", "Lista de frecuencias");
        response.put("frecuencias", cf.Lista_frecuencias().toArray());
        if (cf.Lista_frecuencias().isEmpty()) {
            response.put("frecuencias", new Object[] {});
        }
        return Response.ok(response).build();
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getFrecuencia(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_frecuencia cf = new Controlador_frecuencia();
        try {
            cf.setFrecuencia(cf.get(id));
            response.put("msg", "Frecuencia encontrada");
            response.put("frecuencia", cf.get(id));
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Frecuencia no encontrada");
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
        Controlador_frecuencia cf = new Controlador_frecuencia();
        Controlador_horario ch = new Controlador_horario();
        try {
            cf.getFrecuencia()
                    .setNumero_repeticiones(Integer.parseInt(map.get("numero_repeticiones").toString()));
            cf.getFrecuencia().setPeriodo(map.get("periodo").toString());
            cf.getFrecuencia().setPrecio_recorrido(Float.parseFloat(map.get("precio_recorrido").toString()));
            HashMap<String, Object> horarioMap = (HashMap<String, Object>) map.get("horario");
            Integer horarioId = Integer.parseInt(horarioMap.get("id_horario").toString());
            Horario horario = ch.get(horarioId);
            if (horario == null) {
                response.put("msg", "Horario no encontrado");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            cf.getFrecuencia().setHorario(horario);
            if (cf.save()) {
                response.put("msg", "Frecuencia guardada exitosamente");
                response.put("frecuencia", cf.getFrecuencia());
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
        Controlador_frecuencia cf = new Controlador_frecuencia();
        try {
            if (cf.delete(id)) {
                response.put("msg", "Frecuencia eliminada");
                return Response.ok(response).build();
            }
            else {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al eliminar la frecuencia")).build();
            }
        }
        catch (Exception e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al eliminar la frecuencia")).build();
        }
    }

    @SuppressWarnings("unchecked")
    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_frecuencia cf = new Controlador_frecuencia();
        Controlador_horario ch = new Controlador_horario();
        if (map.get("id_frecuencia") == null || map.get("numero_repeticiones") == null
                || map.get("periodo") == null || map.get("precio_recorrido") == null
                || map.get("horario") == null) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Faltan datos requeridos")).build();
        }
        try {
            cf.getFrecuencia().setId_frecuencia(Integer.parseInt(map.get("id_frecuencia").toString()));
            cf.getFrecuencia()
                    .setNumero_repeticiones(Integer.parseInt(map.get("numero_repeticiones").toString()));
            cf.getFrecuencia().setPeriodo(map.get("periodo").toString());
            cf.getFrecuencia().setPrecio_recorrido(Float.parseFloat(map.get("precio_recorrido").toString()));
            HashMap<String, Object> horarioMap = (HashMap<String, Object>) map.get("horario");
            Integer horarioId = Integer.parseInt(horarioMap.get("id_horario").toString());
            Horario horario = ch.get(horarioId);
            if (horario == null) {
                response.put("msg", "Horario no encontrado");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            cf.getFrecuencia().setHorario(horario);
            if (cf.update()) {
                response.put("msg", "Frecuencia actualizada");
                response.put("frecuencia", cf.getFrecuencia());
                return Response.ok(response).build();
            }
            else {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al actualizar la frecuencia"))
                        .build();
            }
        }
        catch (Exception e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al actualizar la frecuencia")).build();
        }
    }

    @Path("/ordenar/{atributo}/{orden}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response ordenarFrecuencias(@PathParam("atributo") String atributo,
            @PathParam("orden") String orden) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_frecuencia cf = new Controlador_frecuencia();
            LinkedList<Frecuencia> lista = cf.Lista_frecuencias();
            if (!Arrays.asList("numero_repeticiones", "periodo", "precio_recorrido", "horario.hora_llegada")
                    .contains(atributo)) {
                response.put("mensaje", "Atributo de ordenamiento no válido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            lista.quickSort(atributo, orden.equalsIgnoreCase("asc"));
            response.put("mensaje", "Lista ordenada correctamente");
            response.put("frecuencias", lista.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al ordenar frecuencias: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/buscar/{atributo}/{criterio}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarFrecuencia(@PathParam("atributo") String atributo,
            @PathParam("criterio") String criterio) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_frecuencia cd = new Controlador_frecuencia();
            LinkedList<Frecuencia> lista = cd.Lista_frecuencias();
            LinkedList<Frecuencia> resultados = lista.binarySearch(criterio, atributo);
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