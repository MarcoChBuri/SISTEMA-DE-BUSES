from flask import Blueprint, jsonify, render_template, flash, redirect, request, session, url_for
from datetime import datetime, timedelta
from flask import make_response
from dotenv import load_dotenv
from functools import wraps
from os import getenv
import requests
import json
import jwt

router_admin = Blueprint("router_admin", __name__)


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
            return redirect(url_for("router.iniciar_sesion"))
        payload = validar_token(token)
        if not payload:
            session.clear()
            return redirect(url_for("router.iniciar_sesion"))
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


# Inicio de sesión


def requiere_iniciar(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            flash("Por favor inicie sesión para continuar", "warning")
            return redirect(url_for("router.iniciar_sesion"))
        return f(*args, **kwargs)

    return decorated_function


def requiere_administrador(f):
    @wraps(f)
    @no_cache
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            flash("Por favor inicie sesión para continuar", "warning")
            return redirect(url_for("router.iniciar_sesion"))
        if session.get("user", {}).get("tipo_cuenta") != "Administrador":
            flash("Acceso no autorizado", "danger")
            return redirect(url_for("router.cliente"))
        return f(*args, **kwargs)

    return decorated_function


def requiere_cliente(f):
    @wraps(f)
    @no_cache
    def decorated_function(*args, **kwargs):
        if not session.get("user"):
            flash("Por favor inicie sesión para continuar", "warning")
            return redirect(url_for("router.iniciar_sesion"))
        if session.get("user", {}).get("tipo_cuenta") != "Cliente":
            flash("Acceso no autorizado", "danger")
            return redirect(url_for("router.administrador"))
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


@router_admin.route("/cooperativa/lista")
@requiere_administrador
def lista_cooperativa():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/cooperativa/lista")
        if r.status_code == 200:
            try:
                data = r.json()
                return render_template(
                    "crud/cooperativa/cooperativa.html",
                    lista=data.get("cooperativas", []),
                    usuario=usuario,
                )
            except json.JSONDecodeError as je:
                flash("Error al decodificar la respuesta del servidor", "error")
                return render_template(
                    "crud/cooperativa/cooperativa.html", lista=[], usuario=usuario
                )
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/cooperativa.html", lista=[], usuario=usuario)
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/cooperativa/cooperativa.html", lista=[], usuario=usuario)


@router_admin.route("/cooperativa/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_cooperativa():
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            nombre = request.form.get("nombre_cooperativa")
            ruc = request.form.get("ruc")
            telefono = request.form.get("telefono")
            correo = request.form.get("correo_empresarial")
            r_cooperativas = requests.get("http://localhost:8099/api/cooperativa/lista")
            cooperativas = r_cooperativas.json().get("cooperativas", [])
            for coop in cooperativas:
                if coop["nombre_cooperativa"].lower() == nombre.lower():
                    return render_template(
                        "crud/cooperativa/cooperativa_crear.html",
                        usuario=usuario,
                        error="El nombre de la cooperativa ya existe",
                    )
                if coop["ruc"] == ruc:
                    return render_template(
                        "crud/cooperativa/cooperativa_crear.html",
                        usuario=usuario,
                        error="El RUC ya está registrado",
                    )
                if coop["telefono"].replace(" ", "").replace("(", "").replace(")", "").replace(
                    "-", ""
                ) == telefono.replace(" ", "").replace("(", "").replace(")", "").replace("-", ""):
                    return render_template(
                        "crud/cooperativa/cooperativa_crear.html",
                        usuario=usuario,
                        error="El teléfono ya está registrado",
                    )
                if coop["correo_empresarial"].lower() == correo.lower():
                    return render_template(
                        "crud/cooperativa/cooperativa_crear.html",
                        usuario=usuario,
                        error="El correo ya está registrado",
                    )
            datos = {
                "nombre_cooperativa": nombre,
                "ruc": ruc,
                "direccion": request.form.get("direccion"),
                "telefono": telefono,
                "correo_empresarial": correo,
            }
            response = requests.post("http://localhost:8099/api/cooperativa/guardar", json=datos)
            if response.status_code == 200:
                flash("Cooperativa creada exitosamente", "success")
                return redirect(url_for("router_admin.lista_cooperativa"))
            else:
                flash("Error al crear la cooperativa", "error")
                return redirect(url_for("router_admin.lista_cooperativa"))
        except requests.exceptions.ConnectionError:
            flash("Error de conexión con el servidor", "error")
            return redirect(url_for("router_admin.lista_cooperativa"))
        except requests.exceptions.RequestException as e:
            flash(f"Error en la solicitud: {str(e)}", "error")
            return redirect(url_for("router_admin.lista_cooperativa"))
    return render_template("crud/cooperativa/cooperativa_crear.html", usuario=usuario)


@router_admin.route("/cooperativa/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_cooperativa(id):
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            nombre = request.form.get("nombre_cooperativa")
            ruc = request.form.get("ruc")
            telefono = request.form.get("telefono")
            correo = request.form.get("correo_empresarial")
            r_cooperativas = requests.get("http://localhost:8099/api/cooperativa/lista")
            cooperativas = r_cooperativas.json().get("cooperativas", [])
            for coop in cooperativas:
                if coop["id_cooperativa"] != id:
                    if coop["nombre_cooperativa"].lower() == nombre.lower():
                        return render_template(
                            "crud/cooperativa/cooperativa_editar.html",
                            usuario=usuario,
                            error="El nombre de la cooperativa ya existe",
                            cooperativa={
                                "id_cooperativa": id,
                                "nombre_cooperativa": nombre,
                                "ruc": ruc,
                                "direccion": request.form.get("direccion"),
                                "telefono": telefono,
                                "correo_empresarial": correo,
                            },
                        )
                    if coop["ruc"] == ruc:
                        return render_template(
                            "crud/cooperativa/cooperativa_editar.html",
                            usuario=usuario,
                            error="El RUC ya está registrado",
                            cooperativa={
                                "id_cooperativa": id,
                                "nombre_cooperativa": nombre,
                                "ruc": ruc,
                                "direccion": request.form.get("direccion"),
                                "telefono": telefono,
                                "correo_empresarial": correo,
                            },
                        )
                    if coop["telefono"].replace(" ", "").replace("(", "").replace(")", "").replace(
                        "-", ""
                    ) == telefono.replace(" ", "").replace("(", "").replace(")", "").replace(
                        "-", ""
                    ):
                        return render_template(
                            "crud/cooperativa/cooperativa_editar.html",
                            usuario=usuario,
                            error="El teléfono ya está registrado",
                            cooperativa={
                                "id_cooperativa": id,
                                "nombre_cooperativa": nombre,
                                "ruc": ruc,
                                "direccion": request.form.get("direccion"),
                                "telefono": telefono,
                                "correo_empresarial": correo,
                            },
                        )
                    if coop["correo_empresarial"].lower() == correo.lower():
                        return render_template(
                            "crud/cooperativa/cooperativa_editar.html",
                            usuario=usuario,
                            error="El correo ya está registrado",
                            cooperativa={
                                "id_cooperativa": id,
                                "nombre_cooperativa": nombre,
                                "ruc": ruc,
                                "direccion": request.form.get("direccion"),
                                "telefono": telefono,
                                "correo_empresarial": correo,
                            },
                        )
            datos = {
                "id": id,
                "nombre_cooperativa": nombre,
                "ruc": ruc,
                "direccion": request.form.get("direccion"),
                "telefono": telefono,
                "correo_empresarial": correo,
            }
            response = requests.put("http://localhost:8099/api/cooperativa/actualizar", json=datos)
            if response.status_code == 200:
                flash("Cooperativa actualizada exitosamente", "success")
                return redirect(url_for("router_admin.lista_cooperativa"))
            else:
                flash("Error al actualizar la cooperativa", "error")
                return redirect(url_for("router_admin.lista_cooperativa"))
        except requests.exceptions.RequestException as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for("router_admin.lista_cooperativa"))
    try:
        r = requests.get(f"http://localhost:8099/api/cooperativa/lista/{id}")
        if r.status_code == 200:
            cooperativa = r.json().get("cooperativa")
            return render_template(
                "crud/cooperativa/cooperativa_editar.html", cooperativa=cooperativa, usuario=usuario
            )
        else:
            flash("Cooperativa no encontrada", "error")
            return redirect(url_for("router_admin.lista_cooperativa"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router_admin.lista_cooperativa"))


@router_admin.route("/cooperativa/eliminar/<int:id>", methods=["POST"])
def eliminar_cooperativa(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/cooperativa/eliminar/{id}")
        if r.status_code == 200:
            flash("Cooperativa eliminada correctamente", "success")
        else:
            error_msg = f"Error del servidor: {r.status_code} - {r.text}"
            flash(error_msg, "error")
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión: {str(e)}"
        flash(error_msg, "error")
    return redirect(url_for("router_admin.lista_cooperativa"))


@router_admin.route("/cooperativa/ordenar/<atributo>/<orden>")
def ordenar_cooperativa(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/cooperativa/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_msg = response.json().get("mensaje", "Error desconocido al ordenar")
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Error al ordenar boletos: {str(e)}"}), 500


@router_admin.route("/cooperativa/buscar/<atributo>/<criterio>")
def buscar_cooperativa(atributo, criterio):
    try:
        response = requests.get(
            f"http://localhost:8099/api/cooperativa/buscar/{atributo}/{criterio}"
        )
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500


# CRUD de Buses


@router_admin.route("/bus/lista")
@requiere_administrador
def lista_bus():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/bus/lista")
        if r.status_code == 200:
            try:
                data = r.json()
                return render_template(
                    "crud/bus/bus.html", lista=data.get("buses", []), usuario=usuario
                )
            except json.JSONDecodeError as je:
                flash("Error al decodificar la respuesta del servidor", "error")
                return render_template("crud/bus/bus.html", lista=[], usuario=usuario)
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/bus/bus.html", lista=[], usuario=usuario)
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/bus/bus.html", lista=[], usuario=usuario)


@router_admin.route("/bus/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_bus():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/cooperativa/lista")
        cooperativas = r.json().get("cooperativas", []) if r.status_code == 200 else []
        r_buses = requests.get("http://localhost:8099/api/bus/lista")
        buses = r_buses.json().get("buses", []) if r_buses.status_code == 200 else []
        ultimo_numero = max([bus.get("numero_bus", 0) for bus in buses], default=0)
        siguiente_numero = ultimo_numero + 1
    except:
        cooperativas = []
        flash("Error al cargar las cooperativas", "error")
    if request.method == "POST":
        try:
            r_buses = requests.get("http://localhost:8099/api/bus/lista")
            buses = r_buses.json().get("buses", [])
            numero = request.form.get("numero_bus")
            placa = request.form.get("placa")
            for bus in buses:
                if bus["numero_bus"] == int(numero):
                    return render_template(
                        "crud/bus/bus_crear.html",
                        usuario=usuario,
                        error="El número de bus ya existe",
                        cooperativas=cooperativas,
                        siguiente_numero=siguiente_numero,
                        valores=request.form,
                    )
                if bus["placa"].upper() == placa.upper():
                    return render_template(
                        "crud/bus/bus_crear.html",
                        usuario=usuario,
                        error="La placa ya está registrada",
                        cooperativas=cooperativas,
                        siguiente_numero=siguiente_numero,
                        valores=request.form,
                    )
            headers = {"Content-Type": "application/json"}
            data = {
                "numero_bus": siguiente_numero,
                "placa": request.form["placa"],
                "marca": request.form["marca"],
                "modelo": request.form["modelo"],
                "capacidad_pasajeros": request.form["capacidad_pasajeros"],
                "velocidad": request.form["velocidad"],
                "estado_bus": request.form["estado_bus"],
                "cooperativa_id": request.form["cooperativa_id"],
            }
            r = requests.post(
                "http://localhost:8099/api/bus/guardar", headers=headers, json=data, timeout=5
            )
            if r.status_code == 200:
                flash("Bus creado correctamente", "success")
                return redirect(url_for("router_admin.lista_bus"))
            else:
                error_msg = f"Error {r.status_code}: {r.text}"
                flash(error_msg, "error")
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar al servidor"
            flash(error_msg, "error")
        except requests.exceptions.RequestException as e:
            error_msg = f"Error en la petición: {str(e)}"
            flash(error_msg, "error")
    return render_template(
        "crud/bus/bus_crear.html",
        cooperativas=cooperativas,
        usuario=usuario,
        siguiente_numero=siguiente_numero,
        valores={},
    )


@router_admin.route("/bus/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_bus(id):
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            r_buses = requests.get("http://localhost:8099/api/bus/lista")
            buses = r_buses.json().get("buses", [])
            numero_bus = request.form["numero_bus"]
            placa = request.form["placa"].upper()
            for bus in buses:
                if bus["id_bus"] != id:
                    if str(bus["numero_bus"]) == numero_bus:
                        r = requests.get(f"http://localhost:8099/api/bus/lista/{id}")
                        bus_actual = r.json().get("bus")
                        r_coop = requests.get("http://localhost:8099/api/cooperativa/lista")
                        cooperativas = r_coop.json().get("cooperativas", [])
                        return render_template(
                            "crud/bus/bus_editar.html",
                            bus=bus_actual,
                            cooperativas=cooperativas,
                            usuario=usuario,
                            error="El número de bus ya existe",
                        )
                    if bus["placa"].upper() == placa:
                        r = requests.get(f"http://localhost:8099/api/bus/lista/{id}")
                        bus_actual = r.json().get("bus")
                        r_coop = requests.get("http://localhost:8099/api/cooperativa/lista")
                        cooperativas = r_coop.json().get("cooperativas", [])
                        return render_template(
                            "crud/bus/bus_editar.html",
                            bus=bus_actual,
                            cooperativas=cooperativas,
                            usuario=usuario,
                            error="La placa ya está registrada",
                        )
            headers = {"Content-Type": "application/json"}
            data = {
                "id": id,
                "numero_bus": request.form["numero_bus"],
                "placa": request.form["placa"],
                "marca": request.form["marca"],
                "modelo": request.form["modelo"],
                "capacidad_pasajeros": request.form["capacidad_pasajeros"],
                "velocidad": request.form["velocidad"],
                "estado_bus": request.form["estado_bus"],
                "cooperativa_id": request.form["cooperativa_id"],
            }
            r = requests.put("http://localhost:8099/api/bus/actualizar", headers=headers, json=data)
            if r.status_code == 200:
                flash("Bus actualizado correctamente", "success")
                return redirect(url_for("router_admin.lista_bus"))
            else:
                error_msg = f"Error {r.status_code}: {r.text}"
                flash(error_msg, "error")
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión: {str(e)}"
            flash(error_msg, "error")
    try:
        r = requests.get(f"http://localhost:8099/api/bus/lista/{id}")
        bus = r.json().get("bus") if r.status_code == 200 else None
        r_coop = requests.get("http://localhost:8099/api/cooperativa/lista")
        cooperativas = r_coop.json().get("cooperativas", []) if r_coop.status_code == 200 else []
        if bus:
            return render_template(
                "crud/bus/bus_editar.html", bus=bus, cooperativas=cooperativas, usuario=usuario
            )
        else:
            flash("No se encontró el bus", "error")
            return redirect(url_for("router_admin.lista_bus"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router_admin.lista_bus"))


@router_admin.route("/bus/eliminar/<int:id>", methods=["POST"])
def eliminar_bus(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/bus/eliminar/{id}")
        if r.status_code == 200:
            flash("Bus eliminado correctamente", "success")
        else:
            error_msg = f"Error del servidor: {r.status_code} - {r.text}"
            flash(error_msg, "error")
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión: {str(e)}"
        flash(error_msg, "error")
    return redirect(url_for("router_admin.lista_bus"))


@router_admin.route("/bus/ordenar/<atributo>/<orden>")
def ordenar_bus(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/bus/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_msg = response.json().get("mensaje", "Error desconocido al ordenar")
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Error al ordenar boletos: {str(e)}"}), 500


@router_admin.route("/bus/buscar/<atributo>/<criterio>")
def buscar_bus(atributo, criterio):
    try:
        response = requests.get(f"http://localhost:8099/api/bus/buscar/{atributo}/{criterio}")
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500


# CRUD de Rutas


@router_admin.route("/ruta/lista")
@requiere_administrador
def lista_ruta():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/ruta/lista")
        if r.status_code == 200:
            try:
                data = r.json()
                for ruta in data.get("rutas", []):
                    escalas = ruta.get("escalas", {})
                    escalas_formateadas = []
                    if isinstance(escalas, dict) and "header" in escalas:
                        current = escalas.get("header", {})
                        while current:
                            info = current.get("info", {})
                            if info:
                                lugar = info.get("lugar_escala")
                                tiempo = info.get("tiempo")
                                if lugar and tiempo:
                                    escalas_formateadas.append(f"{lugar} ({tiempo})")
                            current = current.get("next", {})
                    ruta["escala"] = (
                        ", ".join(escalas_formateadas) if escalas_formateadas else "Sin escalas"
                    )
                return render_template(
                    "crud/ruta/ruta.html", lista=data.get("rutas", []), usuario=usuario
                )
            except Exception as e:
                flash(f"Error al procesar datos: {str(e)}", "error")
                return render_template("crud/ruta/ruta.html", lista=[], usuario=usuario)
        else:
            flash("Error al obtener datos del servidor", "error")
            return render_template("crud/ruta/ruta.html", lista=[], usuario=usuario)
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/ruta/ruta.html", lista=[], usuario=usuario)


@router_admin.route("/ruta/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_ruta():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/bus/lista")
        buses = r.json().get("buses", []) if r.status_code == 200 else []
    except:
        buses = []
        flash("Error al cargar los buses", "error")
    if request.method == "POST":
        try:
            r_rutas = requests.get("http://localhost:8099/api/ruta/lista")
            rutas = r_rutas.json().get("rutas", [])
            origen = request.form["origen"]
            destino = request.form["destino"]
            bus_id = request.form.get("bus_id")
            for ruta in rutas:
                if (
                    ruta["origen"].lower() == origen.lower()
                    and ruta["destino"].lower() == destino.lower()
                ):
                    if (
                        str(ruta["bus"]["id_bus"]) == str(bus_id)
                        and ruta["estado_ruta"] == "Disponible"
                    ):
                        return render_template(
                            "crud/ruta/ruta_crear.html",
                            buses=buses,
                            usuario=usuario,
                            error="Este bus ya tiene asignada una ruta con el mismo origen y destino",
                        )
            headers = {"Content-Type": "application/json"}
            data = {
                "origen": request.form["origen"],
                "destino": request.form["destino"],
                "precio_unitario": request.form.get("precio_unitario"),
                "distancia": int(request.form["distancia"]),
                "tiempo_estimado": request.form["tiempo_estimado"],
                "estado_ruta": request.form["estado_ruta"],
                "bus": {
                    "id_bus": int(request.form["bus_id"]),
                },
                "escalas": [],
            }
            i = 0
            while f"lugar_escala_{i}" in request.form:
                if request.form[f"lugar_escala_{i}"].strip():
                    escala = {
                        "lugar_escala": request.form[f"lugar_escala_{i}"],
                        "tiempo": request.form[f"tiempo_escala_{i}"],
                    }
                    data["escalas"].append(escala)
                i += 1
            r = requests.post("http://localhost:8099/api/ruta/guardar", headers=headers, json=data)
            if r.status_code == 200:
                flash("Ruta creada correctamente", "success")
                return redirect(url_for("router_admin.lista_ruta"))
            else:
                flash(f"Error al crear la ruta: {r.text}", "error")
        except requests.exceptions.ConnectionError:
            flash("Error de conexión con el servidor", "error")
        except Exception as e:
            flash(f"Error al crear la ruta: {str(e)}", "error")
    return render_template("crud/ruta/ruta_crear.html", buses=buses, usuario=usuario)


@router_admin.route("/ruta/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_ruta(id):
    usuario = obtener_info_usuario()
    if request.method == "GET":
        try:
            r = requests.get(f"http://localhost:8099/api/ruta/lista/{id}")
            ruta = r.json().get("ruta") if r.status_code == 200 else None
            r_bus = requests.get("http://localhost:8099/api/bus/lista")
            buses = r_bus.json().get("buses", []) if r_bus.status_code == 200 else []
            if ruta:
                escalas = ruta.get("escalas", [])
                if isinstance(escalas, dict) and "header" in escalas:
                    escalas_formateadas = []
                    current = escalas["header"]
                    while current:
                        if "info" in current:
                            escalas_formateadas.append(current["info"])
                        current = current.get("next")
                    ruta["escalas"] = escalas_formateadas
                return render_template(
                    "crud/ruta/ruta_editar.html", ruta=ruta, buses=buses, usuario=usuario
                )
            flash("Ruta no encontrada", "error")
            return redirect(url_for("router_admin.lista_ruta"))
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
            return redirect(url_for("router_admin.lista_ruta"))
    elif request.method == "POST":
        try:
            r = requests.get(f"http://localhost:8099/api/ruta/lista/{id}")
            ruta_actual = r.json().get("ruta") if r.status_code == 200 else None
            r_bus = requests.get("http://localhost:8099/api/bus/lista")
            buses = r_bus.json().get("buses", []) if r_bus.status_code == 200 else []

            if request.method == "POST":
                r_rutas = requests.get("http://localhost:8099/api/ruta/lista")
                rutas = r_rutas.json().get("rutas", [])
                origen = request.form.get("origen", "").strip()
                destino = request.form.get("destino", "").strip()
                bus_id = request.form.get("bus_id")
                for ruta in rutas:
                    if ruta["id_ruta"] != id:
                        if (
                            ruta["origen"].lower() == origen.lower()
                            and ruta["destino"].lower() == destino.lower()
                        ):
                            if (
                                str(ruta["bus"]["id_bus"]) == str(bus_id)
                                and ruta["estado_ruta"] == "Disponible"
                            ):
                                return render_template(
                                    "crud/ruta/ruta_editar.html",
                                    ruta=ruta_actual,
                                    buses=buses,
                                    usuario=usuario,
                                    error="Este bus ya tiene asignada una ruta con el mismo origen y destino",
                                )
            datos_ruta = {
                "id_ruta": id,
                "origen": origen,
                "destino": destino,
                "precio_unitario": float(request.form["precio_unitario"]),
                "distancia": int(request.form["distancia"]),
                "tiempo_estimado": request.form["tiempo_estimado"],
                "estado_ruta": request.form["estado_ruta"],
                "bus": {"id_bus": int(request.form["bus_id"])},
            }
            lugares_escala = request.form.getlist("lugar_escala[]")
            tiempos_escala = request.form.getlist("tiempo_escala[]")
            ids_escala = request.form.getlist("id_escala[]")
            escalas = []
            if lugares_escala and tiempos_escala:
                for i in range(len(lugares_escala)):
                    if lugares_escala[i].strip() and tiempos_escala[i].strip():
                        escala = {
                            "lugar_escala": lugares_escala[i].strip(),
                            "tiempo": tiempos_escala[i].strip(),
                        }
                        if i < len(ids_escala) and ids_escala[i]:
                            escala["id_escala"] = int(ids_escala[i])
                        escalas.append(escala)
            if escalas:
                datos_ruta["escalas"] = escalas
            r = requests.put(
                "http://localhost:8099/api/ruta/actualizar",
                headers={"Content-Type": "application/json"},
                json=datos_ruta,
            )
            if r.status_code == 200:
                flash("Ruta actualizada correctamente", "success")
                return redirect(url_for("router_admin.lista_ruta"))
            else:
                flash(
                    f"Error al actualizar la ruta: {r.json().get('msg', 'Error desconocido')}",
                    "error",
                )
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
        return redirect(url_for("router_admin.editar_ruta", id=id))


@router_admin.route("/ruta/eliminar/<int:id>", methods=["POST"])
def eliminar_ruta(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/ruta/eliminar/{id}")
        if r.status_code == 200:
            flash("Ruta eliminada correctamente", "success")
        else:
            error_msg = f"Error del servidor: {r.status_code}"
            flash(error_msg, "error")
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión: {str(e)}"
        flash(error_msg, "error")
    return redirect(url_for("router_admin.lista_ruta"))


@router_admin.route("/ruta/ordenar/<atributo>/<orden>")
def ordenar_ruta(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/ruta/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            rutas = response.json().get("rutas", [])
            for ruta in rutas:
                if isinstance(ruta.get("escalas"), dict):
                    escalas_lista = []
                    current = ruta["escalas"].get("header")
                    while current:
                        if "info" in current:
                            escalas_lista.append(
                                {
                                    "lugar_escala": current["info"]["lugar_escala"],
                                    "tiempo_escala": current["info"]["tiempo"],
                                }
                            )
                        current = current.get("next")
                    ruta["escalas"] = escalas_lista
            return jsonify({"rutas": rutas})
        else:
            return jsonify({"error": "Error al ordenar las rutas"})
    except Exception as e:
        return jsonify({"error": str(e)})


@router_admin.route("/ruta/buscar/<atributo>/<criterio>")
def buscar_ruta(atributo, criterio):
    try:
        response = requests.get(f"http://localhost:8099/api/ruta/buscar/{atributo}/{criterio}")
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500


# CRUD de Escalas


@router_admin.route("/escala/lista")
@requiere_administrador
def lista_escala():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/escala/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template(
                "crud/escala/escala.html", lista=data.get("escalas", []), usuario=usuario
            )
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/escala/escala.html", lista=[], usuario=usuario)
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/escala/escala.html", lista=[], usuario=usuario)


@router_admin.route("/escala/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_escala():
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                "lugar_escala": request.form["lugar_escala"],
                "tiempo": request.form["tiempo"],
            }
            r = requests.post(
                "http://localhost:8099/api/escala/guardar", headers=headers, json=data, timeout=5
            )
            if r.status_code == 200:
                flash("Escala creada correctamente", "success")
                return redirect(url_for("router_admin.lista_escala"))
            else:
                error_msg = f"Error al crear la escala: {r.text}"
                flash(error_msg, "error")
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar al servidor"
            flash(error_msg, "error")
        except requests.exceptions.RequestException as e:
            error_msg = f"Error en la petición: {str(e)}"
            flash(error_msg, "error")
    try:
        r = requests.get("http://localhost:8099/api/ruta/lista")
        rutas = r.json().get("rutas", []) if r.status_code == 200 else []
    except:
        rutas = []
        flash("Error al cargar las rutas", "error")
    return render_template("crud/escala/escala_crear.html", rutas=rutas, usuario=usuario)


@router_admin.route("/escala/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_escala(id):
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            data = {
                "id_escala": id,
                "lugar_escala": request.form["lugar_escala"],
                "tiempo": request.form["tiempo"],
            }
            r = requests.put(
                "http://localhost:8099/api/escala/actualizar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Escala actualizada correctamente", "success")
                return redirect(url_for("router_admin.lista_escala"))
            else:
                flash(f"Error al actualizar: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    try:
        r = requests.get(f"http://localhost:8099/api/escala/lista/{id}")
        escala = r.json().get("escala") if r.status_code == 200 else None
        if escala:
            return render_template("crud/escala/escala_editar.html", escala=escala, usuario=usuario)
        else:
            flash("No se encontró la escala", "error")
            return redirect(url_for("router_admin.lista_escala"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router_admin.lista_escala"))


@router_admin.route("/escala/eliminar/<int:id>", methods=["POST"])
def eliminar_escala(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/escala/eliminar/{id}")
        if r.status_code == 200:
            flash("Escala eliminada correctamente", "success")
            return redirect(url_for("router_admin.lista_escala"))
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router_admin.lista_escala"))


@router_admin.route("/escala/ordenar/<atributo>/<orden>")
def ordenar_escala(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/escala/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_msg = response.json().get("mensaje", "Error desconocido al ordenar")
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Error al ordenar boletos: {str(e)}"}), 500


@router_admin.route("/escala/buscar/<atributo>/<criterio>")
def buscar_escala(atributo, criterio):
    try:
        response = requests.get(f"http://localhost:8099/api/escala/buscar/{atributo}/{criterio}")
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500


# CRUD de Horarios


@router_admin.route("/horario/lista")
@requiere_administrador
def lista_horario():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/horario/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template(
                "crud/horario/horario.html", lista=data.get("horarios", []), usuario=usuario
            )
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/horario/horario.html", lista=[], usuario=usuario)
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/horario/horario.html", lista=[], usuario=usuario)


@router_admin.route("/horario/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_horario():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/ruta/lista")
        rutas = r.json().get("rutas", []) if r.status_code == 200 else []
    except:
        rutas = []
        flash("Error al cargar las rutas", "error")
    if request.method == "POST":
        try:
            hora_salida = request.form["hora_salida"]
            hora_llegada = request.form["hora_llegada"]
            ruta_id = int(request.form["ruta_id"])
            r_horarios = requests.get("http://localhost:8099/api/horario/lista")
            horarios = r_horarios.json().get("horarios", [])
            hora_salida_nueva = sum(x * int(t) for x, t in zip([60, 1], hora_salida.split(":")))
            hora_llegada_nueva = sum(x * int(t) for x, t in zip([60, 1], hora_llegada.split(":")))
            for horario in horarios:
                ruta_horario = horario.get("ruta", {})
                if ruta_horario.get("id_ruta") == ruta_id:
                    hora_salida_existente = sum(
                        x * int(t) for x, t in zip([60, 1], horario["hora_salida"].split(":"))
                    )
                    hora_llegada_existente = sum(
                        x * int(t) for x, t in zip([60, 1], horario["hora_llegada"].split(":"))
                    )
                    if not (
                        hora_llegada_nueva <= hora_salida_existente
                        or hora_salida_nueva >= hora_llegada_existente
                    ):
                        return render_template(
                            "crud/horario/horario_crear.html",
                            rutas=rutas,
                            usuario=usuario,
                            error="Ya existe un horario para esta ruta en ese rango de tiempo",
                            valores={
                                "hora_salida": hora_salida,
                                "hora_llegada": hora_llegada,
                                "ruta_id": ruta_id,
                            },
                        )
            data = {
                "hora_salida": hora_salida,
                "hora_llegada": hora_llegada,
                "estado_horario": request.form["estado_horario"],
                "ruta": {"id_ruta": ruta_id},
            }
            response = requests.post("http://localhost:8099/api/horario/guardar", json=data)
            if response.status_code == 200:
                flash("Horario creado correctamente", "success")
                return redirect(url_for("router_admin.lista_horario"))
            else:
                flash(f"Error al crear el horario: {response.text}", "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    return render_template("crud/horario/horario_crear.html", rutas=rutas, usuario=usuario)


@router_admin.route("/horario/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_horario(id):
    usuario = obtener_info_usuario()
    try:
        r = requests.get(f"http://localhost:8099/api/horario/lista/{id}")
        horario = r.json().get("horario") if r.status_code == 200 else None
        r_rutas = requests.get("http://localhost:8099/api/ruta/lista")
        rutas = r_rutas.json().get("rutas", []) if r_rutas.status_code == 200 else []
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    if horario:
        if request.method == "POST":
            try:
                hora_salida = request.form["hora_salida"]
                hora_llegada = request.form["hora_llegada"]
                ruta_id = int(request.form["ruta_id"])
                r_horarios = requests.get("http://localhost:8099/api/horario/lista")
                horarios = r_horarios.json().get("horarios", [])
                hora_salida_nueva = sum(x * int(t) for x, t in zip([60, 1], hora_salida.split(":")))
                hora_llegada_nueva = sum(
                    x * int(t) for x, t in zip([60, 1], hora_llegada.split(":"))
                )
                for horario_existente in horarios:
                    if horario_existente.get("id_horario") != id:
                        ruta_horario = horario_existente.get("ruta", {})
                        if ruta_horario.get("id_ruta") == ruta_id:
                            hora_salida_existente = sum(
                                x * int(t)
                                for x, t in zip(
                                    [60, 1], horario_existente["hora_salida"].split(":")
                                )
                            )
                            hora_llegada_existente = sum(
                                x * int(t)
                                for x, t in zip(
                                    [60, 1], horario_existente["hora_llegada"].split(":")
                                )
                            )
                            if not (
                                hora_llegada_nueva <= hora_salida_existente
                                or hora_salida_nueva >= hora_llegada_existente
                            ):
                                return render_template(
                                    "crud/horario/horario_editar.html",
                                    horario=horario,
                                    rutas=rutas,
                                    usuario=usuario,
                                    error="Ya existe un horario para esta ruta en ese rango de tiempo",
                                )
                    data = {
                        "id_horario": id,
                        "hora_salida": hora_salida,
                        "hora_llegada": hora_llegada,
                        "estado_horario": request.form["estado_horario"],
                        "ruta": {"id_ruta": ruta_id},
                    }
                    r = requests.put(
                        "http://localhost:8099/api/horario/actualizar",
                        headers={"Content-Type": "application/json"},
                        json=data,
                    )
                    if r.status_code == 200:
                        flash("Horario actualizado correctamente", "success")
                        return redirect(url_for("router_admin.lista_horario"))
                    else:
                        flash(f"Error al actualizar el horario: {r.text}", "error")
                else:
                    flash("Ruta no encontrada", "error")
            except Exception as e:
                flash(f"Error al procesar la solicitud: {str(e)}", "error")
        return render_template(
            "crud/horario/horario_editar.html", horario=horario, rutas=rutas, usuario=usuario
        )
    else:
        flash("Horario no encontrado", "error")
    return render_template("crud/horario/horario_editar.html", rutas=rutas, usuario=usuario)


@router_admin.route("/horario/eliminar/<int:id>", methods=["POST"])
def eliminar_horario(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/horario/eliminar/{id}")
        if r.status_code == 200:
            flash("Horario eliminado correctamente", "success")
        else:
            flash("Error al eliminar el horario", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router_admin.lista_horario"))


@router_admin.route("/horario/ordenar/<atributo>/<orden>")
def ordenar_horario(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/horario/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_msg = response.json().get("mensaje", "Error desconocido al ordenar")
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Error al ordenar boletos: {str(e)}"}), 500


@router_admin.route("/horario/buscar/<atributo>/<criterio>")
def buscar_horario(atributo, criterio):
    try:
        response = requests.get(f"http://localhost:8099/api/horario/buscar/{atributo}/{criterio}")
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500


# CRUD de Turnos


@router_admin.route("/turno/lista")
@requiere_administrador
def lista_turno():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/turno/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template(
                "crud/turno/turno.html", lista=data.get("turnos", []), usuario=usuario
            )
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/turno/turno.html", lista=[], usuario=usuario)
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/turno/turno.html", lista=[], usuario=usuario)


@router_admin.route("/turno/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_turno():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/horario/lista")
        horarios = r.json().get("horarios", []) if r.status_code == 200 else []
        r_turno = requests.get("http://localhost:8099/api/turno/lista")
        turnos = r_turno.json().get("turnos", []) if r_turno.status_code == 200 else []
        ultimo_numero = 0
        for turno in turnos:
            num_turno = turno.get("numero_turno", "")
            try:
                if isinstance(num_turno, int):
                    ultimo_numero = max(ultimo_numero, num_turno)
                elif isinstance(num_turno, str) and num_turno:
                    num = int(num_turno[1])
                    ultimo_numero = max(ultimo_numero, num)
            except (ValueError, IndexError):
                continue
        siguiente_numero = ultimo_numero + 1
        if request.method == "POST":
            fecha_salida = request.form.get("fecha_salida")
            horario_id = int(request.form.get("horario_id"))
            try:
                fecha_obj = datetime.strptime(fecha_salida, "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                for turno in turnos:
                    fecha_turno = turno.get("fecha_salida")
                    horario_turno = turno.get("horario", {}).get("id_horario")
                    if fecha_formateada == fecha_turno and horario_id == horario_turno:
                        return render_template(
                            "crud/turno/turno_crear.html",
                            horarios=horarios,
                            usuario=usuario,
                            siguiente_numero=siguiente_numero,
                            error="Ya existe un turno para esta fecha y horario",
                        )
                data = {
                    "numero_turno": siguiente_numero,
                    "fecha_salida": fecha_formateada,
                    "estado_turno": request.form.get("estado_turno", "Disponible"),
                    "horario": {"id_horario": horario_id},
                }
                print("data", data)
                r = requests.post(
                    "http://localhost:8099/api/turno/guardar",
                    headers={"Content-Type": "application/json"},
                    json=data,
                )
                if r.status_code == 200:
                    flash("Turno creado correctamente", "success")
                    return redirect(url_for("router_admin.lista_turno"))
                else:
                    flash(f"Error al crear el turno: {r.text}", "error")
            except ValueError:
                flash("Error en los datos ingresados", "error")
        return render_template(
            "crud/turno/turno_crear.html",
            horarios=horarios,
            usuario=usuario,
            siguiente_numero=siguiente_numero,
        )
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for("router_admin.lista_turno"))


@router_admin.route("/turno/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_turno(id):
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            r_turnos = requests.get("http://localhost:8099/api/turno/lista")
            turnos = r_turnos.json().get("turnos", [])
            numero_turno = int(request.form["numero_turno"])
            fecha_salida = request.form.get("fecha_salida")
            horario_id = int(request.form.get("horario_id"))
            for turno in turnos:
                if turno.get("numero_turno") == numero_turno and turno.get("id_turno") != id:
                    estados_turno = ["Disponible", "Cancelado", "Agotado"]
                    r = requests.get(f"http://localhost:8099/api/turno/lista/{id}")
                    turno = r.json().get("turno") if r.status_code == 200 else None
                    r_horarios = requests.get("http://localhost:8099/api/horario/lista")
                    horarios = (
                        r_horarios.json().get("horarios", [])
                        if r_horarios.status_code == 200
                        else []
                    )
                    return render_template(
                        "crud/turno/turno_editar.html",
                        turno=turno,
                        horarios=horarios,
                        usuario=usuario,
                        estados_turno=estados_turno,
                        error="Ya existe un turno con ese número",
                    )
            try:
                fecha_obj = datetime.strptime(fecha_salida, "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
                for turno in turnos:
                    if (
                        turno.get("id_turno") != id
                        and turno.get("fecha_salida") == fecha_formateada
                        and turno.get("horario", {}).get("id_horario") == horario_id
                    ):
                        estados_turno = ["Disponible", "Cancelado", "Agotado"]
                        r = requests.get(f"http://localhost:8099/api/turno/lista/{id}")
                        turno = r.json().get("turno") if r.status_code == 200 else None
                        r_horarios = requests.get("http://localhost:8099/api/horario/lista")
                        horarios = (
                            r_horarios.json().get("horarios", [])
                            if r_horarios.status_code == 200
                            else []
                        )
                        return render_template(
                            "crud/turno/turno_editar.html",
                            turno=turno,
                            horarios=horarios,
                            usuario=usuario,
                            estados_turno=estados_turno,
                            error="Ya existe un turno para esta fecha y horario",
                        )
            except ValueError:
                flash("Formato de fecha inválido", "error")
                return redirect(url_for("router_admin.editar_turno", id=id))
            data = {
                "id_turno": id,
                "numero_turno": numero_turno,
                "fecha_salida": fecha_formateada,
                "estado_turno": request.form["estado_turno"],
                "horario": {"id_horario": horario_id},
            }
            r = requests.put(
                "http://localhost:8099/api/turno/actualizar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Turno actualizado correctamente", "success")
                return redirect(url_for("router_admin.lista_turno"))
            else:
                flash(f"Error al actualizar: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    try:
        estados_turno = ["Disponible", "Cancelado", "Agotado"]
        r = requests.get(f"http://localhost:8099/api/turno/lista/{id}")
        turno = r.json().get("turno") if r.status_code == 200 else None
        r_horarios = requests.get("http://localhost:8099/api/horario/lista")
        horarios = r_horarios.json().get("horarios", []) if r_horarios.status_code == 200 else []
        if turno and turno.get("fecha_salida"):
            try:
                fecha_obj = datetime.strptime(turno["fecha_salida"], "%d/%m/%Y")
                turno["fecha_salida"] = fecha_obj.strftime("%Y-%m-%d")
            except ValueError:
                pass
        if turno:
            return render_template(
                "crud/turno/turno_editar.html",
                turno=turno,
                horarios=horarios,
                usuario=usuario,
                estados_turno=estados_turno,
            )
        else:
            flash("Turno no encontrado", "error")
            return redirect(url_for("router_admin.lista_turno"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router_admin.lista_turno"))


@router_admin.route("/turno/eliminar/<int:id>", methods=["POST"])
def eliminar_turno(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/turno/eliminar/{id}")
        if r.status_code == 200:
            flash("Turno eliminado correctamente", "success")
        else:
            flash("Error al eliminar el turno", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router_admin.lista_turno"))


@router_admin.route("/turno/ordenar/<atributo>/<orden>")
def ordenar_turno(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/turno/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_msg = response.json().get("mensaje", "Error desconocido al ordenar")
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Error al ordenar boletos: {str(e)}"}), 500


@router_admin.route("/turno/buscar/<atributo>/<criterio>")
def buscar_turno(atributo, criterio):
    try:
        response = requests.get(f"http://localhost:8099/api/turno/buscar/{atributo}/{criterio}")
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500


# CRUD de Frecuencias


@router_admin.route("/frecuencia/lista")
@requiere_administrador
def lista_frecuencia():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/frecuencia/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template(
                "crud/frecuencia/frecuencia.html",
                lista=data.get("frecuencias", []),
                usuario=usuario,
            )
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/frecuencia/frecuencia.html", lista=[], usuario=usuario)
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/frecuencia/frecuencia.html", lista=[], usuario=usuario)


@router_admin.route("/frecuencia/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_frecuencia():
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            data = {
                "numero_repeticiones": int(request.form["numero_repeticiones"]),
                "periodo": request.form["periodo"],
                "precio_recorrido": float(request.form["precio_recorrido"]),
                "horario": {"id_horario": int(request.form["horario_id"])},
            }
            r = requests.post(
                "http://localhost:8099/api/frecuencia/guardar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Frecuencia creada correctamente", "success")
                return redirect(url_for("router_admin.lista_frecuencia"))
            else:
                flash(f"Error al crear la frecuencia: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    try:
        r = requests.get("http://localhost:8099/api/horario/lista")
        horarios = r.json().get("horarios", []) if r.status_code == 200 else []
    except:
        horarios = []
        flash("Error al cargar los horarios", "error")
    return render_template(
        "crud/frecuencia/frecuencia_crear.html", horarios=horarios, usuario=usuario
    )


@router_admin.route("/frecuencia/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_frecuencia(id):
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            data = {
                "id_frecuencia": id,
                "numero_repeticiones": int(request.form["numero_repeticiones"]),
                "periodo": request.form["periodo"],
                "precio_recorrido": float(request.form["precio_recorrido"]),
                "horario": {"id_horario": int(request.form["horario_id"])},
            }
            r = requests.put(
                "http://localhost:8099/api/frecuencia/actualizar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Frecuencia actualizada correctamente", "success")
                return redirect(url_for("router_admin.lista_frecuencia"))
            else:
                flash(f"Error al actualizar: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    try:
        r = requests.get(f"http://localhost:8099/api/frecuencia/lista/{id}")
        frecuencia = r.json().get("frecuencia") if r.status_code == 200 else None
        r_horarios = requests.get("http://localhost:8099/api/horario/lista")
        horarios = r_horarios.json().get("horarios", []) if r_horarios.status_code == 200 else []
        if frecuencia:
            return render_template(
                "crud/frecuencia/frecuencia_editar.html",
                frecuencia=frecuencia,
                horarios=horarios,
                usuario=usuario,
            )
        else:
            flash("Frecuencia no encontrada", "error")
            return redirect(url_for("router_admin.lista_frecuencia"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router_admin.lista_frecuencia"))


@router_admin.route("/frecuencia/eliminar/<int:id>", methods=["POST"])
def eliminar_frecuencia(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/frecuencia/eliminar/{id}")
        if r.status_code == 200:
            flash("Frecuencia eliminada correctamente", "success")
        else:
            flash("Error al eliminar la frecuencia", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router_admin.lista_frecuencia"))


@router_admin.route("/frecuencia/ordenar/<atributo>/<orden>")
def ordenar_frecuencia(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/frecuencia/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_msg = response.json().get("mensaje", "Error desconocido al ordenar")
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Error al ordenar boletos: {str(e)}"}), 500


@router_admin.route("/frecuencia/buscar/<atributo>/<criterio>")
def buscar_frecuencia(atributo, criterio):
    try:
        response = requests.get(
            f"http://localhost:8099/api/frecuencia/buscar/{atributo}/{criterio}"
        )
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500


# CRUD de Personas


@router_admin.route("/persona/lista")
@requiere_administrador
def lista_persona():
    try:
        usuario = obtener_info_usuario()
        r = requests.get("http://localhost:8099/api/persona/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template(
                "crud/persona/persona.html", usuario=usuario, lista=data.get("personas", [])
            )
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/persona/persona.html", usuario=usuario, lista=[])
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/persona/persona.html", usuario=usuario, lista=[])


@router_admin.route("/persona/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_persona():
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            r_personas = requests.get("http://localhost:8099/api/persona/lista")
            personas = r_personas.json().get("personas", [])
            numero_identificacion = request.form.get("numero_identificacion").strip()
            correo = request.form.get("correo").strip()
            telefono = request.form.get("telefono").strip()
            for persona in personas:
                if persona.get("numero_identificacion") == numero_identificacion:
                    return render_template(
                        "crud/persona/persona_crear.html",
                        tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
                        generos=["No_definido", "Masculino", "Femenino", "Otro"],
                        tipos_cuenta=["Administrador", "Cliente"],
                        tipos_tarifa=[
                            "General",
                            "Menor_edad",
                            "Tercera_edad",
                            "Estudiante",
                            "Discapacitado",
                        ],
                        estados_cuenta=["Activo", "Inactivo", "Suspendido"],
                        usuario=usuario,
                        error="Ya existe una persona registrada con este número de identificación",
                    )
                if persona.get("correo") == correo:
                    return render_template(
                        "crud/persona/persona_crear.html",
                        tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
                        generos=["No_definido", "Masculino", "Femenino", "Otro"],
                        tipos_cuenta=["Administrador", "Cliente"],
                        tipos_tarifa=[
                            "General",
                            "Menor_edad",
                            "Tercera_edad",
                            "Estudiante",
                            "Discapacitado",
                        ],
                        estados_cuenta=["Activo", "Inactivo", "Suspendido"],
                        usuario=usuario,
                        error="Ya existe una persona registrada con este correo electrónico",
                    )
                if persona.get("telefono") == telefono:
                    return render_template(
                        "crud/persona/persona_crear.html",
                        tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
                        generos=["No_definido", "Masculino", "Femenino", "Otro"],
                        tipos_cuenta=["Administrador", "Cliente"],
                        tipos_tarifa=[
                            "General",
                            "Menor_edad",
                            "Tercera_edad",
                            "Estudiante",
                            "Discapacitado",
                        ],
                        estados_cuenta=["Activo", "Inactivo", "Suspendido"],
                        usuario=usuario,
                        error="Ya existe una persona registrada con este número de teléfono",
                    )
            data = {
                "tipo_identificacion": request.form["tipo_identificacion"],
                "numero_identificacion": request.form["numero_identificacion"],
                "nombre": request.form["nombre"],
                "apellido": request.form["apellido"],
                "fecha_nacimiento": request.form["fecha_nacimiento"],
                "telefono": request.form["telefono"],
                "correo": request.form["correo"],
                "genero": request.form["genero"],
                "direccion": request.form.get("direccion", ""),
                "tipo_tarifa": request.form.get("tipo_tarifa"),
                "saldo_disponible": "0.0",
                "usuario": request.form["usuario"],
                "contrasenia": request.form["contrasenia"],
                "tipo_cuenta": request.form["tipo_cuenta"],
                "estado_cuenta": request.form["estado_cuenta"],
            }
            if "opcion_pago" in request.form and request.form["opcion_pago"]:
                campos_pago = [
                    "opcion_pago",
                    "titular",
                    "numero_tarjeta",
                    "fecha_vencimiento",
                    "codigo_seguridad",
                    "saldo",
                ]
                if all(request.form.get(campo) for campo in campos_pago):
                    data.update(
                        {
                            "metodo_pago": True,
                            "opcion_pago": request.form["opcion_pago"],
                            "numero_tarjeta": request.form["numero_tarjeta"],
                            "titular": request.form["titular"],
                            "fecha_vencimiento": request.form["fecha_vencimiento"],
                            "codigo_seguridad": request.form["codigo_seguridad"],
                            "saldo": request.form["saldo"],
                        }
                    )
            r = requests.post(
                "http://localhost:8099/api/persona/guardar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Persona creada correctamente", "success")
                return redirect(url_for("router_admin.lista_persona"))
            else:
                flash(f"Error al crear: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
        except ValueError as e:
            flash(f"Error en los datos: {str(e)}", "error")
    return render_template(
        "crud/persona/persona_crear.html",
        tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
        generos=["No_definido", "Masculino", "Femenino", "Otro"],
        tipos_cuenta=["Administrador", "Cliente"],
        tipos_tarifa=["General", "Menor_edad", "Tercera_edad", "Estudiante", "Discapacitado"],
        estados_cuenta=["Activo", "Inactivo", "Suspendido"],
        usuario=usuario,
    )


@router_admin.route("/persona/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_persona(id):
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            r_personas = requests.get("http://localhost:8099/api/persona/lista")
            personas = r_personas.json().get("personas", [])
            numero_identificacion = request.form.get("numero_identificacion").strip()
            correo = request.form.get("correo").strip()
            telefono = request.form.get("telefono").strip()
            otras_personas = [p for p in personas if p.get("id_persona") != id]
            for persona in otras_personas:
                if persona.get("numero_identificacion") == numero_identificacion:
                    return render_template(
                        "crud/persona/persona_editar.html",
                        tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
                        generos=["No_definido", "Masculino", "Femenino", "Otro"],
                        tipos_cuenta=["Administrador", "Cliente"],
                        tipos_tarifa=[
                            "General",
                            "Menor_edad",
                            "Tercera_edad",
                            "Estudiante",
                            "Discapacitado",
                        ],
                        estados_cuenta=["Activo", "Inactivo", "Suspendido"],
                        usuario=usuario,
                        error="Ya existe una persona registrada con este número de identificación",
                    )
            for persona in otras_personas:
                if persona.get("correo") == correo:
                    return render_template(
                        "crud/persona/persona_editar.html",
                        tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
                        generos=["No_definido", "Masculino", "Femenino", "Otro"],
                        tipos_cuenta=["Administrador", "Cliente"],
                        tipos_tarifa=[
                            "General",
                            "Menor_edad",
                            "Tercera_edad",
                            "Estudiante",
                            "Discapacitado",
                        ],
                        estados_cuenta=["Activo", "Inactivo", "Suspendido"],
                        usuario=usuario,
                        error="Ya existe una persona registrada con este correo electrónico",
                    )
            for persona in otras_personas:
                if persona.get("telefono") == telefono:
                    return render_template(
                        "crud/persona/persona_editar.html",
                        tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
                        generos=["No_definido", "Masculino", "Femenino", "Otro"],
                        tipos_cuenta=["Administrador", "Cliente"],
                        tipos_tarifa=[
                            "General",
                            "Menor_edad",
                            "Tercera_edad",
                            "Estudiante",
                            "Discapacitado",
                        ],
                        estados_cuenta=["Activo", "Inactivo", "Suspendido"],
                        usuario=usuario,
                        error="Ya existe una persona registrada con este número de teléfono",
                    )
            fecha_nacimiento = request.form.get("fecha_nacimiento")
            if fecha_nacimiento:
                fecha_parts = fecha_nacimiento.split("-")
                fecha_formateada = f"{fecha_parts[2]}/{fecha_parts[1]}/{fecha_parts[0]}"
            datos_actualizacion = {
                "id_persona": id,
                "tipo_identificacion": request.form.get("tipo_identificacion"),
                "numero_identificacion": request.form.get("numero_identificacion"),
                "nombre": request.form.get("nombre"),
                "apellido": request.form.get("apellido"),
                "fecha_nacimiento": fecha_formateada,
                "direccion": request.form.get("direccion"),
                "genero": request.form.get("genero"),
                "telefono": request.form.get("telefono"),
                "correo": request.form.get("correo"),
                "tipo_tarifa": request.form.get("tipo_tarifa"),
                "saldo_disponible": float(request.form.get("saldo_disponible", 0)),
                "cuenta": {
                    "id_cuenta": request.form.get("cuenta_id"),
                    "correo": request.form.get("cuenta_correo"),
                    "tipo_cuenta": request.form.get("tipo_cuenta"),
                    "estado_cuenta": request.form.get("estado_cuenta"),
                },
            }
            if request.form.get("contrasenia"):
                datos_actualizacion["cuenta"]["contrasenia"] = request.form.get("contrasenia")
            if request.form.get("eliminar_metodo_pago") == "1":
                datos_actualizacion["metodo_pago"] = None
            else:
                metodo_pago = {
                    "opcion_pago": request.form.get("metodo_pago[opcion_pago]"),
                    "titular": request.form.get("metodo_pago[titular]"),
                    "numero_tarjeta": request.form.get("metodo_pago[numero_tarjeta]"),
                    "fecha_vencimiento": request.form.get("metodo_pago[fecha_vencimiento]"),
                    "codigo_seguridad": request.form.get("metodo_pago[codigo_seguridad]"),
                    "saldo": float(request.form.get("metodo_pago[saldo]", 0)),
                }
                if request.form.get("metodo_pago[id_pago]"):
                    metodo_pago["id_pago"] = int(request.form.get("metodo_pago[id_pago]"))
                datos_actualizacion["metodo_pago"] = metodo_pago
            response = requests.put(
                "http://localhost:8099/api/persona/actualizar", json=datos_actualizacion
            )
            if response.status_code == 200:
                flash("Persona actualizada exitosamente", "success")
                return redirect(url_for("router_admin.lista_persona"))
            else:
                flash("Error al actualizar la persona", "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    try:
        r = requests.get(f"http://localhost:8099/api/persona/lista/{id}")
        if r.status_code == 200:
            persona = r.json().get("persona")
            return render_template(
                "crud/persona/persona_editar.html",
                persona=persona,
                tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
                generos=["No_definido", "Masculino", "Femenino", "Otro"],
                tipos_cuenta=["Administrador", "Cliente"],
                tipos_tarifa=[
                    "General",
                    "Menor_edad",
                    "Tercera_edad",
                    "Estudiante",
                    "Discapacitado",
                ],
                estados_cuenta=["Activo", "Inactivo", "Suspendido"],
                metodos_pago=["Tarjeta_credito", "Tarjeta_debito"],
                usuario=usuario,
            )
        else:
            flash("Error al obtener los datos de la persona", "error")
            return redirect(url_for("router_admin.lista_persona"))
    except requests.exceptions.RequestException as e:
        flash(f"Error al cargar los datos: {str(e)}", "error")
        return redirect(url_for("router_admin.lista_persona"))


@router_admin.route("/persona/eliminar/<int:id>", methods=["POST"])
def eliminar_persona(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/persona/eliminar/{id}")
        if r.status_code == 200:
            flash("Persona eliminada correctamente", "success")
        else:
            flash("Error al eliminar la persona", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router_admin.lista_persona"))


@router_admin.route("/persona/ordenar/<atributo>/<orden>")
def ordenar_persona(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/persona/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_msg = response.json().get("mensaje", "Error desconocido al ordenar")
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Error al ordenar boletos: {str(e)}"}), 500


@router_admin.route("/persona/buscar/<atributo>/<criterio>")
def buscar_persona(atributo, criterio):
    try:
        response = requests.get(f"http://localhost:8099/api/persona/buscar/{atributo}/{criterio}")
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500


# CRUD de Cuenta


@router_admin.route("/cuenta/lista")
@requiere_administrador
def lista_cuenta():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/cuenta/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template(
                "crud/cuenta/cuenta.html", lista=data.get("cuentas", []), usuario=usuario
            )
        flash("Error al obtener la lista de cuentas", "error")
        return render_template("crud/cuenta/cuenta.html", lista=[], usuario=usuario)
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/cuenta/cuenta.html", lista=[], usuario=usuario)


@router_admin.route("/cuenta/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_cuenta():
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            r_cuenta = requests.get("http://localhost:8099/api/cuenta/lista")
            cuentas = r_cuenta.json().get("cuentas", [])
            correo = request.form.get("correo")
            for cuenta in cuentas:
                if cuenta["correo"] == correo:
                    return render_template(
                        "crud/cuenta/cuenta_crear.html",
                        tipos_cuenta=["Administrador", "Cliente"],
                        usuario=usuario,
                        error="El correo ya existe",
                        valores=request.form,
                        estados_cuenta=["Activo", "Inactivo", "Suspendido"],
                    )
            data = {
                "correo": request.form["correo"],
                "contrasenia": request.form["contrasenia"],
                "tipo_cuenta": request.form["tipo_cuenta"],
                "estado_cuenta": request.form["estado_cuenta"],
            }
            if not all(data.values()):
                flash("Todos los campos son requeridos", "error")
                return redirect(url_for("router_admin.crear_cuenta"))
            r = requests.post(
                "http://localhost:8099/api/cuenta/guardar",
                json=data,
                headers={"Content-Type": "application/json"},
            )
            if r.status_code == 200:
                flash("Cuenta creada exitosamente", "success")
                return redirect(url_for("router_admin.lista_cuenta"))
            else:
                flash(f"Error al crear la cuenta: {r.text}", "error")
                return redirect(url_for("router_admin.crear_cuenta"))
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
            return redirect(url_for("router_admin.crear_cuenta"))
    try:
        r_tipos = requests.get("http://localhost:8099/api/cuenta/tipos")
        tipos = (
            r_tipos.json()["tipos_cuenta"]
            if r_tipos.status_code == 200
            else ["Administrador", "Cliente"]
        )
        r_estados = requests.get("http://localhost:8099/api/cuenta/estados")
        estados = (
            r_estados.json()["estados_cuenta"]
            if r_estados.status_code == 200
            else ["Activo", "Inactivo", "Suspendido"]
        )
        return render_template(
            "crud/cuenta/cuenta_crear.html",
            tipos_cuenta=tipos,
            estados_cuenta=estados,
            usuario=usuario,
        )
    except requests.exceptions.RequestException:
        flash("Error al cargar los datos del formulario", "error")
        return render_template(
            "crud/cuenta/cuenta_crear.html",
            tipos_cuenta=["Administrador", "Cliente"],
            estados_cuenta=["Activo", "Inactivo", "Suspendido"],
            usuario=usuario,
        )


@router_admin.route("/cuenta/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_cuenta(id):
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            r_cuentas = requests.get("http://localhost:8099/api/cuenta/lista")
            cuentas = r_cuentas.json().get("cuentas", [])
            correo = request.form["correo"]
            for cuenta in cuentas:
                if cuenta["id_cuenta"] != id and cuenta["correo"].lower() == correo.lower():
                    r = requests.get(f"http://localhost:8099/api/cuenta/lista/{id}")
                    cuenta_actual = r.json().get("cuenta")
                    r_tipos = requests.get("http://localhost:8099/api/cuenta/tipos")
                    r_estados = requests.get("http://localhost:8099/api/cuenta/estados")
                    tipos = r_tipos.json().get("tipos_cuenta", ["Administrador", "Cliente"])
                    estados = r_estados.json().get("estados_cuenta", ["Activo", "Inactivo"])
                    return render_template(
                        "crud/cuenta/cuenta_editar.html",
                        cuenta=cuenta_actual,
                        tipos_cuenta=tipos,
                        estados_cuenta=estados,
                        usuario=usuario,
                        error="El correo ya esta registrado",
                    )
            data = {
                "id_cuenta": id,
                "correo": request.form["correo"],
                "contrasenia": request.form["contrasenia"],
                "tipo_cuenta": request.form["tipo_cuenta"],
                "estado_cuenta": request.form["estado_cuenta"],
            }
            if request.form.get("contrasenia") and request.form["contrasenia"].strip():
                data["contrasenia"] = request.form["contrasenia"]
            r = requests.put(
                "http://localhost:8099/api/cuenta/actualizar",
                json=data,
                headers={"Content-Type": "application/json"},
            )
            if r.status_code == 200:
                flash("Cuenta actualizada exitosamente", "success")
                try:
                    r_sync = requests.post("http://localhost:8099/api/cuenta/sincronizar")
                    if r_sync.status_code != 200:
                        flash("Advertencia: Error al sincronizar los datos", "warning")
                except:
                    flash("Advertencia: Error al sincronizar los datos", "warning")
                return redirect(url_for("router_admin.lista_cuenta"))
            else:
                flash(
                    f"Error al actualizar la cuenta: {r.json().get('mensaje', 'Error desconocido')}",
                    "error",
                )
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    try:
        r_cuenta = requests.get(f"http://localhost:8099/api/cuenta/lista/{id}")
        if r_cuenta.status_code != 200:
            flash("Cuenta no encontrada", "error")
            return redirect(url_for("router_admin.lista_cuenta"))
        cuenta = r_cuenta.json()["cuenta"]
        r_tipos = requests.get("http://localhost:8099/api/cuenta/tipos")
        tipos = (
            r_tipos.json()["tipos_cuenta"]
            if r_tipos.status_code == 200
            else ["Administrador", "Cliente"]
        )
        r_estados = requests.get("http://localhost:8099/api/cuenta/estados")
        estados = (
            r_estados.json()["estados_cuenta"]
            if r_estados.status_code == 200
            else ["Activo", "Inactivo", "Suspendido"]
        )
        return render_template(
            "crud/cuenta/cuenta_editar.html",
            cuenta=cuenta,
            tipos_cuenta=tipos,
            estados_cuenta=estados,
            usuario=usuario,
        )
    except requests.exceptions.RequestException as e:
        flash(f"Error al cargar los datos: {str(e)}", "error")
        return redirect(url_for("router_admin.lista_cuenta"))


@router_admin.route("/cuenta/eliminar/<int:id>", methods=["POST"])
def eliminar_cuenta(id):
    try:
        r_verificar = requests.get(f"http://localhost:8099/api/cuenta/lista/{id}")
        if r_verificar.status_code != 200:
            flash("Cuenta no encontrada", "error")
            return redirect(url_for("router_admin.lista_cuenta"))
        r = requests.delete(f"http://localhost:8099/api/cuenta/eliminar/{id}")
        if r.status_code == 200:
            flash("Cuenta eliminada exitosamente", "success")
        else:
            flash(f"Error al eliminar la cuenta: {r.text}", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router_admin.lista_cuenta"))


@router_admin.route("/cuenta/ordenar/<atributo>/<orden>")
def ordenar_cuentas(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/cuenta/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error al ordenar: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error al ordenar: {str(e)}"}), 500


@router_admin.route("/cuenta/buscar/<atributo>/<criterio>")
def buscar_cuentas(atributo, criterio):
    try:
        response = requests.get(f"http://localhost:8099/api/cuenta/buscar/{atributo}/{criterio}")
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500


# CRUD de Pagos


@router_admin.route("/pago/lista")
@requiere_administrador
def lista_pago():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/pago/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template(
                "crud/pago/pago.html", lista=data.get("pagos", []), usuario=usuario
            )
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/pago/pago.html", lista=[], usuario=usuario)
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/pago/pago.html", lista=[], usuario=usuario)


@router_admin.route("/pago/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_pago():
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            data = {
                "opcion_pago": request.form["opcion_pago"],
                "titular": request.form["titular"],
                "numero_tarjeta": request.form["numero_tarjeta"],
                "fecha_vencimiento": request.form["fecha_vencimiento"],
                "codigo_seguridad": request.form["codigo_seguridad"],
                "saldo": request.form.get("saldo"),
            }
            r = requests.post(
                "http://localhost:8099/api/pago/guardar",
                json=data,
            )
            if r.status_code == 200:
                flash("Método de pago creado exitosamente", "success")
                return redirect(url_for("router_admin.lista_pago"))
            else:
                flash(
                    f"Error al crear el método de pago: {r.json().get('mensaje', 'Error desconocido')}",
                    "error",
                )
                return redirect(url_for("router_admin.crear_pago"))
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
            return redirect(url_for("router_admin.crear_pago"))
        except ValueError as e:
            flash("Error en los datos ingresados", "error")
            return redirect(url_for("router_admin.crear_pago"))
    try:
        r = requests.get("http://localhost:8099/api/pago/opciones")
        metodos_pago = (
            r.json()["metodos_pago"]
            if r.status_code == 200
            else ["Tarjeta_credito", "Tarjeta_debito"]
        )
        return render_template(
            "crud/pago/pago_crear.html", metodos_pago=metodos_pago, usuario=usuario
        )
    except:
        return render_template(
            "crud/pago/pago_crear.html",
            metodos_pago=["Tarjeta_credito", "Tarjeta_debito"],
            usuario=usuario,
        )


@router_admin.route("/pago/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_pago(id):
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            data = {
                "id_pago": id,
                "opcion_pago": request.form["opcion_pago"],
                "numero_tarjeta": request.form["numero_tarjeta"],
                "titular": request.form["titular"],
                "fecha_vencimiento": request.form["fecha_vencimiento"],
                "codigo_seguridad": request.form["codigo_seguridad"],
                "saldo": float(request.form["saldo"]),
            }
            r = requests.put(
                "http://localhost:8099/api/pago/actualizar",
                json=data,
                headers={"Content-Type": "application/json"},
            )
            if r.status_code == 200:
                flash("Método de pago actualizado exitosamente", "success")
                return redirect(url_for("router_admin.lista_pago"))
            else:
                flash(
                    f"Error al actualizar: {r.json().get('mensaje', 'Error desconocido')}", "error"
                )
                return redirect(url_for("router_admin.editar_pago", id=id))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for("router_admin.editar_pago", id=id))
    try:
        r_pago = requests.get(f"http://localhost:8099/api/pago/lista/{id}")
        if r_pago.status_code != 200:
            flash("Método de pago no encontrado", "error")
            return redirect(url_for("router_admin.lista_pago"))
        pago = r_pago.json()["pago"]
        r_opciones = requests.get("http://localhost:8099/api/pago/opciones")
        metodos_pago = (
            r_opciones.json()["metodos_pago"]
            if r_opciones.status_code == 200
            else ["Tarjeta_credito", "Tarjeta_debito"]
        )
        return render_template(
            "crud/pago/pago_editar.html", pago=pago, metodos_pago=metodos_pago, usuario=usuario
        )
    except Exception as e:
        flash(f"Error al cargar los datos: {str(e)}", "error")
        return redirect(url_for("router_admin.lista_pago"))


@router_admin.route("/pago/eliminar/<int:id>", methods=["POST"])
def eliminar_pago(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/pago/eliminar/{id}")
        if r.status_code == 200:
            flash("Pago eliminado correctamente", "success")
        else:
            flash("Error al eliminar el pago", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router_admin.lista_pago"))


@router_admin.route("/pago/ordenar/<atributo>/<orden>")
def ordenar_pago(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/pago/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_msg = response.json().get("mensaje", "Error desconocido al ordenar")
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Error al ordenar boletos: {str(e)}"}), 500


@router_admin.route("/pago/buscar/<atributo>/<criterio>")
def buscar_pago(atributo, criterio):
    try:
        response = requests.get(f"http://localhost:8099/api/pago/buscar/{atributo}/{criterio}")
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500


# CRUD de Boletos


@router_admin.route("/boleto/lista")
@requiere_administrador
def lista_boleto():
    usuario = obtener_info_usuario()
    try:
        response = requests.get(f"http://localhost:8099/api/boleto/lista")
        if response.status_code == 200:
            data = response.json()
            return render_template(
                "crud/boleto/boleto.html", lista=data.get("boletos", []), usuario=usuario
            )
        else:
            flash("Error al obtener la lista de boletos", "danger")
            return render_template("crud/boleto/boleto.html", lista=[], usuario=usuario)
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "danger")
        return render_template("crud/boleto/boleto.html", lista=[], usuario=usuario)


@router_admin.route("/boleto/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_boleto():
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            asientos = [
                int(x.strip()) for x in request.form.get("asientos").split(",") if x.strip()
            ]
            data = {
                "fecha_compra": fecha_actual,
                "asientos": asientos,
                "precio_unitario": float(request.form.get("precio_unitario")),
                "persona": {"id_persona": int(request.form.get("persona_id"))},
                "turno": {"id_turno": int(request.form.get("turno_id"))},
            }
            response = requests.post("http://localhost:8099/api/boleto/guardar", json=data)
            if response.status_code == 200:
                flash("Boleto(s) creado(s) exitosamente", "success")
                return redirect(url_for("router_admin.lista_boleto"))
            else:
                error_msg = response.json().get("msg", "Error al crear el boleto")
                flash(error_msg, "danger")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "danger")
        except ValueError as e:
            flash(f"Error en los datos del formulario: {str(e)}", "danger")
    try:
        personas_response = requests.get("http://localhost:8099/api/persona/lista")
        turnos_response = requests.get("http://localhost:8099/api/turno/lista")
        personas = (
            personas_response.json().get("personas", [])
            if personas_response.status_code == 200
            else []
        )
        turnos = (
            turnos_response.json().get("turnos", []) if turnos_response.status_code == 200 else []
        )
        return render_template(
            "crud/boleto/boleto_crear.html", personas=personas, turnos=turnos, usuario=usuario
        )
    except requests.exceptions.RequestException as e:
        flash(f"Error al cargar los datos: {str(e)}", "danger")
        return redirect(url_for("router_admin.lista_boleto"))


@router_admin.route("/boleto/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_boleto(id):
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            data = {
                "id_boleto": id,
                "asientos": request.form.get("asientos"),
                "precio_final": float(request.form.get("precio_final")),
                "persona_id": int(request.form.get("persona_id")),
                "turno_id": int(request.form.get("turno_id")),
            }
            response = requests.put(
                "http://localhost:8099/api/boleto/actualizar",
                json=data,
                headers={"Content-Type": "application/json"},
            )
            if response.status_code == 200:
                flash("Boleto actualizado exitosamente", "success")
                return redirect(url_for("router_admin.lista_boleto"))
            else:
                error_msg = response.json().get("msg", "Error al actualizar el boleto")
                flash(error_msg, "danger")
                return redirect(url_for("router_admin.editar_boleto", id=id))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for("router_admin.editar_boleto", id=id))
    try:
        boleto_response = requests.get(f"http://localhost:8099/api/boleto/lista/{id}")
        personas_response = requests.get("http://localhost:8099/api/persona/lista")
        turnos_response = requests.get("http://localhost:8099/api/turno/lista")
        boleto = boleto_response.json().get("boleto")
        estados_boleto = ["Vendido", "Reservado", "Disponible", "Cancelado"]
        if boleto_response.status_code == 200:
            boleto = boleto_response.json().get("boleto")
            personas = personas_response.json().get("personas", [])
            turnos = turnos_response.json().get("turnos", [])
            return render_template(
                "crud/boleto/boleto_editar.html",
                boleto=boleto,
                personas=personas,
                turnos=turnos,
                usuario=usuario,
                estados_boleto=estados_boleto,
            )
        else:
            flash("Boleto no encontrado", "danger")
            return redirect(url_for("router_admin.lista_boleto"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "danger")
        return redirect(url_for("router_admin.lista_boleto"))


@router_admin.route("/boleto/eliminar/<int:id>", methods=["POST"])
def eliminar_boleto(id):
    try:
        response = requests.delete(f"http://localhost:8099/api/boleto/eliminar/{id}")
        if response.status_code == 200:
            flash("Boleto eliminado exitosamente", "success")
        else:
            flash("Error al eliminar el boleto", "danger")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "danger")
    return redirect(url_for("router_admin.lista_boleto"))


@router_admin.route("/boleto/ordenar/<atributo>/<orden>")
def ordenar_boletos(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/boleto/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_msg = response.json().get("mensaje", "Error desconocido al ordenar")
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Error al ordenar boletos: {str(e)}"}), 500


@router_admin.route("/boleto/buscar/<atributo>/<criterio>")
def buscar_boletos(atributo, criterio):
    try:
        response = requests.get(f"http://localhost:8099/api/boleto/buscar/{atributo}/{criterio}")
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500


# CRUD de Descuentos


@router_admin.route("/descuento/lista")
@requiere_administrador
def lista_descuento():
    usuario = obtener_info_usuario()
    try:
        r = requests.get("http://localhost:8099/api/descuento/lista")
        if r.status_code == 200:
            descuentos = r.json().get("descuentos", [])
            return render_template(
                "crud/descuento/descuento.html", descuentos=descuentos, usuario=usuario
            )
        flash("Error al obtener la lista de descuentos", "error")
        return redirect(url_for("router_admin.administrador"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router_admin.administrador"))


@router_admin.route("/descuento/crear", methods=["GET", "POST"])
@requiere_administrador
def crear_descuento():
    usuario = obtener_info_usuario()
    if request.method == "POST":
        try:
            r_descuento = requests.get("http://localhost:8099/api/descuento/lista")
            descuentos = r_descuento.json().get("descuentos", [])
            nombre_descuento = request.form.get("nombre_descuento")
            for descuento in descuentos:
                if descuento["nombre_descuento"] == nombre_descuento:
                    return render_template(
                        "crud/descuento/descuento_crear.html",
                        descuentos=descuentos,
                        usuario=usuario,
                        estados_descuento=["Activo", "Inactivo", "Expirado", "Agotado"],
                        error="El nombre del descuento ya existe",
                        valores=request.form,
                    )
            data = {
                "nombre_descuento": request.form.get("nombre_descuento"),
                "descripcion": request.form.get("descripcion"),
                "porcentaje": request.form.get("porcentaje"),
                "estado_descuento": request.form.get("estado_descuento"),
                "tipo_descuento": "Promocional",
                "fecha_inicio": datetime.now().strftime("%Y-%m-%d"),
                "fecha_fin": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            }
            response = requests.post("http://localhost:8099/api/descuento/guardar", json=data)
            if response.status_code == 200:
                flash("Descuento creado exitosamente", "success")
                return redirect(url_for("router_admin.lista_descuento"))
            else:
                error_msg = response.json().get("msg", "Error al crear el descuento")
                flash(error_msg, "danger")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "danger")
        except ValueError as e:
            flash(f"Error en los datos del formulario: {str(e)}", "danger")
    try:
        descuento_response = requests.get("http://localhost:8099/api/descuento/estados")
        descuentos = (
            descuento_response.json().get("estados_descuento", [])
            if descuento_response.status_code == 200
            else ["Activo", "Inactivo", "Expirado", "Agotado"]
        )
        return render_template(
            "crud/descuento/descuento_crear.html",
            descuentos=descuentos,
            usuario=usuario,
            estados_descuento=["Activo", "Inactivo", "Expirado", "Agotado"],
        )
    except requests.exceptions.RequestException as e:
        flash(f"Error al cargar los datos: {str(e)}", "danger")
        return redirect(url_for("router_admin.lista_descuento"))


@router_admin.route("/descuento/editar/<int:id>", methods=["GET", "POST"])
@requiere_administrador
def editar_descuento(id):
    usuario = obtener_info_usuario()
    estados_descuento = ["Activo", "Inactivo", "Expirado", "Agotado"]
    if request.method == "POST":
        try:
            r_descuentos = requests.get("http://localhost:8099/api/descuento/lista")
            descuentos = r_descuentos.json().get("descuentos", [])
            nombre_descuento = request.form.get("nombre_descuento")
            for descuento in descuentos:
                if (
                    descuento["id_descuento"] != id
                    and descuento["nombre_descuento"].lower() == nombre_descuento.lower()
                ):
                    r = requests.get(f"http://localhost:8099/api/descuento/lista/{id}")
                    descuento_actual = r.json().get("descuento")
                    return render_template(
                        "crud/descuento/descuento_editar.html",
                        descuento=descuento_actual,
                        estados_descuento=["Activo", "Inactivo", "Expirado", "Agotado"],
                        usuario=usuario,
                        error="El nombre del descuento ya existe",
                    )
            datos = {
                "id_descuento": id,
                "nombre_descuento": request.form.get("nombre_descuento"),
                "descripcion": request.form.get("descripcion"),
                "porcentaje": int(request.form.get("porcentaje")),
                "estado_descuento": request.form.get("estado_descuento"),
            }
            if id > 5:
                fecha_inicio = request.form.get("fecha_inicio")
                fecha_fin = request.form.get("fecha_fin")
                if fecha_inicio:
                    fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                    datos["fecha_inicio"] = fecha_inicio_obj.strftime("%d/%m/%Y")
                if fecha_fin:
                    fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
                    datos["fecha_fin"] = fecha_fin_obj.strftime("%d/%m/%Y")
            r = requests.put("http://localhost:8099/api/descuento/actualizar", json=datos)
            if r.status_code == 200:
                flash("Descuento actualizado exitosamente", "success")
                return redirect(url_for("router_admin.lista_descuento"))
            flash("Error al actualizar el descuento", "error")
        except ValueError:
            flash("Error: El porcentaje debe ser un número", "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    try:
        r = requests.get(f"http://localhost:8099/api/descuento/lista/{id}")
        if r.status_code == 200:
            descuento = r.json().get("descuento")
            return render_template(
                "crud/descuento/descuento_editar.html",
                descuento=descuento,
                usuario=usuario,
                estados_descuento=estados_descuento,
            )
        flash("Error al obtener el descuento", "error")
        return redirect(url_for("router_admin.lista_descuento"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router_admin.lista_descuento"))


@router_admin.route("/descuento/eliminar/<int:id>", methods=["POST"])
def eliminar_descuento(id):
    try:
        response = requests.delete(f"http://localhost:8099/api/descuento/eliminar/{id}")
        if response.status_code == 200:
            flash("Descuento eliminado exitosamente", "success")
        else:
            flash("Error al eliminar el descuento", "danger")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "danger")
    return redirect(url_for("router_admin.lista_descuento"))


@router_admin.route("/descuento/ordenar/<atributo>/<orden>")
def ordenar_descuento(atributo, orden):
    try:
        response = requests.get(f"http://localhost:8099/api/descuento/ordenar/{atributo}/{orden}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            error_msg = response.json().get("mensaje", "Error desconocido al ordenar")
            return jsonify({"error": error_msg}), response.status_code
    except Exception as e:
        return jsonify({"error": f"Error al ordenar boletos: {str(e)}"}), 500


@router_admin.route("/descuento/buscar/<atributo>/<criterio>")
def buscar_descuento(atributo, criterio):
    try:
        response = requests.get(f"http://localhost:8099/api/descuento/buscar/{atributo}/{criterio}")
        if response.status_code == 200:
            return jsonify(response.json())
        return (
            jsonify({"error": f"Error en la búsqueda: {response.json().get('mensaje')}"}),
            response.status_code,
        )
    except Exception as e:
        return jsonify({"error": f"Error en la búsqueda: {str(e)}"}), 500
