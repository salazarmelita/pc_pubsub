from google.cloud import pubsub_v1
from firebase_functions import pubsub_fn

@pubsub_fn.on_message_published(topic="fire")
def subscriber(event: pubsub_fn.CloudEvent[pubsub_fn.MessagePublishedData]) -> None:
    # Obtener el mensaje publicado
    message_data = event.data.message.json
    print(f"Mensaje recibido: {message_data}")
