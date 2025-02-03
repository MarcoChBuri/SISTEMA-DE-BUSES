package controlador.dao.modelo_dao;

import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import com.google.gson.Gson;
import modelo.Persona;
import modelo.Boleto;
import modelo.Pago;

public class Pago_dao extends AdapterDao<Pago> {
    private LinkedList<Pago> lista_pagos;
    private Pago pago;

    public Pago_dao() {
        super(Pago.class);
    }

    public LinkedList<Pago> getLista_pagos() {
        if (lista_pagos == null) {
            this.lista_pagos = listAll();
        }
        return lista_pagos;
    }

    public Pago getPago() {
        if (pago == null) {
            pago = new Pago();
        }
        return this.pago;
    }

    public void setPago(Pago pago) {
        this.pago = pago;
    }

    public Boolean save() throws Exception {
        pago.setId_pago(obtenerSiguienteId());
        persist(pago);
        this.lista_pagos = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        try {
            if (pago == null || pago.getId_pago() == null) {
                throw new Exception("Pago no válido o sin ID");
            }
            LinkedList<Pago> pagos = getLista_pagos();
            LinkedList<Persona> personas = new LinkedList<>();
            LinkedList<Boleto> boletos = new LinkedList<>();
            AdapterDao<Persona> personaDao = new AdapterDao<>(Persona.class);
            AdapterDao<Boleto> boletoDao = new AdapterDao<>(Boleto.class);
            personas = personaDao.listAll();
            boletos = boletoDao.listAll();
            boolean pagoEncontrado = false;
            for (int i = 0; i < pagos.getSize(); i++) {
                if (pagos.get(i).getId_pago().equals(pago.getId_pago())) {
                    pagos.update(pago, i);
                    pagoEncontrado = true;
                    break;
                }
            }
            if (!pagoEncontrado) {
                throw new Exception("Pago no encontrado para actualizar");
            }
            boolean personasActualizadas = false;
            for (int i = 0; i < personas.getSize(); i++) {
                Persona persona = personas.get(i);
                if (persona.getMetodo_pago() != null
                        && persona.getMetodo_pago().getId_pago().equals(pago.getId_pago())) {
                    persona.setMetodo_pago(pago);
                    personasActualizadas = true;
                }
            }
            boolean boletosActualizados = false;
            for (int i = 0; i < boletos.getSize(); i++) {
                Boleto boleto = boletos.get(i);
                if (boleto.getPersona() != null && boleto.getPersona().getMetodo_pago() != null
                        && boleto.getPersona().getMetodo_pago().getId_pago().equals(pago.getId_pago())) {
                    boleto.getPersona().setMetodo_pago(pago);
                    boletosActualizados = true;
                }
            }
            saveFile(new Gson().toJson(pagos.toArray()));
            if (personasActualizadas) {
                personaDao.saveFile(new Gson().toJson(personas.toArray()));
            }
            if (boletosActualizados) {
                boletoDao.saveFile(new Gson().toJson(boletos.toArray()));
            }
            this.lista_pagos = pagos;
            return true;
        }
        catch (Exception e) {
            e.printStackTrace();
            throw new Exception("Error al actualizar el pago: " + e.getMessage());
        }
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Pago> pagos = getLista_pagos();
            LinkedList<Persona> personas = new LinkedList<>();
            LinkedList<Boleto> boletos = new LinkedList<>();
            AdapterDao<Persona> personaDao = new AdapterDao<>(Persona.class);
            AdapterDao<Boleto> boletoDao = new AdapterDao<>(Boleto.class);
            personas = personaDao.listAll();
            boletos = boletoDao.listAll();
            boolean deleted = false;
            for (int i = 0; i < pagos.getSize(); i++) {
                if (pagos.get(i).getId_pago().equals(id)) {
                    pagos.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (!deleted) {
                throw new Exception("No se encontró el pago con el id: " + id);
            }
            boolean cambiosRealizados = false;
            for (int i = 0; i < personas.getSize(); i++) {
                Persona persona = personas.get(i);
                if (persona.getMetodo_pago() != null && persona.getMetodo_pago().getId_pago().equals(id)) {
                    persona.setMetodo_pago(null);
                    cambiosRealizados = true;
                }
            }
            for (int i = 0; i < boletos.getSize(); i++) {
                Boleto boleto = boletos.get(i);
                if (boleto.getPersona() != null && boleto.getPersona().getMetodo_pago() != null
                        && boleto.getPersona().getMetodo_pago().getId_pago().equals(id)) {
                    boleto.getPersona().setMetodo_pago(null);
                    cambiosRealizados = true;
                }
            }
            saveFile(new Gson().toJson(pagos.toArray()));
            if (cambiosRealizados) {
                personaDao.saveFile(new Gson().toJson(personas.toArray()));
                boletoDao.saveFile(new Gson().toJson(boletos.toArray()));
            }
            this.lista_pagos = pagos;
            return true;
        }
        catch (Exception e) {
            throw new Exception("Error al eliminar el pago: " + e.getMessage());
        }
    }
}
