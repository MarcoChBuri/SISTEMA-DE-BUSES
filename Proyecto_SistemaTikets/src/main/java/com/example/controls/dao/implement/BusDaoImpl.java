package com.example.controls.dao.implement;

import java.util.ArrayList;
import java.util.List;

import com.example.controls.dao.BusDao;
import com.example.models.Bus;

public class BusDaoImpl implements BusDao {
    private List<Bus> buses = new ArrayList<>();

    @Override
    public void agregarBus(Bus bus) {
        buses.add(bus);
    }

    @Override
    public Bus obtenerBus(int id) {
        return buses.stream().filter(b -> b.getId() == id).findFirst().orElse(null);
    }

    @Override
    public List<Bus> obtenerTodosLosBuses() {
        return buses;
    }
}
