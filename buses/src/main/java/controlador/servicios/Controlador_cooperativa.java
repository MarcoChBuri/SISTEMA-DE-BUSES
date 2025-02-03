package controlador.servicios;

import controlador.dao.modelo_dao.Cooperativa_dao;
import controlador.tda.lista.LinkedList;
import modelo.Cooperativa;

public class Controlador_cooperativa {
    private Cooperativa_dao cooperativa_dao;

    public Controlador_cooperativa() {
        cooperativa_dao = new Cooperativa_dao();
    }

    public Boolean save() throws Exception {
        return cooperativa_dao.save();
    }

    public Boolean update() throws Exception {
        return cooperativa_dao.update();
    }

    public LinkedList<Cooperativa> Lista_cooperativas() {
        return cooperativa_dao.getLista_cooperativas();
    }

    public Cooperativa getCooperativa() {
        return cooperativa_dao.getCooperativa();
    }

    public void setCooperativa(Cooperativa cooperativa) {
        cooperativa_dao.setCooperativa(cooperativa);
    }

    public Cooperativa get(Integer id) throws Exception {
        return cooperativa_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return cooperativa_dao.delete(id);
    }
}
