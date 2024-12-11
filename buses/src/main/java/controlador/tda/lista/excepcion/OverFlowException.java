package controlador.tda.lista.excepcion;

public class OverFlowException extends Exception {
    public OverFlowException() {
    }

    public OverFlowException(String msg) {
        super(msg);
    }
}
