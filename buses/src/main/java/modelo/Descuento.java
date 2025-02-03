package modelo;

import modelo.enums.Estado_descuento;
import modelo.enums.Tipo_descuento;

public class Descuento {
    private Integer id_descuento;
    private String nombre_descuento;
    private String descripcion;
    private Integer porcentaje;
    private String fecha_inicio;
    private String fecha_fin;

    private Estado_descuento estado_descuento;
    private Tipo_descuento tipo_descuento;

    public Descuento() {

    }

    public Descuento(Integer id_descuento, String nombre_descuento, String descripcion, Integer porcentaje,
            String fecha_inicio, String fecha_fin, Estado_descuento estado_descuento,
            Tipo_descuento tipo_descuento) {
        this.id_descuento = id_descuento;
        this.nombre_descuento = nombre_descuento;
        this.descripcion = descripcion;
        this.porcentaje = porcentaje;
        this.estado_descuento = estado_descuento;
        this.tipo_descuento = tipo_descuento;
    }

    public Integer getId_descuento() {
        return id_descuento;
    }

    public void setId_descuento(Integer id_descuento) {
        this.id_descuento = id_descuento;
    }

    public String getNombre_descuento() {
        return nombre_descuento;
    }

    public void setNombre_descuento(String nombre_descuento) {
        this.nombre_descuento = nombre_descuento;
    }

    public String getDescripcion() {
        return descripcion;
    }

    public void setDescripcion(String descripcion) {
        this.descripcion = descripcion;
    }

    public Integer getPorcentaje() {
        return porcentaje;
    }

    public void setPorcentaje(Integer porcentaje) {
        this.porcentaje = porcentaje;
    }

    public String getFecha_inicio() {
        return fecha_inicio;
    }

    public void setFecha_inicio(String fecha_inicio) {
        this.fecha_inicio = fecha_inicio;
    }

    public String getFecha_fin() {
        return fecha_fin;
    }

    public void setFecha_fin(String fecha_fin) {
        this.fecha_fin = fecha_fin;
    }

    public Estado_descuento getEstado_descuento() {
        return estado_descuento;
    }

    public void setEstado_descuento(Estado_descuento estado_descuento) {
        this.estado_descuento = estado_descuento;
    }

    public Tipo_descuento getTipo_descuento() {
        return tipo_descuento;
    }

    public void setTipo_descuento(Tipo_descuento tipo_descuento) {
        this.tipo_descuento = tipo_descuento;
    }

    @Override
    public String toString() {
        return "id_descuento=" + id_descuento + ", nombre_descuento=" + nombre_descuento + ", descripcion="
                + descripcion + ", porcentaje=" + porcentaje + ", fecha_inicio=" + fecha_inicio
                + ", fecha_fin=" + fecha_fin + ", estado_descuento=" + estado_descuento + ", tipo_descuento="
                + tipo_descuento;
    }

}
