package controlador.tda.cola;

import controlador.tda.lista.excepcion.ListEmptyException;
import controlador.tda.lista.excepcion.OverFlowException;
import controlador.tda.lista.LinkedList;

public class QuequeOperation<E> extends LinkedList<E> {
    private Integer top;

    public QuequeOperation(Integer top) {
        this.top = top;
    }

    public Boolean verify() {
        return getSize().intValue() <= top.intValue();
    }

    public void queque(E dato) throws Exception {
        if (verify()) {
            add(dato, getSize());
        }
        else {
            throw new OverFlowException("Error, desbordamiento");
        }
    }

    public E dequeque() throws ListEmptyException {
        if (isEmpty()) {
            throw new ListEmptyException("Error, lista vacia");
        }
        else {
            return deleteFirst();
        }
    }

    public Integer getTop() {
        return top;
    }

    public void setTop(Integer top) {
        this.top = top;
    }
}
