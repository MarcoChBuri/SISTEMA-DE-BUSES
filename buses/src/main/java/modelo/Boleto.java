package modelo;

import modelo.enums.Estado_boleto;

public class Boleto {
    private Integer id_boleto;
    private String fecha_compra;
    private Integer numero_asiento;
    private Integer cantidad_boleto;
    private float precio_final;
    private Estado_boleto estado_boleto;

    private Persona persona;
    private Turno turno;
    private Descuento descuento;

    public Boleto() {

    }

    public Boleto(Integer id_boleto, String fecha_compra, Integer numero_asiento, Integer cantidad_boleto,
            float precio_final, Estado_boleto estado_boleto, Persona persona, Turno turno,
            Descuento descuento) {
        this.id_boleto = id_boleto;
        this.fecha_compra = fecha_compra;
        this.numero_asiento = numero_asiento;
        this.cantidad_boleto = cantidad_boleto;
        this.precio_final = precio_final;
        this.estado_boleto = estado_boleto;
        this.persona = persona;
        this.turno = turno;
        this.descuento = descuento;
    }

    public Integer getId_boleto() {
        return id_boleto;
    }

    public void setId_boleto(Integer id_boleto) {
        this.id_boleto = id_boleto;
    }

    public String getFecha_compra() {
        return fecha_compra;
    }

    public void setFecha_compra(String fecha_compra) {
        this.fecha_compra = fecha_compra;
    }

    public Integer getNumero_asiento() {
        return numero_asiento;
    }

    public void setNumero_asiento(Integer numero_asiento) {
        this.numero_asiento = numero_asiento;
    }

    public Integer getCantidad_boleto() {
        return cantidad_boleto;
    }

    public void setCantidad_boleto(Integer cantidad_boleto) {
        this.cantidad_boleto = cantidad_boleto;
    }

    public float getPrecio_final() {
        return precio_final;
    }

    public void setPrecio_final(float precio_final) {
        this.precio_final = precio_final;
    }

    public Estado_boleto getEstado_boleto() {
        return estado_boleto;
    }

    public void setEstado_boleto(Estado_boleto estado_boleto) {
        this.estado_boleto = estado_boleto;
    }

    public Persona getPersona() {
        return persona;
    }

    public void setPersona(Persona persona) {
        this.persona = persona;
    }

    public Turno getTurno() {
        return turno;
    }

    public void setTurno(Turno turno) {
        this.turno = turno;
    }

    public Descuento getDescuento() {
        return descuento;
    }

    public void setDescuento(Descuento descuento) {
        this.descuento = descuento;
    }

    @Override
    public String toString() {
        return "id_boleto=" + id_boleto + ", fecha_compra=" + fecha_compra + ", numero_asiento="
                + numero_asiento + ", cantidad_boleto=" + cantidad_boleto + ", precio_final=" + precio_final
                + ", estado_boleto=" + estado_boleto + ", persona=" + persona + ", turno=" + turno
                + ", descuento=" + descuento;
    }

}
