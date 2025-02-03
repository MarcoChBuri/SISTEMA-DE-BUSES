package controlador.dao.modelo_dao;

import controlador.dao.utiles.Sincronizar;
import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import com.google.gson.Gson;
import modelo.Bus;

public class Bus_dao extends AdapterDao<Bus> {
    private LinkedList<Bus> lista_buses;
    private Bus bus;

    public Bus_dao() {
        super(Bus.class);
    }

    public LinkedList<Bus> getLista_buses() {
        if (lista_buses == null) {
            this.lista_buses = listAll();
        }
        return lista_buses;
    }

    public Bus getBus() {
        if (bus == null) {
            bus = new Bus();
        }
        return this.bus;
    }

    public void setBus(Bus bus) {
        this.bus = bus;
    }

    public Boolean save() throws Exception {
        bus.setId_bus(obtenerSiguienteId());
        persist(bus);
        this.lista_buses = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        for (int i = 0; i < getLista_buses().getSize(); i++) {
            Bus b = getLista_buses().get(i);
            if (b.getId_bus().equals(getBus().getId_bus())) {
                merge(getBus(), i);
                this.lista_buses = listAll();
                Sincronizar.sincronizarBus(getBus());
                return true;
            }
        }
        throw new Exception("No se encontró el bus con el id: " + getBus().getId_bus());
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Bus> buses = getLista_buses();
            if (buses == null) {
                buses = new LinkedList<>();
            }
            boolean deleted = false;
            for (int i = 0; i < buses.getSize(); i++) {
                Bus b = buses.get(i);
                if (b.getId_bus().equals(id)) {
                    buses.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (deleted) {
                String info = new Gson().toJson(buses.toArray());
                saveFile(info);
                this.lista_buses = listAll();
                return true;
            }
            return false;
        }
        catch (Exception e) {
            throw new Exception("Error al eliminar el bus: " + e.getMessage());
        }
    }
}
