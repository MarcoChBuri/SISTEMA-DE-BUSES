package com.example.controls.dao.implement;

import java.util.ArrayList;
import java.util.List;

import com.example.controls.dao.TurnoDao;
import com.example.models.Turno;

public class TurnoDaoImpl implements TurnoDao {
    private List<Turno> turnos = new ArrayList<>();

    @Override
    public void agregarTurno(Turno turno) {
        turnos.add(turno);
    }

    @Override
    public Turno obtenerTurno(int id) {
        return turnos.stream().filter(t -> t.getId() == id).findFirst().orElse(null);
    }

    @Override
    public List<Turno> obtenerTodosLosTurnos() {
        return turnos;
    }
}
