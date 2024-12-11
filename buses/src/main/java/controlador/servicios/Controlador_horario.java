package controlador.servicios;

import controlador.dao.modelo_dao.Horario_dao;
import controlador.tda.lista.LinkedList;
import modelo.Horario;

public class Controlador_horario {
    private Horario_dao horario_dao;

    public Controlador_horario() {
        horario_dao = new Horario_dao();
    }

    public Boolean save() throws Exception {
        return horario_dao.save();
    }

    public Boolean update() throws Exception {
        return horario_dao.update();
    }

    public LinkedList<Horario> Lista_horarios() {
        return horario_dao.getLista_horarios();
    }

    public Horario getHorario() {
        return horario_dao.getHorario();
    }

    public void setHorario(Horario horario) {
        horario_dao.setHorario(horario);
    }

    public Horario get(Integer id) throws Exception {
        return horario_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return horario_dao.delete(id);
    }
}
