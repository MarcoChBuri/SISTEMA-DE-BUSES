package com.example.controls.dao.services;

import java.util.List;

import com.example.models.Bus;

public interface BusService {
    void agregarBus(Bus bus);
    Bus obtenerBus(int id);
    List<Bus> obtenerTodosLosBuses();
}