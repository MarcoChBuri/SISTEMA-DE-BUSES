package controlador.dao.modelo_dao;

import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import com.google.gson.Gson;
import modelo.Horario;

public class Horario_dao extends AdapterDao<Horario> {
    private LinkedList<Horario> lista_horarios;
    private Horario horario;

    public Horario_dao() {
        super(Horario.class);
    }

    public LinkedList<Horario> getLista_horarios() {
        if (lista_horarios == null) {
            this.lista_horarios = listAll();
        }
        return lista_horarios;
    }

    public Horario getHorario() {
        if (horario == null) {
            horario = new Horario();
        }
        return this.horario;
    }

    public void setHorario(Horario horario) {
        this.horario = horario;
    }

    public Boolean save() throws Exception {
        horario.setId_horario(obtenerSiguienteId());
        persist(horario);
        this.lista_horarios = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        for (int i = 0; i < getLista_horarios().getSize(); i++) {
            Horario h = getLista_horarios().get(i);
            if (h.getId_horario().equals(getHorario().getId_horario())) {
                merge(getHorario(), i);
                this.lista_horarios = listAll();
                return true;
            }
        }
        throw new Exception("No se encontró el horario con el id: " + horario.getId_horario());
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Horario> horarios = getLista_horarios();
            if (horarios == null) {
                horarios = new LinkedList<>();
            }
            boolean deleted = false;
            for (int i = 0; i < horarios.getSize(); i++) {
                Horario h = horarios.get(i);
                if (h.getId_horario().equals(id)) {
                    horarios.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (deleted) {
                String info = new Gson().toJson(horarios.toArray());
                saveFile(info);
                this.lista_horarios = listAll();
                return true;
            }
            return false;
        }
        catch (Exception e) {
            throw new Exception("No se encontró el horario con el id: " + id);
        }
    }
}
