package com.buses.rest.apis;

import controlador.servicios.Controlador_horario;
import controlador.servicios.Controlador_turno;
import controlador.dao.utiles.Sincronizar;
import controlador.tda.lista.LinkedList;
import controlador.dao.utiles.Fecha;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import modelo.enums.Estado_turno;
import javax.ws.rs.PathParam;
import java.util.Collections;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import java.util.Arrays;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;
import modelo.Horario;
import modelo.Turno;

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
            String fechaNormalizada = Fecha.normalizarFecha(fechaOriginal);
            ct.getTurno().setFecha_salida(fechaNormalizada);
            ct.getTurno().setNumero_turno(Integer.parseInt(map.get("numero_turno").toString()));
            ct.getTurno().setEstado_turno(Estado_turno.valueOf(map.get("estado_turno").toString()));
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
            String fechaNormalizada = Fecha.normalizarFecha(map.get("fecha_salida").toString());
            ct.getTurno().setId_turno(Integer.parseInt(map.get("id_turno").toString()));
            ct.getTurno().setFecha_salida(fechaNormalizada);
            ct.getTurno().setNumero_turno(Integer.parseInt(map.get("numero_turno").toString()));
            ct.getTurno().setEstado_turno(Estado_turno.valueOf(map.get("estado_turno").toString()));
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

    @Path("/ordenar/{atributo}/{orden}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response ordenarTurnos(@PathParam("atributo") String atributo, @PathParam("orden") String orden) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_turno ct = new Controlador_turno();
            LinkedList<modelo.Turno> lista = ct.Lista_turnos();
            if (!Arrays
                    .asList("numero_turno", "fecha_salida", "horario.hora_salida", "horario.hora_llegada",
                            "horario.ruta.origen", "horario.ruta.destino", "horario.ruta.bus.placa",
                            "horario.ruta.bus.cooperativa.nombre_cooperativa", "estado_turno")
                    .contains(atributo)) {
                response.put("mensaje", "Atributo de ordenamiento no válido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            lista.quickSort(atributo, orden.equalsIgnoreCase("asc"));
            response.put("mensaje", "Lista ordenada correctamente");
            response.put("turnos", lista.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al ordenar turnos: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/buscar/{atributo}/{criterio}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarTurno(@PathParam("atributo") String atributo,
            @PathParam("criterio") String criterio) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_turno ct = new Controlador_turno();
            LinkedList<Turno> lista = ct.Lista_turnos();
            LinkedList<Turno> resultados = lista.binarySearch(criterio, atributo);
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