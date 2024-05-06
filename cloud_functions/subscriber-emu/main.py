import os
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError



def subscriber_emu(event, context):
    project_id = os.getenv('GCLOUD_PROJECT')
    subscription_id = "pokedex"
    # Número de segundos que el suscriptor debe escuchar los mensajes
    timeout = 5.0

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        print(f"Received {message.data!r}.")

    # Limita el suscriptor a tener solo diez mensajes pendientes a la vez.
    flow_control = pubsub_v1.types.FlowControl(max_messages=10)

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback, flow_control=flow_control
    )

    print(f"Listening for messages on {subscription_path}..\n")

    try:
        # Cuando `timeout` no está configurado, result() bloqueará indefinidamente,
        # a menos que se encuentre primero una excepción.
        streaming_pull_future.result(timeout=timeout)
    except TimeoutError:
        streaming_pull_future.cancel()  # Desencadena el apagado.
        streaming_pull_future.result()  # Bloquea hasta que se complete el apagado.
