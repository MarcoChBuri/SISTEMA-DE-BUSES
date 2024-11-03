<<<<<<< HEAD
package com.example.controls.dao.services;

public class PersonaServices {
    
=======
package examples.controls.dao.servicies;

import examples.dao.PersonaDAO;
import examples.models.Persona;

public class PersonaService {
    private PersonaDAO personaDAO;

    public PersonaService() {
        this.personaDAO = new PersonaDAO();
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
>>>>>>> fc8ae8d77d957ddfc028d2bbece9579ecd517977
}
