package controlador.dao.modelo_dao;

import controlador.dao.utiles.Sincronizar;
import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import com.google.gson.Gson;
import modelo.Persona;

public class Persona_dao extends AdapterDao<Persona> {
    private LinkedList<Persona> lista_personas;
    private Persona persona;

    public Persona_dao() {
        super(Persona.class);
    }

    public LinkedList<Persona> getLista_personas() {
        if (lista_personas == null) {
            this.lista_personas = listAll();
        }
        return lista_personas;
    }

    public Persona getPersona() {
        if (persona == null) {
            persona = new Persona();
        }
        return this.persona;
    }

    public void setPersona(Persona persona) {
        this.persona = persona;
    }

    public Boolean save() throws Exception {
        if (persona.getCuenta() != null) {
            Cuenta_dao cuentaDao = new Cuenta_dao();
            cuentaDao.setCuenta(persona.getCuenta());
            if (cuentaDao.save()) {
                persona.getCuenta().setId_cuenta(cuentaDao.getCuenta().getId_cuenta());
            }
            else {
                throw new Exception("Error al guardar la cuenta asociada");
            }
        }
        if (persona.getMetodo_pago() != null) {
            Pago_dao pagoDao = new Pago_dao();
            pagoDao.setPago(persona.getMetodo_pago());
            if (pagoDao.save()) {
                persona.getMetodo_pago().setId_pago(pagoDao.getPago().getId_pago());
            }
        }
        persona.setId_persona(getLista_personas().getSize() + 1);
        persist(persona);
        this.lista_personas = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        try {
            if (persona == null || persona.getId_persona() == null) {
                throw new Exception("Persona o ID de persona no válido");
            }
            LinkedList<Persona> personas = getLista_personas();
            boolean found = false;
            for (int i = 0; i < personas.getSize(); i++) {
                Persona p = personas.get(i);
                if (p.getId_persona().equals(persona.getId_persona())) {
                    merge(persona, i);
                    found = true;
                    Sincronizar.sincronizarPersona(getPersona());
                    break;
                }
            }
            if (!found) {
                throw new Exception("No se encontró la persona con ID: " + persona.getId_persona());
            }
            this.lista_personas = listAll();
            return true;
        }
        catch (Exception e) {
            throw new Exception("Error al actualizar la persona: " + e.getMessage());
        }
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            Persona persona = get(id);
            if (persona == null) {
                throw new Exception("No se encontró la persona con el id: " + id);
            }
            if (persona.getCuenta() != null && persona.getCuenta().getId_cuenta() != null) {
                Cuenta_dao cuentaDao = new Cuenta_dao();
                cuentaDao.delete(persona.getCuenta().getId_cuenta());
            }
            if (persona.getMetodo_pago() != null && persona.getMetodo_pago().getId_pago() != null) {
                Pago_dao pagoDao = new Pago_dao();
                pagoDao.delete(persona.getMetodo_pago().getId_pago());
            }
            LinkedList<Persona> personas = getLista_personas();
            for (int i = 0; i < personas.getSize(); i++) {
                if (personas.get(i).getId_persona().equals(id)) {
                    personas.delete(i);
                    String info = new Gson().toJson(personas.toArray());
                    saveFile(info);
                    this.lista_personas = listAll();
                    return true;
                }
            }
            return false;
        }
        catch (Exception e) {
            throw new Exception("Error al eliminar la persona: " + e.getMessage());
        }
    }
}
