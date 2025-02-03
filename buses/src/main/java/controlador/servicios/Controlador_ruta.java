package controlador.servicios;

import controlador.dao.modelo_dao.Ruta_dao;
import controlador.tda.lista.LinkedList;
import modelo.Ruta;

public class Controlador_ruta {
    private Ruta_dao ruta_dao;

    public Controlador_ruta() {
        ruta_dao = new Ruta_dao();
    }

    public Boolean save() throws Exception {
        return ruta_dao.save();
    }

    public Boolean update() throws Exception {
        return ruta_dao.update();
    }

    public LinkedList<Ruta> Lista_rutas() {
        return ruta_dao.getLista_rutas();
    }

    public Ruta getRuta() {
        return ruta_dao.getRuta();
    }

    public void setRuta(Ruta ruta) {
        ruta_dao.setRuta(ruta);
    }

    public Ruta get(Integer id) throws Exception {
        return ruta_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return ruta_dao.delete(id);
    }
}
