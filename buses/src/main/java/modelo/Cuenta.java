package modelo;

import modelo.enums.Estado_cuenta;
import modelo.enums.Tipo_cuenta;

public class Cuenta {
    private Integer id_cuenta;
    private String correo;
    private String contrasenia;
    private Estado_cuenta estado_cuenta;
    private Tipo_cuenta tipo_cuenta;

    public Cuenta() {

    }

    public Cuenta(Integer id_cuenta, String correo, String contrasenia, Estado_cuenta estado_cuenta,
            Tipo_cuenta tipo_cuenta) {
        this.id_cuenta = id_cuenta;
        this.correo = correo;
        this.contrasenia = contrasenia;
        this.estado_cuenta = estado_cuenta;
        this.tipo_cuenta = tipo_cuenta;
    }

    public Integer getId_cuenta() {
        return id_cuenta;
    }

    public void setId_cuenta(Integer id_cuenta) {
        this.id_cuenta = id_cuenta;
    }

    public String getCorreo() {
        return correo;
    }

    public void setCorreo(String correo) {
        this.correo = correo;
    }

    public String getContrasenia() {
        return contrasenia;
    }

    public void setContrasenia(String contrasenia) {
        this.contrasenia = contrasenia;
    }

    public Estado_cuenta getEstado_cuenta() {
        return estado_cuenta;
    }

    public void setEstado_cuenta(Estado_cuenta estado_cuenta) {
        this.estado_cuenta = estado_cuenta;
    }

    public Tipo_cuenta getTipo_cuenta() {
        return tipo_cuenta;
    }

    public void setTipo_cuenta(Tipo_cuenta tipo_cuenta) {
        this.tipo_cuenta = tipo_cuenta;
    }

    @Override
    public String toString() {
        return "id_cuenta=" + id_cuenta + ", correo=" + correo + ", contrasenia=" + contrasenia
                + ", estado_cuenta=" + estado_cuenta + ", tipo_cuenta=" + tipo_cuenta;
    }

}
