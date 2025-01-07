import random
import time
import warnings
warnings.filterwarnings("ignore", category=Warning)  # Ignorer les avertissements

from modules.display.main import Display
from modules.patient.pdm import GlucoseSensor, PDM
from modules.patient.cgm import CGM
from modules.patient.patient import Patient
import requests
from fastapi.testclient import TestClient
from modules.data_platform.main import app as platform_app
from modules.cloud.main import app as cloud_app
import pika
import json
import threading

# Configuration RabbitMQ
RABBITMQ_HOST = "localhost"
QUEUE_NAME = "cloud_data"
STOP_THREAD = False

def visual_separator(title):
    """Affiche une séparation visuelle pour les étapes."""
    print("\n" + "=" * 50)
    print(f"{title:^50}")
    print("=" * 50)

def test_display_initialization():
    """Tester l'initialisation du dispositif d'affichage."""
    visual_separator("Test : Initialisation du Dispositif d'Affichage")
    display = Display()
    assert isinstance(display, Display), "[TEST ÉCHEC] Le dispositif d'affichage n'a pas été correctement initialisé."
    print("[TEST SUCCÈS] Le dispositif d'affichage a été initialisé avec succès.")

def test_sensor_initialization():
    """Tester l'initialisation du capteur de glucose."""
    visual_separator("Test : Initialisation du Capteur de Glucose")
    display = Display()
    sensor = GlucoseSensor(display)
    assert isinstance(sensor, GlucoseSensor), "[TEST ÉCHEC] Le capteur de glucose n'a pas été correctement initialisé."
    print("[TEST SUCCÈS] Le capteur de glucose a été initialisé avec succès.")

def test_glucose_sensor_to_display(num_simulations=10):
    """Tester l'interaction entre le capteur de glucose et le dispositif d'affichage."""
    visual_separator("Test : Simulation de l'envoi de données de glucose")
    display = Display()
    sensor = GlucoseSensor(display)

    # Simuler et envoyer les données de glucose spécifiées par num_simulations
    for i in range(num_simulations):
        print(f"[TEST] Simulation #{i + 1}")
        sensor.simulate_and_send_data()
        time.sleep(1)

    # Vérifier les données reçues
    received_data = display.get_all_data()
    assert len(received_data) == num_simulations, f"[TEST ÉCHEC] Le dispositif d'affichage n'a pas reçu toutes les données ({num_simulations} attendues)."
    print(f"[TEST SUCCÈS] Le dispositif d'affichage a reçu toutes les données ({num_simulations}).")

    # Afficher les données reçues
    print("\n[TEST] Données reçues par le dispositif d'affichage :")
    for idx, value in enumerate(received_data, 1):
        print(f" - Donnée #{idx} : {value} mg/dL")

    # Vérifier les seuils critiques
    visual_separator("Test : Détection des Seuils Critiques")
    pdm = PDM(target_glucose=120)
    for idx, value in enumerate(received_data, 1):
        # Utiliser le CGM pour mesurer et obtenir les alertes via le PDM
        cgm = CGM()
        patient = Patient(initial_glucose=value)
        glucose_level, message, alarms = cgm.measure_glucose(patient)
        
        if alarms:
            print(f"\033[91m[ALERTE] Alarmes actives : {', '.join(alarms)}")
            print(f"[ALERTE] Message : {message}\033[0m")
        else:
            print(f"Test #{idx} : [OK] Niveau de glucose : {value} mg/dL")

# Tester l'API REST de la plateforme
def test_platform_to_cloud():
    visual_separator("Test : Connexion de la Plateforme au Cloud")

    # Créer les clients de test pour la plateforme et le cloud
    platform_client = TestClient(platform_app)
    cloud_client = TestClient(cloud_app)

    # Données de test
    test_data = {
        "glucose_level": 150,
        "timestamp": "2023-12-20T10:00:00",
        "device_id": "CGM_001"
    }

    # Envoyer les données via la plateforme
    platform_response = platform_client.post("/send_to_cloud", json=test_data)
    
    # Vérifier la réponse de la plateforme
    assert platform_response.status_code == 200, "[TEST ÉCHEC] La plateforme n'a pas réussi à envoyer les données"
    print("[TEST SUCCÈS] La plateforme a envoyé les données au cloud")

    # Envoyer directement au cloud pour vérifier la réception
    cloud_response = cloud_client.post("/cloud_data", json=test_data)
    
    # Vérifier la réponse du cloud
    assert cloud_response.status_code == 200, "[TEST ÉCHEC] Le cloud n'a pas reçu les données"
    assert cloud_response.json()["status"] == "success", "[TEST ÉCHEC] Le cloud n'a pas confirmé la réception"
    print(f"[TEST SUCCÈS] Le cloud a bien reçu les données : {test_data}")

def publish_message_to_queue(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=json.dumps(message))
    print(f"[TEST] Message publié dans la queue {QUEUE_NAME} : {message}")
    connection.close()

def consume_message_from_queue():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        global STOP_THREAD
        data = json.loads(body)
        print(f"[TEST] Message consommé depuis la queue {QUEUE_NAME} : {data}")
        assert "glucose_level" in data, "[TEST ÉCHEC] Le message ne contient pas 'glucose_level'."
        print("[TEST SUCCÈS] Le message est valide.")
        STOP_THREAD = True
        channel.stop_consuming()

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    print("[TEST] En attente de messages dans la queue...")
    channel.start_consuming()

# Fonction pour tester la connexion RabbitMQ
def test_platform_to_cloud_with_rabbitmq():
    visual_separator("Test : Connexion Plateforme au Cloud via RabbitMQ")
    message = {"glucose_level": 150}
    global STOP_THREAD
    STOP_THREAD = False

    # Lancer le consommateur dans un thread séparé
    consumer_thread = threading.Thread(target=consume_message_from_queue)
    consumer_thread.daemon = True  # Le thread s'arrêtera quand le programme principal s'arrête
    consumer_thread.start()

    # Pause pour s'assurer que le consommateur est prêt
    time.sleep(1)

    # Publier un message
    publish_message_to_queue(message)

    # Attendre que le message soit consommé
    timeout = 5  # timeout de 5 secondes
    start_time = time.time()
    while not STOP_THREAD and time.time() - start_time < timeout:
        time.sleep(0.1)

    if not STOP_THREAD:
        print("[AVERTISSEMENT] Timeout atteint en attendant le message RabbitMQ")


def wait_for_key():
    """Attend silencieusement l'appui d'une touche."""
    input()

if __name__ == "__main__":
    try:
        visual_separator("DÉBUT DES TESTS")
        wait_for_key()
        
        # Tests de connexion
        test_platform_to_cloud()
        wait_for_key()
        
        # Tests fonctionnels
        test_display_initialization()
        wait_for_key()
        
        test_sensor_initialization()
        wait_for_key()
        
        test_glucose_sensor_to_display()
        wait_for_key()
        
        visual_separator("FIN DES TESTS")
        print("[SUCCÈS] Tous les tests ont réussi!")
    except Exception as e:
        print(f"[ÉCHEC] Une erreur s'est produite : {str(e)}")