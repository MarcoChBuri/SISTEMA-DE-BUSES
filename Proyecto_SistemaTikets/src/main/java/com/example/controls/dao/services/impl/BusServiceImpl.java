package com.example.controls.dao.services.impl;
import java.util.List;

import com.example.controls.dao.BusDao;
import com.example.controls.dao.services.BusService;
import com.example.models.Bus;

public class BusServiceImpl implements BusService {
    private BusDao busDao;

    public BusServiceImpl(BusDao busDao) {
        this.busDao = busDao;
    }

    @Override
    public void agregarBus(Bus bus) {
        busDao.agregarBus(bus);
    }

    @Override
    public Bus obtenerBus(int id) {
        return busDao.obtenerBus(id);
    }

    @Override
    public List<Bus> obtenerTodosLosBuses() {
        return busDao.obtenerTodosLosBuses();
    }
}
