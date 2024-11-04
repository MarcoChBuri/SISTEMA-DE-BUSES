package com.example.controls.dao.services;

import com.example.controls.dao.PersonaDao;
import com.example.models.Persona;

public class PersonaServices {
    private PersonaDao personaDAO;

    public PersonaServices() {
        this.personaDAO = new PersonaDao();
    }

    public void agregarPersona(Persona persona) {
        personaDAO.guardar(persona);
    }

    public void actualizarPersona(Persona persona) {
        personaDAO.actualizar(persona);
    }

    public Persona buscarPersonaId(int id) {
        return personaDAO.buscarId(id);
    }

    // Validar usuario
    public boolean validarUsuario(String correo, String clave) {
        return personaDAO.validarUsuario(correo, clave);
    }
}
