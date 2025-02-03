package controlador.servicios;

import controlador.dao.modelo_dao.Pago_dao;
import controlador.tda.lista.LinkedList;
import modelo.Pago;

public class Controlador_pago {
    private Pago_dao pago_dao;

    public Controlador_pago() {
        pago_dao = new Pago_dao();
    }

    public Boolean save() throws Exception {
        return pago_dao.save();
    }

    public Boolean update() throws Exception {
        return pago_dao.update();
    }

    public LinkedList<Pago> Lista_pagos() {
        return pago_dao.getLista_pagos();
    }

    public Pago getPago() {
        return pago_dao.getPago();
    }

    public void setPago(Pago pago) {
        pago_dao.setPago(pago);
    }

    public Pago get(Integer id) throws Exception {
        return pago_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return pago_dao.delete(id);
    }
}
