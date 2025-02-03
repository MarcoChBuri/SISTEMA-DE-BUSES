from flask import Blueprint, jsonify, render_template, flash, redirect, request, session, url_for
from datetime import datetime, timedelta
from flask import make_response
from dotenv import load_dotenv
from functools import wraps
from os import getenv
import requests
import jwt

router_bus = Blueprint("router_bus", __name__)


load_dotenv()
SECRET_KEY = getenv("JWT_SECRET_KEY", "tu_contrasenia_secreta")
ALGORITHM = "HS256"


def generar_token(user_data):
    payload = {
        "user_id": user_data.get("id"),
        "tipo_cuenta": user_data.get("tipo_cuenta"),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def validar_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def requiere_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get("token")
        if not token:
            return redirect(url_for("router_bus.iniciar_sesion"))
        payload = validar_token(token)
        if not payload:
            session.clear()
            return redirect(url_for("router_bus.iniciar_sesion"))
        return f(*args, **kwargs)

    return decorated_function


def no_cache(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        response = make_response(view_function(*args, **kwargs))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    return decorated_function


def requiere_iniciar(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            flash("Por favor inicie sesión para continuar", "warning")
            return redirect(url_for("router_bus.iniciar_sesion"))
        return f(*args, **kwargs)

    return decorated_function


def requiere_administrador(f):
    @wraps(f)
    @no_cache
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            flash("Por favor inicie sesión para continuar", "warning")
            return redirect(url_for("router_bus.iniciar_sesion"))
        if session.get("user", {}).get("tipo_cuenta") != "Administrador":
            flash("Acceso no autorizado", "danger")
            return redirect(url_for("router_bus.cliente"))
        return f(*args, **kwargs)

    return decorated_function


def requiere_cliente(f):
    @wraps(f)
    @no_cache
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            flash("Por favor inicie sesión para continuar", "warning")
            return redirect(url_for("router_bus.iniciar_sesion"))
        if session.get("user", {}).get("tipo_cuenta") != "Cliente":
            flash("Acceso no autorizado", "danger")
            return redirect(url_for("router_bus.administrador"))
        return f(*args, **kwargs)

    return decorated_function


def obtener_info_usuario():
    try:
        usuario_id = session.get("user", {}).get("id")
        r_usuario = requests.get(f"http://localhost:8099/api/persona/lista/{usuario_id}")
        datos_usuario = r_usuario.json().get("persona", {}) if r_usuario.status_code == 200 else {}
        return {
            "nombre": datos_usuario.get("nombre", "Usuario"),
            "apellido": datos_usuario.get("apellido", ""),
        }
    except:
        return {"nombre": "Usuario", "apellido": ""}


@router_bus.route("/api/rutas/opciones")
def turnos_disponibles():
    try:
        r = requests.get("http://localhost:8099/api/turno/lista")
        if r.status_code == 200:
            turnos = r.json().get("turnos", [])
            turnos_activos = [t for t in turnos if t.get("estado_turno") == "Disponible"]
            origenes = list(
                {
                    t.get("horario", {}).get("ruta", {}).get("origen")
                    for t in turnos_activos
                    if t.get("horario", {}).get("ruta", {}).get("origen")
                }
            )
            return jsonify({"turnos": turnos, "origenes": sorted(origenes)})
        return jsonify({"error": "Error al obtener datos"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@router_bus.route("/buscar_cooperativas")
def buscar_cooperativas():
    try:
        origen = request.args.get("origen")
        destino = request.args.get("destino")
        fecha = request.args.get("fecha")
        if not all([origen, destino, fecha]):
            flash("Por favor complete todos los campos", "error")
            return redirect(url_for("router_bus.index"))
        r = requests.get("http://localhost:8099/api/turno/lista")
        if r.status_code == 200:
            turnos = r.json()
            cooperativas_set = set()
            cooperativas_lista = []
            for turno in turnos["turnos"]:
                ruta = turno["horario"]["ruta"]
                if (
                    ruta["origen"] == origen
                    and ruta["destino"] == destino
                    and turno["fecha_salida"] == fecha
                ):
                    cooperativa = ruta["bus"]["cooperativa"]
                    if cooperativa["id_cooperativa"] not in cooperativas_set:
                        cooperativas_set.add(cooperativa["id_cooperativa"])
                        cooperativas_lista.append(cooperativa)
            return render_template(
                "seleccion_boleto/cooperativa_disponible.html",
                cooperativas=cooperativas_lista,
                origen=origen,
                destino=destino,
                fecha=fecha,
            )
        flash("Error al obtener datos del servidor", "error")
        return redirect(url_for("router_bus.index"))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for("router_bus.index"))


@router_bus.route("/api/buses/disponibles")
def buses_disponibles():
    try:
        cooperativa_id = request.args.get("cooperativa")
        origen = request.args.get("origen")
        destino = request.args.get("destino")
        fecha = request.args.get("fecha")
        r = requests.get("http://localhost:8099/api/turno/lista")
        if r.status_code == 200:
            turnos = r.json().get("turnos", [])
            buses_disponibles = []
            for turno in turnos:
                ruta = turno["horario"]["ruta"]
                bus = ruta["bus"]
                if (
                    ruta["origen"] == origen
                    and ruta["destino"] == destino
                    and turno["fecha_salida"] == fecha
                    and bus["cooperativa"]["id_cooperativa"] == int(cooperativa_id)
                ):
                    buses_disponibles.append(
                        {
                            "id_bus": bus["id_bus"],
                            "numero_bus": bus["numero_bus"],
                            "velocidad": bus["velocidad"],
                            "modelo": bus["modelo"],
                            "placa": bus["placa"],
                            "capacidad_pasajeros": bus["capacidad_pasajeros"],
                            "horario": f"{turno['horario']['hora_salida']} - {turno['horario']['hora_llegada']}",
                        }
                    )
            return jsonify({"buses": buses_disponibles})
        return jsonify({"error": "Error al obtener datos"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@router_bus.route("/seleccion_boleto/asientos/<int:bus_id>")
def mostrar_asientos(bus_id):
    try:
        origen = request.args.get("origen")
        destino = request.args.get("destino")
        fecha = request.args.get("fecha")
        if "user" not in session:
            session["redirect_after_login"] = (
                f"/seleccion_boleto/asientos/{bus_id}?origen={origen}&destino={destino}&fecha={fecha}"
            )
            flash("Por favor inicie sesión para continuar", "warning")
            return redirect(url_for("router.iniciar_sesion"))
        r_bus = requests.get(f"http://localhost:8099/api/bus/lista/{bus_id}")
        r_turnos = requests.get("http://localhost:8099/api/turno/lista")
        r_boletos = requests.get(f"http://localhost:8099/api/boleto/lista")
        if r_bus.status_code == 200:
            bus = r_bus.json().get("bus")
            turnos = r_turnos.json().get("turnos", []) if r_turnos.status_code == 200 else []
            turno = next(
                (
                    t
                    for t in turnos
                    if t["horario"]["ruta"]["bus"]["id_bus"] == bus_id
                    and t["horario"]["ruta"]["origen"] == origen
                    and t["horario"]["ruta"]["destino"] == destino
                    and t["fecha_salida"] == fecha
                ),
                None,
            )
            if not turno:
                flash("No se encontró el turno especificado", "error")
                return redirect(url_for("router_bus.index"))
            ruta = turno["horario"]["ruta"]
            hora_salida = turno["horario"]["hora_salida"]
            precio_unitario = ruta["precio_unitario"]
            boletos = r_boletos.json().get("boletos", []) if r_boletos.status_code == 200 else []
            estados_asientos = ["disponible"] * bus["capacidad_pasajeros"]
            for boleto in boletos:
                if boleto["turno"]["id_turno"] == turno["id_turno"] and boleto["estado_boleto"] in [
                    "Vendido",
                    "Reservado",
                ]:
                    estados_asientos[boleto["numero_asiento"] - 1] = boleto["estado_boleto"].lower()
            return render_template(
                "seleccion_boleto/asientos_disponibles.html",
                bus=bus,
                ruta=ruta,
                turno=turno,
                estados_asientos=estados_asientos,
                origen=origen,
                destino=destino,
                fecha_salida=fecha,
                hora_salida=hora_salida,
                precio_unitario=precio_unitario,
            )
        return jsonify({"error": "Bus no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
