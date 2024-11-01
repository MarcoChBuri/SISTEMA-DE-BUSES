package com.example.adapters;

import com.example.models.Bus;

public class BusAdapter {

    // Convierte un objeto Bus a BusDTO
    public static BusDTO toDTO(Bus bus) {
        if (bus == null) {
            return null; // Manejo de error por si el objeto es nulo
        }
        BusDTO dto = new BusDTO(bus.getId(), bus.getNumeroBus(), bus.getPlaca(), bus.getCantidadAsiento());
        return dto;
    }

    // Convierte un objeto BusDTO a Bus
    public static Bus fromDTO(BusDTO dto) {
        if (dto == null) {
            return null; // Manejo de error por si el objeto es nulo
        }
        Bus bus = new Bus();
        bus.setId(dto.getId());
        bus.setNumeroBus(dto.getNumeroBus());
        bus.setPlaca(dto.getPlaca());
        bus.setCantidadAsiento(dto.getCantidadAsiento());
        return bus;
    }
}
