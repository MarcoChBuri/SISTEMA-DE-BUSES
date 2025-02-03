
package com.buses.rest;

import controlador.servicios.Controlador_boleto;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import java.util.logging.Logger;
import java.util.logging.Level;
import javax.ws.rs.Produces;
import java.util.HashMap;
import javax.ws.rs.Path;
import javax.ws.rs.GET;

@Path("/buses")
public class MyResource {
    private static final Logger logger = Logger.getLogger(MyResource.class.getName());

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response getIt() {
        HashMap<String, Object> response = new HashMap<>();
        Controlador_boleto controlador = new Controlador_boleto();
        String aux = "";
        try {
            controlador.getBoleto().setNumero_asiento(1);
            controlador.save();
            aux = "Lista vacia: " + controlador.Lista_boletos().isEmpty();
            logger.info("Guardado. Lista: " + aux);
        }
        catch (Exception e) {
            logger.log(Level.SEVERE, "Error al guardar: " + e.getMessage(), e);
            e.printStackTrace();
            response.put("error", e.getMessage());
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(response).build();
        }
        response.put("message", "Boleto guardado exitosamente");
        response.put("Data", "Test: " + aux);
        return Response.ok(response).build();
    }
}
