package controlador.dao.modelo_dao;

import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import com.google.gson.Gson;
import modelo.Cuenta;

public class Cuenta_dao extends AdapterDao<Cuenta> {
    private LinkedList<Cuenta> lista_cuentas;
    private Cuenta cuenta;

    public Cuenta_dao() {
        super(Cuenta.class);
    }

    public LinkedList<Cuenta> getLista_cuentas() {
        if (lista_cuentas == null) {
            this.lista_cuentas = listAll();
        }
        return lista_cuentas;
    }

    public Cuenta getCuenta() {
        if (cuenta == null) {
            cuenta = new Cuenta();
        }
        return this.cuenta;
    }

    public void setCuenta(Cuenta cuenta) {
        this.cuenta = cuenta;
    }

    public Boolean save() throws Exception {
        cuenta.setId_cuenta(getLista_cuentas().getSize() + 1);
        persist(cuenta);
        this.lista_cuentas = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        LinkedList<Cuenta> cuentas = getLista_cuentas();
        if (cuentas == null) {
            cuentas = new LinkedList<>();
        }
        if (cuenta.getId_cuenta() == null) {
            cuenta.setId_cuenta(cuentas.getSize() + 1);
            persist(cuenta);
            this.lista_cuentas = listAll();
            return true;
        }
        boolean found = false;
        for (int i = 0; i < cuentas.getSize(); i++) {
            Cuenta c = cuentas.get(i);
            if (c.getId_cuenta().equals(cuenta.getId_cuenta())) {
                merge(cuenta, i);
                this.lista_cuentas = listAll();
                found = true;
                break;
            }
        }
        if (!found) {
            cuenta.setId_cuenta(cuentas.getSize() + 1);
            persist(cuenta);
            this.lista_cuentas = listAll();
        }
        return true;
    }

    // public Boolean update() throws Exception {
    //     LinkedList<Cuenta> cuentas = getLista_cuentas();
    //     if (cuentas == null) {
    //         cuentas = new LinkedList<>();
    //     }
    //     if (cuenta.getId_cuenta() == null) {
    //         cuenta.setId_cuenta(cuentas.getSize() + 1);
    //         persist(cuenta);
    //         this.lista_cuentas = listAll();
    //         return true;
    //     }
    //     boolean found = false;
    //     for (int i = 0; i < cuentas.getSize(); i++) {
    //         Cuenta c = cuentas.get(i);
    //         if (c.getId_cuenta().equals(cuenta.getId_cuenta())) {
    //             merge(cuenta, i);
    //             this.lista_cuentas = listAll();
    //             found = true;
    //             break;
    //         }
    //     }
    //     if (!found) {
    //         cuenta.setId_cuenta(cuentas.getSize() + 1);
    //         persist(cuenta);
    //         this.lista_cuentas = listAll();
    //     }
    //     return true;
    // }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Cuenta> cuentas = getLista_cuentas();
            if (cuentas == null) {
                cuentas = new LinkedList<>();
            }
            boolean deleted = false;
            for (int i = 0; i < cuentas.getSize(); i++) {
                Cuenta c = cuentas.get(i);
                if (c.getId_cuenta().equals(id)) {
                    cuentas.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (deleted) {
                String info = new Gson().toJson(cuentas.toArray());
                saveFile(info);
                this.lista_cuentas = listAll();
                return true;
            }
            throw new Exception("No se encontró la cuenta con el id: " + id);
        }
        catch (Exception e) {
            throw new Exception("Error al eliminar la cuenta: " + e.getMessage());
        }
    }
}
