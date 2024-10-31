package com.example.models;

import java.util.Date;

public class Turno {
    private int id;
    private int numeroTurno;
    private Date fecha;
    private String horario;
    private int idFrecuencia; // Relación con Frecuencia

    // Constructor
    public Turno(int id, int numeroTurno, Date fecha, String horario, int idFrecuencia) {
        this.id = id;
        this.numeroTurno = numeroTurno;
        this.fecha = fecha;
        this.horario = horario;
        this.idFrecuencia = idFrecuencia;
    }

    // Getters y Setters
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getNumeroTurno() {
        return numeroTurno;
    }

    public void setNumeroTurno(int numeroTurno) {
        this.numeroTurno = numeroTurno;
    }

    public Date getFecha() {
        return fecha;
    }

    public void setFecha(Date fecha) {
        this.fecha = fecha;
    }

    public String getHorario() {
        return horario;
    }

    public void setHorario(String horario) {
        this.horario = horario;
    }

    public int getIdFrecuencia() {
        return idFrecuencia;
    }

    public void setIdFrecuencia(int idFrecuencia) {
        this.idFrecuencia = idFrecuencia;
    }

    @Override
    public String toString() {
        return "Turno{" +
                "id=" + id +
                ", numeroTurno=" + numeroTurno +
                ", fecha=" + fecha +
                ", horario='" + horario + '\'' +
                ", idFrecuencia=" + idFrecuencia +
                '}';
    }
}
