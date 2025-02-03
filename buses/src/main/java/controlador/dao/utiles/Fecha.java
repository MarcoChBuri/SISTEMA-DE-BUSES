package controlador.dao.utiles;

import java.text.SimpleDateFormat;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class Fecha {
    private static final String FORMATO_DESEADO = "dd/MM/yyyy";
    private static final List<SimpleDateFormat> formatosReconocidos = new ArrayList<>();

    static {
        formatosReconocidos.add(new SimpleDateFormat("dd/MM/yyyy"));
        formatosReconocidos.add(new SimpleDateFormat("yyyy-MM-dd"));
        formatosReconocidos.add(new SimpleDateFormat("MM/dd/yyyy"));
        formatosReconocidos.add(new SimpleDateFormat("dd-MM-yyyy"));
        formatosReconocidos.add(new SimpleDateFormat("yyyy/MM/dd"));
        for (SimpleDateFormat sdf : formatosReconocidos) {
            sdf.setLenient(false);
        }
    }

    public static String normalizarFecha(String fecha) throws Exception {
        if (fecha == null || fecha.trim().isEmpty()) {
            throw new Exception("Fecha nula o vacía");
        }
        Date fechaParseada = null;
        for (SimpleDateFormat formato : formatosReconocidos) {
            try {
                fechaParseada = formato.parse(fecha);
                break;
            }
            catch (ParseException e) {
                continue;
            }
        }
        if (fechaParseada == null) {
            throw new Exception("Formato de fecha no reconocido");
        }
        SimpleDateFormat formatoSalida = new SimpleDateFormat(FORMATO_DESEADO);
        return formatoSalida.format(fechaParseada);
    }
}
