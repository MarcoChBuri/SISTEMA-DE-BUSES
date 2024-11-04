package com.example.controls.dao;

import com.example.controls.dao.implement.AdapterDao;
import com.example.controls.tda.list.LinkedList;
import com.example.models.Ruta;

public class RutaDao extends AdapterDao<Ruta> {
    private Ruta ruta = new Ruta(0, "", "");
    private LinkedList<Ruta> listAll;

    public RutaDao() {
        super(Ruta.class);
    }

    public Ruta getRuta() {
        if (ruta == null) {
            ruta = new Ruta(0, "", "");
        }
        return this.ruta;
    }

    public void setRuta(Ruta ruta) {
        this.ruta = ruta;
    }

    public LinkedList<Ruta> getlistAll() {
        if (listAll == null) {
            this.listAll = listAll();
        }
        return listAll;
    }

    public Boolean save() throws Exception {
        Integer id = getlistAll().getSize() + 1;
        ruta.setId(id);
        this.persist(this.ruta);
        this.listAll = listAll();
        return true;
    }
}
