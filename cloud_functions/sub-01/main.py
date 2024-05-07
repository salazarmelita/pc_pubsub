from flask import Flask, request
from firebase_functions import https_fn
import base64
import json

app = Flask(__name__)

@app.post("/pokedex")
def receiver():
    try:
        envelope = json.loads(request.data.decode('utf-8'))
        message_codified = envelope['message']["data"]
        message_data = base64.b64decode(message_codified).decode('utf-8')
        print(f"Data: {message_data}")

        return 'success', 200

    except Exception as error:
        return error, 500

@https_fn.on_request(max_instances=10, timeout_sec=120, memory=256, min_instances=0)
def PLG_FV01_REP03_ARQ02_COM_SUB_01(req: https_fn.Request) -> https_fn.Response:
    try:
        with app.request_context(req.environ):
            return app.full_dispatch_request()
    
    except Exception as ex:
        print(str(ex))
        return https_fn.Response("Error al procesar la solicitud", status=500, mimetype="application/json")
