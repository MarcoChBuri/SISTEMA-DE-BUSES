package controlador.servicios;

import controlador.dao.modelo_dao.Escala_dao;
import controlador.tda.lista.LinkedList;
import modelo.Escala;

public class Controlador_escala {
    private Escala_dao escala_dao;

    public Controlador_escala() {
        escala_dao = new Escala_dao();
    }

    public Boolean save() throws Exception {
        return escala_dao.save();
    }

    public Boolean update() throws Exception {
        return escala_dao.update();
    }

    public LinkedList<Escala> Lista_escala() {
        return escala_dao.getLista_escala();
    }

    public Escala getEscala() {
        return escala_dao.getEscala();
    }

    public void setEscala(Escala escala) {
        escala_dao.setEscala(escala);
    }

    public Escala get(Integer id) throws Exception {
        return escala_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return escala_dao.delete(id);
    }
}
