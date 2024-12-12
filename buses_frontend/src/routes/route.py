from flask import Blueprint, jsonify, render_template, flash, redirect, request, session, url_for
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import make_response
from datetime import datetime
from functools import wraps
from fpdf import FPDF
import requests
import logging
import secrets
import smtplib
import qrcode
import time
import json
import os

router = Blueprint("router", __name__)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@router.route("/")
def home():
    return render_template("index.html")


def requiere_iniciar(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            flash("Por favor inicie sesión para acceder", "danger")
            return redirect(url_for("router.iniciar_sesion"))
        return f(*args, **kwargs)

    return decorated_function


@router.route("/verificar_sesion")
def verificar_sesion():
    return jsonify({"sesion_activa": "user" in session})


@router.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        try:
            campos_requeridos = [
                "nombres",
                "apellidos",
                "tipo_identificacion",
                "numero_identificacion",
                "correo",
                "password",
                "fecha_nacimiento",
            ]
            for campo in campos_requeridos:
                if not request.form.get(campo):
                    flash(f"El campo {campo} es requerido", "danger")
                    return render_template("registro_usuario.html")
            datos_registro = {
                "nombres": request.form["nombres"],
                "apellidos": request.form["apellidos"],
                "tipo_identificacion": request.form["tipo_identificacion"],
                "num_identificacion": request.form["numero_identificacion"],
                "fecha_nacimiento": request.form["fecha_nacimiento"],
                "correo": request.form["correo"],
                "genero": "No_definido",
                "direccion": "",
                "telefono": "",
                "saldo_disponible": 0.0,
                "usuario": request.form["correo"],
                "clave": request.form["password"],
            }
            r = requests.post(
                "http://localhost:8099/api/persona/guardar",
                headers={"Content-Type": "application/json"},
                json=datos_registro,
            )
            if r.status_code == 200:
                flash("Registro exitoso", "success")
                return redirect(url_for("router.iniciar_sesion"))
            else:
                flash(f"Error en el registro: {r.json().get('msg', 'Error desconocido')}", "danger")
        except Exception as e:
            flash(f"Error en el registro: {str(e)}", "danger")
            logger.error(f"Error en el registro: {str(e)}")
    return render_template("registro_usuario.html")


@router.route("/iniciar_sesion", methods=["GET", "POST"])
def iniciar_sesion():
    if "user" in session:
        redirect_url = session.pop("redirect_after_login", None)
        if redirect_url:
            return redirect(redirect_url)
        if session["user"].get("tipo_cuenta") == "Administrador":
            return redirect(url_for("router.administrador"))
        return redirect(url_for("router.cliente"))
    if request.method == "POST":
        correo = request.form.get("correo")
        contrasenia = request.form.get("contrasenia")
        try:
            response = requests.get("http://localhost:8099/api/persona/lista")
            if response.status_code == 200:
                personas = response.json().get("personas", [])
                for persona in personas:
                    cuenta = persona.get("cuenta", {})
                    if cuenta.get("correo") == correo and cuenta.get("contrasenia") == contrasenia:
                        session["user"] = {
                            "id": persona.get("id_persona"),
                            "nombre": persona.get("nombre"),
                            "apellido": persona.get("apellido"),
                            "tipo_cuenta": cuenta.get("tipo_cuenta"),
                            "correo": cuenta.get("correo"),
                        }
                        redirect_url = session.pop("redirect_after_login", None)
                        if redirect_url:
                            return redirect(redirect_url)
                        if cuenta.get("tipo_cuenta") == "Administrador":
                            flash("Bienvenido Administrador!", "success")
                            return redirect(url_for("router.administrador"))
                        else:
                            flash("Bienvenido!", "success")
                            return redirect(url_for("router.cliente"))
                flash("Correo o contraseña incorrectos", "danger")
                return redirect(url_for("router.iniciar_sesion"))
            flash("Error al verificar credenciales", "danger")
            return redirect(url_for("router.iniciar_sesion"))
        except requests.exceptions.RequestException as e:
            flash("Error de conexión", "danger")
            return redirect(url_for("router.iniciar_sesion"))
    return render_template("iniciar_sesion.html")


@router.route("/logout")
def cerrar_sesion():
    session.clear()
    flash("Has cerrado sesión exitosamente", "success")
    return redirect(url_for("router.iniciar_sesion"))


@router.route("/recuperar-contrasenia", methods=["GET", "POST"])
def recuperar_contrasenia():
    if request.method == "POST":
        correo = request.form.get("correo")
        try:
            response = requests.get("http://localhost:8099/api/persona/lista")
            if response.status_code == 200:
                personas = response.json().get("personas", [])
                persona = next((p for p in personas if p.get("correo") == correo), None)
                if persona:
                    token = secrets.token_urlsafe(32)
                    session[f"reset_token_{token}"] = persona["id_persona"]
                    session[f"reset_token_{token}_expiry"] = int(time.time()) + 3600
                    reset_url = url_for("router.cambiar_contrasenia", token=token, _external=True)
                    print("\nURL para cambiar contraseña:")
                    print(f"Token: {token}")
                    print(f"URL completa: {reset_url}\n")
                    enviar_al_correo(correo, reset_url)
                    return redirect(url_for("router.correo_enviado"))
                flash("No se encontró una cuenta con ese correo", "warning")
            else:
                flash("Error al verificar el correo", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
    return render_template("utiles/rc_recuperar_contrasenia.html")


@router.route("/correo-enviado")
def correo_enviado():
    return render_template("utiles/rc_correo_enviado.html")


@router.route("/cambiar-contrasenia/<token>", methods=["GET", "POST"])
def cambiar_contrasenia(token):
    persona_id = session.get(f"reset_token_{token}")
    expiry = session.get(f"reset_token_{token}_expiry")
    if not persona_id or not expiry or int(time.time()) > expiry:
        flash("El enlace para restablecer la contraseña es inválido o ha expirado", "danger")
        return redirect(url_for("router.recuperar_contrasenia"))
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if not password or not confirm_password:
            flash("Por favor ingrese la contraseña", "danger")
            return redirect(url_for("router.cambiar_contrasenia", token=token))
        if password != confirm_password:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for("router.cambiar_contrasenia", token=token))
        try:
            response = requests.get(f"http://localhost:8099/api/persona/lista/{persona_id}")
            if response.status_code == 200:
                persona_data = response.json()["persona"]
                update_data = {
                    "id_persona": int(persona_id),
                    "nombres": persona_data["nombre"],
                    "apellidos": persona_data["apellido"],
                    "tipo_identificacion": persona_data["tipo_identificacion"],
                    "num_identificacion": persona_data["numero_identificacion"],
                    "fecha_nacimiento": persona_data["fecha_nacimiento"],
                    "direccion": persona_data.get("direccion", ""),
                    "telefono": persona_data["telefono"],
                    "correo": persona_data["correo"],
                    "genero": persona_data["genero"],
                    "metodo_pago": persona_data["metodo_pago"],
                    "cuenta": {
                        "id_cuenta": persona_data["cuenta"]["id_cuenta"],
                        "correo": persona_data["cuenta"]["correo"],
                        "clave": password,
                        "tipo_cuenta": persona_data["cuenta"]["tipo_cuenta"],
                        "estado_cuenta": persona_data["cuenta"]["estado_cuenta"],
                    },
                }
                update_response = requests.put(
                    "http://localhost:8099/api/persona/actualizar", json=update_data
                )
                if update_response.status_code == 200:
                    session.pop(f"reset_token_{token}", None)
                    session.pop(f"reset_token_{token}_expiry", None)
                    flash("Contraseña actualizada exitosamente", "success")
                    return redirect(url_for("router.iniciar_sesion"))
                else:
                    flash("Error al actualizar la contraseña", "danger")
            else:
                flash("Error al obtener los datos de la persona", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
    return render_template("utiles/rc_cambiar_contrasenia.html")


def enviar_al_correo(to_email, reset_url):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "tu_correo@gmail.com"
    sender_password = "tu_contraseña_app"
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = "Recuperación de Contraseña"
    body = f"""
    Has solicitado restablecer tu contraseña.
    
    Para continuar, haz clic en el siguiente enlace:
    {reset_url}
    
    Si no solicitaste este cambio, ignora este correo.
    
    El enlace expirará en 1 hora.
    """
    msg.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Error enviando email: {str(e)}")


@router.route("/perfil", methods=["GET", "POST"])
@requiere_iniciar
def perfil():
    if request.method == "POST":
        try:
            r_usuario = requests.get(
                f"http://localhost:8099/api/persona/lista/{session['user']['id']}"
            )
            datos_actuales = r_usuario.json().get("persona", {})
            fecha_str = request.form.get("fecha_nacimiento")
            if fecha_str:
                fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d")
                fecha_formateada = fecha_obj.strftime("%d/%m/%Y")
            else:
                fecha_formateada = datos_actuales.get("fecha_nacimiento")
            datos_actualizacion = {
                "id_persona": session["user"]["id"],
                "nombres": request.form.get("nombres"),
                "apellidos": request.form.get("apellidos"),
                "direccion": request.form.get("direccion", ""),
                "tipo_identificacion": request.form.get("tipo_identificacion"),
                "num_identificacion": request.form.get("num_identificacion"),
                "fecha_nacimiento": fecha_formateada,
                "correo": request.form.get("correo"),
                "telefono": request.form.get("telefono", ""),
                "genero": request.form.get("genero", datos_actuales.get("genero", "No_definido")),
                "metodo_pago": datos_actuales.get("metodo_pago", "No_definido"),
                "saldo_disponible": datos_actuales.get("saldo_disponible", 0),
                "cuenta": {
                    "id_cuenta": datos_actuales.get("cuenta", {}).get("id_cuenta"),
                    "correo": request.form.get("correo"),
                    "contrasenia": (
                        request.form.get("contrasenia")
                        if request.form.get("contrasenia")
                        else datos_actuales.get("cuenta", {}).get("contrasenia")
                    ),
                    "tipo_cuenta": datos_actuales.get("cuenta", {}).get("tipo_cuenta", "Cliente"),
                    "estado_cuenta": datos_actuales.get("cuenta", {}).get(
                        "estado_cuenta", "Activo"
                    ),
                },
            }
            r = requests.put(
                "http://localhost:8099/api/persona/actualizar", json=datos_actualizacion
            )
            if r.status_code == 200:
                session["user"].update(
                    {
                        "nombre": request.form.get("nombres"),
                        "apellido": request.form.get("apellidos"),
                        "correo": request.form.get("correo"),
                    }
                )
                flash("Perfil actualizado exitosamente", "success")
            else:
                flash(
                    f"Error al actualizar el perfil: {r.json().get('msg', 'Error desconocido')}",
                    "error",
                )
        except Exception as e:
            flash(f"Error en el primer try: {str(e)}", "error")
        return redirect(url_for("router.perfil"))
    try:
        r = requests.get(f"http://localhost:8099/api/persona/lista/{session['user']['id']}")
        if r.status_code == 200:
            datos_usuario = r.json().get("persona", {})
            return render_template(
                "perfil.html",
                usuario=datos_usuario,
                tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
                generos=["Masculino", "Femenino", "Otro", "No_definido"],
                metodos_pago=["Efectivo", "Tarjeta", "Transferencia", "No_definido"],
            )
        else:
            flash("Error al cargar los datos del usuario", "error")
    except Exception as e:
        flash(f"Error al cargar el perfil: {str(e)}", "error")
    if session.get("user", {}).get("tipo_cuenta") == "Administrador":
        return redirect(url_for("router.administrador"))
    return redirect(url_for("router.cliente"))


@router.route("/cliente")
@requiere_iniciar
def cliente():
    try:
        usuario_id = session.get("user", {}).get("id")
        if not usuario_id:
            flash("Debe iniciar sesión", "warning")
            return redirect(url_for("router.iniciar_sesion"))
        response_persona = requests.get(f"http://localhost:8099/api/persona/lista/{usuario_id}")
        if response_persona.status_code != 200:
            flash("Error al obtener datos del usuario", "error")
            return redirect(url_for("router.iniciar_sesion"))
        persona_data = response_persona.json().get("persona", {})
        response_boletos = requests.get("http://localhost:8099/api/boleto/lista")
        boletos = response_boletos.json().get("boletos", [])
        boletos_usuario = [
            b for b in boletos if b.get("persona", {}).get("id_persona") == usuario_id
        ]
        fecha_actual = datetime.now()
        viajes_realizados = []
        boletos_activos = []
        for b in boletos_usuario:
            if b.get("estado_boleto") == "Vendido":
                try:
                    fecha_salida = datetime.strptime(
                        b.get("turno", {}).get("fecha_salida"), "%d/%m/%Y"
                    )
                    if fecha_salida < fecha_actual:
                        viajes_realizados.append(b)
                    else:
                        boletos_activos.append(b)
                except Exception:
                    continue
        stats = {
            "viajes_realizados": len(viajes_realizados),
            "destinos_visitados": len(
                {
                    b.get("turno", {}).get("horario", {}).get("ruta", {}).get("destino")
                    for b in viajes_realizados
                    if b
                }
            ),
            "boletos_activos": len(boletos_activos),
            "rutas_favoritas": len(
                {
                    b.get("turno", {}).get("horario", {}).get("ruta", {}).get("id_ruta")
                    for b in boletos_usuario
                    if b.get("estado_boleto") == "Vendido"
                }
            ),
        }
        historial_viajes = []
        proximos_viajes = []
        for b in boletos_usuario:
            try:
                fecha_salida = datetime.strptime(b.get("turno", {}).get("fecha_salida"), "%d/%m/%Y")
                datos_viaje = {
                    "fecha_compra": b.get("fecha_compra"),
                    "fecha_salida": b.get("turno", {}).get("fecha_salida"),
                    "hora_salida": b.get("turno", {}).get("horario", {}).get("hora_salida"),
                    "destino": f"{b.get('turno', {}).get('horario', {}).get('ruta', {}).get('origen')} - "
                    f"{b.get('turno', {}).get('horario', {}).get('ruta', {}).get('destino')}",
                    "numero_asiento": b.get("numero_asiento"),
                    "bus_numero": b.get("turno", {})
                    .get("horario", {})
                    .get("ruta", {})
                    .get("bus", {})
                    .get("numero_bus"),
                    "cooperativa": b.get("turno", {})
                    .get("horario", {})
                    .get("ruta", {})
                    .get("bus", {})
                    .get("cooperativa", {})
                    .get("nombre"),
                    "estado": b.get("estado_boleto"),
                    "precio_final": b.get("precio_final"),
                    "id": b.get("id_boleto"),
                }
                if fecha_salida < fecha_actual:
                    historial_viajes.append(datos_viaje)
                else:
                    if b.get("estado_boleto") == "Vendido":
                        proximos_viajes.append(datos_viaje)
            except Exception as e:
                continue
        proximos_viajes = sorted(
            proximos_viajes, key=lambda x: datetime.strptime(x["fecha_salida"], "%d/%m/%Y")
        )
        usuario = {
            "nombre": persona_data.get("nombre", "Usuario"),
            "apellido": persona_data.get("apellido", ""),
        }
        return render_template(
            "panel_cliente.html",
            stats=stats,
            historial_viajes=historial_viajes,
            proximos_viajes=proximos_viajes,
            usuario=usuario,
        )
    except Exception as e:
        flash(f"Error al cargar el dashboard: {str(e)}", "danger")
        return redirect(url_for("router.iniciar_sesion"))


@router.route("/administrador")
@requiere_iniciar
def administrador():
    if session.get("user", {}).get("tipo_cuenta") != "Administrador":
        flash("Acceso no autorizado", "danger")
        return redirect(url_for("router.cliente"))
    try:
        r_personas = requests.get("http://localhost:8099/api/persona/lista")
        r_boletos = requests.get("http://localhost:8099/api/boleto/lista")
        r_buses = requests.get("http://localhost:8099/api/bus/lista")
        r_rutas = requests.get("http://localhost:8099/api/ruta/lista")
        r_turnos = requests.get("http://localhost:8099/api/turno/lista")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            requested_data = request.args.get("data")
            if requested_data == "personas":
                return jsonify(r_personas.json())
            elif requested_data == "boletos":
                return jsonify(r_boletos.json())
            elif requested_data == "buses":
                return jsonify(r_buses.json())
            elif requested_data == "rutas":
                return jsonify(r_rutas.json())
        personas = r_personas.json().get("personas", [])
        boletos = r_boletos.json().get("boletos", [])
        buses = r_buses.json().get("buses", [])
        rutas = r_rutas.json().get("rutas", [])
        turnos = r_turnos.json().get("turnos", [])
        stats = {
            "total_usuarios": len(personas),
            "total_ventas": len(boletos),
            "total_buses": len(buses),
            "total_rutas": len(rutas),
            "ingresos_totales": sum(float(b.get("precio_final", 0)) for b in boletos),
            "viajes_activos": len([t for t in turnos if t.get("estado_turno") == "Activo"]),
        }
        ultimas_ventas = []
        for b in sorted(boletos, key=lambda x: x.get("fecha_compra", ""), reverse=True)[:5]:
            persona = next(
                (
                    p
                    for p in personas
                    if p.get("id_persona") == b.get("persona", {}).get("id_persona")
                ),
                {},
            )
            turno = next(
                (t for t in turnos if t.get("id_turno") == b.get("turno", {}).get("id_turno")), {}
            )
            ultimas_ventas.append(
                {
                    "id": b.get("id_boleto"),
                    "cliente": f"{persona.get('nombre', '')} {persona.get('apellido', '')}",
                    "ruta": f"{turno.get('horario', {}).get('ruta', {}).get('origen')} - {turno.get('horario', {}).get('ruta', {}).get('destino')}",
                    "fecha": b.get("fecha_compra"),
                    "estado": b.get("estado_boleto"),
                    "precio": b.get("precio_final"),
                }
            )
        fecha_actual = datetime.now()
        proximas_salidas = []
        for t in sorted(turnos, key=lambda x: x.get("fecha_salida", ""))[:5]:
            try:
                fecha_turno = datetime.strptime(t.get("fecha_salida"), "%d/%m/%Y")
                if fecha_turno >= fecha_actual:
                    ruta = next(
                        (
                            r
                            for r in rutas
                            if r.get("id_ruta")
                            == t.get("horario", {}).get("ruta", {}).get("id_ruta")
                        ),
                        {},
                    )
                    bus = next(
                        (b for b in buses if b.get("id_bus") == ruta.get("bus", {}).get("id_bus")),
                        {},
                    )
                    boletos_turno = [
                        b
                        for b in boletos
                        if b.get("turno", {}).get("id_turno") == t.get("id_turno")
                    ]
                    asientos_ocupados = len(boletos_turno)
                    proximas_salidas.append(
                        {
                            "id": t.get("id_turno"),
                            "ruta": f"{ruta.get('origen')} - {ruta.get('destino')}",
                            "fecha": t.get("fecha_salida"),
                            "hora": t.get("horario", {}).get("hora_salida"),
                            "bus": bus.get("numero_bus"),
                            "asientos_disponibles": bus.get("capacidad_pasajeros", 0)
                            - asientos_ocupados,
                        }
                    )
            except ValueError:
                continue
        estado_buses = []
        for b in buses:
            turnos_bus = [
                t
                for t in turnos
                if t.get("horario", {}).get("ruta", {}).get("bus", {}).get("id_bus")
                == b.get("id_bus")
            ]
            estado = "En servicio" if turnos_bus else "Disponible"
            estado_buses.append(
                {
                    "id": b.get("id_bus"),
                    "numero": b.get("numero_bus"),
                    "placa": b.get("placa"),
                    "estado": estado,
                    "estado_clase": "success" if estado == "En servicio" else "info",
                    "ruta": (
                        f"{turnos_bus[0].get('horario', {}).get('ruta', {}).get('origen')} - {turnos_bus[0].get('horario', {}).get('ruta', {}).get('destino')}"
                        if turnos_bus
                        else "Sin ruta asignada"
                    ),
                }
            )
        return render_template(
            "panel_administrador.html",
            stats=stats,
            ultimas_ventas=ultimas_ventas,
            proximas_salidas=proximas_salidas,
            estado_buses=estado_buses,
        )
    except Exception as e:
        flash(f"Error al cargar los datos: {str(e)}", "danger")
        return render_template("panel_administrador.html")


# Agrega estos endpoints al archivo route.py


@router.route("/api/persona/lista")
def api_personas():
    try:
        r = requests.get("http://localhost:8099/api/persona/lista")
        if r.status_code == 200:
            return jsonify(r.json())
        return jsonify({"error": "Error al obtener personas"}), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@router.route("/api/boleto/lista")
def api_boletos():
    try:
        r = requests.get("http://localhost:8099/api/boleto/lista")
        if r.status_code == 200:
            return jsonify(r.json())
        return jsonify({"error": "Error al obtener boletos"}), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@router.route("/api/bus/lista")
def api_buses():
    try:
        r = requests.get("http://localhost:8099/api/bus/lista")
        if r.status_code == 200:
            return jsonify(r.json())
        return jsonify({"error": "Error al obtener buses"}), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@router.route("/api/ruta/lista")
def api_rutas():
    try:
        r = requests.get("http://localhost:8099/api/ruta/lista")
        if r.status_code == 200:
            return jsonify(r.json())
        return jsonify({"error": "Error al obtener rutas"}), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@router.route("/index.html")
def index():
    return render_template("index.html")


@router.route("/about.html")
def about():
    return render_template("about.html")


@router.route("/blog.html")
def blog():
    return render_template("blog.html")


@router.route("/contact.html")
def contact():
    return render_template("contact.html")


@router.route("/destination.html")
def destination():
    return render_template("destination.html")


@router.route("/guide.html")
def guide():
    return render_template("guide.html")


@router.route("/package.html")
def package():
    return render_template("package.html")


@router.route("/service.html")
def service():
    return render_template("service.html")


@router.route("/single.html")
def single_blog():
    return render_template("single.html")


@router.route("/testimonial.html")
def testimonials():
    return render_template("testimonial.html")


@router.route("/cooperativa/lista")
def lista_cooperativa():
    try:
        r = requests.get("http://localhost:8099/api/cooperativa/lista")
        if r.status_code == 200:
            try:
                data = r.json()
                return render_template(
                    "crud/cooperativa/cooperativa.html", lista=data.get("cooperativas", [])
                )
            except json.JSONDecodeError as je:
                flash("Error al decodificar la respuesta del servidor", "error")
                return render_template("crud/cooperativa/cooperativa.html", lista=[])
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/cooperativa.html", lista=[])
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/cooperativa/cooperativa.html", lista=[])


@router.route("/cooperativa/crear", methods=["GET", "POST"])
def crear_cooperativa():
    if request.method == "POST":
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                "nombre": request.form["nombre"],
                "ruc": request.form["ruc"],
                "direccion": request.form["direccion"],
                "telefono": request.form["telefono"],
                "correo_empresarial": request.form["correo_empresarial"],
            }
            r = requests.post(
                "http://localhost:8099/api/cooperativa/guardar",
                headers=headers,
                json=data,
                timeout=5,
            )
            if r.status_code == 200:
                flash("Cooperativa creada correctamente", "success")
                return redirect(url_for("router.lista_cooperativa"))
            else:
                error_msg = f"Error {r.status_code}: {r.text}"
                logger.error(error_msg)
                flash(error_msg, "error")
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar al servidor. Verifique que el servidor Java esté ejecutándose en el puerto 8099"
            logger.error(error_msg)
            flash(error_msg, "error")
        except requests.exceptions.RequestException as e:
            error_msg = f"Error en la petición: {str(e)}"
            logger.error(error_msg)
            flash(error_msg, "error")
    return render_template("crud/cooperativa/cooperativa_crear.html")


@router.route("/cooperativa/editar/<int:id>", methods=["GET", "POST"])
def editar_cooperativa(id):
    if request.method == "POST":
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                "id": id,
                "nombre": request.form["nombre"],
                "ruc": request.form["ruc"],
                "direccion": request.form["direccion"],
                "telefono": request.form["telefono"],
                "correo_empresarial": request.form["correo_empresarial"],
            }
            r = requests.put(
                "http://localhost:8099/api/cooperativa/actualizar", headers=headers, json=data
            )
            if r.status_code == 200:
                flash("Cooperativa actualizada correctamente", "success")
                return redirect(url_for("router.lista_cooperativa"))
            else:
                error_msg = f"Error {r.status_code}: {r.text}"
                logger.error(error_msg)
                flash(error_msg, "error")
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión: {str(e)}"
            logger.error(error_msg)
            flash(error_msg, "error")
    try:
        r = requests.get(f"http://localhost:8099/api/cooperativa/lista/{id}")
        if r.status_code == 200:
            cooperativa = r.json().get("cooperativa")
            return render_template(
                "crud/cooperativa/cooperativa_editar.html", cooperativa=cooperativa
            )
        else:
            flash("No se encontró la cooperativa", "error")
            return redirect(url_for("router.lista_cooperativa"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router.lista_cooperativa"))


@router.route("/cooperativa/eliminar/<int:id>", methods=["POST"])
def eliminar_cooperativa(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/cooperativa/eliminar/{id}")
        if r.status_code == 200:
            flash("Cooperativa eliminada correctamente", "success")
        else:
            error_msg = f"Error del servidor: {r.status_code} - {r.text}"
            logger.error(error_msg)
            flash(error_msg, "error")
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión: {str(e)}"
        logger.error(error_msg)
        flash(error_msg, "error")
    return redirect(url_for("router.lista_cooperativa"))


@router.route("/bus/lista")
def lista_bus():
    try:
        r = requests.get("http://localhost:8099/api/bus/lista")
        if r.status_code == 200:
            try:
                data = r.json()
                return render_template("crud/bus/bus.html", lista=data.get("buses", []))
            except json.JSONDecodeError as je:
                flash("Error al decodificar la respuesta del servidor", "error")
                return render_template("crud/bus/bus.html", lista=[])
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/bus/bus.html", lista=[])
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/bus/bus.html", lista=[])


@router.route("/bus/crear", methods=["GET", "POST"])
def crear_bus():
    if request.method == "POST":
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                "numero_bus": request.form["numero_bus"],
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
                return redirect(url_for("router.lista_bus"))
            else:
                error_msg = f"Error {r.status_code}: {r.text}"
                logger.error(error_msg)
                flash(error_msg, "error")
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar al servidor"
            logger.error(error_msg)
            flash(error_msg, "error")
        except requests.exceptions.RequestException as e:
            error_msg = f"Error en la petición: {str(e)}"
            logger.error(error_msg)
            flash(error_msg, "error")
    try:
        r = requests.get("http://localhost:8099/api/cooperativa/lista")
        cooperativas = r.json().get("cooperativas", []) if r.status_code == 200 else []
    except:
        cooperativas = []
        flash("Error al cargar las cooperativas", "error")
    return render_template("crud/bus/bus_crear.html", cooperativas=cooperativas)


@router.route("/bus/editar/<int:id>", methods=["GET", "POST"])
def editar_bus(id):
    if request.method == "POST":
        try:
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
                return redirect(url_for("router.lista_bus"))
            else:
                error_msg = f"Error {r.status_code}: {r.text}"
                logger.error(error_msg)
                flash(error_msg, "error")
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión: {str(e)}"
            logger.error(error_msg)
            flash(error_msg, "error")
    try:
        r = requests.get(f"http://localhost:8099/api/bus/lista/{id}")
        bus = r.json().get("bus") if r.status_code == 200 else None
        r_coop = requests.get("http://localhost:8099/api/cooperativa/lista")
        cooperativas = r_coop.json().get("cooperativas", []) if r_coop.status_code == 200 else []
        if bus:
            return render_template("crud/bus/bus_editar.html", bus=bus, cooperativas=cooperativas)
        else:
            flash("No se encontró el bus", "error")
            return redirect(url_for("router.lista_bus"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router.lista_bus"))


@router.route("/bus/eliminar/<int:id>", methods=["POST"])
def eliminar_bus(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/bus/eliminar/{id}")
        if r.status_code == 200:
            flash("Bus eliminado correctamente", "success")
        else:
            error_msg = f"Error del servidor: {r.status_code} - {r.text}"
            logger.error(error_msg)
            flash(error_msg, "error")
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión: {str(e)}"
        logger.error(error_msg)
        flash(error_msg, "error")
    return redirect(url_for("router.lista_bus"))


@router.route("/ruta/lista")
def lista_ruta():
    try:
        r = requests.get("http://localhost:8099/api/ruta/lista")
        if r.status_code == 200:
            try:
                data = r.json()
                origenes = set()
                destinos = set()
                for ruta in data.get("rutas", []):
                    origenes.add(ruta.get("origen", "No especificado"))
                    destinos.add(ruta.get("destino", "No especificado"))
                print("Orígenes disponibles:", list(origenes))
                print("Destinos disponibles:", list(destinos))
                return render_template("crud/ruta/ruta.html", lista=data.get("rutas", []))
            except json.JSONDecodeError as je:
                flash("Error al decodificar la respuesta del servidor", "error")
                return render_template("crud/ruta/ruta.html", lista=[])
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/ruta/ruta.html", lista=[])
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/ruta/ruta.html", lista=[])


@router.route("/ruta/crear", methods=["GET", "POST"])
def crear_ruta():
    if request.method == "POST":
        try:
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
            }
            r = requests.post(
                "http://localhost:8099/api/ruta/guardar", headers=headers, json=data, timeout=5
            )
            if r.status_code == 200:
                flash("Ruta creada correctamente", "success")
                return redirect(url_for("router.lista_ruta"))
            else:
                error_msg = f"Error al crear la ruta: {r.text}"
                logger.error(error_msg)
                flash(error_msg, "error")
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar al servidor"
            logger.error(error_msg)
            flash(error_msg, "error")
        except requests.exceptions.RequestException as e:
            error_msg = f"Error en la petición: {str(e)}"
            logger.error(error_msg)
            flash(error_msg, "error")
    try:
        r = requests.get("http://localhost:8099/api/bus/lista")
        buses = r.json().get("buses", []) if r.status_code == 200 else []
    except:
        buses = []
        flash("Error al cargar los buses", "error")
    return render_template("crud/ruta/ruta_crear.html", buses=buses)


@router.route("/ruta/editar/<int:id>", methods=["GET", "POST"])
def editar_ruta(id):
    if request.method == "POST":
        try:
            headers = {"Content-Type": "application/json"}
            data = {
                "id_ruta": id,
                "origen": request.form["origen"],
                "destino": request.form["destino"],
                "precio_unitario": request.form.get("precio_unitario"),
                "distancia": int(request.form["distancia"]),
                "tiempo_estimado": request.form["tiempo_estimado"],
                "estado_ruta": request.form["estado_ruta"],
                "bus": {
                    "id_bus": int(request.form["bus_id"]),
                },
            }
            r = requests.put(
                "http://localhost:8099/api/ruta/actualizar", headers=headers, json=data
            )
            if r.status_code == 200:
                flash("Ruta actualizada correctamente", "success")
                return redirect(url_for("router.lista_ruta"))
            else:
                error_msg = f"Error al actualizar la ruta: {r.text}"
                flash(error_msg, "error")
        except requests.exceptions.RequestException as e:
            error_msg = f"Error en la petición: {str(e)}"
            flash(error_msg, "error")
            return redirect(url_for("router.lista_ruta"))
    try:
        r = requests.get(f"http://localhost:8099/api/ruta/lista/{id}")
        ruta = r.json().get("ruta") if r.status_code == 200 else None
        r_bus = requests.get("http://localhost:8099/api/bus/lista")
        buses = r_bus.json().get("buses", []) if r_bus.status_code == 200 else []
        if ruta:
            return render_template("crud/ruta/ruta_editar.html", ruta=ruta, buses=buses)
        else:
            flash("No se encontró la ruta", "error")
            return redirect(url_for("router.lista_ruta"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router.lista_ruta"))


@router.route("/ruta/eliminar/<int:id>", methods=["POST"])
def eliminar_ruta(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/ruta/eliminar/{id}")
        if r.status_code == 200:
            flash("Ruta eliminada correctamente", "success")
        else:
            error_msg = f"Error del servidor: {r.status_code}"
            logger.error(error_msg)
            flash(error_msg, "error")
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión: {str(e)}"
        logger.error(error_msg)
        flash(error_msg, "error")
    return redirect(url_for("router.lista_ruta"))


@router.route("/horario/lista")
def lista_horario():
    try:
        r = requests.get("http://localhost:8099/api/horario/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template("crud/horario/horario.html", lista=data.get("horarios", []))
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/horario/horario.html", lista=[])
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/horario/horario.html", lista=[])


@router.route("/horario/crear", methods=["GET", "POST"])
def crear_horario():
    if request.method == "POST":
        try:
            data = {
                "hora_salida": request.form["hora_salida"],
                "hora_llegada": request.form["hora_llegada"],
                "estado_horario": request.form["estado_horario"],
                "ruta": {"id_ruta": int(request.form["ruta_id"])},
            }
            r = requests.post(
                "http://localhost:8099/api/horario/guardar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Horario creado correctamente", "success")
                return redirect(url_for("router.lista_horario"))
            else:
                flash(f"Error al crear el horario: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    try:
        r = requests.get("http://localhost:8099/api/ruta/lista")
        rutas = r.json().get("rutas", []) if r.status_code == 200 else []
    except:
        rutas = []
        flash("Error al cargar las rutas", "error")
    return render_template("crud/horario/horario_crear.html", rutas=rutas)


@router.route("/horario/editar/<int:id>", methods=["GET", "POST"])
def editar_horario(id):
    if request.method == "POST":
        try:
            data = {
                "id_horario": id,
                "hora_salida": request.form["hora_salida"],
                "hora_llegada": request.form["hora_llegada"],
                "estado_horario": request.form["estado_horario"],
                "ruta": {"id_ruta": int(request.form["ruta_id"])},
            }
            r = requests.put(
                "http://localhost:8099/api/horario/actualizar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Horario actualizado correctamente", "success")
                return redirect(url_for("router.lista_horario"))
            else:
                flash(f"Error al actualizar: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    try:
        r = requests.get(f"http://localhost:8099/api/horario/lista/{id}")
        horario = r.json().get("horario") if r.status_code == 200 else None
        r_rutas = requests.get("http://localhost:8099/api/ruta/lista")
        rutas = r_rutas.json().get("rutas", []) if r_rutas.status_code == 200 else []
        if horario:
            return render_template("crud/horario/horario_editar.html", horario=horario, rutas=rutas)
        else:
            flash("Horario no encontrado", "error")
            return redirect(url_for("router.lista_horario"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router.lista_horario"))


@router.route("/horario/eliminar/<int:id>", methods=["POST"])
def eliminar_horario(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/horario/eliminar/{id}")
        if r.status_code == 200:
            flash("Horario eliminado correctamente", "success")
        else:
            flash("Error al eliminar el horario", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router.lista_horario"))


@router.route("/frecuencia/lista")
def lista_frecuencia():
    try:
        r = requests.get("http://localhost:8099/api/frecuencia/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template(
                "crud/frecuencia/frecuencia.html", lista=data.get("frecuencias", [])
            )
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/frecuencia/frecuencia.html", lista=[])
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/frecuencia/frecuencia.html", lista=[])


@router.route("/frecuencia/crear", methods=["GET", "POST"])
def crear_frecuencia():
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
                return redirect(url_for("router.lista_frecuencia"))
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
    return render_template("crud/frecuencia/frecuencia_crear.html", horarios=horarios)


@router.route("/frecuencia/editar/<int:id>", methods=["GET", "POST"])
def editar_frecuencia(id):
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
                return redirect(url_for("router.lista_frecuencia"))
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
                "crud/frecuencia/frecuencia_editar.html", frecuencia=frecuencia, horarios=horarios
            )
        else:
            flash("Frecuencia no encontrada", "error")
            return redirect(url_for("router.lista_frecuencia"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router.lista_frecuencia"))


@router.route("/frecuencia/eliminar/<int:id>", methods=["POST"])
def eliminar_frecuencia(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/frecuencia/eliminar/{id}")
        if r.status_code == 200:
            flash("Frecuencia eliminada correctamente", "success")
        else:
            flash("Error al eliminar la frecuencia", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router.lista_frecuencia"))


@router.route("/persona/lista")
def lista_persona():
    try:
        r = requests.get("http://localhost:8099/api/persona/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template("crud/persona/persona.html", lista=data.get("personas", []))
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/persona/persona.html", lista=[])
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/persona/persona.html", lista=[])


@router.route("/persona/crear", methods=["GET", "POST"])
def crear_persona():
    if request.method == "POST":
        try:
            data = {
                "nombres": request.form["nombres"],
                "apellidos": request.form["apellidos"],
                "tipo_identificacion": request.form["tipo_identificacion"],
                "num_identificacion": request.form["num_identificacion"],
                "fecha_nacimiento": request.form["fecha_nacimiento"],
                "telefono": request.form["telefono"],
                "correo": request.form["correo"],
                "genero": request.form["genero"],
                "direccion": request.form.get("direccion", ""),
                "saldo_disponible": "0.0",
                "usuario": request.form["usuario"],
                "clave": request.form["clave"],
            }
            metodo_pago = request.form.get("metodo_pago")
            if metodo_pago and metodo_pago != "ninguno":
                campos_pago = [
                    "saldo",
                    "numero_tarjeta",
                    "titular",
                    "fecha_vencimiento",
                    "codigo_seguridad",
                ]
                if all(request.form.get(campo) for campo in campos_pago):
                    data.update(
                        {
                            "metodo_pago": metodo_pago,
                            "saldo": request.form["saldo"],
                            "numero_tarjeta": request.form["numero_tarjeta"],
                            "titular": request.form["titular"],
                            "fecha_vencimiento": request.form["fecha_vencimiento"],
                            "codigo_seguridad": request.form["codigo_seguridad"],
                        }
                    )
            r = requests.post(
                "http://localhost:8099/api/persona/guardar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Persona creada correctamente", "success")
                return redirect(url_for("router.lista_persona"))
            else:
                flash(f"Error al crear: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
        except ValueError as e:
            flash(f"Error en los datos: {str(e)}", "error")
    return render_template(
        "crud/persona/persona_crear.html",
        tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
        generos=["Masculino", "Femenino", "Otro"],
        metodos_pago=["ninguno", "Tarjeta_credito", "Tarjeta_debito"],
    )


@router.route("/persona/editar/<int:id>", methods=["GET", "POST"])
def editar_persona(id):
    if request.method == "POST":
        try:
            data = {
                "id_persona": id,
                "nombres": request.form["nombres"],
                "apellidos": request.form["apellidos"],
                "tipo_identificacion": request.form["tipo_identificacion"],
                "num_identificacion": request.form["num_identificacion"],
                "fecha_nacimiento": request.form["fecha_nacimiento"],
                "telefono": request.form.get("telefono", ""),
                "correo": request.form["correo"],
                "genero": request.form["genero"],
                "direccion": request.form.get("direccion", ""),
                "saldo_disponible": float(request.form.get("saldo_disponible", "0.0")),
                "cuenta": {
                    "id_cuenta": int(request.form["cuenta_id"]),
                    "correo": request.form["cuenta_correo"],
                    "tipo_cuenta": request.form["tipo_cuenta"],
                    "estado_cuenta": request.form["estado_cuenta"],
                },
            }
            if request.form.get("cuenta_clave"):
                data["cuenta"]["contrasenia"] = request.form["cuenta_clave"]
            if request.form.get("metodo_pago"):
                metodo_pago_id = request.form.get("metodo_pago_id")
                data["metodo_pago"] = {
                    "id_pago": (
                        int(metodo_pago_id)
                        if metodo_pago_id and metodo_pago_id.isdigit() and metodo_pago_id != "0"
                        else None
                    ),
                    "saldo": float(request.form.get("saldo", 0.0)),
                    "numero_tarjeta": request.form.get("numero_tarjeta", ""),
                    "titular": request.form.get("titular", ""),
                    "fecha_vencimiento": request.form.get("fecha_vencimiento", ""),
                    "codigo_seguridad": request.form.get("codigo_seguridad", ""),
                    "opcion_pago": request.form["metodo_pago"],
                }
            r = requests.put(
                "http://localhost:8099/api/persona/actualizar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Persona actualizada correctamente", "success")
                return redirect(url_for("router.lista_persona"))
            else:
                return redirect(url_for("router.editar_persona", id=id))
        except Exception as e:
            flash(f"Error en los datos: {str(e)}", "error")
            print("Exception:", e)
            return redirect(url_for("router.editar_persona", id=id))
    try:
        r = requests.get(f"http://localhost:8099/api/persona/lista/{id}")
        if r.status_code == 200:
            return render_template(
                "crud/persona/persona_editar.html",
                persona=r.json().get("persona"),
                tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
                generos=["Masculino", "Femenino", "Otro"],
                metodos_pago=["Tarjeta_credito", "Tarjeta_debito"],
                tipos_cuenta=["Administrador", "Cliente"],
                estados_cuenta=["Activo", "Inactivo"],
            )
        else:
            flash("Persona no encontrada", "error")
            return redirect(url_for("router.lista_persona"))
    except requests.exceptions.RequestException as e:
        flash(f"Error al cargar los datos: {str(e)}", "error")
        return redirect(url_for("router.lista_persona"))


@router.route("/persona/eliminar/<int:id>", methods=["POST"])
def eliminar_persona(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/persona/eliminar/{id}")
        if r.status_code == 200:
            flash("Persona eliminada correctamente", "success")
        else:
            flash("Error al eliminar la persona", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router.lista_persona"))


@router.route("/cuenta/lista")
def lista_cuenta():
    try:
        r = requests.get("http://localhost:8099/api/cuenta/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template("crud/cuenta/cuenta.html", lista=data.get("cuentas", []))
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/cuenta/cuenta.html", lista=[])
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/cuenta/cuenta.html", lista=[])


@router.route("/cuenta/crear", methods=["GET", "POST"])
def crear_cuenta():
    if request.method == "POST":
        try:
            data = {
                "correo": request.form["correo"],
                "clave": request.form["clave"],
                "tipo_cuenta": request.form["tipo_cuenta"],
                "estado_cuenta": request.form["estado_cuenta"],
            }
            r = requests.post(
                "http://localhost:8099/api/cuenta/guardar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Cuenta creada correctamente", "success")
                return redirect(url_for("router.lista_cuenta"))
            else:
                flash(f"Error al crear la cuenta: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    return render_template("crud/cuenta/cuenta_crear.html")


@router.route("/cuenta/editar/<int:id>", methods=["GET", "POST"])
def editar_cuenta(id):
    if request.method == "POST":
        try:
            data = {
                "id_cuenta": id,
                "correo": request.form["correo"],
                "clave": request.form["clave"],
                "tipo_cuenta": request.form["tipo_cuenta"],
                "estado_cuenta": request.form["estado_cuenta"],
            }
            r = requests.put(
                "http://localhost:8099/api/cuenta/actualizar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Cuenta actualizada correctamente", "success")
                return redirect(url_for("router.lista_cuenta"))
            else:
                flash(f"Error al actualizar: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    try:
        r = requests.get(f"http://localhost:8099/api/cuenta/lista/{id}")
        cuenta = r.json().get("cuenta") if r.status_code == 200 else None
        if cuenta:
            return render_template("crud/cuenta/cuenta_editar.html", cuenta=cuenta)
        else:
            flash("Cuenta no encontrada", "error")
            return redirect(url_for("router.lista_cuenta"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router.lista_cuenta"))


@router.route("/cuenta/eliminar/<int:id>", methods=["POST"])
def eliminar_cuenta(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/cuenta/eliminar/{id}")
        if r.status_code == 200:
            flash("Cuenta eliminada correctamente", "success")
        else:
            flash("Error al eliminar la cuenta", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router.lista_cuenta"))


@router.route("/pago/lista")
def lista_pago():
    try:
        r = requests.get("http://localhost:8099/api/pago/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template("crud/pago/pago.html", lista=data.get("pagos", []))
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/pago/pago.html", lista=[])
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/pago/pago.html", lista=[])


@router.route("/pago/crear", methods=["GET", "POST"])
def crear_pago():
    if request.method == "POST":
        try:
            data = {
                "monto": float(request.form["monto"]),
                "fecha_pago": request.form["fecha_pago"],
                "estado_pago": request.form["estado_pago"],
                "frecuencia": {"id_frecuencia": int(request.form["frecuencia_id"])},
            }
            r = requests.post(
                "http://localhost:8099/api/pago/guardar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Pago creado correctamente", "success")
                return redirect(url_for("router.lista_pago"))
            else:
                flash(f"Error al crear el pago: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    return render_template("crud/pago/pago_crear.html")


@router.route("/pago/editar/<int:id>", methods=["GET", "POST"])
def editar_pago(id):
    if request.method == "POST":
        try:
            data = {
                "id_pago": id,
                "monto": float(request.form["monto"]),
                "fecha_pago": request.form["fecha_pago"],
                "estado_pago": request.form["estado_pago"],
                "frecuencia": {"id_frecuencia": int(request.form["frecuencia_id"])},
            }
            r = requests.put(
                "http://localhost:8099/api/pago/actualizar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Pago actualizado correctamente", "success")
                return redirect(url_for("router.lista_pago"))
            else:
                flash(f"Error al actualizar: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    try:
        r = requests.get(f"http://localhost:8099/api/pago/lista/{id}")
        pago = r.json().get("pago") if r.status_code == 200 else None
        r_frecuencias = requests.get("http://localhost:8099/api/frecuencia/lista")
        frecuencias = (
            r_frecuencias.json().get("frecuencias", []) if r_frecuencias.status_code == 200 else []
        )
        if pago:
            return render_template("crud/pago/pago_editar.html", pago=pago, frecuencias=frecuencias)
        else:
            flash("Pago no encontrado", "error")
            return redirect(url_for("router.lista_pago"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router.lista_pago"))


@router.route("/pago/eliminar/<int:id>", methods=["POST"])
def eliminar_pago(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/pago/eliminar/{id}")
        if r.status_code == 200:
            flash("Pago eliminado correctamente", "success")
        else:
            flash("Error al eliminar el pago", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router.lista_pago"))


@router.route("/turno/lista")
def lista_turno():
    try:
        r = requests.get("http://localhost:8099/api/turno/lista")
        if r.status_code == 200:
            data = r.json()
            return render_template("crud/turno/turno.html", lista=data.get("turnos", []))
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
            return render_template("crud/turno/turno.html", lista=[])
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return render_template("crud/turno/turno.html", lista=[])


@router.route("/turno/crear", methods=["GET", "POST"])
def crear_turno():
    if request.method == "POST":
        try:
            data = {
                "numero_turno": int(request.form["numero_turno"]),
                "fecha_salida": request.form["fecha_salida"],
                "horario": {"id_horario": int(request.form["horario_id"])},
            }
            r = requests.post(
                "http://localhost:8099/api/turno/guardar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Turno creado correctamente", "success")
                return redirect(url_for("router.lista_turno"))
            else:
                flash(f"Error al crear el turno: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    try:
        r = requests.get("http://localhost:8099/api/horario/lista")
        horarios = r.json().get("horarios", []) if r.status_code == 200 else []
    except:
        horarios = []
        flash("Error al cargar los horarios", "error")
    return render_template("crud/turno/turno_crear.html", horarios=horarios)


@router.route("/turno/editar/<int:id>", methods=["GET", "POST"])
def editar_turno(id):
    if request.method == "POST":
        try:
            data = {
                "id_turno": id,
                "numero_turno": int(request.form["numero_turno"]),
                "fecha_salida": request.form["fecha_salida"],
                "horario": {"id_horario": int(request.form["horario_id"])},
            }
            r = requests.put(
                "http://localhost:8099/api/turno/actualizar",
                headers={"Content-Type": "application/json"},
                json=data,
            )
            if r.status_code == 200:
                flash("Turno actualizado correctamente", "success")
                return redirect(url_for("router.lista_turno"))
            else:
                flash(f"Error al actualizar: {r.text}", "error")
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
    try:
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
            return render_template("crud/turno/turno_editar.html", turno=turno, horarios=horarios)
        else:
            flash("Turno no encontrado", "error")
            return redirect(url_for("router.lista_turno"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router.lista_turno"))


@router.route("/turno/eliminar/<int:id>", methods=["POST"])
def eliminar_turno(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/turno/eliminar/{id}")
        if r.status_code == 200:
            flash("Turno eliminado correctamente", "success")
        else:
            flash("Error al eliminar el turno", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router.lista_turno"))


@router.route("/boleto/lista")
def lista_boleto():
    try:
        response = requests.get(f"http://localhost:8099/api/boleto/lista")
        if response.status_code == 200:
            data = response.json()
            return render_template("crud/boleto/boleto.html", lista=data.get("boletos", []))
        else:
            flash("Error al obtener la lista de boletos", "danger")
            return render_template("crud/boleto/boleto.html", lista=[])
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "danger")
        return render_template("crud/boleto/boleto.html", lista=[])


@router.route("/boleto/crear", methods=["GET", "POST"])
def crear_boleto():
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
                return redirect(url_for("router.lista_boleto"))
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
        return render_template("crud/boleto/boleto_crear.html", personas=personas, turnos=turnos)
    except requests.exceptions.RequestException as e:
        flash(f"Error al cargar los datos: {str(e)}", "danger")
        return redirect(url_for("router.lista_boleto"))


@router.route("/boleto/editar/<int:id>", methods=["GET", "POST"])
def editar_boleto(id):
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
                return redirect(url_for("router.lista_boleto"))
            else:
                error_msg = response.json().get("msg", "Error al actualizar el boleto")
                flash(error_msg, "danger")
                return redirect(url_for("router.editar_boleto", id=id))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for("router.editar_boleto", id=id))
    try:
        boleto_response = requests.get(f"http://localhost:8099/api/boleto/lista/{id}")
        personas_response = requests.get("http://localhost:8099/api/persona/lista")
        turnos_response = requests.get("http://localhost:8099/api/turno/lista")
        if boleto_response.status_code == 200:
            boleto = boleto_response.json().get("boleto")
            personas = personas_response.json().get("personas", [])
            turnos = turnos_response.json().get("turnos", [])
            return render_template(
                "crud/boleto/boleto_editar.html", boleto=boleto, personas=personas, turnos=turnos
            )
        else:
            flash("Boleto no encontrado", "danger")
            return redirect(url_for("router.lista_boleto"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "danger")
        return redirect(url_for("router.lista_boleto"))


@router.route("/boleto/eliminar/<int:id>", methods=["POST"])
def eliminar_boleto(id):
    try:
        response = requests.delete(f"http://localhost:8099/api/boleto/eliminar/{id}")
        if response.status_code == 200:
            flash("Boleto eliminado exitosamente", "success")
        else:
            flash("Error al eliminar el boleto", "danger")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "danger")
    return redirect(url_for("router.lista_boleto"))


@router.route("/seleccion_boleto/asientos/<int:bus_id>")
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
        r_rutas = requests.get("http://localhost:8099/api/ruta/lista")
        r_horarios = requests.get("http://localhost:8099/api/horario/lista")
        r_turnos = requests.get("http://localhost:8099/api/turno/lista")
        r_boletos = requests.get(f"http://localhost:8099/api/boleto/lista")
        if r_bus.status_code == 200:
            bus = r_bus.json().get("bus")
            rutas = r_rutas.json().get("rutas", []) if r_rutas.status_code == 200 else []
            horarios = (
                r_horarios.json().get("horarios", []) if r_horarios.status_code == 200 else []
            )
            turnos = r_turnos.json().get("turnos", []) if r_turnos.status_code == 200 else []
            horario = next((h for h in horarios if h["ruta"]["bus"]["id_bus"] == bus_id), None)
            ruta = next((r for r in rutas if r["bus"]["id_bus"] == bus_id), None)
            turno = next(
                (
                    t
                    for t in turnos
                    if (
                        t["horario"]["ruta"]["bus"]["id_bus"] == bus_id
                        and t["fecha_salida"] == request.args.get("fecha")
                        and t["horario"]["hora_salida"] == request.args.get("hora")
                    )
                ),
                None,
            )
            hora_salida = horario["hora_salida"] if horario else ""
            precio_unitario = ruta["precio_unitario"] if ruta else 0
            boletos = r_boletos.json().get("boletos", []) if r_boletos.status_code == 200 else []
            estados_asientos = ["disponible"] * bus["capacidad_pasajeros"]
            for boleto in boletos:
                if boleto["turno"]["horario"]["ruta"]["bus"]["id_bus"] == bus_id:
                    asiento = boleto["numero_asiento"] - 1
                    estados_asientos[asiento] = boleto["estado_boleto"].lower()
            return render_template(
                "seleccion_boleto/asientos_disponibles.html",
                ruta=ruta,
                bus=bus,
                turno=turno,
                estados_asientos=estados_asientos,
                origen=request.args.get("origen"),
                destino=request.args.get("destino"),
                fecha_salida=request.args.get("fecha"),
                hora_salida=hora_salida,
                precio_unitario=precio_unitario,
            )
        return jsonify({"error": "Bus no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@router.route("/buscar_cooperativas")
def buscar_cooperativas():
    try:
        origen = request.args.get("origen")
        destino = request.args.get("destino")
        fecha = request.args.get("fecha")
        if not all([origen, destino, fecha]):
            flash("Por favor complete todos los campos", "error")
            return redirect(url_for("router.index"))
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
        return redirect(url_for("router.index"))
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for("router.index"))


@router.route("/api/rutas/opciones")
def get_turnos_dispobibles():
    try:
        r = requests.get("http://localhost:8099/api/turno/lista")
        if r.status_code == 200:
            data = r.json()
            origenes = set()
            destinos = set()
            fechas = set()
            turnos = data.get("turnos", [])
            if not turnos:
                return jsonify({"origenes": [], "destinos": [], "fechas": [], "turnos": []})
            for turno in turnos:
                if turno.get("horario") and turno.get("horario").get("ruta"):
                    ruta = turno.get("horario").get("ruta")
                    origen = ruta.get("origen")
                    destino = ruta.get("destino")
                    fecha = turno.get("fecha_salida")
                    if origen:
                        origenes.add(origen)
                    if destino:
                        destinos.add(destino)
                    if fecha:
                        fechas.add(fecha)
            return jsonify(
                {
                    "origenes": sorted(list(origenes)),
                    "destinos": sorted(list(destinos)),
                    "fechas": sorted(list(fechas)),
                    "turnos": turnos,
                }
            )
        return jsonify({"error": "Error al obtener datos"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@router.route("/api/buses/disponibles")
def get_buses_disponibles():
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


@router.route("/procesar_pago", methods=["GET", "POST"])
@requiere_iniciar
def procesar_pago():
    if request.method == "POST":
        try:
            viaje_info = json.loads(request.form.get("viajeInfo"))
            logger.debug(f"Datos del viaje recibidos: {viaje_info}")
            if not viaje_info or not viaje_info.get("asientos"):
                raise ValueError("Debe especificar los números de asiento")
            r = requests.get("http://localhost:8099/api/turno/lista")
            if r.status_code != 200:
                raise ValueError("Error al obtener turnos")
            turnos = r.json().get("turnos", [])
            logger.debug(f"Turnos disponibles: {turnos}")
            turno_encontrado = None
            for turno in turnos:
                fecha_turno = datetime.strptime(turno["fecha_salida"], "%d/%m/%Y").date()
                fecha_viaje = datetime.strptime(viaje_info["fecha"], "%d/%m/%Y").date()
                ruta = turno["horario"]["ruta"]
                logger.debug(
                    f"Comparando - Turno: {fecha_turno} {turno['horario']['hora_salida']} {ruta['origen']}-{ruta['destino']}"
                )
                logger.debug(
                    f"Con Viaje: {fecha_viaje} {viaje_info['hora']} {viaje_info['origen']}-{viaje_info['destino']}"
                )
                if (
                    fecha_turno == fecha_viaje
                    and turno["horario"]["hora_salida"] == viaje_info["hora"]
                    and ruta["origen"] == viaje_info["origen"]
                    and ruta["destino"] == viaje_info["destino"]
                ):
                    turno_encontrado = turno
                    break
            if not turno_encontrado:
                raise ValueError(
                    "No se encontró un turno válido para la fecha y hora especificadas"
                )
            boletos_creados = []
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            for numero_asiento in viaje_info["asientos"]:
                boleto_data = {
                    "fecha_compra": fecha_actual,
                    "asientos": [numero_asiento],
                    "precio_unitario": float(viaje_info["precio_unitario"]),
                    "estado_boleto": "Vendido",
                    "persona": {"id_persona": session["user"]["id"]},
                    "turno": {"id_turno": turno_encontrado["id_turno"]},
                }
                logger.debug(f"Enviando datos de boleto: {boleto_data}")
                response = requests.post(
                    "http://localhost:8099/api/boleto/guardar",
                    headers={"Content-Type": "application/json"},
                    json=boleto_data,
                )
                if response.status_code != 200:
                    raise Exception(f"Error al guardar boleto: {response.text}")
                boleto_guardado = response.json().get("boleto")
                if boleto_guardado:
                    boletos_creados.append(boleto_guardado)
            pdf_paths = []
            for boleto in boletos_creados:
                pdf_data = {
                    **boleto,
                    "origen": viaje_info["origen"],
                    "destino": viaje_info["destino"],
                    "cooperativa": viaje_info["cooperativa"],
                }
                pdf_path = generar_pdf_boleto_endpoint(pdf_data)
                if pdf_path:
                    pdf_paths.append(pdf_path)
            return jsonify(
                {
                    "success": True,
                    "message": "Boletos generados correctamente",
                    "pdf_paths": pdf_paths,
                }
            )
        except ValueError as e:
            return jsonify({"success": False, "message": str(e)}), 400
        except Exception as e:
            logger.error(f"Error en procesar_pago: {str(e)}")
            return jsonify({"success": False, "message": str(e)}), 500
    return render_template(
        "pago_boleto.html", metodos_pago=["Efectivo", "Tarjeta", "Transferencia"]
    )


@router.route("/generar_pdf_boleto/<int:boleto_id>")
def generar_pdf_boleto_endpoint(boleto_id):
    try:
        response = requests.get(f"http://localhost:8099/api/boleto/lista/{boleto_id}")
        if response.status_code != 200:
            return jsonify({"error": "Boleto no encontrado"}), 404
        boleto_data = response.json().get("boleto", {})
        turno = boleto_data.get("turno", {})
        horario = turno.get("horario", {})
        ruta = horario.get("ruta", {})
        bus = ruta.get("bus", {})
        cooperativa = bus.get("cooperativa", {})
        persona = boleto_data.get("persona", {})
        pdf = FPDF("P", "mm", "A5")
        pdf.add_page()
        pdf.set_fill_color(122, 183, 48)
        pdf.rect(0, 0, 148, 20, "F")
        pdf.set_font("Arial", "B", 16)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(130, 12, "BOLETO", 0, 1, "C")
        pdf.set_draw_color(122, 183, 48)
        pdf.rect(5, 25, 138, 155)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 11)
        pdf.set_xy(10, 27)
        pdf.cell(120, 8, f'Boleto N° {boleto_data.get("id_boleto", "N/A")}', 0, 1, "C")
        pdf.line(5, 38, 143, 38)
        pdf.set_xy(10, 40)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(60, 5, "DETALLES DEL VIAJE", 0, 1)
        pdf.set_font("Arial", "", 8)
        detalles_izq = [
            f'Fecha de compra: {boleto_data.get("fecha_compra")}',
            f'Fecha de viaje: {turno.get("fecha_salida")}',
            f'Hora de salida: {horario.get("hora_salida")}',
            f'Origen: {ruta.get("origen")}',
            f'Destino: {ruta.get("destino")}',
            f'Estado: {boleto_data.get("estado_boleto")}',
        ]
        y = 46
        for detalle in detalles_izq:
            pdf.set_xy(12, y)
            pdf.cell(65, 5, detalle)
            y += 6
        pdf.set_xy(75, 40)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(65, 5, "INFORMACIÓN DEL BUS", 0, 1)
        pdf.set_font("Arial", "", 8)
        detalles_der = [
            f'Cooperativa: {cooperativa.get("nombre")}',
            f'N° de Bus: {bus.get("numero_bus")}',
            f'Placa: {bus.get("placa")}',
            f'N° de Asiento: {boleto_data.get("numero_asiento")}',
            f'Precio: $ {boleto_data.get("precio_final", "0.00")}',
            f'Modelo: {bus.get("modelo")}',
        ]
        y = 46
        for detalle in detalles_der:
            pdf.set_xy(77, y)
            pdf.cell(65, 5, detalle)
            y += 6
        pdf.set_xy(10, 85)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(128, 5, "DATOS DEL PASAJERO", 0, 1)
        pdf.set_font("Arial", "", 8)
        pdf.set_xy(12, 91)
        pdf.multi_cell(
            130,
            5,
            f'Nombre: {persona.get("nombre", "")} {persona.get("apellido", "")}\nIdentificación: {persona.get("numero_identificacion", "")}\nTeléfono: {persona.get("telefono", "")}',
        )
        qr = qrcode.QRCode(version=1, box_size=3)
        qr_data = f'Boleto #{boleto_data.get("id_boleto")}\nPasajero: {persona.get("nombre")} {persona.get("apellido")}\nRuta: {ruta.get("origen")} - {ruta.get("destino")}'
        qr.add_data(qr_data)
        qr.make()
        qr_img = qr.make_image()
        qr_path = f"temp_qr_{boleto_id}.png"
        qr_img.save(qr_path)
        pdf.image(qr_path, x=55, y=110, w=35)
        os.remove(qr_path)
        pdf.set_y(155)
        pdf.set_font("Arial", "I", 7)
        pdf.multi_cell(
            130,
            3,
            f"Este documento es válido únicamente para la fecha y hora indicadas.\nCooperativa de Transportes {cooperativa.get('nombre')}\nDirección: {cooperativa.get('direccion')}\nTeléfono: {cooperativa.get('telefono')}",
            0,
            "C",
        )
        pdf_output = pdf.output(dest="S").encode("latin-1")
        response = make_response(pdf_output)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename=boleto_{boleto_id}.pdf"
        return response
    except Exception as e:
        logger.error(f"Error generando PDF: {str(e)}")
        return jsonify({"error": "Error generando el PDF"}), 500


@router.route("/generar_ticket/<int:boleto_id>")
def generar_ticket(boleto_id):
    try:
        response = requests.get(f"http://localhost:8099/api/boleto/lista/{boleto_id}")
        if response.status_code != 200:
            return jsonify({"error": "Boleto no encontrado"}), 404
        boleto = response.json().get("boleto", {})
        turno = boleto.get("turno", {})
        horario = turno.get("horario", {})
        ruta = horario.get("ruta", {})
        bus = ruta.get("bus", {})
        cooperativa = bus.get("cooperativa", {})
        persona = boleto.get("persona", {})
        pdf = FPDF("P", "mm", (80, 160))
        pdf.add_page()
        pdf.set_fill_color(122, 183, 48)
        pdf.rect(0, 0, 80, 15, "F")
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(55, 2, f'{cooperativa.get("nombre", "").upper()}', 0, 1, "C")
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(55, 12, f'TICKET #{boleto.get("id_boleto", "N/A")}', 0, 1, "C")
        pdf.set_draw_color(122, 183, 48)
        pdf.line(5, pdf.get_y(), 75, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(80, 5, "DETALLES DEL VIAJE:", 0, 1, "L")
        pdf.set_font("Arial", "", 8)
        detalles = [
            f'Fecha: {turno.get("fecha_salida")}',
            f'Hora: {horario.get("hora_salida")}',
            f'Origen: {ruta.get("origen")}',
            f'Destino: {ruta.get("destino")}',
        ]
        for detalle in detalles:
            pdf.cell(80, 4, detalle, 0, 1, "L")
        pdf.ln(2)
        pdf.line(5, pdf.get_y(), 75, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(80, 5, "PASAJERO:", 0, 1, "L")
        pdf.set_font("Arial", "", 8)
        pasajero = [
            f'Nombre: {persona.get("nombre")} {persona.get("apellido")}',
            f'ID: {persona.get("numero_identificacion")}',
        ]
        for dato in pasajero:
            pdf.cell(80, 4, dato, 0, 1, "L")
        pdf.ln(2)
        pdf.line(5, pdf.get_y(), 75, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(80, 5, "DETALLES DEL SERVICIO:", 0, 1, "L")
        pdf.set_font("Arial", "", 8)
        servicio = [
            f'Bus #: {bus.get("numero_bus")}',
            f'Asiento: {boleto.get("numero_asiento")}',
            f'Precio: $ {boleto.get("precio_final")}',
        ]
        for detalle in servicio:
            pdf.cell(80, 4, detalle, 0, 1, "L")
        qr = qrcode.QRCode(version=1, box_size=2)
        qr_data = (
            f'Ticket #{boleto.get("id_boleto")}\n'
            f'Ruta: {ruta.get("origen")} - {ruta.get("destino")}\n'
            f'Fecha: {turno.get("fecha_salida")}'
        )
        qr.add_data(qr_data)
        qr.make()
        qr_img = qr.make_image()
        qr_path = f"temp_qr_ticket_{boleto_id}.png"
        qr_img.save(qr_path)
        pdf.image(qr_path, x=25, y=95, w=30)
        os.remove(qr_path)
        pdf.set_y(125)
        pdf.set_font("Arial", "I", 4)
        pdf.multi_cell(
            60,
            2,
            f'Tel: {cooperativa.get("telefono")}\n'
            f'{cooperativa.get("direccion")}\n'
            f"¡Gracias por viajar con nosotros!\n"
            f"Válido solo para la fecha y hora indicadas",
            0,
            "C",
        )
        pdf_output = pdf.output(dest="S").encode("latin-1")
        response = make_response(pdf_output)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename=ticket_{boleto_id}.pdf"
        return response
    except Exception as e:
        logger.error(f"Error generando ticket: {str(e)}")
        return jsonify({"error": "Error generando el ticket"}), 500
