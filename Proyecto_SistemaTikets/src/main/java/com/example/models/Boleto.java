package com.example.models;
import java.util.Date;



public class Boleto {
    private Integer id;
    private Date fecha;
    private float precioFinal;
    private Bus idBus;
    private Persona persona;

    public Integer getId() {
        return this.id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public Date getFecha() {
        return this.fecha;
    }

    public void setFecha(Date fecha) {
        this.fecha = fecha;
    }

    public float getPrecioFinal() {
        return this.precioFinal;
    }

    public void setPrecioFinal(float precioFinal) {
        this.precioFinal = precioFinal;
    }

    public Bus getIdBus() {
        return this.idBus;
    }

    public void setIdBus(Bus idBus) {
        this.idBus = idBus;
    }

    public Persona getPersona() {
        return this.persona;
    }

    public void setPersona(Persona persona) {
        this.persona = persona;
    }

}
