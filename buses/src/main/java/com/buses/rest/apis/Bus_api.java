package com.buses.rest.apis;

import controlador.servicios.Controlador_cooperativa;
import controlador.servicios.Controlador_bus;
import controlador.tda.lista.LinkedList;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import modelo.enums.Estado_bus;
import javax.ws.rs.PathParam;
import java.util.Collections;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import modelo.Cooperativa;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import java.util.Arrays;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;
import modelo.Bus;

@Path("/bus")
public class Bus_api {

    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_bus() {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_bus cb = new Controlador_bus();
        response.put("msg", "Lista de buses");
        response.put("buses", cb.Lista_buses().toArray());
        if (cb.Lista_buses().isEmpty()) {
            response.put("buses", new Object[] {});
        }
        return Response.ok(response).build();
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getBus(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_bus cb = new Controlador_bus();
        try {
            cb.setBus(cb.get(id));
            response.put("msg", "Bus encontrado");
            response.put("bus", cb.get(id));
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Bus no encontrado");
        }
        if (cb.getBus().getId_bus() == null) {
            response.put("msg", "Bus no encontrado");
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
        Controlador_bus cb = new Controlador_bus();
        Controlador_cooperativa cc = new Controlador_cooperativa();
        try {
            cb.getBus().setNumero_bus(Integer.parseInt(map.get("numero_bus").toString()));
            cb.getBus().setPlaca(map.get("placa").toString());
            cb.getBus().setMarca(map.get("marca").toString());
            cb.getBus().setModelo(map.get("modelo").toString());
            cb.getBus().setCapacidad_pasajeros(Integer.parseInt(map.get("capacidad_pasajeros").toString()));
            cb.getBus().setVelocidad(Integer.parseInt(map.get("velocidad").toString()));
            cb.getBus().setEstado_bus(Estado_bus.valueOf(map.get("estado_bus").toString()));
            Integer cooperativa_id = Integer.parseInt(map.get("cooperativa_id").toString());
            Cooperativa cooperativa = cc.get(cooperativa_id);
            if (cooperativa == null) {
                response.put("msg", "Cooperativa no encontrada");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            cb.getBus().setCooperativa(cooperativa);
            if (cb.save()) {
                response.put("msg", "Bus guardado exitosamente");
                response.put("bus", cb.getBus());
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
        Controlador_bus cb = new Controlador_bus();
        try {
            if (cb.delete(id)) {
                response.put("msg", "Bus eliminado");
                return Response.ok(response).build();
            }
            else {
                response.put("msg", "Error al eliminar el bus");
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al eliminar el bus")).build();
            }
        }
        catch (Exception e) {
            response.put("msg", "Error al eliminar el bus");
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al eliminar el bus")).build();
        }
    }

    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_bus cb = new Controlador_bus();
        Controlador_cooperativa cc = new Controlador_cooperativa();
        if (map.get("id") == null || map.get("numero_bus") == null || map.get("placa") == null
                || map.get("marca") == null || map.get("modelo") == null
                || map.get("capacidad_pasajeros") == null || map.get("velocidad") == null
                || map.get("estado_bus") == null || map.get("cooperativa_id") == null) {
            response.put("msg", "Faltan datos");
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Faltan datos requeridos")).build();
        }
        try {
            cb.getBus().setId_bus(Integer.parseInt(map.get("id").toString()));
            cb.getBus().setNumero_bus(Integer.parseInt(map.get("numero_bus").toString()));
            cb.getBus().setPlaca(map.get("placa").toString());
            cb.getBus().setMarca(map.get("marca").toString());
            cb.getBus().setModelo(map.get("modelo").toString());
            cb.getBus().setCapacidad_pasajeros(Integer.parseInt(map.get("capacidad_pasajeros").toString()));
            cb.getBus().setVelocidad(Integer.parseInt(map.get("velocidad").toString()));
            cb.getBus().setEstado_bus(Estado_bus.valueOf(map.get("estado_bus").toString()));
            Integer cooperativa_id = Integer.parseInt(map.get("cooperativa_id").toString());
            Cooperativa cooperativa = cc.get(cooperativa_id);
            if (cooperativa == null) {
                response.put("msg", "Cooperativa no encontrada");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            cb.getBus().setCooperativa(cooperativa);
            if (cb.update()) {
                response.put("msg", "Bus actualizado");
                response.put("bus", cb.getBus());
                return Response.ok(response).build();
            }
            else {
                response.put("msg", "Error al actualizar el bus");
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al actualizar el bus")).build();
            }
        }
        catch (Exception e) {
            response.put("msg", "Error al actualizar el bus");
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al actualizar el bus")).build();
        }
    }

    @Path("/ordenar/{atributo}/{orden}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response ordenarBuses(@PathParam("atributo") String atributo, @PathParam("orden") String orden) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_bus cb = new Controlador_bus();
            LinkedList<modelo.Bus> lista = cb.Lista_buses();
            if (!Arrays.asList("numero_bus", "placa", "marca", "modelo", "capacidad_pasajeros", "velocidad",
                    "cooperativa.nombre_cooperativa", "estado_bus").contains(atributo)) {
                response.put("mensaje", "Atributo de ordenamiento no válido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            lista.quickSort(atributo, orden.equalsIgnoreCase("asc"));
            response.put("mensaje", "Lista ordenada correctamente");
            response.put("buses", lista.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al ordenar buses: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/buscar/{atributo}/{criterio}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarBuses(@PathParam("atributo") String atributo,
            @PathParam("criterio") String criterio) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_bus cb = new Controlador_bus();
            LinkedList<Bus> lista = cb.Lista_buses();
            LinkedList<Bus> resultados = lista.binarySearch(criterio, atributo);
            response.put("mensaje", "Búsqueda realizada");
            response.put("boletos", resultados.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error en la búsqueda");
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }
}