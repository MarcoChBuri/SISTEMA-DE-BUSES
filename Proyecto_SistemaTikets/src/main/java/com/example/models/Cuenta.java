package com.example.models;

import com.fasterxml.jackson.annotation.JsonBackReference;

public class Cuenta {
    private Integer id;
    private String correo;
    private String clave;
    private boolean estado;
    @JsonBackReference
    private Persona persona;

    public Cuenta() {}

    public Cuenta(Integer id, String correo, String clave, boolean estado) {
        this.id = id;
        this.correo = correo;
        this.clave = clave;
        this.estado = estado;
    }

    public void asignarPersona(Persona persona) {
        if (this.persona == null) {
            this.persona = persona;
            persona.agregarCuenta(this);
        }
    }
    public Integer getId() {
        return id;
    }


    public void setId(Integer id) {
        this.id = id;
    }


    public String getCorreo() {
        return correo;
    }


    public void setCorreo(String correo) {
        this.correo = correo;
    }


    public String getClave() {
        return clave;
    }


    public void setClave(String clave) {
        this.clave = clave;
    }


    public boolean isEstado() {
        return estado;
    }


    public void setEstado(boolean estado) {
        this.estado = estado;
    }
    public Persona getPersona() {
        return persona;
    }

    public void setPersona(Persona persona) {
        this.persona = persona;
    }
    public String mostrarInformacion() {
        return "Cuenta{" +
            "id=" + id +
            ", correo='" + correo + '\'' +
            ", estado=" + estado +
            ", persona=" + (persona != null ? persona.getNombre() + " " + persona.getApellido() : "N/A") +
            '}';
    }
}
