import os
from flask import Flask, request, abort, jsonify
from flask_cors import CORS

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)

    # CORS Setup
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'localhost:5000')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST,\
                              PATCH, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Authorization')

        return response

    return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
