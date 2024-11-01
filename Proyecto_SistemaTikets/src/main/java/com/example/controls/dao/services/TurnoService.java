package com.example.controls.dao.services;

import java.util.List;

import com.example.models.Turno;

public interface TurnoService {
    void agregarTurno(Turno turno);
    Turno obtenerTurno(int id);
    List<Turno> obtenerTodosLosTurnos();
}
