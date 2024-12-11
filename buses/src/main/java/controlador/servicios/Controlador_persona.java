package controlador.servicios;

import controlador.dao.modelo_dao.Persona_dao;
import controlador.tda.lista.LinkedList;
import modelo.Persona;

public class Controlador_persona {
    private Persona_dao persona_dao;

    public Controlador_persona() {
        persona_dao = new Persona_dao();
    }

    public Boolean save() throws Exception {
        return persona_dao.save();
    }

    public Boolean update() throws Exception {
        return persona_dao.update();
    }

    public LinkedList<Persona> Lista_personas() {
        return persona_dao.getLista_personas();
    }

    public Persona getPersona() {
        return persona_dao.getPersona();
    }

    public void setPersona(Persona persona) {
        persona_dao.setPersona(persona);
    }

    public Persona get(Integer id) throws Exception {
        return persona_dao.get(id);
    }

    public Boolean delete(Integer id) throws Exception {
        return persona_dao.delete(id);
    }
}
