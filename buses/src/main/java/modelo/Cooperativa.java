package modelo;

public class Cooperativa {
    private Integer id_cooperativa;
    private String nombre;
    private String ruc;
    private String direccion;
    private String telefono;
    private String correo_empresarial;

    public Cooperativa() {

    }

    public Cooperativa(Integer id_cooperativa, String nombre, String ruc, String direccion, String telefono,
            String correo_empresarial) {
        this.id_cooperativa = id_cooperativa;
        this.nombre = nombre;
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

    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
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
        return "id_cooperativa=" + id_cooperativa + ", nombre=" + nombre + ", ruc=" + ruc + ", direccion="
                + direccion + ", telefono=" + telefono + ", correo_empresarial=" + correo_empresarial;
    }

}
