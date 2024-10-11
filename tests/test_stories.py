from insulin_pump_simulator.pdm import PDM
from insulin_pump_simulator.config import PumpConfig
from insulin_pump_simulator.cgm import CGM
from insulin_pump_simulator.controller import ClosedLoopController
from insulin_pump_simulator.patient import Patient
from insulin_pump_simulator.insulin_pump import InsulinPump
import json

with open('data/sample_input_data.json', 'r') as file:
    data = json.load(file)
    config = data['pump_configuration']

# Test user story 1 ---------------------------------------------------------------------------------------------------------------
def test_configure_basal_rates():
    pdm = PDM(120)

    basal_rates = [0.8, 0.6, 0.5, 0.7, 1.0, 1.2, 0.9, 0.8] + [0.8] * 16 
    pdm.apply_new_config(basal_rates)

    assert pdm.pump.config == basal_rates, "Les taux basaux ne sont pas correctement appliqués à la pompe à insuline"
    print("User story 1 : Les taux basaux sont correctement configurés")

def test_configure_insulin_carb_ratio():
    pdm = PDM(120)

    new_icr = 10
    pdm.apply_new_config(PumpConfig(insulin_to_carb_ratio=new_icr))

    assert pdm.config.insulin_to_carb_ratio == new_icr, "Le ratio insuline/glucides n'est pas correctement configuré"
    assert pdm.pump.config.insulin_to_carb_ratio == new_icr, "Le ratio insuline/glucides n'est pas correctement appliqué à la pompe"
    print("User story 1 : Le ratio insuline/glucides est correctement configuré")

def test_configure_max_bolus():
    pdm = PDM(120)

    max_bolus = 10
    pdm.apply_new_config(PumpConfig(max_bolus=max_bolus))

    assert pdm.config.max_bolus == max_bolus, "La dose maximale de bolus n'est pas correctement configurée"
    assert pdm.pump.config.max_bolus == max_bolus, "La dose maximale de bolus n'est pas correctement appliquée à la pompe"
    print("User story 1 : La dose maximale de bolus est correctement configurée")


# Test user story 2 ---------------------------------------------------------------------------------------------------------------
def test_basal_rate_adjustment():
    pdm = PDM(120)
    pdm.apply_new_config(PumpConfig(basal_rates=[0.8] * 24))

    hour = 0
    basal_rate = pdm.pump.deliver_basal(hour)

    assert basal_rate == 0.8, f"Le taux basal administré devrait être 0.8 U, mais est {basal_rate} U"
    assert pdm.pump.last_message == "Insuline basale administrée : 0.8 U", "Le message d'administration basale est incorrect"
    print("User story 2 : Le taux basale est correctement ajusté")

def test_cgm_based_correction():
    pdm = PDM(120)
    pdm.apply_new_config(PumpConfig(insulin_sensitivity_factor=30))

    current_glucose = 180
    target_glucose = 120

    correction_bolus = pdm.pump.calculate_correction_bolus(current_glucose, target_glucose)
    pdm.pump.deliver_bolus(correction_bolus)

    assert correction_bolus == 2, f"Le bolus de correction devrait être 2 U, mais est {correction_bolus} U"
    assert pdm.pump.last_message == "Bolus de correction administré : 2 U", "Le message de bolus de correction est incorrect"
    print("User story 2 : Le bolus de correction est correctement ajusté")


# Test user story 3 ---------------------------------------------------------------------------------------------------------------
def test_meal_bolus_administration():
    pdm = PDM(120)
    pdm.apply_new_config(PumpConfig(insulin_to_carb_ratio=10))
    carbs = 60

    meal_bolus = pdm.pump.calculate_meal_bolus(carbs)

    assert meal_bolus == 6, f"Le bolus alimentaire devrait être 6 U, mais est {meal_bolus} U"

    pdm.pump.deliver_alim_bolus(meal_bolus)

    expected_message = "Bolus alimentaire administré : 6 U pour 60 g de glucides"
    assert pdm.pump.last_message == expected_message, f"Le message de bolus alimentaire est incorrect. Attendu: '{expected_message}', Obtenu: '{pdm.pump.last_message}'"
    print("User story 3 : Le bolus alimentaire est correctement administré")


# Test user story 4
def test_high_glucose_correction_bolus():
    pdm = PDM(100)
    pdm.apply_new_config(PumpConfig(insulin_sensitivity_factor=40))

    current_glucose = 250
    target_glucose = 100

    correction_bolus = pdm.pump.calculate_correction_bolus(current_glucose, target_glucose)

    assert correction_bolus == 3.75, f"Le bolus de correction devrait être 3.75 U, mais est {correction_bolus} U" 
    
    pdm.pump.deliver_correction_bolus(correction_bolus)

    expected_message = "Bolus de correction administré : 3.75 U"
    assert pdm.pump.last_message == expected_message, f"Le message de bolus de correction est incorrect. Attendu: '{expected_message}', Obtenu: '{pdm.pump.last_message}'"
    print("User story 4 : Le bolus de correction est correctement ajusté")


