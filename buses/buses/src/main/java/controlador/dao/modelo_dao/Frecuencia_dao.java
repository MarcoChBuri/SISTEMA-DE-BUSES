package controlador.dao.modelo_dao;

import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import com.google.gson.Gson;
import modelo.Frecuencia;

public class Frecuencia_dao extends AdapterDao<Frecuencia> {
    private LinkedList<Frecuencia> lista_frecuencias;
    private Frecuencia frecuencia;

    public Frecuencia_dao() {
        super(Frecuencia.class);
    }

    public LinkedList<Frecuencia> getLista_frecuencias() {
        if (lista_frecuencias == null) {
            this.lista_frecuencias = listAll();
        }
        return lista_frecuencias;
    }

    public Frecuencia getFrecuencia() {
        if (frecuencia == null) {
            frecuencia = new Frecuencia();
        }
        return this.frecuencia;
    }

    public void setFrecuencia(Frecuencia frecuencia) {
        this.frecuencia = frecuencia;
    }

    public Boolean save() throws Exception {
        frecuencia.setId_frecuencia(obtenerSiguienteId());
        persist(frecuencia);
        this.lista_frecuencias = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        for (int i = 0; i < getLista_frecuencias().getSize(); i++) {
            Frecuencia f = getLista_frecuencias().get(i);
            if (f.getId_frecuencia().equals(getFrecuencia().getId_frecuencia())) {
                merge(getFrecuencia(), i);
                this.lista_frecuencias = listAll();
                return true;
            }
        }
        throw new Exception("No se encontró la frecuencia con el id: " + frecuencia.getId_frecuencia());
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Frecuencia> frecuencias = getLista_frecuencias();
            if (frecuencias == null) {
                frecuencias = new LinkedList<>();
            }
            boolean deleted = false;
            for (int i = 0; i < frecuencias.getSize(); i++) {
                Frecuencia f = frecuencias.get(i);
                if (f.getId_frecuencia().equals(id)) {
                    frecuencias.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (deleted) {
                String json = new Gson().toJson(frecuencias);
                saveFile(json);
                this.lista_frecuencias = listAll();
                return true;
            }
            this.lista_frecuencias = listAll();
            return true;
        }
        catch (Exception e) {
            throw new Exception("No se encontró la frecuencia con el id: " + id);
        }
    }
}
