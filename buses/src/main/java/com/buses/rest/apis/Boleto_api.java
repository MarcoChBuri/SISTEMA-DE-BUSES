package com.buses.rest.apis;

import controlador.servicios.Controlador_descuento;
import controlador.servicios.Controlador_persona;
import controlador.servicios.Controlador_boleto;
import controlador.servicios.Controlador_turno;
import controlador.dao.modelo_dao.Turno_dao;
import controlador.tda.lista.LinkedList;
import modelo.enums.Estado_descuento;
import modelo.enums.Tipo_descuento;
import javax.ws.rs.core.MediaType;
import java.text.SimpleDateFormat;
import modelo.enums.Estado_boleto;
import javax.ws.rs.core.Response;
import javax.ws.rs.PathParam;
import java.util.Collections;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import java.util.ArrayList;
import javax.ws.rs.DELETE;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Arrays;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import modelo.Descuento;
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
        Controlador_descuento cd = new Controlador_descuento();
        try {
            SimpleDateFormat formatoFecha = new SimpleDateFormat("dd/MM/yyyy");
            String fechaCompra = formatoFecha.format(new Date());
            List<Boleto> boletosCreados = new ArrayList<>();
            HashMap<String, Object> personaMap = (HashMap<String, Object>) map.get("persona");
            HashMap<String, Object> turnoMap = (HashMap<String, Object>) map.get("turno");
            Integer personaId = Integer.parseInt(personaMap.get("id_persona").toString());
            Integer turnoId = Integer.parseInt(turnoMap.get("id_turno").toString());
            Persona persona = cp.get(personaId);
            Turno turno = ct.get(turnoId);
            List<Integer> asientos = (List<Integer>) map.get("asientos");
            float precioUnitarioOriginal = Float.parseFloat(map.get("precio_unitario").toString());
            float precioUnitario = precioUnitarioOriginal;
            Descuento descuentoAplicable = obtenerMejorDescuento(persona, cd.Lista_descuentos());
            if (descuentoAplicable != null
                    && descuentoAplicable.getEstado_descuento() == Estado_descuento.Activo) {
                float porcentajeDescuento = descuentoAplicable.getPorcentaje() / 100f;
                precioUnitario = precioUnitario * (1 - porcentajeDescuento);
            }
            float costoTotal = precioUnitario * asientos.size();
            int capacidadBus = turno.getHorario().getRuta().getBus().getCapacidad_pasajeros();
            if (!map.containsKey("asientos") || !(map.get("asientos") instanceof java.util.List)) {
                response.put("msg", "Debe especificar los números de asiento");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            if (asientos.size() != new HashSet<>(asientos).size()) {
                response.put("msg", "No se permiten asientos duplicados");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            if (persona == null || turno == null) {
                response.put("msg", "Persona o turno no encontrados");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            if (persona.getSaldo_disponible() < costoTotal) {
                response.put("msg", "Saldo insuficiente para comprar los boletos");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            for (Integer asiento : asientos) {
                if (asiento < 1 || asiento > capacidadBus) {
                    response.put("msg", "Número de asiento inválido: " + asiento);
                    return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
                }
            }
            for (Integer asiento : asientos) {
                Boleto boleto = new Boleto();
                boleto.setFecha_compra(fechaCompra);
                boleto.setNumero_asiento(asiento);
                boleto.setCantidad_boleto(1);
                boleto.setPrecio_final(precioUnitario);
                boleto.setEstado_boleto(Estado_boleto.Vendido);
                boleto.setPersona(persona);
                boleto.setTurno(turno);
                if (descuentoAplicable != null) {
                    boleto.setDescuento(descuentoAplicable);
                }
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
            float nuevoSaldo = persona.getSaldo_disponible() - costoTotal;
            persona.setSaldo_disponible(nuevoSaldo);
            cp.setPersona(persona);
            if (!cp.update()) {
                for (Boleto boletoCreado : boletosCreados) {
                    cb.delete(boletoCreado.getId_boleto());
                }
                response.put("msg", "Error al actualizar el saldo");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            if (!boletosCreados.isEmpty()) {
                Turno_dao turnoDao = new Turno_dao();
                Integer idTurno = boletosCreados.get(0).getTurno().getId_turno();
                turnoDao.verificarYActualizarEstadoTurno(idTurno);
            }
            response.put("msg", "Boletos guardados exitosamente");
            response.put("boletos", boletosCreados);
            response.put("total", costoTotal);
            response.put("saldo_restante", nuevoSaldo);
            if (descuentoAplicable != null) {
                response.put("descuento_aplicado", descuentoAplicable);
                response.put("precio_original", precioUnitarioOriginal * asientos.size());
                response.put("ahorro", (precioUnitarioOriginal * asientos.size()) - costoTotal);
            }
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

    @Path("/ordenar/{atributo}/{orden}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response ordenarBoletos(@PathParam("atributo") String atributo, @PathParam("orden") String orden) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_boleto cb = new Controlador_boleto();
            LinkedList<Boleto> lista = cb.Lista_boletos();
            if (!Arrays.asList("fecha_compra", "turno.fecha_salida", "turno.horario.hora_salida",
                    "numero_asiento", "precio_final", "persona.nombre_completo", "turno.numero_turno",
                    "turno.horario.ruta.origen", "turno.horario.ruta.destino", "turno.horario.ruta.bus.placa",
                    "turno.horario.ruta.bus.cooperativa.nombre_cooperativa", "estado_boleto")
                    .contains(atributo)) {
                response.put("mensaje", "Atributo de ordenamiento no válido");
                return Response.status(Response.Status.BAD_REQUEST).entity(response).build();
            }
            lista.quickSort(atributo, orden.equalsIgnoreCase("asc"));
            response.put("mensaje", "Lista ordenada correctamente");
            response.put("boletos", lista.toArray());
            return Response.ok(response).build();
        }
        catch (Exception e) {
            response.put("mensaje", "Error al ordenar boletos: " + e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
    }

    @Path("/buscar/{atributo}/{criterio}")
    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response buscarBoletos(@PathParam("atributo") String atributo,
            @PathParam("criterio") String criterio) {
        HashMap<String, Object> response = new HashMap<>();
        try {
            Controlador_boleto cb = new Controlador_boleto();
            LinkedList<Boleto> lista = cb.Lista_boletos();
            LinkedList<Boleto> resultados = lista.binarySearch(criterio, atributo);
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

    private Descuento obtenerMejorDescuento(Persona persona, LinkedList<Descuento> descuentos)
            throws Exception {
        Descuento descuentoBase = null;
        Descuento descuentoPromocional = null;
        for (int i = 0; i < descuentos.getSize(); i++) {
            Descuento descuento = descuentos.get(i);
            if (descuento.getEstado_descuento() != Estado_descuento.Activo) {
                continue;
            }
            if (descuento.getTipo_descuento().toString().equals(persona.getTipo_tarifa().toString())) {
                descuentoBase = descuento;
            }
            else if (descuento.getTipo_descuento() == Tipo_descuento.Promocional
                    && esDescuentoVigente(descuento)) {
                if (descuentoPromocional == null
                        || descuento.getPorcentaje() > descuentoPromocional.getPorcentaje()) {
                    descuentoPromocional = descuento;
                }
            }
        }
        if (descuentoBase != null && descuentoPromocional != null) {
            return combinarDescuentos(descuentoBase, descuentoPromocional);
        }
        return descuentoBase != null ? descuentoBase : descuentoPromocional;
    }

    private Descuento combinarDescuentos(Descuento descuentoBase, Descuento descuentoPromocional) {
        Descuento descuentoCombinado = new Descuento();
        descuentoCombinado.setId_descuento(descuentoBase.getId_descuento());
        descuentoCombinado.setNombre_descuento(
                descuentoBase.getNombre_descuento() + " + " + descuentoPromocional.getNombre_descuento());
        descuentoCombinado.setDescripcion("Descuento combinado");
        descuentoCombinado.setTipo_descuento(descuentoBase.getTipo_descuento());
        int porcentajeCombinado = descuentoBase.getPorcentaje() + descuentoPromocional.getPorcentaje();
        descuentoCombinado.setPorcentaje(Math.min(porcentajeCombinado, 100)); // Máximo 100%
        descuentoCombinado.setEstado_descuento(Estado_descuento.Activo);
        descuentoCombinado.setFecha_inicio(descuentoPromocional.getFecha_inicio());
        descuentoCombinado.setFecha_fin(descuentoPromocional.getFecha_fin());
        return descuentoCombinado;
    }

    private boolean esDescuentoVigente(Descuento descuento) {
        if (descuento.getFecha_inicio() == null || descuento.getFecha_fin() == null) {
            return false;
        }
        try {
            SimpleDateFormat sdf = new SimpleDateFormat("dd/MM/yyyy");
            Date fechaActual = new Date();
            Date fechaInicio = sdf.parse(descuento.getFecha_inicio());
            Date fechaFin = sdf.parse(descuento.getFecha_fin());
            return fechaActual.after(fechaInicio) && fechaActual.before(fechaFin);
        }
        catch (Exception e) {
            return false;
        }
    }
}