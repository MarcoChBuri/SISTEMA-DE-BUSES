package com.buses.rest.apis;

import controlador.servicios.Controlador_escala;
import controlador.servicios.Controlador_ruta;
import controlador.servicios.Controlador_bus;
import controlador.dao.utiles.Sincronizar;
import controlador.tda.lista.LinkedList;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import modelo.enums.Estado_ruta;
import javax.ws.rs.PathParam;
import java.util.Collections;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import java.util.ArrayList;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import java.util.Arrays;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;
import modelo.Escala;
import modelo.Ruta;
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
        Controlador_escala ce = new Controlador_escala();
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
            LinkedList<Escala> escalas = new LinkedList<>();
            if (map.containsKey("escalas") && map.get("escalas") != null) {
                ArrayList<HashMap<String, Object>> escalasArray = (ArrayList<HashMap<String, Object>>) map
                        .get("escalas");
                for (HashMap<String, Object> escalaMap : escalasArray) {
                    Escala escala;
                    if (escalaMap.containsKey("id_escala") && escalaMap.get("id_escala") != null) {
                        escala = ce.get(Integer.parseInt(escalaMap.get("id_escala").toString()));
                        if (escala == null) {
                            response.put("msg", "Escala no encontrada: " + escalaMap.get("id_escala"));
                            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
                        }
                    }
                    else {
                        escala = new Escala();
                    }
                    escala.setLugar_escala(escalaMap.get("lugar_escala").toString());
                    escala.setTiempo(escalaMap.get("tiempo").toString());
                    if (escala.getId_escala() == null) {
                        ce.setEscala(escala);
                        ce.save();
                    }
                    else {
                        ce.setEscala(escala);
                        ce.update();
                    }
                    escalas.add(escala);
                }
            }
            cr.getRuta().setEscalas(escalas.isEmpty() ? null : escalas);
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
        try {
            if (!map.containsKey("id_ruta")) {
                response.put("msg", "ID de ruta requerido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            Controlador_ruta cr = new Controlador_ruta();
            Controlador_bus cb = new Controlador_bus();
            cr.setRuta(cr.get(Integer.parseInt(map.get("id_ruta").toString())));
            cr.getRuta().setOrigen(map.get("origen").toString());
            cr.getRuta().setDestino(map.get("destino").toString());
            cr.getRuta().setPrecio_unitario(Float.parseFloat(map.get("precio_unitario").toString()));
            cr.getRuta().setDistancia(Integer.parseInt(map.get("distancia").toString()));
            cr.getRuta().setTiempo_estimado(map.get("tiempo_estimado").toString());
            cr.getRuta().setEstado_ruta(Estado_ruta.valueOf(map.get("estado_ruta").toString()));
            if (map.containsKey("bus")) {
                HashMap<String, Object> busMap = (HashMap<String, Object>) map.get("bus");
                Bus bus = cb.get(Integer.parseInt(busMap.get("id_bus").toString()));
                if (bus == null) {
                    response.put("msg", "Bus no encontrado");
                    return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
                }
                cr.getRuta().setBus(bus);
            }
            LinkedList<Escala> escalasActuales = cr.getRuta().getEscalas();
            if (map.containsKey("escalas")) {
                ArrayList<HashMap<String, Object>> escalasArray = (ArrayList<HashMap<String, Object>>) map
                        .get("escalas");
                if (escalasArray != null && !escalasArray.isEmpty()) {
                    LinkedList<Escala> escalasNuevas = new LinkedList<>();
                    Controlador_escala ce = new Controlador_escala();
                    ArrayList<Integer> nuevosIds = new ArrayList<>();
                    for (HashMap<String, Object> escalaMap : escalasArray) {
                        Escala escala;
                        if (escalaMap.containsKey("id_escala") && escalaMap.get("id_escala") != null) {
                            try {
                                escala = ce.get(Integer.parseInt(escalaMap.get("id_escala").toString()));
                                if (escala == null) {
                                    escala = new Escala();
                                }
                                else {
                                    nuevosIds.add(escala.getId_escala());
                                }
                            }
                            catch (Exception e) {
                                escala = new Escala();
                            }
                        }
                        else {
                            escala = new Escala();
                        }
                        escala.setLugar_escala(escalaMap.get("lugar_escala").toString());
                        escala.setTiempo(escalaMap.get("tiempo").toString());
                        if (escala.getId_escala() == null) {
                            ce.setEscala(escala);
                            ce.save();
                        }
                        else {
                            ce.setEscala(escala);
                            ce.update();
                        }
                        escalasNuevas.add(escala);
                    }
                    if (escalasActuales != null) {
                        for (int i = 0; i < escalasActuales.getSize(); i++) {
                            Escala escalaActual = escalasActuales.get(i);
                            if (!nuevosIds.contains(escalaActual.getId_escala())) {
                                Sincronizar.sincronizarEscalaEliminada(escalaActual.getId_escala());
                            }
                        }
                    }
                    cr.getRuta().setEscalas(escalasNuevas);
                }
                else {
                    if (escalasActuales != null) {
                        for (int i = 0; i < escalasActuales.getSize(); i++) {
                            Sincronizar.sincronizarEscalaEliminada(escalasActuales.get(i).getId_escala());
                        }
                    }
                    cr.getRuta().setEscalas(null);
                }
            }
            else {
                if (escalasActuales != null) {
                    for (int i = 0; i < escalasActuales.getSize(); i++) {
                        Sincronizar.sincronizarEscalaEliminada(escalasActuales.get(i).getId_escala());
                    }
                }
                cr.getRuta().setEscalas(null);
            }
            if (cr.update()) {
                Sincronizar.sincronizarRuta(cr.getRuta());
                response.put("msg", "Ruta actualizada exitosamente");
                response.put("ruta", cr.getRuta());
                return Response.ok(response).build();
            }
            response.put("msg", "Error al actualizar");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Error: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/ordenar/{atributo}/{orden}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response ordenarRutas(@PathParam("atributo") String atributo, @PathParam("orden") String orden) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_ruta cr = new Controlador_ruta();
            LinkedList<Ruta> lista = cr.Lista_rutas();
            if (!Arrays
                    .asList("origen", "destino", "precio_unitario", "distancia", "tiempo_estimado",
                            "bus.placa", "bus.cooperativa.nombre_cooperativa", "estado_ruta")
                    .contains(atributo)) {
                response.put("mensaje", "Atributo de ordenamiento no válido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            lista.quickSort(atributo, orden.equalsIgnoreCase("asc"));
            response.put("mensaje", "Lista ordenada correctamente");
            response.put("rutas", lista.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al ordenar rutas: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/buscar/{atributo}/{criterio}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarRuta(@PathParam("atributo") String atributo,
            @PathParam("criterio") String criterio) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_ruta cr = new Controlador_ruta();
            LinkedList<Ruta> lista = cr.Lista_rutas();
            LinkedList<Ruta> resultados = lista.binarySearch(criterio, atributo);
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