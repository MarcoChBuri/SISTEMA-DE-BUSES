package modelo;

import controlador.tda.lista.LinkedList;
import modelo.enums.Estado_ruta;

public class Ruta {
    private Integer id_ruta;
    private String origen;
    private String destino;
    private float precio_unitario;
    private Integer distancia;
    private String tiempo_estimado;
    private Estado_ruta estado_ruta;

    private LinkedList<Escala> escalas;
    private Bus bus;

    public Ruta() {

    }

    public Ruta(Integer id_ruta, String origen, String destino, float precio_unitario, Integer distancia,
            String tiempo_estimado, Estado_ruta estado_ruta, LinkedList<Escala> escalas, Bus bus) {
        this.id_ruta = id_ruta;
        this.origen = origen;
        this.destino = destino;
        this.precio_unitario = precio_unitario;
        this.distancia = distancia;
        this.tiempo_estimado = tiempo_estimado;
        this.estado_ruta = estado_ruta;
        this.escalas = escalas;
        this.bus = bus;
    }

    public Integer getId_ruta() {
        return id_ruta;
    }

    public void setId_ruta(Integer id_ruta) {
        this.id_ruta = id_ruta;
    }

    public String getOrigen() {
        return origen;
    }

    public void setOrigen(String origen) {
        this.origen = origen;
    }

    public String getDestino() {
        return destino;
    }

    public void setDestino(String destino) {
        this.destino = destino;
    }

    public float getPrecio_unitario() {
        return precio_unitario;
    }

    public void setPrecio_unitario(float precio_unitario) {
        this.precio_unitario = precio_unitario;
    }

    public Integer getDistancia() {
        return distancia;
    }

    public void setDistancia(Integer distancia) {
        this.distancia = distancia;
    }

    public String getTiempo_estimado() {
        return tiempo_estimado;
    }

    public void setTiempo_estimado(String tiempo_estimado) {
        this.tiempo_estimado = tiempo_estimado;
    }

    public Estado_ruta getEstado_ruta() {
        return estado_ruta;
    }

    public void setEstado_ruta(Estado_ruta estado_ruta) {
        this.estado_ruta = estado_ruta;
    }

    public LinkedList<Escala> getEscalas() {
        return escalas;
    }

    public void setEscalas(LinkedList<Escala> escalas) {
        this.escalas = escalas;
    }

    public Bus getBus() {
        return bus;
    }

    public void setBus(Bus bus) {
        this.bus = bus;
    }

    @Override
    public String toString() {
        return "id_ruta=" + id_ruta + ", origen=" + origen + ", destino=" + destino + ", precio_unitario="
                + precio_unitario + ", distancia=" + distancia + ", tiempo_estimado=" + tiempo_estimado
                + ", estado_ruta=" + estado_ruta + ", escalas=" + escalas + ", bus=" + bus;
    }

}
