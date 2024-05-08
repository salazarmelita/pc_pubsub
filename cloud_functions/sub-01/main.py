from flask import Flask, request
import firebase_admin
from firebase_admin import firestore
from flask_cors import CORS
from firebase_functions import https_fn
from google.cloud import pubsub_v1
from datetime import datetime
import os
import base64
import json
import time

app = Flask(__name__)
firebase_admin.initialize_app()
CORS(app)

def topic_exists(topic_name):
    client = pubsub_v1.PublisherClient()
    topic_path = client.topic_path(os.getenv('GCLOUD_PROJECT'), topic_name)
    try:
        client.get_topic(topic=topic_path)
        return True
    except Exception as e:
        return False
    
def publish_message(topic_name, message):

    if not topic_exists(topic_name):
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(os.getenv('GCLOUD_PROJECT'), topic_name)
        publisher.create_topic(request={"name": topic_path})

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(os.getenv('GCLOUD_PROJECT'), topic_name)

    message_json = json.dumps(message)
    message_bytes = message_json.encode('utf-8')
    future = publisher.publish(topic_path, message_bytes)
    future.result()
    return

@firestore.transactional
def perform_transaction(transaction, doc_ref, current_time, pub_seconds):
    # Calcular la diferencia de tiempo en segundos
    current_pub_doc = list(transaction.get(doc_ref))[0]
    current_pub = current_pub_doc.get("last_pub")
    current_pub_format = datetime.fromisoformat(current_pub.strftime("%Y-%m-%d %H:%M:%S.%f"))
    time_difference_seconds = (current_time - current_pub_format).total_seconds()
    print("Tiempo transcurrido desde última publicación:", time_difference_seconds)
    
    if time_difference_seconds > pub_seconds:
        transaction.update(doc_ref, {"last_pub": current_time})
        return True
    return False

@app.post("/pokedex")
def receiver():
    try:
        #Obtener la fecha y hora actual
        current_time = datetime.now()
        envelope = json.loads(request.data.decode('utf-8'))
        message_codified = envelope['message']["data"]
        message_data = base64.b64decode(message_codified).decode('utf-8')

        db = firestore.client()
        plugin_id = "qTikhWtY44z1rjX9I1C3"
        transaction = db.transaction()
        doc_ref = db.collection("rates").document(plugin_id)
        doc_snapshot = doc_ref.get()
        #return "succes", 200
        if doc_snapshot.exists:
            doc_data = doc_snapshot.to_dict()
            dinamic = doc_data.get("dinamic")
            pub_seconds = 60.0 / dinamic
            print(f"Diferencia de tiempo entre cada publicación (tasa de {dinamic} [mensajes/min]): {pub_seconds}")
        
            result = perform_transaction(transaction, doc_ref, current_time, pub_seconds)
            
            if result:
                message_data = json.loads(message_data)
                topic_name = message_data["type"]
                message = {
                    "type": message_data["type"],
                    "pokemon": message_data["pokemon"],
                    "rate": f"{dinamic} msj/min",
                    "count": message_data["count"]
                }
                publish_message(topic_name, message)
                print(f"Mensaje publicado: {message}")
                print(f"Tópico publicado ({topic_name}) dentro del rango de la tasa")
                return 'success', 200
            else:
                return "error", 500
        else:
            return "error", 500

    except Exception as error:
        print(f"Error: {error}")
        return error, 500

@https_fn.on_request(max_instances=10, timeout_sec=120, memory=256, min_instances=0)
def PLG_FV01_REP03_ARQ02_COM_SUB_01(req: https_fn.Request) -> https_fn.Response:
    try:
        with app.request_context(req.environ):
            return app.full_dispatch_request()
    
    except Exception as ex:
        print(str(ex))
        return https_fn.Response("Error al procesar la solicitud", status=500, mimetype="application/json")
