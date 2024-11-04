package com.example.rest;

import java.util.List;

import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import com.example.controls.dao.services.CuentaService;
import com.example.controls.dao.services.PersonaService;
import com.example.models.Cuenta;
import com.example.models.Persona;

@Path("/api") // Prefijo común para el acceso
public class MyResource {

    private CuentaService cuentaService = new CuentaService();
    private PersonaService personaService = new PersonaService(); // Instancia de PersonaService

    // Obtener todas las cuentas
    @GET
    @Path("/cuentas")
    @Produces(MediaType.APPLICATION_JSON)
    public List<Cuenta> getAllCuentas() {
        return cuentaService.obtenerTodasLasCuentas();
    }

    // Agregar una nueva cuenta
    @POST
    @Path("/cuentas")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response agregarCuenta(Cuenta cuenta) {
        if (cuenta.getPersona() == null || cuenta.getPersona().getId() == 0) {
            return Response.status(Response.Status.BAD_REQUEST).entity("Debe proporcionar un ID de persona válido").build();
        }

        // Busca la persona por ID en el servicio
        Persona persona = personaService.obtenerPersonaPorId(cuenta.getPersona().getId());
        if (persona == null) {
            return Response.status(Response.Status.NOT_FOUND).entity("Persona no encontrada").build();
        }

        // Asocia la cuenta a la persona
        cuenta.setPersona(persona);
        cuentaService.agregarCuenta(cuenta, persona);

        return Response.status(Response.Status.CREATED).entity(cuenta).build();
    }

    // Agregar una nueva persona
    @POST
    @Path("/personas")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response agregarPersona(Persona persona) {
        if (persona == null || persona.getNombre() == null || persona.getApellido() == null) {
            return Response.status(Response.Status.BAD_REQUEST).entity("Debe proporcionar datos válidos para la persona").build();
        }

        personaService.agregarPersona(persona); // Llama al servicio para agregar la persona
        return Response.status(Response.Status.CREATED).entity(persona).build();
    }

    // Obtener todas las personas
    @GET
    @Path("/personas")
    @Produces(MediaType.APPLICATION_JSON)
    public List<Persona> getAllPersonas() {
        return personaService.obtenerTodasLasPersonas(); // Asegúrate de tener este método en el servicio
    }
}
