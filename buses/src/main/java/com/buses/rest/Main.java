
package com.buses.rest;

import org.glassfish.jersey.grizzly2.httpserver.GrizzlyHttpServerFactory;
import org.glassfish.grizzly.http.server.HttpServer;
import org.glassfish.jersey.server.ResourceConfig;

import controlador.dao.modelo_dao.Descuento_dao;

import java.io.IOException;
import java.io.File;
import java.net.URI;

public class Main {

    public static final String BASE_URI = "http://localhost:8099/api/";

    public static HttpServer startServer() {
        File dataDir = new File("data");
        if (!dataDir.exists()) {
            dataDir.mkdirs();
        }
        try {
            Descuento_dao descuentoDao = new Descuento_dao();
            descuentoDao.inicializarSiVacio();
        }
        catch (Exception e) {
            System.err.println("Error al inicializar descuentos: " + e.getMessage());
        }
        final ResourceConfig rc = new ResourceConfig().packages("com.buses.rest")
                .packages("com.buses.rest.apis");
        return GrizzlyHttpServerFactory.createHttpServer(URI.create(BASE_URI), rc);
    }

    public static void main(String[] args) throws IOException {
        final HttpServer server = startServer();
        System.out.println(String.format(
                "Jersey app started with WADL available at " + "%sapplication.wadl\nHit enter to stop it...",
                BASE_URI));
        System.in.read();
        server.shutdownNow();
    }
}
