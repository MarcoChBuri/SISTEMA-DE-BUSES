package controlador.servicios;

import controlador.dao.modelo_dao.Boleto_dao;
import controlador.tda.lista.LinkedList;
import modelo.Boleto;

public class Controlador_boleto {
    private Boleto_dao boleto_dao;

    public Controlador_boleto() {
        boleto_dao = new Boleto_dao();
    }

    public Boolean save() throws Exception {
        return boleto_dao.save();
    }

    public Boolean update() throws Exception {
        return boleto_dao.update();
    }

    public LinkedList<Boleto> Lista_boletos() {
        return boleto_dao.getLista_boletos();
    }

    public Boleto getBoleto() {
        return boleto_dao.getBoleto();
    }

    public void setBoleto(Boleto boleto) {
        boleto_dao.setBoleto(boleto);
    }

    public Boleto get(Integer id) throws Exception {
        return boleto_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return boleto_dao.delete(id);
    }
}
