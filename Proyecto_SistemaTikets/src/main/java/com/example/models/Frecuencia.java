package com.example.models;

public class Frecuencia {
    private int id;
    private int numeroRepeticiones;
    private String periodo;
    private float precioRecorrido;
    private Horario horario;
    private Ruta ruta;
    private int idTurno;

    public Frecuencia(int id, int numeroRepeticiones, String periodo, float precioRecorrido, Horario horario, Ruta ruta,
            int idTurno) {
        this.id = id;
        this.numeroRepeticiones = numeroRepeticiones;
        this.periodo = periodo;
        this.precioRecorrido = precioRecorrido;
        this.horario = horario;
        this.ruta = ruta;
        this.idTurno = idTurno;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getNumeroRepeticiones() {
        return numeroRepeticiones;
    }

    public void setNumeroRepeticiones(int numeroRepeticiones) {
        this.numeroRepeticiones = numeroRepeticiones;
    }

    public String getPeriodo() {
        return periodo;
    }

    public void setPeriodo(String periodo) {
        this.periodo = periodo;
    }

    public float getPrecioRecorrido() {
        return precioRecorrido;
    }

    public void setPrecioRecorrido(float precioRecorrido) {
        this.precioRecorrido = precioRecorrido;
    }

    public Horario getHorario() {
        return horario;
    }

    public void setHorario(Horario horario) {
        this.horario = horario;
    }

    public Ruta getRuta() {
        return ruta;
    }

    public void setRuta(Ruta ruta) {
        this.ruta = ruta;
    }

    public int getIdTurno() {
        return idTurno;
    }

    public void setIdTurno(int idTurno) {
        this.idTurno = idTurno;
    }
}
