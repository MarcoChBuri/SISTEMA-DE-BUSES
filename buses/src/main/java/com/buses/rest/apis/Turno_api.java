package com.buses.rest.apis;

import controlador.servicios.Controlador_horario;
import controlador.servicios.Controlador_turno;
import controlador.dao.utiles.Sincronizar;
import java.text.SimpleDateFormat;
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
import modelo.Horario;
import java.util.Date;


@Path("/turno")
public class Turno_api {

    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_turno() {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_turno ct = new Controlador_turno();
        response.put("msg", "Lista de turnos");
        response.put("turnos", ct.Lista_turnos().toArray());
        if (ct.Lista_turnos().isEmpty()) {
            response.put("turnos", new Object[] {});
        }
        return Response.ok(response).build();
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getTurno(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_turno ct = new Controlador_turno();
        try {
            ct.setTurno(ct.get(id));
            response.put("msg", "Turno encontrado");
            response.put("turno", ct.get(id));
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Turno no encontrado");
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
        Controlador_turno ct = new Controlador_turno();
        Controlador_horario ch = new Controlador_horario();
        try {
            String fechaOriginal = map.get("fecha_salida").toString();
            SimpleDateFormat formatoEntrada = new SimpleDateFormat("yyyy-MM-dd");
            SimpleDateFormat formatoSalida = new SimpleDateFormat("dd/MM/yyyy");
            Date fecha = formatoEntrada.parse(fechaOriginal);
            String fechaFormateada = formatoSalida.format(fecha);
            ct.getTurno().setFecha_salida(fechaFormateada);
            ct.getTurno().setNumero_turno(Integer.parseInt(map.get("numero_turno").toString()));
            HashMap<String, Object> horarioMap = (HashMap<String, Object>) map.get("horario");
            Integer horarioId = Integer.parseInt(horarioMap.get("id_horario").toString());
            Horario horario = ch.get(horarioId);
            if (horario == null) {
                response.put("msg", "Horario no encontrado");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            ct.getTurno().setHorario(horario);
            if (ct.save()) {
                response.put("msg", "Turno guardado exitosamente");
                response.put("turno", ct.getTurno());
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
        Controlador_turno ct = new Controlador_turno();
        try {
            if (ct.delete(id)) {
                response.put("msg", "Turno eliminado");
                return Response.ok(response).build();
            }
            else {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al eliminar el turno")).build();
            }
        }
        catch (Exception e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al eliminar el turno")).build();
        }
    }

    @SuppressWarnings("unchecked")
    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_turno ct = new Controlador_turno();
        Controlador_horario ch = new Controlador_horario();
        if (map.get("id_turno") == null || map.get("numero_turno") == null || map.get("fecha_salida") == null
                || map.get("horario") == null) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Faltan datos requeridos")).build();
        }
        try {
            String fechaOriginal = map.get("fecha_salida").toString();
            SimpleDateFormat formatoEntrada = new SimpleDateFormat("yyyy-MM-dd");
            SimpleDateFormat formatoSalida = new SimpleDateFormat("dd/MM/yyyy");
            Date fecha = formatoEntrada.parse(fechaOriginal);
            String fechaFormateada = formatoSalida.format(fecha);
            ct.getTurno().setId_turno(Integer.parseInt(map.get("id_turno").toString()));
            ct.getTurno().setFecha_salida(fechaFormateada);
            ct.getTurno().setNumero_turno(Integer.parseInt(map.get("numero_turno").toString()));
            HashMap<String, Object> horarioMap = (HashMap<String, Object>) map.get("horario");
            Integer horarioId = Integer.parseInt(horarioMap.get("id_horario").toString());
            Horario horario = ch.get(horarioId);
            if (horario == null) {
                response.put("msg", "Horario no encontrado");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            ct.getTurno().setHorario(horario);
            if (ct.update()) {
                Sincronizar.sincronizarTurno(ct.getTurno());
                response.put("msg", "Turno actualizado exitosamente");
                response.put("turno", ct.getTurno());
                return Response.ok(response).build();
            }
            response.put("msg", "Error al actualizar el turno");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        catch (Exception e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al actualizar el turno")).build();
        }
    }
}