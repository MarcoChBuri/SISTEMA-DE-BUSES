package modelo;

import modelo.enums.Estado_turno;

public class Turno {
    private Integer id_turno;
    private String fecha_salida;
    private Integer numero_turno;
    private Estado_turno estado_turno;

    private Horario horario;

    public Turno() {

    }

    public Turno(Integer id_turno, String fecha_salida, Integer numero_turno, Estado_turno estado_turno,
            Horario horario) {
        this.id_turno = id_turno;
        this.fecha_salida = fecha_salida;
        this.numero_turno = numero_turno;
        this.estado_turno = estado_turno;
        this.horario = horario;
    }

    public Integer getId_turno() {
        return id_turno;
    }

    public void setId_turno(Integer id_turno) {
        this.id_turno = id_turno;
    }

    public String getFecha_salida() {
        return fecha_salida;
    }

    public void setFecha_salida(String fecha_salida) {
        this.fecha_salida = fecha_salida;
    }

    public Integer getNumero_turno() {
        return numero_turno;
    }

    public void setNumero_turno(Integer numero_turno) {
        this.numero_turno = numero_turno;
    }

    public Estado_turno getEstado_turno() {
        return estado_turno;
    }

    public void setEstado_turno(Estado_turno estado_turno) {
        this.estado_turno = estado_turno;
    }

    public Horario getHorario() {
        return horario;
    }

    public void setHorario(Horario horario) {
        this.horario = horario;
    }

    @Override
    public String toString() {
        return "id_turno=" + id_turno + ", fecha_salida=" + fecha_salida + ", numero_turno=" + numero_turno
                + ", estado_turno=" + estado_turno + ", horario=" + horario;
    }

}
