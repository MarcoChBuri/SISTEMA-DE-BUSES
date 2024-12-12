package modelo;

public class Frecuencia {
    private Integer id_frecuencia;
    private Integer numero_repeticiones;
    private String periodo;
    private float precio_recorrido;

    private Horario horario;

    public Frecuencia() {

    }

    public Frecuencia(Integer id_frecuencia, Integer numero_repeticiones, String periodo,
            float precio_recorrido, Horario horario) {
        this.id_frecuencia = id_frecuencia;
        this.numero_repeticiones = numero_repeticiones;
        this.periodo = periodo;
        this.precio_recorrido = precio_recorrido;
        this.horario = horario;
    }

    public Integer getId_frecuencia() {
        return id_frecuencia;
    }

    public void setId_frecuencia(Integer id_frecuencia) {
        this.id_frecuencia = id_frecuencia;
    }

    public Integer getNumero_repeticiones() {
        return numero_repeticiones;
    }

    public void setNumero_repeticiones(Integer numero_repeticiones) {
        this.numero_repeticiones = numero_repeticiones;
    }

    public String getPeriodo() {
        return periodo;
    }

    public void setPeriodo(String periodo) {
        this.periodo = periodo;
    }

    public float getPrecio_recorrido() {
        return precio_recorrido;
    }

    public void setPrecio_recorrido(float precio_recorrido) {
        this.precio_recorrido = precio_recorrido;
    }

    public Horario getHorario() {
        return horario;
    }

    public void setHorario(Horario horario) {
        this.horario = horario;
    }

    @Override
    public String toString() {
        return "id_frecuencia=" + id_frecuencia + ", numero_repeticiones=" + numero_repeticiones
                + ", periodo=" + periodo + ", precio_recorrido=" + precio_recorrido + ", horario=" + horario;
    }

}
