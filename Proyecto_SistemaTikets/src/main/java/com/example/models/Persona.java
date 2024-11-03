package com.example.models;

import com.example.models.Enum.Genero;
import com.example.models.Enum.Identificacion;
import java.util.Date;

public class Persona {
    private int id;
    private String nombre;
    private String apellido;
    private String direccion;
    private Date fechaNacimiento;
    private Genero genero;
    private String telefono;
    private Identificacion tipoIdentificacion;
    private String identificacion;

    //Constructor
    public Persona(int id, String nombre, String apellido, String direccion, Date fechaNacimiento,
                   Genero genero, String telefono, Identificacion tipoIdentificacion, String identificacion) {
        this.id = id;
        this.nombre = nombre;
        this.apellido = apellido;
        this.direccion = direccion;
        this.fechaNacimiento = fechaNacimiento;
        this.genero = genero;
        this.telefono = telefono;
        this.tipoIdentificacion = tipoIdentificacion;
        this.identificacion = identificacion;
    }

    // Getters y setters
    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public String getApellido() {
        return apellido;
    }

    public void setApellido(String apellido) {
        this.apellido = apellido;
    }

    public String getDireccion() {
        return direccion;
    }

    public void setDireccion(String direccion) {
        this.direccion = direccion;
    }

    public Date getFechaNacimiento() {
        return fechaNacimiento;
    }

    public void setFechaNacimiento(Date fechaNacimiento) {
        this.fechaNacimiento = fechaNacimiento;
    }

    public Genero getGenero() {
        return genero;
    }

    public void setGenero(Genero genero) {
        this.genero = genero;
    }

    public String getTelefono() {
        return telefono;
    }

    public void setTelefono(String telefono) {
        this.telefono = telefono;
    }

    public Identificacion getTipoIdentificacion() {
        return tipoIdentificacion;
    }

    public void setTipoIdentificacion(Identificacion tipoIdentificacion) {
        this.tipoIdentificacion = tipoIdentificacion;
    }

    public String getIdentificacion() {
        return identificacion;
    }

    public void setIdentificacion(String identificacion) {
        this.identificacion = identificacion;
    }

    @Override
    public String toString() {
        return "Persona{" +
                "id=" + id +
                ", nombre='" + nombre + '\'' +
                ", apellido='" + apellido + '\'' +
                ", direccion='" + direccion + '\'' +
                ", fechaNacimiento=" + fechaNacimiento +
                ", genero=" + genero +
                ", telefono='" + telefono + '\'' +
                ", tipoIdentificacion=" + tipoIdentificacion +
                ", identificacion='" + identificacion + '\'' +
                '}';
    }
}