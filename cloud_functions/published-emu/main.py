import firebase_admin
from firebase_admin import firestore
from firebase_functions import https_fn
import flask
from flask import jsonify
from flask_cors import CORS
from google.cloud import pubsub_v1
from google.cloud.pubsub_v1.types import GetTopicRequest
import os
import json

app = flask.Flask(__name__) # instancia de app
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
    
@app.post("/publish")
def publish():
    body = flask.request.get_json()
    print(body)

    try:
        topic_name = body.get("topic_name")
        message = body.get("message")

        if not topic_name or not message:
            return jsonify({"error": "Missing topic_name or message in request"}), 400
        
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
        return jsonify({"status": "success"})

    except Exception as e:
        print(f"Error initializing Pub/Sub client: {e}")

@https_fn.on_request(max_instances=10, timeout_sec=120, memory=256, min_instances=0)
def pusblisher_emu(req: https_fn.Request) -> https_fn.Response:
    try:
        with app.request_context(req.environ):
            return app.full_dispatch_request()
    
    except Exception as ex:
        print(str(ex))
        return https_fn.Response("Error al procesar la solicitud", status=500, mimetype="application/json")
