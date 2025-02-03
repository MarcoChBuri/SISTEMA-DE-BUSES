package controlador.dao.modelo_dao;

import controlador.tda.lista.LinkedList;
import modelo.enums.Estado_descuento;
import modelo.enums.Tipo_descuento;
import controlador.dao.AdapterDao;
import com.google.gson.Gson;
import modelo.Descuento;
import java.io.File;

public class Descuento_dao extends AdapterDao<Descuento> {
    private LinkedList<Descuento> lista_descuentos;
    private Descuento descuento;

    public Descuento_dao() {
        super(Descuento.class);
        try {
            LinkedList<Descuento> descuentos = listAll();
            if (descuentos.isEmpty()) {
                inicializarDescuentosPorDefecto();
            }
        }
        catch (Exception e) {
            e.printStackTrace();
        }
    }

    public LinkedList<Descuento> getLista_descuentos() {
        if (lista_descuentos == null) {
            this.lista_descuentos = listAll();
        }
        return lista_descuentos;
    }

    public Descuento getDescuento() {
        if (descuento == null) {
            descuento = new Descuento();
        }
        return this.descuento;
    }

    public void setDescuento(Descuento descuento) {
        this.descuento = descuento;
    }

    public Boolean save() throws Exception {
        descuento.setId_descuento(obtenerSiguienteId());
        persist(descuento);
        this.lista_descuentos = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        for (int i = 0; i < getLista_descuentos().getSize(); i++) {
            Descuento d = getLista_descuentos().get(i);
            if (d.getId_descuento().equals(getDescuento().getId_descuento())) {
                merge(getDescuento(), i);
                this.lista_descuentos = listAll();
                return true;
            }
        }
        throw new Exception("No se encontró el descuento con el id: " + descuento.getId_descuento());
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Descuento> descuentos = getLista_descuentos();
            if (descuentos == null) {
                descuentos = new LinkedList<>();
            }
            boolean deleted = false;
            for (int i = 0; i < descuentos.getSize(); i++) {
                Descuento d = descuentos.get(i);
                if (d.getId_descuento().equals(id)) {
                    descuentos.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (deleted) {
                String info = new Gson().toJson(descuentos.toArray());
                saveFile(info);
                this.lista_descuentos = listAll();
                return true;
            }
            throw new Exception("No se encontró el descuento con el id: " + id);
        }
        catch (Exception e) {
            throw new Exception("Error al eliminar el descuento: " + e.getMessage());
        }
    }

    public void inicializarSiVacio() throws Exception {
        File archivo = new File("data/Descuento.json");
        if (!archivo.exists() || archivo.length() == 0) {
            inicializarDescuentosPorDefecto();
        }
    }

    private void inicializarDescuentosPorDefecto() throws Exception {
        crearDescuentoPorDefecto("General", "Descuento base aplicado a todos los usuarios", 0,
                Tipo_descuento.General);
        crearDescuentoPorDefecto("Estudiante", "Descuento aplicado automáticamente para estudiantes", 30,
                Tipo_descuento.Estudiante);
        crearDescuentoPorDefecto("Menor Edad", "Descuento aplicado automáticamente para menores de edad", 50,
                Tipo_descuento.Menor_edad);
        crearDescuentoPorDefecto("Tercera Edad", "Descuento aplicado automáticamente para adultos mayores",
                50, Tipo_descuento.Tercera_edad);
        crearDescuentoPorDefecto("Discapacidad",
                "Descuento aplicado automáticamente para personas con discapacidad", 50,
                Tipo_descuento.Discapacitado);
    }

    private void crearDescuentoPorDefecto(String nombre, String descripcion, Integer porcentaje,
            Tipo_descuento tipo) throws Exception {
        Descuento descuento = new Descuento();
        descuento.setId_descuento(obtenerSiguienteId());
        descuento.setTipo_descuento(tipo);
        descuento.setNombre_descuento(nombre);
        descuento.setDescripcion(descripcion);
        descuento.setPorcentaje(porcentaje);
        descuento.setEstado_descuento(Estado_descuento.Activo);
        persist(descuento);
    }
}
