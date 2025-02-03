from flask import Blueprint, jsonify, render_template, flash, redirect, request, session, url_for
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from flask import make_response
from dotenv import load_dotenv
from functools import wraps
from fpdf import FPDF
from os import getenv
import requests
import secrets
import smtplib
import qrcode
import time
import json
import jwt
import os


router = Blueprint("router", __name__)


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


@router.route("/")
def home():
    return render_template("index.html")


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


@router.route("/verificar_sesion")
def verificar_sesion():
    return jsonify({"sesion_activa": "user" in session})


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
                        if cuenta.get("estado_cuenta") == "Inactivo":
                            flash("Su cuenta está inactiva. Contacte al administrador", "danger")
                            return redirect(url_for("router.iniciar_sesion"))
                        if cuenta.get("estado_cuenta") == "Suspendido":
                            flash("Su cuenta está suspendida. Contacte al administrador", "danger")
                            return redirect(url_for("router.iniciar_sesion"))
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


@router.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        try:
            campos_requeridos = {
                "tipo_identificacion": request.form.get("tipo_identificacion"),
                "numero_identificacion": request.form.get("numero_identificacion"),
                "nombre": request.form.get("nombre"),
                "apellido": request.form.get("apellido"),
                "correo": request.form.get("correo"),
                "contrasenia": request.form.get("contrasenia"),
                "fecha_nacimiento": request.form.get("fecha_nacimiento"),
            }
            for campo, valor in campos_requeridos.items():
                if not valor or not valor.strip():
                    flash(f"El campo {campo} es requerido", "danger")
                    return render_template("registro_usuario.html")
            r_personas = requests.get("http://localhost:8099/api/persona/lista")
            personas = r_personas.json().get("personas", [])
            numero_identificacion = request.form.get("numero_identificacion")
            correo = request.form.get("correo")
            telefono = request.form.get("telefono")
            for persona in personas:
                if persona.get("numero_identificacion") == numero_identificacion:
                    return render_template(
                        "registro_usuario.html",
                        error="Ya existe una persona registrada con este número de identificación",
                    )
                if persona.get("correo") == correo:
                    return render_template(
                        "registro_usuario.html",
                        error="Ya existe una persona registrada con este correo electrónico",
                    )
                if persona.get("telefono") == telefono:
                    return render_template(
                        "registro_usuario.html",
                        error="Ya existe una persona registrada con este número de teléfono",
                    )
            datos_registro = {
                "tipo_identificacion": campos_requeridos["tipo_identificacion"],
                "numero_identificacion": numero_identificacion,
                "nombre": campos_requeridos["nombre"].strip(),
                "apellido": campos_requeridos["apellido"].strip(),
                "fecha_nacimiento": campos_requeridos["fecha_nacimiento"],
                "correo": correo,
                "genero": "No_definido",
                "direccion": "",
                "telefono": "",
                "saldo_disponible": 0.0,
                "usuario": correo,
                "contrasenia": campos_requeridos["contrasenia"],
                "tipo_tarifa": "General",
                "tipo_cuenta": "Cliente",
                "estado_cuenta": "Activo",
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
    return render_template("registro_usuario.html")


# Recuperacion de contraseña


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
                flash("No se encontró una cuenta con ese correo", "error")
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
        contrasenia = request.form.get("contrasenia")
        confirm_contrasenia = request.form.get("confirm_contrasenia")
        if not contrasenia or not confirm_contrasenia:
            flash("Por favor ingrese la contraseña", "danger")
            return redirect(url_for("router.cambiar_contrasenia", token=token))
        if contrasenia != confirm_contrasenia:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for("router.cambiar_contrasenia", token=token))
        try:
            response = requests.get(f"http://localhost:8099/api/persona/lista/{persona_id}")
            if response.status_code == 200:
                persona_data = response.json()["persona"]
                update_data = {
                    "id_persona": int(persona_id),
                    "tipo_identificacion": persona_data["tipo_identificacion"],
                    "numero_identificacion": persona_data["numero_identificacion"],
                    "nombre": persona_data["nombre"],
                    "apellido": persona_data["apellido"],
                    "fecha_nacimiento": persona_data["fecha_nacimiento"],
                    "direccion": persona_data.get("direccion", ""),
                    "telefono": persona_data["telefono"],
                    "correo": persona_data["correo"],
                    "genero": persona_data["genero"],
                    "saldo_disponible": persona_data["saldo_disponible"],
                    "tipo_tarifa": persona_data["tipo_tarifa"],
                    "metodo_pago": persona_data["metodo_pago"],
                    "cuenta": {
                        "id_cuenta": persona_data["cuenta"]["id_cuenta"],
                        "correo": persona_data["cuenta"]["correo"],
                        "contrasenia": contrasenia,
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
        flash(f"Error enviando email: {str(e)}")


# Usuario


@router.route("/perfil", methods=["GET", "POST"])
@requiere_iniciar
def perfil():
    if request.method == "POST":
        try:
            r_usuario = requests.get(
                f"http://localhost:8099/api/persona/lista/{session['user']['id']}"
            )
            datos_actuales = r_usuario.json().get("persona", {})
            datos_actualizacion = {
                "id_persona": session["user"]["id"],
                "tipo_identificacion": request.form.get("tipo_identificacion"),
                "numero_identificacion": request.form.get("numero_identificacion"),
                "nombre": request.form.get("nombre"),
                "apellido": request.form.get("apellido"),
                "direccion": request.form.get("direccion", ""),
                "fecha_nacimiento": request.form.get("fecha_nacimiento"),
                "correo": request.form.get("correo"),
                "telefono": request.form.get("telefono", ""),
                "genero": request.form.get("genero", "No_definido"),
                "metodo_pago": datos_actuales.get("metodo_pago", "No_definido"),
                "tipo_tarifa": request.form.get("tipo_tarifa", "General"),
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
                        "nombre": request.form.get("nombre"),
                        "apellido": request.form.get("apellido"),
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
        r_usuario = requests.get(f"http://localhost:8099/api/persona/lista/{session['user']['id']}")
        usuario_perfil = r_usuario.json().get("persona", {})
        return render_template(
            "perfil.html",
            usuario=usuario_perfil,
            tipos_identificacion=["Cedula", "Pasaporte", "Licencia_conducir"],
            tipos_tarifa=["General", "Menor_edad", "Tercera_edad", "Estudiante", "Discapacitado"],
            generos=["No_definido", "Masculino", "Femenino", "Otro"],
        )
    except Exception as e:
        flash(f"Error al cargar el perfil: {str(e)}", "error")
    if session.get("user", {}).get("tipo_cuenta") == "Administrador":
        return redirect(url_for("router.administrador"))
    return redirect(url_for("router.cliente"))


@router.route("/cliente")
@requiere_cliente
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
        for boleto in boletos_usuario:
            try:
                fecha_salida = datetime.strptime(
                    boleto.get("turno", {}).get("fecha_salida", ""), "%d/%m/%Y"
                )
                if fecha_salida < fecha_actual:
                    viajes_realizados.append(boleto)
                elif boleto.get("estado_boleto") == "Vendido":
                    boletos_activos.append(boleto)
            except ValueError:
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
                    "precio_unitario": b.get("turno", {})
                    .get("horario", {})
                    .get("ruta", {})
                    .get("precio_unitario"),
                    "distancia": b.get("turno", {})
                    .get("horario", {})
                    .get("ruta", {})
                    .get("distancia"),
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
                    .get("nombre_cooperativa"),
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
            "saldo_disponible": persona_data.get("saldo_disponible", 0.0),
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
@requiere_administrador
def administrador():
    if session.get("user", {}).get("tipo_cuenta") != "Administrador":
        flash("Acceso no autorizado", "danger")
        return redirect(url_for("router.cliente"))
    try:
        usuario_id = session.get("user", {}).get("id")
        r_usuario = requests.get(f"http://localhost:8099/api/persona/lista/{usuario_id}")
        datos_usuario = r_usuario.json().get("persona", {}) if r_usuario.status_code == 200 else {}
        usuario = {
            "nombre": datos_usuario.get("nombre", "Usuario"),
            "apellido": datos_usuario.get("apellido", ""),
        }
        r_personas = requests.get("http://localhost:8099/api/persona/lista")
        r_boletos = requests.get("http://localhost:8099/api/boleto/lista")
        r_turnos = requests.get("http://localhost:8099/api/turno/lista")
        r_rutas = requests.get("http://localhost:8099/api/ruta/lista")
        personas = r_personas.json().get("personas", [])
        boletos = r_boletos.json().get("boletos", [])
        turnos = r_turnos.json().get("turnos", [])
        rutas = r_rutas.json().get("rutas", [])
        rutas = []
        buses = []
        rutas_ids = set()
        buses_ids = set()
        for ruta in rutas:
            bus = ruta.get("bus", {})
            if bus and bus.get("id_bus") not in buses_ids:
                buses_ids.add(bus.get("id_bus"))
                buses.append(bus)
        for turno in turnos:
            horario = turno.get("horario", {})
            ruta = horario.get("ruta", {})
            bus = ruta.get("bus", {})
            if ruta and ruta.get("id_ruta") not in rutas_ids:
                rutas_ids.add(ruta.get("id_ruta"))
                rutas.append(ruta)
            if bus and bus.get("id_bus") not in buses_ids:
                buses_ids.add(bus.get("id_bus"))
                buses.append(bus)
        stats = {
            "total_usuarios": len(personas),
            "total_ventas": len(boletos),
            "total_buses": len(buses),
            "total_rutas": len(rutas),
            "ingresos_totales": sum(float(b.get("precio_final", 0)) for b in boletos),
            "viajes_activos": len([t for t in turnos if t.get("estado_turno") == "Activo"]),
        }
        usuarios = [
            {
                "id": p.get("id_persona"),
                "nombre": f"{p.get('nombre', '')} {p.get('apellido', '')}",
                "correo": p.get("correo"),
                "tipo": p.get("cuenta", {}).get("tipo_cuenta", "Cliente"),
                "estado": (
                    "Activo" if p.get("cuenta", {}).get("estado_cuenta") == "Activo" else "Inactivo"
                ),
                "estado_clase": (
                    "success" if p.get("cuenta", {}).get("estado_cuenta") == "Activo" else "danger"
                ),
            }
            for p in personas
        ]
        boletos_lista = [
            {
                "id": b.get("id_boleto"),
                "cliente": f"{b.get('persona', {}).get('nombre', '')} {b.get('persona', {}).get('apellido', '')}",
                "asiento": f"{b.get('numero_asiento')}",
                "ruta": f"{b.get('turno', {}).get('horario', {}).get('ruta', {}).get('origen')} - {b.get('turno', {}).get('horario', {}).get('ruta', {}).get('destino')}",
                "fecha": b.get("fecha_compra"),
                "bus": b.get("turno", {})
                .get("horario", {})
                .get("ruta", {})
                .get("bus", {})
                .get("placa"),
                "precio": b.get("precio_final"),
                "estado": b.get("estado_boleto", "No disponible"),
                "estado_clase": "success" if b.get("estado_boleto") == "Vendido" else "warning",
            }
            for b in boletos
        ]
        buses_lista = [
            {
                "numero": b.get("numero_bus"),
                "placa": b.get("placa"),
                "marca": b.get("marca"),
                "modelo": b.get("modelo"),
                "cooperativa": b.get("cooperativa", {}).get("nombre_cooperativa"),
                "estado": b.get("estado_bus"),
                "estado_clase": "success" if b.get("estado_bus") == "Activo" else "warning",
                "ruta_actual": next(
                    (
                        f"{r.get('origen')} - {r.get('destino')}"
                        for r in rutas
                        if r.get("bus", {}).get("id_bus") == b.get("id_bus")
                        and r.get("estado_ruta") == "Disponible"
                    ),
                    "Sin ruta asignada",
                ),
            }
            for b in buses
        ]
        rutas_lista = [
            {
                "origen": r.get("origen"),
                "destino": r.get("destino"),
                "bus_asignado": f"{r.get('bus', {}).get('numero_bus')} - {r.get('bus', {}).get('placa')}",
                "horarios": ", ".join(
                    set(
                        t.get("horario", {}).get("hora_salida", "")
                        for t in turnos
                        if t.get("horario", {}).get("ruta", {}).get("id_ruta") == r.get("id_ruta")
                    )
                ),
                "estado": r.get("estado_ruta"),
                "estado_clase": "success" if r.get("estado_ruta") == "Disponible" else "warning",
            }
            for r in rutas
        ]
        ultimas_ventas = sorted(boletos_lista, key=lambda x: x["fecha"], reverse=True)[:25]
        proximas_salidas = [
            {
                "ruta": f"{t.get('horario', {}).get('ruta', {}).get('origen')} - {t.get('horario', {}).get('ruta', {}).get('destino')}",
                "hora": t.get("horario", {}).get("hora_salida"),
                "bus": t.get("horario", {}).get("ruta", {}).get("bus", {}).get("numero_bus"),
                "asientos_disponibles": t.get("horario", {})
                .get("ruta", {})
                .get("bus", {})
                .get("capacidad_pasajeros", 0)
                - len(
                    [b for b in boletos if b.get("turno", {}).get("id_turno") == t.get("id_turno")]
                ),
            }
            for t in sorted(turnos, key=lambda x: x.get("fecha_salida", ""))[:5]
        ]
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
            usuarios=usuarios,
            boletos=boletos_lista,
            buses=buses_lista,
            rutas=rutas_lista,
            estado_buses=estado_buses,
            usuario=usuario,
            ultimas_ventas=ultimas_ventas,
            proximas_salidas=proximas_salidas,
        )
    except Exception as e:
        flash(f"Error al cargar los datos: {str(e)}", "danger")
        return render_template("panel_administrador.html", usuario=usuario)


# Metodos generales


@router.route("/api/metodos-pago/agregar", methods=["POST"])
@requiere_iniciar
def agregar_metodo_pago():
    try:
        usuario_id = session.get("user", {}).get("id")
        if not usuario_id:
            return jsonify({"error": "Usuario no autenticado"}), 401
        r_usuario = requests.get(f"http://localhost:8099/api/persona/lista/{usuario_id}")
        if r_usuario.status_code != 200:
            return jsonify({"error": "Error al obtener datos del usuario"}), 500
        datos_actuales = r_usuario.json().get("persona", {})
        metodo_pago = {
            "opcion_pago": request.json.get("opcion_pago"),
            "titular": request.json.get("titular"),
            "numero_tarjeta": request.json.get("numero_tarjeta"),
            "fecha_vencimiento": request.json.get("fecha_vencimiento"),
            "codigo_seguridad": request.json.get("codigo_seguridad"),
            "saldo": request.json.get("saldo"),
        }
        datos_actualizacion = {
            "id_persona": usuario_id,
            "tipo_identificacion": datos_actuales.get("tipo_identificacion"),
            "numero_identificacion": datos_actuales.get("numero_identificacion"),
            "nombre": datos_actuales.get("nombre"),
            "apellido": datos_actuales.get("apellido"),
            "direccion": datos_actuales.get("direccion"),
            "fecha_nacimiento": datos_actuales.get("fecha_nacimiento"),
            "telefono": datos_actuales.get("telefono"),
            "correo": datos_actuales.get("correo"),
            "genero": datos_actuales.get("genero"),
            "tipo_tarifa": datos_actuales.get("tipo_tarifa", "General"),
            "saldo_disponible": datos_actuales.get("saldo_disponible", 0.0),
            "cuenta": datos_actuales.get("cuenta"),
            "metodo_pago": metodo_pago,
        }
        response = requests.put(
            "http://localhost:8099/api/persona/actualizar", json=datos_actualizacion
        )
        if response.status_code == 500:
            verify_response = requests.get(f"http://localhost:8099/api/persona/lista/{usuario_id}")
            if verify_response.status_code == 200:
                persona_actualizada = verify_response.json().get("persona", {})
                if persona_actualizada.get("metodo_pago"):
                    return jsonify(
                        {"success": True, "message": "Método de pago agregado correctamente"}
                    )
        return jsonify({"success": True, "message": "Método de pago agregado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@router.route("/api/metodos-pago/actualizar", methods=["PUT"])
@requiere_iniciar
def actualizar_metodo_pago():
    try:
        data = request.get_json()
        usuario_id = data.get("id_persona")
        if not usuario_id:
            return jsonify({"success": False, "message": "ID de usuario no proporcionado"}), 401
        r_usuario = requests.get(f"http://localhost:8099/api/persona/lista/{usuario_id}")
        if r_usuario.status_code != 200:
            return jsonify({"success": False, "message": "Error al obtener datos del usuario"}), 400
        datos_actuales = r_usuario.json().get("persona", {})
        metodo_pago = {
            "opcion_pago": data.get("opcion_pago"),
            "numero_tarjeta": data.get("numero_tarjeta"),
            "titular": data.get("titular"),
            "fecha_vencimiento": data.get("fecha_vencimiento"),
            "codigo_seguridad": data.get("codigo_seguridad"),
            "saldo": float(data.get("saldo", 0.0)),
        }
        datos_actualizacion = {
            "id_persona": usuario_id,
            "tipo_identificacion": datos_actuales.get("tipo_identificacion"),
            "numero_identificacion": datos_actuales.get("numero_identificacion"),
            "nombre": datos_actuales.get("nombre"),
            "apellido": datos_actuales.get("apellido"),
            "direccion": datos_actuales.get("direccion"),
            "fecha_nacimiento": datos_actuales.get("fecha_nacimiento"),
            "telefono": datos_actuales.get("telefono"),
            "correo": datos_actuales.get("correo"),
            "genero": datos_actuales.get("genero"),
            "tipo_tarifa": datos_actuales.get("tipo_tarifa", "General"),
            "saldo_disponible": datos_actuales.get("saldo_disponible", 0.0),
            "cuenta": datos_actuales.get("cuenta"),
            "metodo_pago": metodo_pago,
        }
        response = requests.put(
            "http://localhost:8099/api/persona/actualizar", json=datos_actualizacion
        )
        if response.status_code == 200:
            return jsonify({"success": True, "message": "Método de pago actualizado correctamente"})
        return jsonify({"success": False, "message": "Error al actualizar el método de pago"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@router.route("/api/metodos-pago/eliminar", methods=["DELETE"])
@requiere_iniciar
def eliminar_metodo_pago():
    try:
        data = request.get_json()
        usuario_id = data.get("id_persona")
        if not usuario_id:
            return jsonify({"success": False, "message": "ID de usuario no proporcionado"}), 400
        r_usuario = requests.get(f"http://localhost:8099/api/persona/lista/{usuario_id}")
        if r_usuario.status_code != 200:
            return jsonify({"success": False, "message": "Error al obtener datos del usuario"}), 400
        datos_actuales = r_usuario.json().get("persona", {})
        datos_actualizacion = {
            "id_persona": usuario_id,
            "tipo_identificacion": datos_actuales.get("tipo_identificacion"),
            "numero_identificacion": datos_actuales.get("numero_identificacion"),
            "nombre": datos_actuales.get("nombre"),
            "apellido": datos_actuales.get("apellido"),
            "direccion": datos_actuales.get("direccion"),
            "fecha_nacimiento": datos_actuales.get("fecha_nacimiento"),
            "telefono": datos_actuales.get("telefono"),
            "correo": datos_actuales.get("correo"),
            "genero": datos_actuales.get("genero"),
            "tipo_tarifa": datos_actuales.get("tipo_tarifa", "General"),
            "saldo_disponible": datos_actuales.get("saldo_disponible", 0.0),
            "cuenta": datos_actuales.get("cuenta"),
            "metodo_pago": None,
        }
        response = requests.put(
            "http://localhost:8099/api/persona/actualizar", json=datos_actualizacion
        )
        if response.status_code == 200:
            if datos_actuales.get("metodo_pago", {}).get("id_pago"):
                pago_id = datos_actuales["metodo_pago"]["id_pago"]
                requests.delete(f"http://localhost:8099/api/pago/eliminar/{pago_id}")
            return jsonify({"success": True, "message": "Método de pago eliminado correctamente"})
        return jsonify({"success": False, "message": "Error al eliminar el método de pago"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


# Funciones de boletos


# Funciones de pago


@router.route("/procesar_pago", methods=["GET", "POST"])
@requiere_iniciar
def procesar_pago():
    if request.method == "POST":
        try:
            viaje_info = json.loads(request.form.get("viajeInfo"))
            if not viaje_info or not viaje_info.get("asientos"):
                return jsonify({"success": False, "message": "Información de viaje inválida"})
            usuario_id = session.get("user", {}).get("id")
            r_usuario = requests.get(f"http://localhost:8099/api/persona/lista/{usuario_id}")
            if r_usuario.status_code != 200:
                return jsonify({"success": False, "message": "Error al obtener datos del usuario"})
            usuario = r_usuario.json().get("persona", {})
            saldo_actual = float(usuario.get("saldo_disponible", 0))
            total_pagar = float(viaje_info.get("total", 0))
            if saldo_actual < total_pagar:
                return jsonify({"success": False, "message": "Saldo insuficiente"})
            r = requests.get("http://localhost:8099/api/turno/lista")
            if r.status_code != 200:
                raise ValueError("Error al obtener turnos")
            turnos = r.json().get("turnos", [])
            turno_encontrado = None
            for turno in turnos:
                fecha_turno = datetime.strptime(turno["fecha_salida"], "%d/%m/%Y").date()
                fecha_viaje = datetime.strptime(viaje_info["fecha"], "%d/%m/%Y").date()
                ruta = turno["horario"]["ruta"]
                if (
                    fecha_turno == fecha_viaje
                    and turno["horario"]["hora_salida"] == viaje_info["hora"]
                    and ruta["origen"] == viaje_info["origen"]
                    and ruta["destino"] == viaje_info["destino"]
                ):
                    turno_encontrado = turno
                    break
            if not turno_encontrado:
                raise ValueError("No se encontró un turno válido")
            boletos_creados = []
            fecha_actual = datetime.now().strftime("%d/%m/%Y")
            for numero_asiento in viaje_info["asientos"]:
                boleto_data = {
                    "fecha_compra": fecha_actual,
                    "asientos": [numero_asiento],
                    "precio_unitario": float(viaje_info["precio_unitario"]),
                    "estado_boleto": "Vendido",
                    "persona": {"id_persona": usuario_id},
                    "turno": {"id_turno": turno_encontrado["id_turno"]},
                }
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
                pdf_path = generar_boleto_pdf(pdf_data)
                if pdf_path:
                    pdf_paths.append(pdf_path)
            return jsonify(
                {
                    "success": True,
                    "message": "Boletos generados correctamente",
                    "pdf_paths": pdf_paths,
                    "nuevo_saldo": saldo_actual - total_pagar,
                }
            )
        except ValueError as e:
            return jsonify({"success": False, "message": str(e)}), 400
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500
    return render_template(
        "pago_boleto.html", metodos_pago=["Efectivo", "Tarjeta", "Transferencia"]
    )


@router.route("/api/metodos-pago/transferir-saldo", methods=["POST"])
@requiere_iniciar
def transferir_saldo():
    try:
        usuario_id = session.get("user", {}).get("id")
        if not usuario_id:
            return jsonify({"success": False, "message": "Usuario no identificado"}), 401
        response = requests.post(
            "http://localhost:8099/api/persona/transferir-saldo", json={"id_persona": usuario_id}
        )
        if response.status_code == 200:
            return jsonify({"success": True, "message": "Saldo transferido correctamente"})
        return jsonify({"success": False, "message": "Error al transferir el saldo"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@router.route("/api/metodos-pago/usuario")
@requiere_iniciar
def metodos_pago_usuario():
    try:
        usuario_id = session.get("user", {}).get("id")
        if not usuario_id:
            return jsonify({"error": "Usuario no autenticado"}), 401
        viaje_info = request.args.get("viajeInfo")
        precio_original = 0
        if viaje_info:
            viaje_info = json.loads(viaje_info)
            precio_original = float(viaje_info.get("precio_unitario", 0)) * len(
                viaje_info.get("asientos", [])
            )
        response = requests.get(f"http://localhost:8099/api/persona/lista/{usuario_id}")
        if response.status_code == 200:
            persona = response.json().get("persona", {})
            metodos_pago = []
            if persona.get("metodo_pago"):
                metodo = persona["metodo_pago"]
                metodos_pago.append(
                    {
                        "id_pago": metodo.get("id_pago"),
                        "saldo": metodo.get("saldo"),
                        "numero_tarjeta": metodo.get("numero_tarjeta"),
                        "titular": metodo.get("titular"),
                        "fecha_vencimiento": metodo.get("fecha_vencimiento"),
                        "codigo_seguridad": metodo.get("codigo_seguridad"),
                        "opcion_pago": metodo.get("opcion_pago"),
                    }
                )
            else:
                flash("No se encontraron métodos de pago", "info")
            tipo_tarifa = persona.get("tipo_tarifa", "General")
            r_descuentos = requests.get("http://localhost:8099/api/descuento/lista")
            descuentos_aplicables = []
            porcentaje_total = 0
            if r_descuentos.status_code == 200:
                descuentos = r_descuentos.json().get("descuentos", [])
                fecha_actual = datetime.now()
                for d in descuentos:
                    if d["tipo_descuento"] == tipo_tarifa and d["estado_descuento"] == "Activo":
                        porcentaje_total += d["porcentaje"]
                        descuentos_aplicables.append(
                            {
                                "nombre": d["nombre_descuento"],
                                "porcentaje": d["porcentaje"],
                                "tipo": "Tarifa Base",
                            }
                        )
                for d in descuentos:
                    if (
                        d["tipo_descuento"] == "Promocional"
                        and d["estado_descuento"] == "Activo"
                        and "fecha_inicio" in d
                        and "fecha_fin" in d
                    ):
                        fecha_inicio = datetime.strptime(d["fecha_inicio"], "%d/%m/%Y")
                        fecha_fin = datetime.strptime(d["fecha_fin"], "%d/%m/%Y")
                        if fecha_inicio <= fecha_actual <= fecha_fin:
                            porcentaje_total += d["porcentaje"]
                            descuentos_aplicables.append(
                                {
                                    "nombre": d["nombre_descuento"],
                                    "porcentaje": d["porcentaje"],
                                    "tipo": "Promocional",
                                    "vigencia": f"Válido hasta {d['fecha_fin']}",
                                }
                            )
            descuento_monto = precio_original * (porcentaje_total / 100)
            precio_final = precio_original - descuento_monto
            return jsonify(
                {
                    "metodos": metodos_pago,
                    "persona": {
                        "nombre": persona.get("nombre"),
                        "apellido": persona.get("apellido"),
                        "correo": persona.get("correo"),
                        "saldo_disponible": persona.get("saldo_disponible", 0),
                        "tipo_tarifa": tipo_tarifa.replace("_", " "),
                        "descuentos_aplicables": descuentos_aplicables,
                        "precio_original": precio_original,
                        "precio_final": precio_final,
                        "ahorro_total": descuento_monto,
                        "porcentaje_descuento_total": porcentaje_total,
                    },
                }
            )
        return jsonify({"error": "Error al obtener métodos de pago"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Generacion de PDF


@router.route("/generar_pdf_boleto/<int:boleto_id>")
def generar_boleto_pdf(boleto_id):
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
            f'Cooperativa: {cooperativa.get("nombre_cooperativa")}',
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
            f"Este documento es válido únicamente para la fecha y hora indicadas.\nCooperativa de Transportes {cooperativa.get('nombre_cooperativa')}\nDirección: {cooperativa.get('direccion')}\nTeléfono: {cooperativa.get('telefono')}",
            0,
            "C",
        )
        pdf_output = pdf.output(dest="S").encode("latin-1")
        response = make_response(pdf_output)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename=boleto_{boleto_id}.pdf"
        return response
    except Exception as e:
        return jsonify({"error": "Error generando el PDF"}), 500


@router.route("/generar_ticket/<int:boleto_id>")
def generar_ticket_pdf(boleto_id):
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
        pdf.cell(55, 2, f'{cooperativa.get("nombre_cooperativa", "").upper()}', 0, 1, "C")
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
        return jsonify({"error": "Error generando el ticket"}), 500


# CRUD de Cooperativas


@router.route("/cooperativa/lista")
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


@router.route("/cooperativa/crear", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_cooperativa"))
            else:
                flash("Error al crear la cooperativa", "error")
                return redirect(url_for("router.lista_cooperativa"))
        except requests.exceptions.ConnectionError:
            flash("Error de conexión con el servidor", "error")
            return redirect(url_for("router.lista_cooperativa"))
        except requests.exceptions.RequestException as e:
            flash(f"Error en la solicitud: {str(e)}", "error")
            return redirect(url_for("router.lista_cooperativa"))
    return render_template("crud/cooperativa/cooperativa_crear.html", usuario=usuario)


@router.route("/cooperativa/editar/<int:id>", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_cooperativa"))
            else:
                flash("Error al actualizar la cooperativa", "error")
                return redirect(url_for("router.lista_cooperativa"))
        except requests.exceptions.RequestException as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for("router.lista_cooperativa"))
    try:
        r = requests.get(f"http://localhost:8099/api/cooperativa/lista/{id}")
        if r.status_code == 200:
            cooperativa = r.json().get("cooperativa")
            return render_template(
                "crud/cooperativa/cooperativa_editar.html", cooperativa=cooperativa, usuario=usuario
            )
        else:
            flash("Cooperativa no encontrada", "error")
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
            flash(error_msg, "error")
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión: {str(e)}"
        flash(error_msg, "error")
    return redirect(url_for("router.lista_cooperativa"))


@router.route("/cooperativa/ordenar/<atributo>/<orden>")
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


@router.route("/cooperativa/buscar/<atributo>/<criterio>")
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


@router.route("/bus/lista")
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


@router.route("/bus/crear", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_bus"))
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


@router.route("/bus/editar/<int:id>", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_bus"))
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
            flash(error_msg, "error")
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión: {str(e)}"
        flash(error_msg, "error")
    return redirect(url_for("router.lista_bus"))


@router.route("/bus/ordenar/<atributo>/<orden>")
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


@router.route("/bus/buscar/<atributo>/<criterio>")
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


@router.route("/ruta/lista")
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


@router.route("/ruta/crear", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_ruta"))
            else:
                flash(f"Error al crear la ruta: {r.text}", "error")
        except requests.exceptions.ConnectionError:
            flash("Error de conexión con el servidor", "error")
        except Exception as e:
            flash(f"Error al crear la ruta: {str(e)}", "error")
    return render_template("crud/ruta/ruta_crear.html", buses=buses, usuario=usuario)


@router.route("/ruta/editar/<int:id>", methods=["GET", "POST"])
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
            return redirect(url_for("router.lista_ruta"))
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
            return redirect(url_for("router.lista_ruta"))
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
                return redirect(url_for("router.lista_ruta"))
            else:
                flash(
                    f"Error al actualizar la ruta: {r.json().get('msg', 'Error desconocido')}",
                    "error",
                )
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
        return redirect(url_for("router.editar_ruta", id=id))


@router.route("/ruta/eliminar/<int:id>", methods=["POST"])
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
    return redirect(url_for("router.lista_ruta"))


@router.route("/ruta/ordenar/<atributo>/<orden>")
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


@router.route("/ruta/buscar/<atributo>/<criterio>")
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


@router.route("/escala/lista")
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


@router.route("/escala/crear", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_escala"))
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


@router.route("/escala/editar/<int:id>", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_escala"))
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
            return redirect(url_for("router.lista_escala"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router.lista_escala"))


@router.route("/escala/eliminar/<int:id>", methods=["POST"])
def eliminar_escala(id):
    try:
        r = requests.delete(f"http://localhost:8099/api/escala/eliminar/{id}")
        if r.status_code == 200:
            flash("Escala eliminada correctamente", "success")
            return redirect(url_for("router.lista_escala"))
        else:
            flash(f"Error del servidor: {r.status_code}", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router.lista_escala"))


@router.route("/escala/ordenar/<atributo>/<orden>")
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


@router.route("/escala/buscar/<atributo>/<criterio>")
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


@router.route("/horario/lista")
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


@router.route("/horario/crear", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_horario"))
            else:
                flash(f"Error al crear el horario: {response.text}", "error")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
    return render_template("crud/horario/horario_crear.html", rutas=rutas, usuario=usuario)


@router.route("/horario/editar/<int:id>", methods=["GET", "POST"])
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
                        return redirect(url_for("router.lista_horario"))
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


@router.route("/horario/ordenar/<atributo>/<orden>")
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


@router.route("/horario/buscar/<atributo>/<criterio>")
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


@router.route("/turno/lista")
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


@router.route("/turno/crear", methods=["GET", "POST"])
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
                    return redirect(url_for("router.lista_turno"))
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
        return redirect(url_for("router.lista_turno"))


@router.route("/turno/editar/<int:id>", methods=["GET", "POST"])
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
                return redirect(url_for("router.editar_turno", id=id))
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
                return redirect(url_for("router.lista_turno"))
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


@router.route("/turno/ordenar/<atributo>/<orden>")
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


@router.route("/turno/buscar/<atributo>/<criterio>")
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


@router.route("/frecuencia/lista")
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


@router.route("/frecuencia/crear", methods=["GET", "POST"])
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
    return render_template(
        "crud/frecuencia/frecuencia_crear.html", horarios=horarios, usuario=usuario
    )


@router.route("/frecuencia/editar/<int:id>", methods=["GET", "POST"])
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
                "crud/frecuencia/frecuencia_editar.html",
                frecuencia=frecuencia,
                horarios=horarios,
                usuario=usuario,
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


@router.route("/frecuencia/ordenar/<atributo>/<orden>")
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


@router.route("/frecuencia/buscar/<atributo>/<criterio>")
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


@router.route("/persona/lista")
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


@router.route("/persona/crear", methods=["GET", "POST"])
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
        generos=["No_definido", "Masculino", "Femenino", "Otro"],
        tipos_cuenta=["Administrador", "Cliente"],
        tipos_tarifa=["General", "Menor_edad", "Tercera_edad", "Estudiante", "Discapacitado"],
        estados_cuenta=["Activo", "Inactivo", "Suspendido"],
        usuario=usuario,
    )


@router.route("/persona/editar/<int:id>", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_persona"))
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


@router.route("/persona/ordenar/<atributo>/<orden>")
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


@router.route("/persona/buscar/<atributo>/<criterio>")
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


@router.route("/cuenta/lista")
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


@router.route("/cuenta/crear", methods=["GET", "POST"])
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
                return redirect(url_for("router.crear_cuenta"))
            r = requests.post(
                "http://localhost:8099/api/cuenta/guardar",
                json=data,
                headers={"Content-Type": "application/json"},
            )
            if r.status_code == 200:
                flash("Cuenta creada exitosamente", "success")
                return redirect(url_for("router.lista_cuenta"))
            else:
                flash(f"Error al crear la cuenta: {r.text}", "error")
                return redirect(url_for("router.crear_cuenta"))
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
            return redirect(url_for("router.crear_cuenta"))
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


@router.route("/cuenta/editar/<int:id>", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_cuenta"))
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
            return redirect(url_for("router.lista_cuenta"))
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
        return redirect(url_for("router.lista_cuenta"))


@router.route("/cuenta/eliminar/<int:id>", methods=["POST"])
def eliminar_cuenta(id):
    try:
        r_verificar = requests.get(f"http://localhost:8099/api/cuenta/lista/{id}")
        if r_verificar.status_code != 200:
            flash("Cuenta no encontrada", "error")
            return redirect(url_for("router.lista_cuenta"))
        r = requests.delete(f"http://localhost:8099/api/cuenta/eliminar/{id}")
        if r.status_code == 200:
            flash("Cuenta eliminada exitosamente", "success")
        else:
            flash(f"Error al eliminar la cuenta: {r.text}", "error")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
    return redirect(url_for("router.lista_cuenta"))


@router.route("/cuenta/ordenar/<atributo>/<orden>")
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


@router.route("/cuenta/buscar/<atributo>/<criterio>")
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


@router.route("/pago/lista")
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


@router.route("/pago/crear", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_pago"))
            else:
                flash(
                    f"Error al crear el método de pago: {r.json().get('mensaje', 'Error desconocido')}",
                    "error",
                )
                return redirect(url_for("router.crear_pago"))
        except requests.exceptions.RequestException as e:
            flash(f"Error de conexión: {str(e)}", "error")
            return redirect(url_for("router.crear_pago"))
        except ValueError as e:
            flash("Error en los datos ingresados", "error")
            return redirect(url_for("router.crear_pago"))
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


@router.route("/pago/editar/<int:id>", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_pago"))
            else:
                flash(
                    f"Error al actualizar: {r.json().get('mensaje', 'Error desconocido')}", "error"
                )
                return redirect(url_for("router.editar_pago", id=id))
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for("router.editar_pago", id=id))
    try:
        r_pago = requests.get(f"http://localhost:8099/api/pago/lista/{id}")
        if r_pago.status_code != 200:
            flash("Método de pago no encontrado", "error")
            return redirect(url_for("router.lista_pago"))
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


@router.route("/pago/ordenar/<atributo>/<orden>")
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


@router.route("/pago/buscar/<atributo>/<criterio>")
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


@router.route("/boleto/lista")
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


@router.route("/boleto/crear", methods=["GET", "POST"])
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
        return render_template(
            "crud/boleto/boleto_crear.html", personas=personas, turnos=turnos, usuario=usuario
        )
    except requests.exceptions.RequestException as e:
        flash(f"Error al cargar los datos: {str(e)}", "danger")
        return redirect(url_for("router.lista_boleto"))


@router.route("/boleto/editar/<int:id>", methods=["GET", "POST"])
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


@router.route("/boleto/ordenar/<atributo>/<orden>")
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


@router.route("/boleto/buscar/<atributo>/<criterio>")
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


@router.route("/descuento/lista")
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
        return redirect(url_for("router.administrador"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router.administrador"))


@router.route("/descuento/crear", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_descuento"))
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
        return redirect(url_for("router.lista_descuento"))


@router.route("/descuento/editar/<int:id>", methods=["GET", "POST"])
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
                return redirect(url_for("router.lista_descuento"))
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
        return redirect(url_for("router.lista_descuento"))
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "error")
        return redirect(url_for("router.lista_descuento"))


@router.route("/descuento/eliminar/<int:id>", methods=["POST"])
def eliminar_descuento(id):
    try:
        response = requests.delete(f"http://localhost:8099/api/descuento/eliminar/{id}")
        if response.status_code == 200:
            flash("Descuento eliminado exitosamente", "success")
        else:
            flash("Error al eliminar el descuento", "danger")
    except requests.exceptions.RequestException as e:
        flash(f"Error de conexión: {str(e)}", "danger")
    return redirect(url_for("router.lista_descuento"))


@router.route("/descuento/ordenar/<atributo>/<orden>")
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


@router.route("/descuento/buscar/<atributo>/<criterio>")
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


# Paginas generales


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
