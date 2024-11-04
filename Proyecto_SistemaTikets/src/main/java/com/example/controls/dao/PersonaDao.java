
package com.example.controls.dao;

import com.example.models.Persona;
import java.util.ArrayList;
import java.util.List;
import com.example.models.Cuenta;

public class PersonaDao {
    private List<Persona> personas;

    public PersonaDao() {
        personas = new ArrayList<>();
    }

    // Aggregar una nueva persona
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

    //LA CLASE PERSONA NO TINE CORREO REVSEN ESO PORFA


    //public boolean validarUsuario(String correo, String clave) {
        //for (Persona persona : personas) {
          //  if (persona.getCorreo().equals(correo) && persona.getClave().equals(clave)) {
          //      return true;
          //  }
      //  }
      //  return false;
    //}
}
