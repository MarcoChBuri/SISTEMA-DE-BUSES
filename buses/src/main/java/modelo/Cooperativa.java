package modelo;

public class Cooperativa {
    private Integer id_cooperativa;
    private String nombre_cooperativa;
    private String ruc;
    private String direccion;
    private String telefono;
    private String correo_empresarial;

    // private Cuenta cuenta_administrador;

    public Cooperativa() {

    }

    public Cooperativa(Integer id_cooperativa, String nombre_cooperativa, String ruc, String direccion,
            String telefono, String correo_empresarial) {
        this.id_cooperativa = id_cooperativa;
        this.nombre_cooperativa = nombre_cooperativa;
        this.ruc = ruc;
        this.direccion = direccion;
        this.telefono = telefono;
        this.correo_empresarial = correo_empresarial;
    }

    public Integer getId_cooperativa() {
        return id_cooperativa;
    }

    public void setId_cooperativa(Integer id_cooperativa) {
        this.id_cooperativa = id_cooperativa;
    }

    public String getNombre_cooperativa() {
        return nombre_cooperativa;
    }

    public void setNombre_cooperativa(String nombre_cooperativa) {
        this.nombre_cooperativa = nombre_cooperativa;
    }

    public String getRuc() {
        return ruc;
    }

    public void setRuc(String ruc) {
        this.ruc = ruc;
    }

    public String getDireccion() {
        return direccion;
    }

    public void setDireccion(String direccion) {
        this.direccion = direccion;
    }

    public String getTelefono() {
        return telefono;
    }

    public void setTelefono(String telefono) {
        this.telefono = telefono;
    }

    public String getCorreo_empresarial() {
        return correo_empresarial;
    }

    public void setCorreo_empresarial(String correo_empresarial) {
        this.correo_empresarial = correo_empresarial;
    }

    @Override
    public String toString() {
        return "id_cooperativa=" + id_cooperativa + ", nombre_cooperativa=" + nombre_cooperativa + ", ruc="
                + ruc + ", direccion=" + direccion + ", telefono=" + telefono + ", correo_empresarial="
                + correo_empresarial;
    }

}
