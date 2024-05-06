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
    project_id = os.getenv('GCLOUD_PROJECT')
    topic_id = body.get("topic_name")
    subscription_id = body.get("subscription_name")
    endpoint = "https://us-central1-andreslab-50edf.cloudfunctions.net/subscriber_emu"
    
    if not topic_id:
        return jsonify({"error": "Missing topic_name or message in request"}), 400
        
    if not topic_exists(topic_id):
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(os.getenv('GCLOUD_PROJECT'), topic_id)
        publisher.create_topic(request={"name": topic_path})
    
        try:
            publisher = pubsub_v1.PublisherClient()
            subscriber = pubsub_v1.SubscriberClient()
            topic_path = publisher.topic_path(project_id, topic_id)
            subscription_path = subscriber.subscription_path(project_id, subscription_id)

            push_config = pubsub_v1.types.PushConfig(push_endpoint=endpoint)

            # Wrap the subscriber in a 'with' block to automatically call close() to
            # close the underlying gRPC channel when done.
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
            return jsonify({"status": "success"})
        except Exception as e:
            print(f"Error initializing Pub/Sub client: {e}")

    # Add a return statement for other cases
    return jsonify({"error": "Unknown error occurred"}), 500

@https_fn.on_request(max_instances=10, timeout_sec=120, memory=256, min_instances=0)
def publisher_emu(req: https_fn.Request) -> https_fn.Response:
    try:
        with app.request_context(req.environ):
            return app.full_dispatch_request()
    
    except Exception as ex:
        print(str(ex))
        return https_fn.Response("Error al procesar la solicitud", status=500, mimetype="application/json")
