package controlador.dao.modelo_dao;

import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import controlador.dao.utiles.Sincronizar;

import com.google.gson.Gson;
import modelo.Escala;

public class Escala_dao extends AdapterDao<Escala> {
    private LinkedList<Escala> lista_escala;
    private Escala escala;

    public Escala_dao() {
        super(Escala.class);
    }

    public LinkedList<Escala> getLista_escala() {
        if (lista_escala == null) {
            this.lista_escala = listAll();
        }
        return lista_escala;
    }

    public Escala getEscala() {
        if (escala == null) {
            escala = new Escala();
        }
        return this.escala;
    }

    public void setEscala(Escala escala) {
        this.escala = escala;
    }

    public Boolean save() throws Exception {
        escala.setId_escala(obtenerSiguienteId());
        persist(escala);
        this.lista_escala = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        for (int i = 0; i < getLista_escala().getSize(); i++) {
            Escala e = getLista_escala().get(i);
            if (e.getId_escala().equals(getEscala().getId_escala())) {
                merge(getEscala(), i);
                this.lista_escala = listAll();
                return true;
            }
        }
        throw new Exception("No se encontró la escala con el id: " + escala.getId_escala());
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Escala> escalas = getLista_escala();
            if (escalas == null) {
                escalas = new LinkedList<>();
            }
            boolean deleted = false;
            for (int i = 0; i < escalas.getSize(); i++) {
                Escala e = escalas.get(i);
                if (e.getId_escala().equals(id)) {
                    escalas.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (deleted) {
                Sincronizar.sincronizarEscalaEliminada(id);
                String json = new Gson().toJson(escalas.toArray());
                saveFile(json);
                this.lista_escala = listAll();
                return true;
            }
            return false;
        }
        catch (Exception e) {
            throw new Exception("No se encontró la escala con el id: " + id);
        }
    }

}
