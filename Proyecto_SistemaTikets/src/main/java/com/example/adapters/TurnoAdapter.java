package com.example.adapters;

import com.example.models.Turno;

public class TurnoAdapter {

    // Convierte un objeto Turno a TurnoDTO
    public static TurnoDTO toDTO(Turno turno) {
        if (turno == null) {
            return null; // Manejo de error por si el objeto es nulo
        }
        TurnoDTO dto = new TurnoDTO(turno.getId(), turno.getNumeroTurno(), turno.getFecha(), turno.getHorario(), turno.getIdFrecuencia());
        return dto;
    }

    // Convierte un objeto TurnoDTO a Turno
    public static Turno fromDTO(TurnoDTO dto) {
        if (dto == null) {
            return null; // Manejo de error por si el objeto es nulo
        }
        Turno turno = new Turno();
        turno.setId(dto.getId());
        turno.setNumeroTurno(dto.getNumeroTurno());
        turno.setFecha(dto.getFecha());
        turno.setHorario(dto.getHorario());
        turno.setIdFrecuencia(dto.getIdFrecuencia());
        return turno;
    }
}
