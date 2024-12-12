package controlador.dao.modelo_dao;

import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import com.google.gson.Gson;
import modelo.Pago;

public class Pago_dao extends AdapterDao<Pago> {
    private LinkedList<Pago> lista_pagos;
    private Pago pago;

    public Pago_dao() {
        super(Pago.class);
    }

    public LinkedList<Pago> getLista_pagos() {
        if (lista_pagos == null) {
            this.lista_pagos = listAll();
        }
        return lista_pagos;
    }

    public Pago getPago() {
        if (pago == null) {
            pago = new Pago();
        }
        return this.pago;
    }

    public void setPago(Pago pago) {
        this.pago = pago;
    }

    public Boolean save() throws Exception {
        pago.setId_pago(getLista_pagos().getSize() + 1);
        persist(pago);
        this.lista_pagos = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        try {
            if (pago == null) {
                throw new Exception("Pago no válido");
            }
            LinkedList<Pago> pagos = getLista_pagos();
            boolean found = false;
            if (pago.getId_pago() != null) {
                for (int i = 0; i < pagos.getSize(); i++) {
                    Pago p = pagos.get(i);
                    if (p.getId_pago().equals(pago.getId_pago())) {
                        merge(pago, i);
                        found = true;
                        break;
                    }
                }
            }
            if (!found) {
                if (pago.getId_pago() == null) {
                    pago.setId_pago(pagos.getSize() + 1);
                }
                persist(pago);
            }
            this.lista_pagos = listAll();
            return true;
        }
        catch (Exception e) {
            throw new Exception("Error al actualizar el pago: " + e.getMessage());
        }
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Pago> pagos = getLista_pagos();
            if (pagos == null) {
                pagos = new LinkedList<>();
            }
            boolean deleted = false;
            for (int i = 0; i < pagos.getSize(); i++) {
                Pago p = pagos.get(i);
                if (p.getId_pago().equals(id)) {
                    pagos.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (deleted) {
                Gson gson = new Gson();
                String json = gson.toJson(pagos);
                saveFile(json);
                return true;
            }
            throw new Exception("No se encontró el pago con el id: " + id);
        }
        catch (Exception e) {
            throw e;
        }
    }
}
