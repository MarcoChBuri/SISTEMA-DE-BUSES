package com.buses.rest.apis;

import controlador.servicios.Controlador_ruta;
import controlador.servicios.Controlador_bus;
import controlador.dao.utiles.Sincronizar;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import modelo.enums.Estado_ruta;
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
import modelo.Bus;

@Path("/ruta")
public class Ruta_api {

    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_ruta() {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_ruta cr = new Controlador_ruta();
        response.put("msg", "Lista de rutas");
        response.put("rutas", cr.Lista_rutas().toArray());
        if (cr.Lista_rutas().isEmpty()) {
            response.put("rutas", new Object[] {});
        }
        return Response.ok(response).build();
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getRuta(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_ruta cr = new Controlador_ruta();
        try {
            cr.setRuta(cr.get(id));
            response.put("msg", "Ruta encontrada");
            response.put("ruta", cr.get(id));
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Ruta no encontrada");
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
        Controlador_ruta cr = new Controlador_ruta();
        Controlador_bus cb = new Controlador_bus();
        try {
            cr.getRuta().setOrigen(map.get("origen").toString());
            cr.getRuta().setDestino(map.get("destino").toString());
            cr.getRuta().setPrecio_unitario(Float.parseFloat(map.get("precio_unitario").toString()));
            cr.getRuta().setDistancia(Integer.parseInt(map.get("distancia").toString()));
            cr.getRuta().setTiempo_estimado(map.get("tiempo_estimado").toString());
            cr.getRuta().setEstado_ruta(Estado_ruta.valueOf(map.get("estado_ruta").toString()));
            HashMap<String, Object> busMap = (HashMap<String, Object>) map.get("bus");
            Integer busId = Integer.parseInt(busMap.get("id_bus").toString());
            Bus bus = cb.get(busId);
            if (bus == null) {
                response.put("msg", "Bus no encontrado");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            cr.getRuta().setBus(bus);
            if (cr.save()) {
                response.put("msg", "Ruta guardada exitosamente");
                response.put("ruta", cr.getRuta());
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
        Controlador_ruta cr = new Controlador_ruta();
        try {
            if (cr.delete(id)) {
                response.put("msg", "Ruta eliminada");
                return Response.ok(response).build();
            }
            else {
                response.put("msg", "Error al eliminar la ruta");
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al eliminar la ruta")).build();
            }
        }
        catch (Exception e) {
            response.put("msg", "Error al eliminar la ruta");
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al eliminar la ruta")).build();
        }
    }

    @SuppressWarnings("unchecked")
    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_ruta cr = new Controlador_ruta();
        Controlador_bus cb = new Controlador_bus();
        if (map.get("id_ruta") == null || map.get("origen") == null || map.get("destino") == null
                || map.get("distancia") == null || map.get("tiempo_estimado") == null
                || map.get("estado_ruta") == null || map.get("bus") == null) {
            response.put("msg", "Faltan datos");
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Faltan datos requeridos")).build();
        }
        try {
            cr.getRuta().setId_ruta(Integer.parseInt(map.get("id_ruta").toString()));
            cr.getRuta().setOrigen(map.get("origen").toString());
            cr.getRuta().setDestino(map.get("destino").toString());
            cr.getRuta().setPrecio_unitario(Float.parseFloat(map.get("precio_unitario").toString()));
            cr.getRuta().setDistancia(Integer.parseInt(map.get("distancia").toString()));
            cr.getRuta().setTiempo_estimado(map.get("tiempo_estimado").toString());
            cr.getRuta().setEstado_ruta(Estado_ruta.valueOf(map.get("estado_ruta").toString()));
            HashMap<String, Object> busMap = (HashMap<String, Object>) map.get("bus");
            Integer busId = Integer.parseInt(busMap.get("id_bus").toString());
            Bus bus = cb.get(busId);
            if (bus == null) {
                response.put("msg", "Bus no encontrado");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            cr.getRuta().setBus(bus);
            if (cr.update()) {
                Sincronizar.sincronizarRuta(cr.getRuta());
                response.put("msg", "Ruta actualizada");
                response.put("ruta", cr.getRuta());
                return Response.ok(response).build();
            }
            else {
                response.put("msg", "Error al actualizar la ruta");
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al actualizar la ruta")).build();
            }
        }
        catch (Exception e) {
            response.put("msg", "Error al actualizar la ruta");
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al actualizar la ruta")).build();
        }
    }
}