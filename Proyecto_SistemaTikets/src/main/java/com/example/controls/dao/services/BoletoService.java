package com.example.controls.dao.services;


import com.example.controls.dao.BoletoDao;
import com.example.models.Boleto;
import com.example.controls.tda.list.LinkedList;

public class BoletoService {
    private BoletoDao boletoDao;

    public BoletoService() {
        this.boletoDao = new BoletoDao();
    }

    public Boleto getBoletoById(Integer idBoleto) {
        LinkedList<Boleto> boletos = boletoDao.getListAll();
        if (boletos == null || boletos.getSize() == 0) {
            return null; 
        }
        try {
            for (int i = 0; i < boletos.getSize(); i++) {
                Boleto boleto = boletos.get(i);
                if (boleto.getId().equals(idBoleto)) {
                    return boleto;
                }
            }
        } catch (Exception e) {
            System.out.println("Error al acceder a la lista de boletos: " + e.getMessage());
        }
        return null; 
    }
    

    public LinkedList<Boleto> getAllBoletos() {
        return boletoDao.getListAll();
    }

    public boolean createBoleto(Boleto boleto) throws Exception {
        boletoDao.setBoleto(boleto);
        return boletoDao.save();
    }


}