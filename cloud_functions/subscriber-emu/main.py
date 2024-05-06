import os
from google.cloud import pubsub_v1
from firebase_functions import pubsub_fn

def acknowledge_message(project_id, event_id, subscription_id):
    # Configurar el cliente de Pub/Sub
    subscriber = pubsub_v1.SubscriberClient()

    # Obtener el nombre completo de la suscripción
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    # Enviar el acknowledgement al servidor de Pub/Sub
    ack_ids = [event_id]
    subscriber.acknowledge(request={"subscription": subscription_path, "ack_ids": ack_ids})

def count_unacknowledged_messages(project_id, subscription_id):
    try:
        # Configurar el cliente de Pub/Sub
        subscriber = pubsub_v1.SubscriberClient()

        # Construir el nombre completo de la suscripción
        subscription_path = subscriber.subscription_path(project_id, subscription_id)

        # Obtener el estado de la suscripción
        subscription = subscriber.get_subscription(request={"subscription": subscription_path})

        # Obtener el número de mensajes no confirmados
        unacknowledged_messages = subscription.num_undelivered_messages

        print(f"Número de mensajes no confirmados en la suscripción {subscription_path}: {unacknowledged_messages}")
    
    except Exception as e:
        print(f"Error al obtener el número de mensajes no confirmados: {e}")

@pubsub_fn.on_message_published(topic="pokemon")
def subscriber_emu(event: pubsub_fn.CloudEvent[pubsub_fn.MessagePublishedData]) -> None:
    # Obtener el mensaje publicado
    message_data = event.data.message.json

    # Aquí puedes agregar la lógica para procesar el mensaje como desees
    print(f"Mensaje recibido: {message_data}")
    print(f"Mensaje ID: {event.data.message.message_id}")
    print(f"Mensaje subscription: {event.data.subscription}")





    project_id = os.getenv('GCLOUD_PROJECT')
    # Confirmar la recepción del mensaje
    # acknowledge_message(project_id, event.data.message.message_id, event.data.subscription)
    # Contar los mensajes no confirmados
    count_unacknowledged_messages(project_id, event.data.subscription)