package modelo;

import modelo.enums.Opcion_pago;

public class Pago {
    private Integer id_pago;
    private Float saldo;
    private String numero_tarjeta;
    private String titular;
    private String fecha_vencimiento;
    private String codigo_seguridad;

    private Opcion_pago opcion_pago;

    public Pago() {

    }

    public Pago(Integer id_pago, Float saldo, String numero_tarjeta, String titular, String fecha_vencimiento,
            String codigo_seguridad, Opcion_pago opcion_pago) {
        this.id_pago = id_pago;
        this.saldo = saldo;
        this.numero_tarjeta = numero_tarjeta;
        this.titular = titular;
        this.fecha_vencimiento = fecha_vencimiento;
        this.codigo_seguridad = codigo_seguridad;
        this.opcion_pago = opcion_pago;
    }

    public Integer getId_pago() {
        return id_pago;
    }

    public void setId_pago(Integer id_pago) {
        this.id_pago = id_pago;
    }

    public Float getSaldo() {
        return saldo;
    }

    public void setSaldo(Float saldo) {
        this.saldo = saldo;
    }

    public String getNumero_tarjeta() {
        return numero_tarjeta;
    }

    public void setNumero_tarjeta(String numero_tarjeta) {
        this.numero_tarjeta = numero_tarjeta;
    }

    public String getTitular() {
        return titular;
    }

    public void setTitular(String titular) {
        this.titular = titular;
    }

    public String getFecha_vencimiento() {
        return fecha_vencimiento;
    }

    public void setFecha_vencimiento(String fecha_vencimiento) {
        this.fecha_vencimiento = fecha_vencimiento;
    }

    public String getCodigo_seguridad() {
        return codigo_seguridad;
    }

    public void setCodigo_seguridad(String codigo_seguridad) {
        this.codigo_seguridad = codigo_seguridad;
    }

    public Opcion_pago getOpcion_pago() {
        return opcion_pago;
    }

    public void setOpcion_pago(Opcion_pago opcion_pago) {
        this.opcion_pago = opcion_pago;
    }

    @Override
    public String toString() {
        return "id_pago=" + id_pago + ", saldo=" + saldo + ", numero_tarjeta=" + numero_tarjeta + ", titular="
                + titular + ", fecha_vencimiento=" + fecha_vencimiento + ", codigo_seguridad="
                + codigo_seguridad + ", opcion_pago=" + opcion_pago;
    }

}
