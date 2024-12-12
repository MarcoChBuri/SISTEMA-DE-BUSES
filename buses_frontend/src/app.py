from datetime import datetime
from flask import Flask

def create_app():
    app = Flask(__name__, instance_relative_config=False)
    
    # Registrar el filtro de template dentro del contexto de la app
    @app.template_filter('timestamp_to_date')
    def timestamp_to_date(value):
        if not value:
            return ""
        try:
            return datetime.fromtimestamp(int(value)/1000).strftime('%Y-%m-%d')
        except:
            return ""

    # Registrar blueprint
    with app.app_context():
        from routes.route import router
        app.register_blueprint(router)
        
    return app