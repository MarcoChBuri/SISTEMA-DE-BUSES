package modelo;

public class Escala {
    private Integer id_escala;
    private String lugar_escala;
    private String tiempo;

    public Escala() {

    }

    public Escala(Integer id_escala, String lugar_escala, String tiempo) {
        this.id_escala = id_escala;
        this.lugar_escala = lugar_escala;
        this.tiempo = tiempo;
    }

    public Integer getId_escala() {
        return id_escala;
    }

    public void setId_escala(Integer id_escala) {
        this.id_escala = id_escala;
    }

    public String getLugar_escala() {
        return lugar_escala;
    }

    public void setLugar_escala(String lugar_escala) {
        this.lugar_escala = lugar_escala;
    }

    public String getTiempo() {
        return tiempo;
    }

    public void setTiempo(String tiempo) {
        this.tiempo = tiempo;
    }

    @Override
    public String toString() {
        return "id_escala=" + id_escala + ", lugar_escala=" + lugar_escala + ", tiempo=" + tiempo;
    }

}
