import pika
import json

# Configuration RabbitMQ
RABBITMQ_HOST = "localhost"
GLUCOSE_QUEUE = "glucose_data"
PLATFORM_QUEUE = "platform_data"

def consume_and_publish():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=GLUCOSE_QUEUE)
    channel.queue_declare(queue=PLATFORM_QUEUE)

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f"Dispositif d'affichage - Données reçues : {data['glucose_level']} mg/dL")
        # Publier à la plateforme
        channel.basic_publish(exchange="", routing_key=PLATFORM_QUEUE, body=json.dumps(data))
        print("Dispositif d'affichage - Données envoyées à la plateforme.")

    channel.basic_consume(queue=GLUCOSE_QUEUE, on_message_callback=callback, auto_ack=True)
    print("Dispositif d'affichage - En attente des données de glucose...")
    channel.start_consuming()

if __name__ == "__main__":
    consume_and_publish()

class Display:
    def __init__(self):
        self.received_data = []  # Stockage temporaire des données

    def receive_glucose_data(self, glucose_level):
        # Traiter et afficher les données reçues
        self.received_data.append(glucose_level)
        print(f"[DISPLAY] Niveau de glucose reçu : {glucose_level} mg/dL")

    def get_all_data(self):
        # Retourne toutes les données reçues
        return self.received_data

