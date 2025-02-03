package controlador.dao.modelo_dao;

import controlador.tda.lista.LinkedList;
import controlador.dao.AdapterDao;
import modelo.enums.Estado_turno;
import com.google.gson.Gson;
import modelo.Turno;

public class Turno_dao extends AdapterDao<Turno> {
    private LinkedList<Turno> lista_turnos;
    private Turno turno;

    public Turno_dao() {
        super(Turno.class);
    }

    public LinkedList<Turno> getLista_turnos() {
        if (lista_turnos == null) {
            this.lista_turnos = listAll();
        }
        return lista_turnos;
    }

    public Turno getTurno() {
        if (turno == null) {
            turno = new Turno();
        }
        return this.turno;
    }

    public void setTurno(Turno turno) {
        this.turno = turno;
    }

    public Boolean save() throws Exception {
        turno.setId_turno(obtenerSiguienteId());
        persist(turno);
        this.lista_turnos = listAll();
        return true;
    }

    public Boolean update() throws Exception {
        for (int i = 0; i < getLista_turnos().getSize(); i++) {
            Turno t = getLista_turnos().get(i);
            if (t.getId_turno().equals(getTurno().getId_turno())) {
                merge(getTurno(), i);
                this.lista_turnos = listAll();
                return true;
            }
        }
        throw new Exception("No se encontró el turno con el id: " + turno.getId_turno());
    }

    public Boolean delete(Integer id) throws Exception {
        try {
            LinkedList<Turno> turnos = getLista_turnos();
            if (turnos == null) {
                turnos = new LinkedList<>();
            }
            boolean deleted = false;
            for (int i = 0; i < turnos.getSize(); i++) {
                Turno t = turnos.get(i);
                if (t.getId_turno().equals(id)) {
                    turnos.delete(i);
                    deleted = true;
                    break;
                }
            }
            if (deleted) {
                String info = new Gson().toJson(turnos.toArray());
                saveFile(info);
                this.lista_turnos = listAll();
                return true;
            }
            throw new Exception("No se encontró el turno con el id: " + id);
        }
        catch (Exception e) {
            throw new Exception("Error al eliminar el turno: " + e.getMessage());
        }
    }

    public void verificarYActualizarEstadoTurno(Integer idTurno) throws Exception {
        Boleto_dao boletoDao = new Boleto_dao();
        Turno turno = get(idTurno);
        if (turno != null) {
            Integer capacidadBus = turno.getHorario().getRuta().getBus().getCapacidad_pasajeros();
            Integer boletosVendidos = boletoDao.contarBoletosVendidosPorTurno(idTurno);
            if (boletosVendidos >= capacidadBus && turno.getEstado_turno() != Estado_turno.Agotado) {
                turno.setEstado_turno(Estado_turno.Agotado);
                setTurno(turno);
                update();
            }
        }
    }
}
