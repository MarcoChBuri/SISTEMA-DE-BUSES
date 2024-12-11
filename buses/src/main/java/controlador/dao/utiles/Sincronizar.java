package controlador.dao.utiles;

import controlador.tda.lista.LinkedList;
import controlador.dao.modelo_dao.*;
import com.google.gson.Gson;
import modelo.*;

public class Sincronizar {
    public static void sincronizarCooperativa(Cooperativa cooperativa) throws Exception {
        Bus_dao busDao = new Bus_dao();
        actualizarBusesDeCooperativa(busDao, cooperativa);
        sincronizarEntidadesRelacionadasCooperativa(cooperativa.getId_cooperativa());
    }

    public static void sincronizarBus(Bus bus) throws Exception {
        Ruta_dao rutaDao = new Ruta_dao();
        actualizarRutasDeBus(rutaDao, bus);
        sincronizarEntidadesRelacionadasBus(bus.getId_bus());
    }

    public static void sincronizarRuta(Ruta ruta) throws Exception {
        Horario_dao horarioDao = new Horario_dao();
        actualizarHorariosDeRuta(horarioDao, ruta);
        sincronizarEntidadesRelacionadasRuta(ruta.getId_ruta());
    }

    public static void sincronizarHorario(Horario horario) throws Exception {
        Turno_dao turnoDao = new Turno_dao();
        Frecuencia_dao frecuenciaDao = new Frecuencia_dao();
        actualizarTurnosDeHorario(turnoDao, horario);
        actualizarFrecuenciasDeHorario(frecuenciaDao, horario);
        sincronizarEntidadesRelacionadasHorario(horario.getId_horario());
    }

    public static void sincronizarTurno(Turno turno) throws Exception {
        Boleto_dao boletoDao = new Boleto_dao();
        actualizarBoletosDelTurno(boletoDao, turno);
    }

    public static void sincronizarPersona(Persona persona) throws Exception {
        if (persona.getCuenta() != null) {
            Cuenta_dao cuentaDao = new Cuenta_dao();
            cuentaDao.setCuenta(persona.getCuenta());
            if (persona.getCuenta().getId_cuenta() == null) {
                persona.getCuenta().setId_cuenta(cuentaDao.getLista_cuentas().getSize() + 1);
            }
            cuentaDao.update();
        }
        if (persona.getMetodo_pago() != null) {
            Pago_dao pagoDao = new Pago_dao();
            pagoDao.setPago(persona.getMetodo_pago());
            if (persona.getMetodo_pago().getId_pago() == null) {
                persona.getMetodo_pago().setId_pago(pagoDao.getLista_pagos().getSize() + 1);
            }
            pagoDao.update();
        }
        Persona_dao personaDao = new Persona_dao();
        personaDao.setPersona(persona);
        if (persona.getId_persona() == null) {
            persona.setId_persona(personaDao.getLista_personas().getSize() + 1);
        }
        personaDao.update();
    }

    private static void actualizarBusesDeCooperativa(Bus_dao busDao, Cooperativa cooperativa)
            throws Exception {
        LinkedList<Bus> buses = busDao.getLista_buses();
        boolean actualizado = false;
        for (int i = 0; i < buses.getSize(); i++) {
            Bus bus = buses.get(i);
            if (bus.getCooperativa().getId_cooperativa().equals(cooperativa.getId_cooperativa())) {
                bus.setCooperativa(cooperativa);
                actualizado = true;
            }
        }
        if (actualizado) {
            busDao.saveFile(new Gson().toJson(buses.toArray()));
        }
    }

    private static void actualizarRutasDeBus(Ruta_dao rutaDao, Bus bus) throws Exception {
        LinkedList<Ruta> rutas = rutaDao.getLista_rutas();
        boolean actualizado = false;
        for (int i = 0; i < rutas.getSize(); i++) {
            Ruta ruta = rutas.get(i);
            if (ruta.getBus().getId_bus().equals(bus.getId_bus())) {
                ruta.setBus(bus);
                actualizado = true;
            }
        }
        if (actualizado) {
            rutaDao.saveFile(new Gson().toJson(rutas.toArray()));
        }
    }

    private static void actualizarHorariosDeRuta(Horario_dao horarioDao, Ruta ruta) throws Exception {
        LinkedList<Horario> horarios = horarioDao.getLista_horarios();
        boolean actualizado = false;
        for (int i = 0; i < horarios.getSize(); i++) {
            Horario horario = horarios.get(i);
            if (horario.getRuta().getId_ruta().equals(ruta.getId_ruta())) {
                horario.setRuta(ruta);
                actualizado = true;
            }
        }
        if (actualizado) {
            horarioDao.saveFile(new Gson().toJson(horarios.toArray()));
        }
    }

