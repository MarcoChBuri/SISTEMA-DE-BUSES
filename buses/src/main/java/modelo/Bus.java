package modelo;

import modelo.enums.Estado_bus;

public class Bus {
    private Integer id_bus;
    private Integer numero_bus;
    private String placa;
    private String marca;
    private String modelo;
    private Integer capacidad_pasajeros;
    private Integer Velocidad;
    private Estado_bus estado_bus;

    private Cooperativa cooperativa;

    public Bus() {

    }

    public Bus(Integer id_bus, Integer numero_bus, String placa, String marca, String modelo,
            Integer capacidad_pasajeros, Integer Velocidad, Estado_bus estado_bus, Cooperativa cooperativa) {
        this.id_bus = id_bus;
        this.numero_bus = numero_bus;
        this.placa = placa;
        this.marca = marca;
        this.modelo = modelo;
        this.capacidad_pasajeros = capacidad_pasajeros;
        this.Velocidad = Velocidad;
        this.estado_bus = estado_bus;
        this.cooperativa = cooperativa;
    }

    public Integer getId_bus() {
        return id_bus;
    }

    public void setId_bus(Integer id_bus) {
        this.id_bus = id_bus;
    }

    public Integer getNumero_bus() {
        return numero_bus;
    }

    public void setNumero_bus(Integer numero_bus) {
        this.numero_bus = numero_bus;
    }

    public String getPlaca() {
        return placa;
    }

    public void setPlaca(String placa) {
        this.placa = placa;
    }

    public String getMarca() {
        return marca;
    }

    public void setMarca(String marca) {
        this.marca = marca;
    }

    public String getModelo() {
        return modelo;
    }

    public void setModelo(String modelo) {
        this.modelo = modelo;
    }

    public Integer getCapacidad_pasajeros() {
        return capacidad_pasajeros;
    }

    public void setCapacidad_pasajeros(Integer capacidad_pasajeros) {
        this.capacidad_pasajeros = capacidad_pasajeros;
    }

    public Integer getVelocidad() {
        return Velocidad;
    }

    public void setVelocidad(Integer Velocidad) {
        this.Velocidad = Velocidad;
    }

    public Estado_bus getEstado_bus() {
        return estado_bus;
    }

    public void setEstado_bus(Estado_bus estado_bus) {
        this.estado_bus = estado_bus;
    }

    public Cooperativa getCooperativa() {
        return cooperativa;
    }

    public void setCooperativa(Cooperativa cooperativa) {
        this.cooperativa = cooperativa;
    }

    @Override
    public String toString() {
        return "id_bus=" + id_bus + ", numero_bus=" + numero_bus + ", placa=" + placa + ", marca=" + marca
                + ", modelo=" + modelo + ", capacidad_pasajeros=" + capacidad_pasajeros + ", Velocidad="
                + Velocidad + ", estado_bus=" + estado_bus + ", cooperativa=" + cooperativa;
    }

}
