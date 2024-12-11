package controlador.dao;

import controlador.tda.lista.LinkedList;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import com.google.gson.Gson;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.Scanner;
import java.io.File;

public class AdapterDao<T> implements InterfazDao<T> {
    private Class<T> clazz;
    private Gson g;

    public static String filePath = "data/";

    public AdapterDao(Class<T> clazz) {
        this.clazz = clazz;
        this.g = new Gson();
    }

    public T get(Integer id) throws Exception {
        LinkedList<T> list = listAll();
        if (!list.isEmpty()) {
            T[] matriz = list.toArray();
            return matriz[id - 1];
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    public LinkedList<T> listAll() {
        LinkedList<T> list = new LinkedList<>();
        try {
            String data = readFile();
            if (data != null && !data.trim().isEmpty() && !data.equals("[]")) {
                T[] matrix = (T[]) g.fromJson(data, java.lang.reflect.Array.newInstance(clazz, 0).getClass());
                if (matrix != null) {
                    list.toList(matrix);
                }
            }
        }
        catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }

    public void merge(T object, Integer index) throws Exception {
        LinkedList<T> list = listAll();
        if (index < 0 || index >= list.getSize()) {
            throw new Exception("Índice fuera de rango");
        }
        list.update(object, index);
        String info = g.toJson(list.toArray());
        saveFile(info);
    }

    public void persist(T object) throws Exception {
        LinkedList<T> list = listAll();
        if (list == null) {
            list = new LinkedList<>();
        }
        list.add(object);
        String info = g.toJson(list.toArray());
        saveFile(info);
    }

    private String readFile() throws Exception {
        File file = new File(filePath + clazz.getSimpleName() + ".json");
        if (!file.exists()) {
            System.out.println("El archivo no existe, creando uno nuevo: " + file.getAbsolutePath());
            saveFile("[]");
        }
        StringBuilder sb = new StringBuilder();
        try (Scanner in = new Scanner(new FileReader(file))) {
            while (in.hasNextLine()) {
                sb.append(in.nextLine()).append("\n");
            }
        }
        return sb.toString().trim();
    }

    public void saveFile(String data) throws Exception {
        File file = new File(filePath + clazz.getSimpleName() + ".json");
        file.getParentFile().mkdirs();
        Gson gson = new GsonBuilder().setPrettyPrinting().create();
        try {
            JsonElement jsonElement = JsonParser.parseString(data);
            String formattedJson = gson.toJson(jsonElement);
            try (FileWriter f = new FileWriter(file)) {
                f.write(formattedJson);
                f.flush();
            }
        }
        catch (Exception e) {
            System.out.println("Error al escribir en el archivo: " + e.getMessage());
            throw e;
        }
    }
}
