from bottle import default_app

from .api import api_app


app = default_app()
app.mount('/api', api_app)


def run():
    app.run(host='0.0.0.0', port=8080, server='paste', reloader=False, debug=True)