# Test user story 5 ---------------------------------------------------------------------------------------------------------------
def test_cgm_measurement_every_5_minutes():
    cgm = CGM()
    controller = ClosedLoopController(target_glucose=100)
    
    glucose_data = [110, 112, 115, 118, 120, 123]
    
    for i, glucose in enumerate(glucose_data):

        patient = Patient(initial_glucose=glucose)
        measured_glucose = cgm.measure_glucose(patient)

        assert measured_glucose[0] == glucose, f"La glycémie mesurée à {i*5} minutes devrait être {glucose} mg/dL, mais est {measured_glucose} mg/dL"
        assert cgm.last_message == "Données de glycémie transmises au contrôleur", f"Le message de transmission des données est incorrect à {i*5} minutes"
    print("User story 5 : La mesure de glycémie toutes les 5 minutes est correcte")


# Tests user story 6 ---------------------------------------------------------------------------------------------------------------
def test_high_glucose_notification():
    pdm = PDM(120)
    cgm = CGM()
    controller = ClosedLoopController(target_glucose=100)
    
    # Simuler une glycémie élevée
    patient = Patient()
    patient.glucose_level = 300
    data = cgm.measure_glucose(patient)
    
    assert 'High glucose alert' == data[2][0], "L'alerte de glycémie élevée n'a pas été ajoutée"
    expected_message = "Alerte : glycémie critique de 300 mg/dL"

    assert data[1] == expected_message, f"Le message d'alerte est incorrect. Attendu: '{expected_message}', Obtenu: '{pdm.pump.last_message}'"
    print("User story 6 : La notification de glycémie élevée est correcte")

def test_low_battery_alert():
    pdm = PDM(120)
    
    # Simuler un niveau de batterie faible
    pdm.pump.battery_level = 10
    
    # Vérifier le niveau de batterie
    pdm.check_battery_level()
    
    # Vérifier que l'alerte a été ajoutée
    assert "Low battery alert" in pdm.pump.alarms, "L'alerte de batterie faible n'a pas été ajoutée"
    
    # Vérifier le message d'alerte
    expected_message = "Alerte : Batterie faible, niveau actuel à 10 %"
    assert pdm.pump.last_message == expected_message, f"Le message d'alerte est incorrect. Attendu: '{expected_message}', Obtenu: '{pdm.pump.last_message}'"
    print("User story 6 : La notification de batterie faible est correcte")

# Tests user story 7 ---------------------------------------------------------------------------------------------------------------
from datetime import datetime, timedelta

def test_glucose_history_consultation():
    pdm = PDM(120)
    history = pdm.view_glucose_history()
    assert pdm.last_message == "Historique de glycémie consulté avec succès", "Le message de succès n'est pas correct"
    
    for i, (data) in enumerate(history):
        expected = {"date": data['date'], "glucose": data['glucose']}
        assert history[i] == expected, f"La ligne {i} de l'historique n'est pas correcte"
    
    print("User story 7 : La consultation de l'historique de la glycémie est correcte")

def test_insulin_dose_history_consultation():
    pdm = PDM(120)
    history = pdm.view_insulin_dose_history()
    assert pdm.last_message == "Historique de glycémie consulté avec succès", "Le message de succès n'est pas correct"
    
    for i, (data) in enumerate(history):
        expected = {"date": data['date'], "dose": data['dose']}
        assert history[i] == expected, f"La ligne {i} de l'historique n'est pas correcte"
    
    print("User story 7 : La consultation de l'historique des doses d'insuline est correcte")


# Test user story 8 ---------------------------------------------------------------------------------------------------------------
def test_configure_sport_mode():
    pdm = PDM(120)
    
    # Configurer le mode Sport
    pdm.set_mode("Sport", {"basal_rate_adjustment": 0.8})
    
    # Vérifier que le mode a été correctement enregistré
    assert "Sport" in pdm.config.modes, "Le mode 'Sport' n'a pas été enregistré"
    assert pdm.config.modes["Sport"]["basal_rate_adjustment"] == 0.8, "La réduction basale n'est pas correcte"
    
    # Vérifier le message de confirmation
    expected_message = "Mode 'Sport' configuré avec succès"
    assert pdm.last_message == expected_message, f"Le message de confirmation est incorrect. Attendu: '{expected_message}', Obtenu: '{pdm.last_message}'"
    
    print("User story 8 : La configuration du mode personnalisé 'Sport' est correcte")

def test_activate_sport_mode():
    pdm = PDM(120)
    
    # Configurer le mode Sport
    pdm.activate_mode("Sport")
    
    mode = pdm.get_mode()
    # Vérifier que le mode a été activé
    assert mode[0] == "Sport", "Le mode 'Sport' n'a pas été activé"
    
    # Vérifier que les paramètres ont été appliqués
    assert pdm.pump.config.basal_rates == [round(rate * 0.8, 2) for rate in config["basal_rates"]], "Les taux basaux n'ont pas été ajustés correctement"
    # Vérifier le message de confirmation
    expected_message = "Mode 'Sport' activé avec succès"
    assert pdm.pump.last_message == expected_message, f"Le message de confirmation est incorrect. Attendu: '{expected_message}', Obtenu: '{pdm.pump.last_message}'"
    
    print("User story 8 : L'activation du mode personnalisé 'Sport' est correcte")

