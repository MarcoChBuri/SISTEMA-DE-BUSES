package com.example.models;

public class Ruta {
    private int id;
    private String destino;
    private String origen;

    public Ruta(int id, String destino, String origen) {
        this.id = id;
        this.destino = destino;
        this.origen = origen;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getDestino() {
        return destino;
    }

    public void setDestino(String destino) {
        this.destino = destino;
    }

    public String getOrigen() {
        return origen;
    }

    public void setOrigen(String origen) {
        this.origen = origen;
    }
}
