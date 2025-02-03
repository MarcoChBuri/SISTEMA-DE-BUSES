package com.buses.rest.apis;

import controlador.servicios.Controlador_descuento;
import controlador.tda.lista.LinkedList;
import modelo.enums.Estado_descuento;
import controlador.dao.utiles.Fecha;
import modelo.enums.Tipo_descuento;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.PathParam;
import java.util.Collections;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import java.util.Arrays;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import modelo.Descuento;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;

@Path("/descuento")
public class Descuento_api {

    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_descuento() {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_descuento cd = new Controlador_descuento();
        response.put("msg", "Lista de descuentos");
        response.put("descuentos", cd.Lista_descuentos().toArray());
        if (cd.Lista_descuentos().isEmpty()) {
            response.put("descuentos", new Object[] {});
        }
        return Response.ok(response).build();
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getDescuento(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_descuento cd = new Controlador_descuento();
        try {
            cd.setDescuento(cd.get(id));
            response.put("msg", "Descuento encontrado");
            response.put("descuento", cd.get(id));
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Descuento no encontrado");
            return Response.status(Response.Status.NOT_FOUND).entity(response).build();
        }
    }

    @Path("/guardar")
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response save(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_descuento cd = new Controlador_descuento();
        try {
            if (map.get("nombre_descuento") == null || map.get("porcentaje") == null
                    || map.get("estado_descuento") == null) {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Faltan datos requeridos")).build();
            }
            String fechaInicio = Fecha.normalizarFecha(map.get("fecha_inicio").toString());
            String fechaFin = Fecha.normalizarFecha(map.get("fecha_fin").toString());
            cd.getDescuento().setTipo_descuento(Tipo_descuento.Promocional);
            cd.getDescuento().setNombre_descuento(map.get("nombre_descuento").toString());
            cd.getDescuento().setPorcentaje(Integer.parseInt(map.get("porcentaje").toString()));
            cd.getDescuento().setDescripcion(map.get("descripcion").toString());
            cd.getDescuento().setFecha_inicio(fechaInicio);
            cd.getDescuento().setFecha_fin(fechaFin);
            cd.getDescuento()
                    .setEstado_descuento(Estado_descuento.valueOf(map.get("estado_descuento").toString()));
            if (cd.save()) {
                response.put("msg", "Descuento guardado exitosamente");
                response.put("descuento", cd.getDescuento());
                return Response.ok(response).build();
            }
            response.put("msg", "Error al guardar el descuento");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        catch (Exception e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(
                    Collections.singletonMap("error", "Error al guardar el descuento: " + e.getMessage()))
                    .build();
        }
    }

    @Path("/eliminar/{id}")
    @DELETE
    @Produces(MediaType.APPLICATION_JSON)
    public Response delete(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_descuento cd = new Controlador_descuento();
        try {
            if (cd.delete(id)) {
                response.put("msg", "Descuento eliminado");
                return Response.ok(response).build();
            }
            response.put("msg", "Error al eliminar descuento");
            return Response.status(Response.Status.NOT_FOUND).entity(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Error al eliminar descuento");
            return Response.status(Response.Status.NOT_FOUND).entity(response).build();
        }
    }

    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_descuento cd = new Controlador_descuento();
        try {
            cd.setDescuento(cd.get(Integer.parseInt(map.get("id_descuento").toString())));
            Descuento descuentoExistente = cd.getDescuento();
            if (descuentoExistente.getTipo_descuento() == Tipo_descuento.Promocional) {
                if (map.get("fecha_inicio") != null) {
                    descuentoExistente
                            .setFecha_inicio(Fecha.normalizarFecha(map.get("fecha_inicio").toString()));
                }
                if (map.get("fecha_fin") != null) {
                    descuentoExistente.setFecha_fin(Fecha.normalizarFecha(map.get("fecha_fin").toString()));
                }
            }
            descuentoExistente.setNombre_descuento(map.get("nombre_descuento").toString());
            descuentoExistente.setPorcentaje(Integer.parseInt(map.get("porcentaje").toString()));
            descuentoExistente.setDescripcion(map.get("descripcion").toString());
            descuentoExistente
                    .setEstado_descuento(Estado_descuento.valueOf(map.get("estado_descuento").toString()));
            if (cd.update()) {
                response.put("msg", "Descuento actualizado exitosamente");
                response.put("descuento", cd.getDescuento());
                return Response.ok(response).build();
            }
            response.put("msg", "Error al actualizar el descuento");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        catch (Exception e) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR)
                    .entity(Collections.singletonMap("error", "Error al actualizar: " + e.getMessage()))
                    .build();
        }
    }

    @Path("/ordenar/{atributo}/{orden}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response ordenarDescuentos(@PathParam("atributo") String atributo,
            @PathParam("orden") String orden) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_descuento cd = new Controlador_descuento();
            LinkedList<Descuento> lista = cd.Lista_descuentos();
            if (!Arrays.asList("nombre_descuento", "descripcion", "porcentaje", "estado_descuento",
                    "fecha_inicio", "fecha_fin", "tipo_descuento").contains(atributo)) {
                response.put("mensaje", "Atributo de ordenamiento no válido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            lista.quickSort(atributo, orden.equalsIgnoreCase("asc"));
            response.put("mensaje", "Lista ordenada correctamente");
            response.put("descuentos", lista.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al ordenar descuentos: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/buscar/{atributo}/{criterio}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarDescuento(@PathParam("atributo") String atributo,
            @PathParam("criterio") String criterio) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_descuento cd = new Controlador_descuento();
            LinkedList<Descuento> lista = cd.Lista_descuentos();
            LinkedList<Descuento> resultados = lista.binarySearch(criterio, atributo);
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
