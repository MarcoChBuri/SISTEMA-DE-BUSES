package modelo;

import modelo.enums.Identificacion;
import modelo.enums.Tipo_tarifa;
import modelo.enums.Genero;

public class Persona {
    private Integer id_persona;
    private Identificacion tipo_identificacion;
    private String numero_identificacion;
    private String nombre;
    private String apellido;
    private Genero genero;
    private String correo;
    private String telefono;
    private String direccion;
    private String fecha_nacimiento;
    private Float saldo_disponible;

    private Tipo_tarifa tipo_tarifa;
    private Cuenta cuenta;
    private Pago metodo_pago;

    public Persona() {

    }

    public Persona(Integer id_persona, Identificacion tipo_identificacion, String numero_identificacion,
            String nombre, String apellido, Genero genero, String correo, String telefono, String direccion,
            String fecha_nacimiento, Float saldo_disponible, Tipo_tarifa tipo_tarifa, Cuenta cuenta,
            Pago metodo_pago) {
        this.id_persona = id_persona;
        this.tipo_identificacion = tipo_identificacion;
        this.numero_identificacion = numero_identificacion;
        this.nombre = nombre;
        this.apellido = apellido;
        this.genero = genero;
        this.correo = correo;
        this.telefono = telefono;
        this.direccion = direccion;
        this.fecha_nacimiento = fecha_nacimiento;
        this.saldo_disponible = saldo_disponible;
        this.tipo_tarifa = tipo_tarifa;
        this.cuenta = cuenta;
        this.metodo_pago = metodo_pago;
    }

    public Integer getId_persona() {
        return id_persona;
    }

    public void setId_persona(Integer id_persona) {
        this.id_persona = id_persona;
    }

    public Identificacion getTipo_identificacion() {
        return tipo_identificacion;
    }

    public void setTipo_identificacion(Identificacion tipo_identificacion) {
        this.tipo_identificacion = tipo_identificacion;
    }

    public String getNumero_identificacion() {
        return numero_identificacion;
    }

    public void setNumero_identificacion(String numero_identificacion) {
        this.numero_identificacion = numero_identificacion;
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

    public Genero getGenero() {
        return genero;
    }

    public void setGenero(Genero genero) {
        this.genero = genero;
    }

    public String getCorreo() {
        return correo;
    }

    public void setCorreo(String correo) {
        this.correo = correo;
    }

    public String getTelefono() {
        return telefono;
    }

    public void setTelefono(String telefono) {
        this.telefono = telefono;
    }

    public String getDireccion() {
        return direccion;
    }

    public void setDireccion(String direccion) {
        this.direccion = direccion;
    }

    public String getFecha_nacimiento() {
        return fecha_nacimiento;
    }

    public void setFecha_nacimiento(String fecha_nacimiento) {
        this.fecha_nacimiento = fecha_nacimiento;
    }

    public Float getSaldo_disponible() {
        return saldo_disponible;
    }

    public void setSaldo_disponible(Float saldo_disponible) {
        this.saldo_disponible = saldo_disponible;
    }

    public Tipo_tarifa getTipo_tarifa() {
        return tipo_tarifa;
    }

    public void setTipo_tarifa(Tipo_tarifa tipo_tarifa) {
        this.tipo_tarifa = tipo_tarifa;
    }

    public Cuenta getCuenta() {
        return cuenta;
    }

    public void setCuenta(Cuenta cuenta) {
        this.cuenta = cuenta;
    }

    public Pago getMetodo_pago() {
        return metodo_pago;
    }

    public void setMetodo_pago(Pago metodo_pago) {
        this.metodo_pago = metodo_pago;
    }

    @Override
    public String toString() {
        return "id_persona=" + id_persona + ", tipo_identificacion=" + tipo_identificacion
                + ", numero_identificacion=" + numero_identificacion + ", nombre=" + nombre + ", apellido="
                + apellido + ", genero=" + genero + ", correo=" + correo + ", telefono=" + telefono
                + ", direccion=" + direccion + ", fecha_nacimiento=" + fecha_nacimiento
                + ", saldo_disponible=" + saldo_disponible + ", tipo_tarifa=" + tipo_tarifa + ", cuenta="
                + cuenta + ", metodo_pago=" + metodo_pago;
    }

}
