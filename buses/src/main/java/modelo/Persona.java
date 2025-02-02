package modelo;

import modelo.enums.Identificacion;
import modelo.enums.Genero;

public class Persona {
    private Integer id_persona;
    private String nombre;
    private String apellido;
    private String direccion;
    private String fecha_nacimiento;
    private String telefono;
    private Genero genero;
    private String correo;
    private Float saldo_disponible;
    private String numero_identificacion;

    private Identificacion tipo_identificacion;
    private Cuenta cuenta;
    private Pago metodo_pago;

    public Persona() {

    }

    public Persona(Integer id_persona, String nombre, String apellido, String direccion, String fecha_nacimiento, String telefono, Genero genero, String correo, Float saldo_disponible, String numero_identificacion, Identificacion tipo_identificacion, Cuenta cuenta, Pago metodo_pago) {
        this.id_persona = id_persona;
        this.nombre = nombre;
        this.apellido = apellido;
        this.direccion = direccion;
        this.fecha_nacimiento = fecha_nacimiento;
        this.telefono = telefono;
        this.genero = genero;
        this.correo = correo;
        this.saldo_disponible = saldo_disponible;
        this.numero_identificacion = numero_identificacion;
        this.tipo_identificacion = tipo_identificacion;
        this.cuenta = cuenta;
        this.metodo_pago = metodo_pago;
    }

    public Integer getId_persona() {
        return id_persona;
    }

    public void setId_persona(Integer id_persona) {
        this.id_persona = id_persona;
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

    public String getFecha_nacimiento() {
        return fecha_nacimiento;
    }

    public void setFecha_nacimiento(String fecha_nacimiento) {
        this.fecha_nacimiento = fecha_nacimiento;
    }

    public String getTelefono() {
        return telefono;
    }

    public void setTelefono(String telefono) {
        this.telefono = telefono;
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

    public Float getSaldo_disponible() {
        return saldo_disponible;
    }

    public void setSaldo_disponible(Float saldo_disponible) {
        this.saldo_disponible = saldo_disponible;
    }

    public String getNumero_identificacion() {
        return numero_identificacion;
    }

    public void setNumero_identificacion(String numero_identificacion) {
        this.numero_identificacion = numero_identificacion;
    }

    public Identificacion getTipo_identificacion() {
        return tipo_identificacion;
    }

    public void setTipo_identificacion(Identificacion tipo_identificacion) {
        this.tipo_identificacion = tipo_identificacion;
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
        return "Persona{" + "id_persona=" + id_persona + ", nombre=" + nombre + ", apellido=" + apellido + ", direccion=" + direccion + ", fecha_nacimiento=" + fecha_nacimiento + ", telefono=" + telefono + ", genero=" + genero + ", correo=" + correo + ", saldo_disponible=" + saldo_disponible + ", numero_identificacion=" + numero_identificacion + ", tipo_identificacion=" + tipo_identificacion + ", cuenta=" + cuenta + ", metodo_pago=" + metodo_pago + '}';
    }

    
}
