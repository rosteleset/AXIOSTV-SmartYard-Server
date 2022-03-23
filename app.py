from smartyard import create_app
from smartyard.config import get_config

if __name__ == "__main__":
    app, migrate = create_app(get_config())
    app.run(debug=True)
