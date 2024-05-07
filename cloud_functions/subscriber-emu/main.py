# import firebase_admin
# from firebase_admin import firestore
# import os
# import base64
# import flask
# from flask import jsonify
# from flask import request
# from flask_cors import CORS
# from google.cloud import pubsub_v1
# from concurrent.futures import TimeoutError

# app = flask.Flask(__name__) # instancia de app
# firebase_admin.initialize_app()
# CORS(app)

# @app.route("/", methods=["POST"])
# def subscriber_emu():
#     """Receive and parse Pub/Sub messages."""
#     envelope = request.get_json()
#     if not envelope:
#         msg = "no Pub/Sub message received"
#         print(f"error: {msg}")
#         return f"Bad Request: {msg}", 400

#     if not isinstance(envelope, dict) or "message" not in envelope:
#         msg = "invalid Pub/Sub message format"
#         print(f"error: {msg}")
#         return f"Bad Request: {msg}", 400

#     pubsub_message = envelope["message"]

#     if isinstance(pubsub_message, dict) and "data" in pubsub_message:
#         data = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()
#         print(f"Message: {data}")

#     return ("", 204)


from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    # Extract Pub/Sub message from request
    envelope = request.get_json()
    message = envelope['message']

    try:
        # Process message
        # ...
        # Acknowledge message with 200 OK
        return '', 200
    except Exception as e:
        # Log exception
        # ...

        # Message not acknowledged, will be retried
        return '', 500

if __name__ == '__main__':
    app.run(port=8080, debug=True)
# def subscriber_emu(event, context):
#     project_id = os.getenv('GCLOUD_PROJECT')
#     subscription_id = "pokedex"
#     # Número de segundos que el suscriptor debe escuchar los mensajes
#     timeout = 5.0

#     subscriber = pubsub_v1.SubscriberClient()
#     subscription_path = subscriber.subscription_path(project_id, subscription_id)

#     def callback(message: pubsub_v1.subscriber.message.Message) -> None:
#         print(f"Received {message.data!r}.")

#     # Limita el suscriptor a tener solo diez mensajes pendientes a la vez.
#     flow_control = pubsub_v1.types.FlowControl(max_messages=10)

#     streaming_pull_future = subscriber.subscribe(
#         subscription_path, callback=callback, flow_control=flow_control
#     )

#     print(f"Listening for messages on {subscription_path}..\n")

#     try:
#         # Cuando `timeout` no está configurado, result() bloqueará indefinidamente,
#         # a menos que se encuentre primero una excepción.
#         streaming_pull_future.result(timeout=timeout)
#     except TimeoutError:
#         streaming_pull_future.cancel()  # Desencadena el apagado.
#         streaming_pull_future.result()  # Bloquea hasta que se complete el apagado.
