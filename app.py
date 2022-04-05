"""Сервис системы Умный двор"""
import smartyard

def create_app():
    """Создание Flask-приложения"""
    config = smartyard.config.get_config()
    app, _ = smartyard.create_app(config)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
