package com.example.adapters;

public class BusDTO {
    private int id;
    private int numeroBus;
    private String placa;
    private int cantidadAsiento;

    // Constructor
    public BusDTO(int id, int numeroBus, String placa, int cantidadAsiento) {
        this.id = id;
        this.numeroBus = numeroBus;
        this.placa = placa;
        this.cantidadAsiento = cantidadAsiento;
    }

    // Getters y Setters
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getNumeroBus() {
        return numeroBus;
    }

    public void setNumeroBus(int numeroBus) {
        this.numeroBus = numeroBus;
    }

    public String getPlaca() {
        return placa;
    }

    public void setPlaca(String placa) {
        this.placa = placa;
    }

    public int getCantidadAsiento() {
        return cantidadAsiento;
    }

    public void setCantidadAsiento(int cantidadAsiento) {
        this.cantidadAsiento = cantidadAsiento;
    }

    @Override
    public String toString() {
        return "BusDTO{" +
                "id=" + id +
                ", numeroBus=" + numeroBus +
                ", placa='" + placa + '\'' +
                ", cantidadAsiento=" + cantidadAsiento +
                '}';
    }
}
