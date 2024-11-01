package com.example.controls.dao;

import java.util.List;

import com.example.models.Turno;

public interface TurnoDao {
    void agregarTurno(Turno turno);
    Turno obtenerTurno(int id);
    List<Turno> obtenerTodosLosTurnos();
}
