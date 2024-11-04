package com.example.rest;

import org.glassfish.grizzly.http.server.HttpServer;
import org.glassfish.jersey.grizzly2.httpserver.GrizzlyHttpServerFactory;
import org.glassfish.jersey.server.ResourceConfig;

import com.example.controls.dao.services.CuentaService;
import com.example.controls.dao.services.PersonaService;
import com.example.models.Cuenta;
import com.example.models.Persona;
import com.example.models.Enum.Genero;
import com.example.models.Enum.Identificacion;

import java.net.URI;
import java.util.Date;

public class Main {
<<<<<<< HEAD
    // Base URI the Grizzly HTTP server will listen on
    public static final String BASE_URI = "http://localhost:9090/myapp/";
=======
    // Base URI where the Grizzly HTTP server will listen
    public static final String BASE_URI = "http://localhost:8080/myapp/";
>>>>>>> DILAN

    public static HttpServer startServer() {
        final ResourceConfig rc = new ResourceConfig().packages("com.example.rest");
        return GrizzlyHttpServerFactory.createHttpServer(URI.create(BASE_URI), rc);
    }

    public static void main(String[] args) {
        // Start the Grizzly server
        final HttpServer server = startServer();
        System.out.println("Server running at: " + BASE_URI);
        
        // Services for managing personas and cuentas
        PersonaService personaService = new PersonaService();
        CuentaService cuentaService = new CuentaService();
        
        // Create a new Persona
        Persona persona = new Persona(1, "Juan", "Perez", "Calle Falsa 123", new Date(),
                Genero.MASCULINO, "123456789", Identificacion.DNI, "987654321");
        
        // Add the Persona to the PersonaService
        personaService.agregarPersona(persona);
        
        // Create a new Cuenta associated with the Persona
        Cuenta cuenta1 = new Cuenta(1, "juan.perez@example.com", "password123", true);
        cuenta1.asignarPersona(persona); // Asigna la persona a la cuenta
    
        // Link the Cuentas to the Persona in the CuentaService
        cuentaService.agregarCuenta(cuenta1, persona);
        
        // Display Persona's account information
        System.out.println("Cuentas de la persona: " + persona.getNombre() + " " + persona.getApellido());
        for (Cuenta cuenta : persona.getCuentas()) {
            System.out.println(cuenta.mostrarInformacion());
        }
    
        // Ensure the server shuts down properly
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            server.shutdownNow();
            System.out.println("Server stopped.");
        }));
    }
    
}