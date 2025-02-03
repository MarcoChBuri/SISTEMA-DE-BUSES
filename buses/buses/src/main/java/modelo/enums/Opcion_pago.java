package modelo.enums;

public enum Opcion_pago {
    Tarjeta_credito("Tarjeta de crédito"), Tarjeta_debito("Tarjeta de débito");

    private final String displayName;

    Opcion_pago(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }
}