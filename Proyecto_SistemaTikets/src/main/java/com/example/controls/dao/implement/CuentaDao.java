package com.example.controls.dao.implement;

import java.util.ArrayList;
import java.util.List;

import com.example.models.Cuenta;


public class CuentaDao {
    private List<Cuenta> cuentas;
    
    public boolean validarUsuario(String correo, String clave) {
        for (Cuenta cuenta : cuentas) {
            
            if (cuenta.getCorreo().equals(correo) && cuenta.getClave().equals(clave)) {
                return true;
            }
        }
        return false;
    }

    public CuentaDao() {
        cuentas = new ArrayList<>(); // Inicializa la lista de cuentas.
    }

    public void guardar(Cuenta cuenta) {
        cuentas.add(cuenta);
    }

    public Cuenta buscarId(int id) {
        for (Cuenta cuenta : cuentas) {
            if (cuenta.getId() == id) {
                return cuenta;
            }
        }
        return null;
    }

    public  List<Cuenta> getAll() {
        return cuentas;
    }
}
