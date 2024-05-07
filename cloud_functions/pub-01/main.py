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

def topic_exists(project_id, topic_id):
    client = pubsub_v1.PublisherClient()
    
    
    topic_path = client.topic_path(project_id, topic_id)
    try:
        client.get_topic(topic=topic_path)
        return True
    except Exception as e:
        return False
    
def get_pubsub_data(body):
    project_id = os.getenv('GCLOUD_PROJECT')
    topic_id = body.get("topic_id")
    subscription_id = body.get("subscription_id")
    endpoint = f"https://us-central1-{project_id}.cloudfunctions.net/PLG_FV01_REP03_ARQ02_COM_SUB_01/{subscription_id}"
    message = body.get("message")
    return project_id, topic_id, subscription_id, endpoint, message

@app.post("/publish")
def publish():
    try:
        body = flask.request.get_json()
        project_id, topic_id, subscription_id, endpoint, message = get_pubsub_data(body)
        print(body)
        
        if not topic_id or not message:
            return jsonify({"error": "Missing topic_id or message in request"}), 400

        if not topic_exists(project_id, topic_id):
            publisher = pubsub_v1.PublisherClient()
            subscriber = pubsub_v1.SubscriberClient() 
            
            topic_path = publisher.topic_path(project_id, topic_id)
            subscription_path = subscriber.subscription_path(project_id, subscription_id) 
            
            push_config = pubsub_v1.types.PushConfig(push_endpoint=endpoint)
            publisher.create_topic(request={"name": topic_path})
            
            with subscriber:
                subscription = subscriber.create_subscription(
                    request={
                        "name": subscription_path,
                        "topic": topic_path,
                        "push_config": push_config,
                    }
                )
                print(f"Push subscription created: {subscription}.")
                print(f"Endpoint for subscription is: {endpoint}")

        publisher = pubsub_v1.PublisherClient()
        
        topic_path = publisher.topic_path(project_id, topic_id)

        message_json = json.dumps(message)
        message_bytes = message_json.encode('utf-8')
        future = publisher.publish(topic_path, message_bytes)
        
        future.result()
        return jsonify({"status": "success"})

    except Exception as e:
        print(f"Error initializing Pub/Sub client: {e}")
        
@app.post("/publish_10")
def publish_10():
    try:
        body = flask.request.get_json()
        project_id, topic_id, subscription_id, endpoint, message = get_pubsub_data(body)
        print(body)
        
        if not topic_id or not message:
            return jsonify({"error": "Missing topic_id or message in request"}), 400

        if not topic_exists(project_id, topic_id):
            publisher = pubsub_v1.PublisherClient()
            subscriber = pubsub_v1.SubscriberClient()

            topic_path = publisher.topic_path(project_id, topic_id)
            subscription_path = subscriber.subscription_path(project_id, subscription_id)

            push_config = pubsub_v1.types.PushConfig(push_endpoint=endpoint)
            publisher.create_topic(request={"name": topic_path})

            with subscriber:
                subscription = subscriber.create_subscription(
                    request={
                        "name": subscription_path,
                        "topic": topic_path,
                        "push_config": push_config,
                    }
                )
                print(f"Push subscription created: {subscription}.")
                print(f"Endpoint for subscription is: {endpoint}")

        publisher = pubsub_v1.PublisherClient()

        topic_path = publisher.topic_path(project_id, topic_id)

        for i in range(1, 11):  # Publicar el mensaje 10 veces
            message_with_count = message.copy()  
            message_with_count["count"] = i
            message_json = json.dumps(message_with_count)
            message_bytes = message_json.encode('utf-8')
            future = publisher.publish(topic_path, message_bytes)
            future.result()

        return jsonify({"status": "success"})

    except Exception as e:
        print(f"Error initializing Pub/Sub client: {e}")

@https_fn.on_request(max_instances=10, timeout_sec=120, memory=256, min_instances=0)
def PLG_FV01_REP03_ARQ02_COM_PUB_01(req: https_fn.Request) -> https_fn.Response:
    try:
        with app.request_context(req.environ):
            return app.full_dispatch_request()

    except Exception as ex:
        print(str(ex))
        return https_fn.Response("Error al procesar la solicitud", status=500, mimetype="application/json")