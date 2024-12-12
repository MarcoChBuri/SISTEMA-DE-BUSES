package controlador.servicios;

import controlador.dao.modelo_dao.Turno_dao;
import controlador.tda.lista.LinkedList;
import modelo.Turno;

public class Controlador_turno {
    private Turno_dao turno_dao;

    public Controlador_turno() {
        turno_dao = new Turno_dao();
    }

    public Boolean save() throws Exception {
        return turno_dao.save();
    }

    public Boolean update() throws Exception {
        return turno_dao.update();
    }

    public LinkedList<Turno> Lista_turnos() {
        return turno_dao.getLista_turnos();
    }

    public Turno getTurno() {
        return turno_dao.getTurno();
    }

    public void setTurno(Turno turno) {
        turno_dao.setTurno(turno);
    }

    public Turno get(Integer id) throws Exception {
        return turno_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return turno_dao.delete(id);
    }
}
