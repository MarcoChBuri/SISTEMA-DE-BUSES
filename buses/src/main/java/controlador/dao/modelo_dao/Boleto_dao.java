package controlador.dao.modelo_dao;

import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import com.google.gson.Gson;
import modelo.Boleto;

public class Boleto_dao extends AdapterDao<Boleto> {
    private LinkedList<Boleto> lista_boletos;
    private Boleto boleto;

    public Boleto_dao() {
        super(Boleto.class);
    }

    public LinkedList<Boleto> getLista_boletos() {
        if (lista_boletos == null) {
            this.lista_boletos = listAll();
        }
        return lista_boletos;
    }

    public Boleto getBoleto() {
        if (boleto == null) {
            boleto = new Boleto();
        }
        return this.boleto;
    }

    public void setBoleto(Boleto boleto) {
        this.boleto = boleto;
    }

    public Boolean save() throws Exception {
        boleto.setId_boleto(getLista_boletos().getSize() + 1);
        persist(boleto);
        this.lista_boletos = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        for (int i = 0; i < getLista_boletos().getSize(); i++) {
            Boleto b = getLista_boletos().get(i);
            if (b.getId_boleto().equals(getBoleto().getId_boleto())) {
                merge(getBoleto(), i);
                this.lista_boletos = listAll();
                return true;
            }
        }
        throw new Exception("No se encontró el boleto con el id: " + boleto.getId_boleto());
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Boleto> boletos = getLista_boletos();
            if (boletos == null) {
                boletos = new LinkedList<>();
            }
            boolean deleted = false;
            for (int i = 0; i < boletos.getSize(); i++) {
                Boleto b = boletos.get(i);
                if (b.getId_boleto().equals(id)) {
                    boletos.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (deleted) {
                String info = new Gson().toJson(boletos.toArray());
                saveFile(info);
                this.lista_boletos = boletos;
                return true;
            }
            throw new Exception("No se encontró el boleto con el id: " + id);
        }
        catch (Exception e) {
            throw new Exception("Error al eliminar el boleto: " + e.getMessage());
        }
    }
}
