package com.example.controls.dao;

import com.example.controls.dao.implement.AdapterDao;
import com.example.controls.tda.list.LinkedList;
import com.example.models.Frecuencia;

public class FrecuenciaDao extends AdapterDao<Frecuencia> {
    private Frecuencia frecuencia;
    private LinkedList<Frecuencia> listAll;

    public FrecuenciaDao() {
        super(Frecuencia.class);
        frecuencia = new Frecuencia(0, 0, "", 0.0f, null, null, 0);
    }

    public Frecuencia getFrecuencia() {
        if (frecuencia == null) {
            frecuencia = new Frecuencia(0, 0, "", 0.0f, null, null, 0);
        }
        return this.frecuencia;
    }

    public void setFrecuencia(Frecuencia frecuencia) {
        this.frecuencia = frecuencia;
    }

    public LinkedList<Frecuencia> getlistAll() {
        if (listAll == null) {
            this.listAll = listAll();
        }
        return listAll;
    }

    public Boolean save() throws Exception {
        Integer id = getlistAll().getSize() + 1;
        frecuencia.setId(id);
        this.persist(this.frecuencia);
        this.listAll = listAll();
        return true;
    }
}
