package controlador.tda.cola;

public class Queque<E> {
    private QuequeOperation<E> quequeOperation;

    public Queque(Integer cant) {
        this.quequeOperation = new QuequeOperation<>(cant);
    }

    public void queque(E dato) throws Exception {
        quequeOperation.queque(dato);
    }

    public Integer getSize() {
        return this.quequeOperation.getSize();
    }

    public void clear() {
        this.quequeOperation.reset();
    }

    public Integer getTop() {
        return this.quequeOperation.getTop();
    }

    public void print() {
        System.out.println("Cola");
        System.out.println(quequeOperation.toString());
        System.out.println("*****");
    }

    public E dequeque() throws Exception {
        return quequeOperation.dequeque();
    }
}
