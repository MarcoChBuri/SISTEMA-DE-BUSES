package com.buses.rest.apis;

import controlador.servicios.Controlador_persona;
import controlador.servicios.Controlador_boleto;
import controlador.servicios.Controlador_turno;
import java.text.SimpleDateFormat;
import modelo.enums.Estado_boleto;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import javax.ws.rs.PathParam;
import java.util.Collections;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import java.util.ArrayList;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import java.util.HashSet;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PUT;
import javax.ws.rs.GET;
import modelo.Persona;
import java.util.Date;
import java.util.List;
import modelo.Boleto;
import modelo.Turno;

@Path("/boleto")
public class Boleto_api {

    @Path("/lista")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getLista_boleto() {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_boleto cb = new Controlador_boleto();
        response.put("msg", "Lista de boletos");
        response.put("boletos", cb.Lista_boletos().toArray());
        if (cb.Lista_boletos().isEmpty()) {
            response.put("boletos", new Object[] {});
        }
        return Response.ok(response).build();
    }

    @Path("/lista/{id}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getBoleto(@PathParam("id") Integer id) {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_boleto cb = new Controlador_boleto();
        try {
            cb.setBoleto(cb.get(id));
            response.put("msg", "Boleto encontrado");
            response.put("boleto", cb.getBoleto());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Boleto no encontrado");
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
        Controlador_boleto cb = new Controlador_boleto();
        Controlador_persona cp = new Controlador_persona();
        Controlador_turno ct = new Controlador_turno();
        try {
            if (!map.containsKey("asientos") || !(map.get("asientos") instanceof java.util.List)) {
                response.put("msg", "Debe especificar los números de asiento");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            List<Integer> asientos = (List<Integer>) map.get("asientos");
            float precioUnitario = Float.parseFloat(map.get("precio_unitario").toString());
            if (asientos.size() != new HashSet<>(asientos).size()) {
                response.put("msg", "No se permiten asientos duplicados");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            HashMap<String, Object> personaMap = (HashMap<String, Object>) map.get("persona");
            Integer personaId = Integer.parseInt(personaMap.get("id_persona").toString());
            Persona persona = cp.get(personaId);
            HashMap<String, Object> turnoMap = (HashMap<String, Object>) map.get("turno");
            Integer turnoId = Integer.parseInt(turnoMap.get("id_turno").toString());
            Turno turno = ct.get(turnoId);
            if (persona == null || turno == null) {
                response.put("msg", "Persona o turno no encontrados");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            int capacidadBus = turno.getHorario().getRuta().getBus().getCapacidad_pasajeros();
            for (Integer asiento : asientos) {
                if (asiento < 1 || asiento > capacidadBus) {
                    response.put("msg", "Número de asiento inválido: " + asiento);
                    return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
                }
            }
            SimpleDateFormat formatoFecha = new SimpleDateFormat("dd/MM/yyyy");
            String fechaCompra = formatoFecha.format(new Date());
            List<Boleto> boletosCreados = new ArrayList<>();
            for (Integer asiento : asientos) {
                Boleto boleto = new Boleto();
                boleto.setFecha_compra(fechaCompra);
                boleto.setNumero_asiento(asiento);
                boleto.setCantidad_boleto(1);
                boleto.setPrecio_final(precioUnitario);
                boleto.setEstado_boleto(Estado_boleto.Vendido);
                boleto.setPersona(persona);
                boleto.setTurno(turno);
                cb.setBoleto(boleto);
                if (cb.save()) {
                    boletosCreados.add(boleto);
                }
                else {
                    for (Boleto boletoCreado : boletosCreados) {
                        cb.delete(boletoCreado.getId_boleto());
                    }
                    response.put("msg", "Error al guardar los boletos");
                    return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
                }
            }
            response.put("msg", "Boletos guardados exitosamente");
            response.put("boletos", boletosCreados);
            response.put("total", precioUnitario * asientos.size());
            return Response.ok(response).build();
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
        Controlador_boleto cb = new Controlador_boleto();
        try {
            if (cb.delete(id)) {
                response.put("msg", "Boleto eliminado");
                return Response.ok(response).build();
            }
            else {
                return Response.status(Response.Status.BAD_REQUEST)
                        .entity(Collections.singletonMap("error", "Error al eliminar el boleto")).build();
            }
        }
        catch (Exception e) {
            return Response.status(Response.Status.BAD_REQUEST)
                    .entity(Collections.singletonMap("error", "Error al eliminar el boleto")).build();
        }
    }

    @Path("/actualizar")
    @PUT
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(HashMap<String, Object> map) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_boleto cb = new Controlador_boleto();
            Controlador_persona cp = new Controlador_persona();
            Controlador_turno ct = new Controlador_turno();
            if (map.get("asientos") == null || map.get("precio_final") == null
                    || map.get("persona_id") == null || map.get("turno_id") == null
                    || map.get("id_boleto") == null) {
                response.put("msg", "Faltan datos requeridos");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            Integer idBoleto = Integer.parseInt(map.get("id_boleto").toString());
            Boleto boleto = cb.get(idBoleto);
            if (boleto == null) {
                response.put("msg", "Boleto no encontrado");
                return Response.status(Response.Status.NOT_FOUND).entity(response).build();
            }
            String asientosStr = map.get("asientos").toString();
            Integer personaId = Integer.parseInt(map.get("persona_id").toString());
            Integer turnoId = Integer.parseInt(map.get("turno_id").toString());
            Persona persona = cp.get(personaId);
            Turno turno = ct.get(turnoId);
            if (persona == null || turno == null) {
                response.put("msg", "Persona o turno no encontrado");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            Float precioUnitario = turno.getHorario().getRuta().getPrecio_unitario();
            String[] asientosArray = asientosStr.split(",");
            int numeroAsiento = Integer.parseInt(asientosArray[0].trim());
            int cantidadBoletos = asientosArray.length;
            boleto.setNumero_asiento(numeroAsiento);
            boleto.setCantidad_boleto(cantidadBoletos);
            boleto.setPrecio_final(precioUnitario * cantidadBoletos);
            boleto.setPersona(persona);
            boleto.setTurno(turno);
            boleto.setFecha_compra(new SimpleDateFormat("dd/MM/yyyy").format(new Date()));
            cb.setBoleto(boleto);
            if (cb.update()) {
                response.put("msg", "Boleto actualizado exitosamente");
                response.put("boleto", boleto);
                return Response.ok(response).build();
            }
            response.put("msg", "Error al actualizar el boleto");
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        catch (NumberFormatException e) {
            response.put("msg", "Error en el formato de los datos: " + e.getMessage());
            return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
        }
        catch (Exception e) {
            response.put("msg", "Error: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }
}