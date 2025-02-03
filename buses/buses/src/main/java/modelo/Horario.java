package modelo;

import modelo.enums.Estado_horario;

public class Horario {
    private Integer id_horario;
    private String hora_salida;
    private String hora_llegada;
    private Estado_horario estado_horario;

    private Ruta ruta;

    public Horario() {

    }

    public Horario(Integer id_horario, String hora_salida, String hora_llegada, Estado_horario estado_horario,
            Ruta ruta) {
        this.id_horario = id_horario;
        this.hora_salida = hora_salida;
        this.hora_llegada = hora_llegada;
        this.estado_horario = estado_horario;
        this.ruta = ruta;
    }

    public Integer getId_horario() {
        return id_horario;
    }

    public void setId_horario(Integer id_horario) {
        this.id_horario = id_horario;
    }

    public String getHora_salida() {
        return hora_salida;
    }

    public void setHora_salida(String hora_salida) {
        this.hora_salida = hora_salida;
    }

    public String getHora_llegada() {
        return hora_llegada;
    }

    public void setHora_llegada(String hora_llegada) {
        this.hora_llegada = hora_llegada;
    }

    public Estado_horario getEstado_horario() {
        return estado_horario;
    }

    public void setEstado_horario(Estado_horario estado_horario) {
        this.estado_horario = estado_horario;
    }

    public Ruta getRuta() {
        return ruta;
    }

    public void setRuta(Ruta ruta) {
        this.ruta = ruta;
    }

    @Override
    public String toString() {
        return "id_horario=" + id_horario + ", hora_salida=" + hora_salida + ", hora_llegada=" + hora_llegada
                + ", estado_horario=" + estado_horario + ", ruta=" + ruta;
    }

}
