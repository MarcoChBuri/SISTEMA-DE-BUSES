package controlador.servicios;

import controlador.dao.modelo_dao.Cuenta_dao;
import controlador.tda.lista.LinkedList;
import modelo.Cuenta;

public class Controlador_cuenta {
    private Cuenta_dao cuenta_dao;

    public Controlador_cuenta() {
        cuenta_dao = new Cuenta_dao();
    }

    public Boolean save() throws Exception {
        return cuenta_dao.save();
    }

    public Boolean update() throws Exception {
        return cuenta_dao.update();
    }

    public LinkedList<Cuenta> Lista_cuentas() {
        return cuenta_dao.getLista_cuentas();
    }

    public Cuenta getCuenta() {
        return cuenta_dao.getCuenta();
    }

    public void setCuenta(Cuenta cuenta) {
        cuenta_dao.setCuenta(cuenta);
    }

    public Cuenta get(Integer id) throws Exception {
        return cuenta_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return cuenta_dao.delete(id);
    }
}