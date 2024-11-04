package com.example.controls.dao;

import com.example.controls.dao.implement.AdapterDao;
import com.example.controls.tda.list.LinkedList;
import com.example.models.Boleto;

public class BoletoDao extends AdapterDao<Boleto> {
    private Boleto boleto;
    private LinkedList<Boleto> listAll;

    public BoletoDao() {
        super(Boleto.class);
        boleto = new Boleto(); 
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

    public LinkedList<Boleto> getListAll() {
        if (listAll == null) {
            this.listAll = listAll();
        }
        return listAll;
    }

    public Boolean save() throws Exception {
        Integer id = getListAll().getSize() + 1;
        boleto.setId(id);
        this.persist(this.boleto);
        this.listAll = listAll();
        return true;
    }
}
