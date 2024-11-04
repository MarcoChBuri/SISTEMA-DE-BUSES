package com.example.controls.dao.services;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

import javax.ws.rs.core.Response;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.example.controls.dao.implement.CuentaDao;
import com.example.models.Cuenta;
import com.example.models.Persona;

public class CuentaService {
    private List<Cuenta> cuentas; // Lista de cuentas en memoria
    private CuentaDao cuentaDao; // Instancia de CuentaDao
    private static final String CARPETA_CUENTAS = "data"; // Carpeta para guardar los archivos
    private ObjectMapper objectMapper;

    public CuentaService() {
        this.cuentas = new ArrayList<>();
        this.cuentaDao = new CuentaDao(); // Inicializa cuentaDao
        this.objectMapper = new ObjectMapper();
        objectMapper.enable(SerializationFeature.INDENT_OUTPUT); 
        cargarCuentas(); // Carga cuentas desde archivos JSON
    }

    public void agregarCuenta(Cuenta cuenta, Persona persona) {
        if (cuenta.getPersona() == null || cuenta.getPersona().getId() == 0) {
            return ;
        }
        
        // Verificar si la cuenta ya existe para esta persona
        List<Cuenta> cuentasExistentes = obtenerCuentasPorPersonaId(persona.getId());

        if (cuentasExistentes.stream().anyMatch(c -> c.getCorreo().equals(cuenta.getCorreo()))) {
            System.out.println("La cuenta con este correo ya existe para esta persona.");
            return; // No agregar la cuenta si ya existe
        }

        // Asociar la cuenta a la persona
        persona.agregarCuenta(cuenta);
        cuentas.add(cuenta);
        guardarCuenta(cuenta);
    }
    
    public List<Cuenta> obtenerCuentasPorPersonaId(Integer personaId) {
        return cuentas.stream()
            .filter(cuenta -> cuenta.getPersona() != null && cuenta.getPersona().getId() != null && cuenta.getPersona().getId().equals(personaId))
            .collect(Collectors.toList());
    }

    // Este método crea el JSON para la cuenta 
    private void guardarCuenta(Cuenta cuenta) {
        try {
            File carpeta = new File(CARPETA_CUENTAS);
            if (!carpeta.exists()) {
                carpeta.mkdir(); // Crea la carpeta si no existe
            }
            String nombreArchivo = CARPETA_CUENTAS + "/" + cuenta.getCorreo().replaceAll(" ", "_") + ".json";
            objectMapper.writeValue(new File(nombreArchivo), cuenta); // Escribe el objeto Cuenta en un archivo JSON
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Método para cargar los archivos de cuentas JSON desde la carpeta
    private void cargarCuentas() {
        try {
            File carpeta = new File(CARPETA_CUENTAS);
            if (carpeta.exists()) {
                File[] archivos = carpeta.listFiles((dir, name) -> name.endsWith(".json"));
                if (archivos != null) {
                    for (File archivo : archivos) {
                        System.out.println("Cargando archivo: " + archivo.getName());
                        Cuenta cuenta = objectMapper.readValue(archivo, Cuenta.class);
                        cuentas.add(cuenta); // Añade cada cuenta a la lista
                        System.out.println("Cuenta cargada: " + cuenta.getCorreo());
                    }
                } else {
                    System.out.println("No se encontraron archivos JSON en la carpeta.");
                }
            } else {
                System.out.println("La carpeta 'data' no existe.");
            }
        } catch (IOException e) {
            e.printStackTrace();
            cuentas = new ArrayList<>(); // Inicializa lista vacía en caso de error
        }
    }

    // Método para obtener todas las cuentas
    public List<Cuenta> obtenerTodasLasCuentas() {
        return cuentas; // Retorna la lista de cuentas cargadas
    }
}
