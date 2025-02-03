package controlador.servicios;

import controlador.dao.modelo_dao.Bus_dao;
import controlador.tda.lista.LinkedList;
import modelo.Bus;

public class Controlador_bus {
    private Bus_dao bus_dao;

    public Controlador_bus() {
        bus_dao = new Bus_dao();
    }

    public Boolean save() throws Exception {
        return bus_dao.save();
    }

    public Boolean update() throws Exception {
        return bus_dao.update();
    }

    public LinkedList<Bus> Lista_buses() {
        return bus_dao.getLista_buses();
    }

    public Bus getBus() {
        return bus_dao.getBus();
    }

    public void setBus(Bus bus) {
        bus_dao.setBus(bus);
    }

    public Bus get(Integer id) throws Exception {
        return bus_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return bus_dao.delete(id);
    }
}
