package controlador.dao;

import controlador.tda.lista.LinkedList;

interface InterfazDao<T> {

    public void persist(T object) throws Exception;

    public void merge(T object, Integer index) throws Exception;

    public LinkedList<T> listAll();

    public T get(Integer id) throws Exception;
}