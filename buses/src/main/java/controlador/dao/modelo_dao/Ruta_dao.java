package controlador.dao.modelo_dao;

import controlador.dao.utiles.Sincronizar;
import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import com.google.gson.Gson;
import modelo.Ruta;

public class Ruta_dao extends AdapterDao<Ruta> {
    private LinkedList<Ruta> lista_rutas;
    private Ruta ruta;

    public Ruta_dao() {
        super(Ruta.class);
    }

    public LinkedList<Ruta> getLista_rutas() {
        if (lista_rutas == null) {
            this.lista_rutas = listAll();
        }
        return lista_rutas;
    }

    public Ruta getRuta() {
        if (ruta == null) {
            ruta = new Ruta();
        }
        return this.ruta;
    }

    public void setRuta(Ruta ruta) {
        this.ruta = ruta;
    }

    public Boolean save() throws Exception {
        ruta.setId_ruta(obtenerSiguienteId());
        persist(ruta);
        this.lista_rutas = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        for (int i = 0; i < getLista_rutas().getSize(); i++) {
            Ruta r = getLista_rutas().get(i);
            if (r.getId_ruta().equals(getRuta().getId_ruta())) {
                merge(getRuta(), i);
                this.lista_rutas = listAll();
                Sincronizar.sincronizarRuta(getRuta());
                return true;
            }
        }
        throw new Exception("No se encontró la ruta");
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Ruta> rutas = getLista_rutas();
            if (rutas == null) {
                rutas = new LinkedList<>();
            }
            boolean deleted = false;
            for (int i = 0; i < rutas.getSize(); i++) {
                Ruta r = rutas.get(i);
                if (r.getId_ruta().equals(id)) {
                    rutas.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (deleted) {
                String info = new Gson().toJson(rutas.toArray());
                saveFile(info);
                this.lista_rutas = listAll();
                return true;
            }
            return false;
        }
        catch (Exception e) {
            throw new Exception("No se encontró la ruta con el id: " + id);
        }
    }
}
