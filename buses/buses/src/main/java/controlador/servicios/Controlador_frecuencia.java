package controlador.servicios;

import controlador.dao.modelo_dao.Frecuencia_dao;
import controlador.tda.lista.LinkedList;
import modelo.Frecuencia;

public class Controlador_frecuencia {
    private Frecuencia_dao frecuencia_dao;

    public Controlador_frecuencia() {
        frecuencia_dao = new Frecuencia_dao();
    }

    public Boolean save() throws Exception {
        return frecuencia_dao.save();
    }

    public Boolean update() throws Exception {
        return frecuencia_dao.update();
    }

    public LinkedList<Frecuencia> Lista_frecuencias() {
        return frecuencia_dao.getLista_frecuencias();
    }

    public Frecuencia getFrecuencia() {
        return frecuencia_dao.getFrecuencia();
    }

    public void setFrecuencia(Frecuencia frecuencia) {
        frecuencia_dao.setFrecuencia(frecuencia);
    }

    public Frecuencia get(Integer id) throws Exception {
        return frecuencia_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return frecuencia_dao.delete(id);
    }
}