    private static void actualizarTurnosDeHorario(Turno_dao turnoDao, Horario horario) throws Exception {
        LinkedList<Turno> turnos = turnoDao.getLista_turnos();
        boolean actualizado = false;
        for (int i = 0; i < turnos.getSize(); i++) {
            Turno turno = turnos.get(i);
            if (turno.getHorario().getId_horario().equals(horario.getId_horario())) {
                turno.setHorario(horario);
                actualizado = true;
            }
        }
        if (actualizado) {
            turnoDao.saveFile(new Gson().toJson(turnos.toArray()));
        }
    }

    private static void actualizarFrecuenciasDeHorario(Frecuencia_dao frecuenciaDao, Horario horario)
            throws Exception {
        LinkedList<Frecuencia> frecuencias = frecuenciaDao.getLista_frecuencias();
        boolean actualizado = false;
        for (int i = 0; i < frecuencias.getSize(); i++) {
            Frecuencia frecuencia = frecuencias.get(i);
            if (frecuencia.getHorario().getId_horario().equals(horario.getId_horario())) {
                frecuencia.setHorario(horario);
                actualizado = true;
            }
        }
        if (actualizado) {
            frecuenciaDao.saveFile(new Gson().toJson(frecuencias.toArray()));
        }
    }

    private static void actualizarBoletosDelTurno(Boleto_dao boletoDao, Turno turno) throws Exception {
        LinkedList<Boleto> boletos = boletoDao.getLista_boletos();
        boolean actualizado = false;
        for (int i = 0; i < boletos.getSize(); i++) {
            Boleto boleto = boletos.get(i);
            if (boleto.getTurno().getId_turno().equals(turno.getId_turno())) {
                boleto.setTurno(turno);
                actualizado = true;
            }
        }
        if (actualizado) {
            boletoDao.saveFile(new Gson().toJson(boletos.toArray()));
        }
    }

    @SuppressWarnings("unused")
    private static void actualizarBoletosDePersona(Boleto_dao boletoDao, Persona persona) throws Exception {
        LinkedList<Boleto> boletos = boletoDao.getLista_boletos();
        boolean actualizado = false;
        for (int i = 0; i < boletos.getSize(); i++) {
            Boleto boleto = boletos.get(i);
            if (boleto.getPersona().getId_persona().equals(persona.getId_persona())) {
                boleto.setPersona(persona);
                actualizado = true;
            }
        }
        if (actualizado) {
            boletoDao.saveFile(new Gson().toJson(boletos.toArray()));
        }
    }

    private static void sincronizarEntidadesRelacionadasCooperativa(Integer idCooperativa) throws Exception {
        Bus_dao busDao = new Bus_dao();
        LinkedList<Bus> buses = busDao.getLista_buses();
        for (int i = 0; i < buses.getSize(); i++) {
            Bus bus = buses.get(i);
            if (bus.getCooperativa().getId_cooperativa().equals(idCooperativa)) {
                sincronizarBus(bus);
            }
        }
    }

    private static void sincronizarEntidadesRelacionadasBus(Integer idBus) throws Exception {
        Ruta_dao rutaDao = new Ruta_dao();
        LinkedList<Ruta> rutas = rutaDao.getLista_rutas();
        for (int i = 0; i < rutas.getSize(); i++) {
            Ruta ruta = rutas.get(i);
            if (ruta.getBus().getId_bus().equals(idBus)) {
                sincronizarRuta(ruta);
            }
        }
    }

    private static void sincronizarEntidadesRelacionadasRuta(Integer idRuta) throws Exception {
        Horario_dao horarioDao = new Horario_dao();
        LinkedList<Horario> horarios = horarioDao.getLista_horarios();
        for (int i = 0; i < horarios.getSize(); i++) {
            Horario horario = horarios.get(i);
            if (horario.getRuta().getId_ruta().equals(idRuta)) {
                sincronizarHorario(horario);
            }
        }
    }

    private static void sincronizarEntidadesRelacionadasHorario(Integer idHorario) throws Exception {
        Turno_dao turnoDao = new Turno_dao();
        LinkedList<Turno> turnos = turnoDao.getLista_turnos();
        for (int i = 0; i < turnos.getSize(); i++) {
            Turno turno = turnos.get(i);
            if (turno.getHorario().getId_horario().equals(idHorario)) {
                sincronizarTurno(turno);
            }
        }
    }
}
