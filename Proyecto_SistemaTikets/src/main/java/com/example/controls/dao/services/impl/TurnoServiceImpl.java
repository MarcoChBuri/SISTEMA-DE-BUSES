package com.example.controls.dao.services.impl;


import java.util.List;

import com.example.controls.dao.TurnoDao;
import com.example.controls.dao.services.TurnoService;
import com.example.models.Turno;

public class TurnoServiceImpl implements TurnoService {
    private TurnoDao turnoDao;

    public TurnoServiceImpl(TurnoDao turnoDao) {
        this.turnoDao = turnoDao;
    }

    @Override
    public void agregarTurno(Turno turno) {
        turnoDao.agregarTurno(turno);
    }

    @Override
    public Turno obtenerTurno(int id) {
        return turnoDao.obtenerTurno(id);
    }

    @Override
    public List<Turno> obtenerTodosLosTurnos() {
        return turnoDao.obtenerTodosLosTurnos();
    }
}
