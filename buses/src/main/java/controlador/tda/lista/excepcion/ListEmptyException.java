package controlador.tda.lista.excepcion;

public class ListEmptyException extends Exception {
    public ListEmptyException() {

    }

    public ListEmptyException(String msg) {
        super(msg);
    }
}
