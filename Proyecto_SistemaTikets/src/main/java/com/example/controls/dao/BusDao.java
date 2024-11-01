package com.example.controls.dao;

import java.util.List;

import com.example.models.Bus;

public interface BusDao {
    void agregarBus(Bus bus);
    Bus obtenerBus(int id);
    List<Bus> obtenerTodosLosBuses();
}
