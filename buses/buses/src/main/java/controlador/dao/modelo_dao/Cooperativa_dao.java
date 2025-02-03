package controlador.dao.modelo_dao;

import controlador.dao.utiles.Sincronizar;
import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import com.google.gson.Gson;
import modelo.Cooperativa;

public class Cooperativa_dao extends AdapterDao<Cooperativa> {
    private LinkedList<Cooperativa> lista_cooperativas;
    private Cooperativa cooperativa;

    public Cooperativa_dao() {
        super(Cooperativa.class);
    }

    public LinkedList<Cooperativa> getLista_cooperativas() {
        if (lista_cooperativas == null) {
            this.lista_cooperativas = listAll();
        }
        return lista_cooperativas;
    }

    public Cooperativa getCooperativa() {
        if (cooperativa == null) {
            cooperativa = new Cooperativa();
        }
        return this.cooperativa;
    }

    public void setCooperativa(Cooperativa cooperativa) {
        this.cooperativa = cooperativa;
    }

    public Boolean save() throws Exception {
        try {
            cooperativa.setId_cooperativa(obtenerSiguienteId());
            persist(cooperativa);
            this.lista_cooperativas = listAll();
            return true;
        }
        catch (Exception e) {
            throw new Exception("Error al guardar la cooperativa: " + e.getMessage());
        }
    }

    public Boolean update() throws Exception {
        for (int i = 0; i < getLista_cooperativas().getSize(); i++) {
            Cooperativa c = getLista_cooperativas().get(i);
            if (c.getId_cooperativa().equals(getCooperativa().getId_cooperativa())) {
                merge(getCooperativa(), i);
                this.lista_cooperativas = listAll();
                Sincronizar.sincronizarCooperativa(getCooperativa());
                return true;
            }
        }
        throw new Exception("No se encontró la cooperativa");
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Cooperativa> cooperativas = getLista_cooperativas();
            if (cooperativas == null) {
                cooperativas = new LinkedList<>();
            }
            boolean deleted = false;
            for (int i = 0; i < cooperativas.getSize(); i++) {
                Cooperativa c = cooperativas.get(i);
                if (c.getId_cooperativa().equals(id)) {
                    cooperativas.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (deleted) {
                String info = new Gson().toJson(cooperativas.toArray());
                saveFile(info);
                this.lista_cooperativas = listAll();
                return true;
            }
            return false;
        }
        catch (Exception e) {
            throw new Exception("Error al eliminar la cooperativa: " + e.getMessage());
        }
    }
}
