package com.example.controls.dao.implement;

import com.example.models.Persona;
import java.util.ArrayList;
import java.util.List;

public class PersonaDao {
    private List<Persona> personas;

    public PersonaDao() {
        personas = new ArrayList<>();
    }

    // Agregar una nueva persona
    public void guardar(Persona persona) {
        personas.add(persona);
    }

    // Actualizar una persona
    public void actualizar(Persona persona) {
        for (int i = 0; i < personas.size(); i++) {
            if (personas.get(i).getId() == persona.getId()) {
                personas.set(i, persona);
                break;
            }
        }
    }

    // Buscar por ID
    public Persona buscarId(int id) {
        for (Persona persona : personas) {
            if (persona.getId() == id) {
                return persona;
            }
        }
        return null;
    }

    
}
