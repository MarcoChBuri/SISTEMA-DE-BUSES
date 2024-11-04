package com.example.controls.dao.services;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.example.controls.dao.implement.PersonaDao;
import com.example.models.Persona;

public class PersonaService {
    private PersonaDao personaDao;
    private List<Persona> personas; // No estático, lista de personas en memoria
    private ObjectMapper objectMapper;
    private static final String CARPETA_PERSONAS = "data/personas"; // Carpeta para guardar archivos JSON

    // Constructor para inicializar PersonaDao y ObjectMapper
    public PersonaService() {
        this.personaDao = new PersonaDao();
        this.objectMapper = new ObjectMapper();
        this.objectMapper.enable(SerializationFeature.INDENT_OUTPUT); // Para JSON legible
        this.personas = new ArrayList<>(); // Inicializa la lista de personas
        cargarPersonasDesdeArchivos();
    }

    // Método para cargar personas desde archivos JSON
private void cargarPersonasDesdeArchivos() {
    File carpeta = new File(CARPETA_PERSONAS);
    if (carpeta.exists()) {
        File[] archivos = carpeta.listFiles();
        if (archivos != null) {
            for (File archivo : archivos) {
                try {
                    Persona persona = objectMapper.readValue(archivo, Persona.class);
                    personas.add(persona); // Agrega la persona a la lista en memoria
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}

    // Método para agregar persona y guardar en archivo JSON
    public void agregarPersona(Persona persona) {
        
        personas.add(persona); // Agrega la persona a la lista en memoria
        personaDao.guardar(persona); // Guardar en lista del DAO
        guardarPersona(persona); // Guardar en archivo JSON
    }

    // Método para buscar persona por ID
    public Persona obtenerPersonaPorId(int id) {
        for (Persona persona : personas) {
            if (persona.getId() == id) {
                return persona;
            }
        }
        return null; // Si no se encuentra la persona
    }

    // Guardar una persona en un archivo JSON
    private void guardarPersona(Persona persona) {
        try {
            File carpeta = new File(CARPETA_PERSONAS);
            if (!carpeta.exists()) {
                carpeta.mkdirs(); // Crear la carpeta si no existe
            }
            String nombreArchivo = CARPETA_PERSONAS + "/" + persona.getId() + "_" + persona.getNombre() + ".json";
            objectMapper.writeValue(new File(nombreArchivo), persona);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public List<Persona> obtenerTodasLasPersonas() {
        return personas;
    }
}
