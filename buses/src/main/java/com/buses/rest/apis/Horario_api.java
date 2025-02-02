package com.buses.rest.apis;

import controlador.servicios.Controlador_horario;
import controlador.servicios.Controlador_ruta;
import controlador.dao.utiles.Sincronizar;
import controlador.tda.lista.LinkedList;
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
import java.util.Arrays;
import javax.ws.rs.Path;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;
import modelo.Horario;

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
            String horaSalida = map.get("hora_salida").toString();
            String horaLlegada = map.get("hora_llegada").toString();
            HashMap<String, Object> rutaMap = (HashMap<String, Object>) map.get("ruta");
            Integer rutaId = Integer.parseInt(rutaMap.get("id_ruta").toString());
            Ruta ruta = cr.get(rutaId);
            if (ruta == null) {
                response.put("msg", "Ruta no encontrada");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            if (existeSuperposicionHorarios(horaSalida, horaLlegada, ruta.getBus().getId_bus(), null)) {
                response.put("msg", "El bus ya tiene un horario asignado en ese rango de tiempo");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            ch.getHorario().setHora_salida(map.get("hora_salida").toString());
            ch.getHorario().setHora_llegada(map.get("hora_llegada").toString());
            ch.getHorario().setEstado_horario(Estado_horario.valueOf(map.get("estado_horario").toString()));
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
        HashMap<String, Object> response = new HashMap<>();
        Controlador_horario ch = new Controlador_horario();
        Controlador_ruta cr = new Controlador_ruta();
        if (map.get("id_horario") == null || map.get("hora_salida") == null || map.get("hora_llegada") == null
                || map.get("estado_horario") == null || map.get("ruta") == null) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Faltan datos requeridos")).build();
        }
        try {
            Integer horarioId = Integer.parseInt(map.get("id_horario").toString());
            String horaSalida = map.get("hora_salida").toString();
            String horaLlegada = map.get("hora_llegada").toString();
            HashMap<String, Object> rutaMap = (HashMap<String, Object>) map.get("ruta");
            Integer rutaId = Integer.parseInt(rutaMap.get("id_ruta").toString());
            Ruta ruta = cr.get(rutaId);
            if (ruta == null) {
                response.put("msg", "Ruta no encontrada");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            if (existeSuperposicionHorarios(horaSalida, horaLlegada, ruta.getBus().getId_bus(), horarioId)) {
                response.put("msg", "El bus ya tiene un horario asignado en ese rango de tiempo");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            ch.getHorario().setId_horario(Integer.parseInt(map.get("id_horario").toString()));
            ch.getHorario().setHora_salida(map.get("hora_salida").toString());
            ch.getHorario().setHora_llegada(map.get("hora_llegada").toString());
            ch.getHorario().setEstado_horario(Estado_horario.valueOf(map.get("estado_horario").toString()));
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

    @Path("/ordenar/{atributo}/{orden}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response ordenarHorarios(@PathParam("atributo") String atributo,
            @PathParam("orden") String orden) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_horario ch = new Controlador_horario();
            LinkedList<Horario> lista = ch.Lista_horarios();
            if (!Arrays.asList("hora_salida", "hora_llegada", "ruta.origen", "ruta.destino", "ruta.bus.placa",
                    "ruta.bus.cooperativa.nombre_cooperativa", "estado_horario").contains(atributo)) {
                response.put("mensaje", "Atributo de ordenamiento no válido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            lista.quickSort(atributo, orden.equalsIgnoreCase("asc"));
            response.put("mensaje", "Lista ordenada correctamente");
            response.put("horarios", lista.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al ordenar horarios: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/buscar/{atributo}/{criterio}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarHorario(@PathParam("atributo") String atributo,
            @PathParam("criterio") String criterio) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_horario ch = new Controlador_horario();
            LinkedList<Horario> lista = ch.Lista_horarios();
            LinkedList<Horario> resultados = lista.binarySearch(criterio, atributo);
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

    private boolean existeSuperposicionHorarios(String horaSalida, String horaLlegada, Integer busId,
            Integer horarioId) {
        try {
            Controlador_horario ch = new Controlador_horario();
            LinkedList<Horario> horarios = ch.Lista_horarios();
            int nuevaSalida = convertirHoraAMinutos(horaSalida);
            int nuevaLlegada = convertirHoraAMinutos(horaLlegada);
            for (int i = 0; i < horarios.getSize(); i++) {
                Horario horario = horarios.get(i);
                if (horarioId != null && horario.getId_horario().equals(horarioId)) {
                    continue;
                }
                if (horario.getRuta().getBus().getId_bus().equals(busId)
                        && horario.getRuta().getId_ruta().equals(horarioId)) {
                    int existenteSalida = convertirHoraAMinutos(horario.getHora_salida());
                    int existenteLlegada = convertirHoraAMinutos(horario.getHora_llegada());
                    if (!(nuevaLlegada <= existenteSalida || nuevaSalida >= existenteLlegada)) {
                        return true;
                    }
                }
            }
            return false;
        }
        catch (Exception e) {
            return false;
        }
    }

    private int convertirHoraAMinutos(String hora) {
        String[] partes = hora.split(":");
        return Integer.parseInt(partes[0]) * 60 + Integer.parseInt(partes[1]);
    }
}