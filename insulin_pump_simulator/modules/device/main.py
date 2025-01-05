import pika
import json

# Configuration RabbitMQ
RABBITMQ_HOST = "localhost"
COMMAND_QUEUE = "device_commands"

def send_command(dosage):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=COMMAND_QUEUE)

    command = {"dosage": dosage}
    channel.basic_publish(exchange="", routing_key=COMMAND_QUEUE, body=json.dumps(command))
    connection.close()
    print(f"Dispositif tiers - Commande envoyée : {command}")

if __name__ == "__main__":
    send_command(dosage=5.0)
