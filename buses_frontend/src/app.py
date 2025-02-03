from flask import Flask
from my_routes.route import router
from my_routes.router_usuario import router_usuario
from my_routes.route_bus import router_bus
from my_routes.route_admin import router_admin


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "tu_clave_secreta"

    app.register_blueprint(router)
    app.register_blueprint(router_usuario)
    app.register_blueprint(router_bus)
    app.register_blueprint(router_admin)

    @app.template_filter("formato_fecha")
    def formato_fecha(fecha):
        if not fecha:
            return ""
        try:
            if isinstance(fecha, str):
                from datetime import datetime

                fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")
                return fecha_obj.strftime("%Y-%m-%d")
            return fecha
        except ValueError:
            return fecha

    return app
