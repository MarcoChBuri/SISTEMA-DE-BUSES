package controlador.servicios;

import controlador.dao.modelo_dao.Descuento_dao;
import controlador.tda.lista.LinkedList;
import modelo.Descuento;

public class Controlador_descuento {
    private Descuento_dao descuento_dao;

    public Controlador_descuento() {
        descuento_dao = new Descuento_dao();
    }

    public Boolean save() throws Exception {
        return descuento_dao.save();
    }

    public Boolean update() throws Exception {
        return descuento_dao.update();
    }

    public LinkedList<Descuento> Lista_descuentos() {
        return descuento_dao.getLista_descuentos();
    }

    public Descuento getDescuento() {
        return descuento_dao.getDescuento();
    }

    public void setDescuento(Descuento descuento) {
        descuento_dao.setDescuento(descuento);
    }

    public Descuento get(Integer id) throws Exception {
        return descuento_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return descuento_dao.delete(id);
    }
}
