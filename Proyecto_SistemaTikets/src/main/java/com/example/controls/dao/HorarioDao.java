package com.example.controls.dao;

import com.example.controls.dao.implement.AdapterDao;
import com.example.controls.tda.list.LinkedList;
import com.example.models.Horario;

public class HorarioDao extends AdapterDao<Horario> {
    private Horario horario = new Horario(0, "", "");
    private LinkedList<Horario> listAll;

    public HorarioDao() {
        super(Horario.class);
    }

    public Horario getHorario() {
        if (horario == null) {
            horario = new Horario(0, "", "");
        }
        return this.horario;
    }

    public void setHorario(Horario horario) {
        this.horario = horario;
    }

    public LinkedList<Horario> getlistAll() {
        if (listAll == null) {
            this.listAll = listAll();
        }
        return listAll;
    }

    public Boolean save() throws Exception {
        Integer id = getlistAll().getSize() + 1;
        horario.setId(id);
        this.persist(this.horario);
        this.listAll = listAll();
        return true;
    }
}