def test_confirm_sport_mode_active():
    pdm = PDM(120)

    pdm.activate_mode("Sport")
    
    mode = pdm.get_mode()
    # Vérifier le message de confirmation
    expected_message = "Mode 'Sport' est actuellement actif"
    assert mode[1] == expected_message, f"Le message de confirmation est incorrect. Attendu: '{expected_message}', Obtenu: '{mode[1]}'"
    
    print("User story 8 : La confirmation du mode 'Sport' actif est correcte")


# Test user story 9 ---------------------------------------------------------------------------------------------------------------
def test_cgm_measurement():
    patient = Patient(initial_glucose=150)
    cgm = CGM()
    controller = ClosedLoopController(target_glucose=100)
    
    glucose = cgm.measure_glucose(patient)
    
    assert glucose[0] == 150, f"La mesure de glycémie devrait être 150 mg/dL, mais est {glucose[0]} mg/dL"
    assert cgm.last_message == "Données de glycémie transmises au contrôleur", "Le message d'envoi des données est incorrect"
    print("User story 9 : La mesure de glycémie par le CGM est correcte")

def test_insulin_dose_adjustment():
    controller = ClosedLoopController(target_glucose=100)
    controller.pump.config.insulin_sensitivity_factor = 30
    
    adjustment = controller.adjust_basal_rate(150)
    
    expected_adjustment = round(1.67, 2)
    assert adjustment == expected_adjustment, f"L'ajustement calculé devrait être {expected_adjustment} U, mais est {adjustment} U"
    assert controller.pump.last_message == f"Ajustement calculé : {expected_adjustment} U d'insuline", "Le message d'ajustement calculé est incorrect"
    print("User story 9 : L'ajustement de la dose d'insuline est correct")

def test_adjusted_dose_administration():
    controller = ClosedLoopController(target_glucose=100)
    adjustment = 1.67
    
    controller.pump.deliver_adjusted_basal(adjustment)
    
    assert controller.pump.last_message == f"Dose ajustée administrée : {adjustment} U", "Le message d'administration de la dose ajustée est incorrect"
    print("User story 9 : L'administration de la dose ajustée est correcte")


# Test user story 10 ---------------------------------------------------------------------------------------------------------------

def test_simulate_interaction():
    patient = Patient(initial_glucose=110)
    pump = InsulinPump()
    cgm = CGM()
    controller = ClosedLoopController(target_glucose=100)
    
    # Simulate for 24 hours (assuming 5-minute intervals)
    simulation_duration = 24 * 12  # 12 measurements per hour
    glucose_data = []
    insulin_data = []
    
    for _ in range(simulation_duration):
        current_glucose = cgm.measure_glucose(patient)[0]
        glucose_data.append(current_glucose)
        
        adjustment = controller.adjust_basal_rate(current_glucose)
        pump.deliver_adjusted_basal(adjustment)
        insulin_data.append(adjustment)
        
        # Update patient's glucose level based on insulin delivered
        patient.update_glucose_level(insulin=adjustment)
    
    assert len(glucose_data) == simulation_duration, "Glucose data should be recorded for the entire simulation"
    assert len(insulin_data) == simulation_duration, "Insulin data should be recorded for the entire simulation"
    
    print("User story 10 : La simulation d'interaction est correcte")

def test_meal_bolus_calculation():
    pump = InsulinPump()
    pump.config.insulin_to_carb_ratio = 10  # Set ICR to 10
    
    carbs = 60
    expected_bolus = 6  # 60g / 10 (ICR) = 6U
    
    calculated_bolus = pump.calculate_meal_bolus(carbs)
    
    assert calculated_bolus == expected_bolus, f"Le bolus calculé devrait être {expected_bolus}U, mais est {calculated_bolus}U"
    print("User story 10 : Le calcul du bolus alimentaire est correct")


if __name__ == "__main__":
    all_tests_passed = True
    try:
        test_configure_basal_rates()
        test_configure_insulin_carb_ratio()
        test_configure_max_bolus()
        test_basal_rate_adjustment()
        test_cgm_based_correction()
        test_meal_bolus_administration()
        test_high_glucose_correction_bolus()
        test_cgm_measurement_every_5_minutes()
        test_high_glucose_notification()
        test_low_battery_alert()
        test_glucose_history_consultation()
        test_insulin_dose_history_consultation()
        test_configure_sport_mode()
        test_activate_sport_mode()
        test_confirm_sport_mode_active()
        test_cgm_measurement()
        test_insulin_dose_adjustment()
        test_adjusted_dose_administration()
        test_simulate_interaction()
        test_meal_bolus_calculation()

    except AssertionError as e:
        print(f"Le test a échoué : {str(e)}")
        all_tests_passed = False
    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {str(e)}")
        all_tests_passed = False

    if all_tests_passed:
        print("Tous les tests ont réussi!")