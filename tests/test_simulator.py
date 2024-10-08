import pytest
from datetime import datetime, timedelta
from insulin_pump_simulator.simulator import Simulator
from insulin_pump_simulator.patient import Patient
from insulin_pump_simulator.insulin_pump import InsulinPump
from insulin_pump_simulator.cgm import CGM
from insulin_pump_simulator.controller import ClosedLoopController
from insulin_pump_simulator.pdm import PDM
from insulin_pump_simulator.config import PumpConfig

@pytest.fixture
def setup_simulator():
    patient = Patient(initial_glucose=110, insulin_sensitivity=50, carb_ratio=10)
    config = PumpConfig(basal_rates=[0.8]*24, insulin_to_carb_ratio=10, insulin_sensitivity_factor=50, max_bolus=10)
    pump = InsulinPump(config)
    cgm = CGM()
    controller = ClosedLoopController(target_glucose=120, pump=pump, cgm=cgm)
    pdm = PDM(pump)
    simulator = Simulator(patient, pump, cgm, controller, duration=24)
    return simulator

# User Story n°1 : Configuration de la Pompe à Insuline
def test_configure_basal_rates(setup_simulator):
    simulator = setup_simulator
    basal_rates = [0.8, 0.6, 0.5, 0.7, 1.0, 1.2, 0.9, 0.8] + [0.8] * 16
    message = simulator.pdm.configure_basal_rates(basal_rates)
    assert message == "Taux basaux configurés avec succès"
    assert simulator.pump.config.basal_rates == basal_rates

# User Story n°1 : Configuration de la Pompe à Insuline
def test_configure_icr(setup_simulator):
    simulator = setup_simulator
    icr = 10
    message = simulator.pdm.configure_insulin_to_carb_ratio(icr)
    assert message == "Ratio insuline/glucides configuré avec succès"
    assert simulator.pump.config.insulin_to_carb_ratio == icr

# User Story n°1 : Configuration de la Pompe à Insuline
def test_configure_isf(setup_simulator):
    simulator = setup_simulator
    isf = 50
    message = simulator.pdm.configure_insulin_sensitivity_factor(isf)
    assert message == "Facteur de sensibilité à l'insuline configuré avec succès"
    assert simulator.pump.config.insulin_sensitivity_factor == isf

# User Story n°1 : Configuration de la Pompe à Insuline
def test_configure_max_bolus(setup_simulator):
    simulator = setup_simulator
    max_bolus = 10
    message = simulator.pdm.configure_max_bolus(max_bolus)
    assert message == "Dose maximale de bolus configurée avec succès"
    assert simulator.pump.config.max_bolus == max_bolus

# User Story n°2 : Administration de l'Insuline Basale Continue
def test_basal_insulin_administration(setup_simulator):
    simulator = setup_simulator
    simulator.run(60)  # Run for 1 hour
    assert "Insuline basale administrée :" in simulator.pump.last_message

# User Story n°2 : Administration de l'Insuline Basale Continue
def test_glycemic_correction(setup_simulator):
    simulator = setup_simulator
    simulator.patient.glucose_level = 180
    simulator.run(5)  # Run for 5 minutes
    assert "Bolus de correction calculé :" in simulator.controller.last_message

# User Story n°3 : Programmation du Bolus Alimentaire
def test_meal_bolus_calculation(setup_simulator):
    simulator = setup_simulator
    carbs = 60
    bolus = simulator.pdm.calculate_meal_bolus(carbs)
    assert bolus == 6.0
    assert "Bolus alimentaire calculé : 6.0 U" in simulator.pdm.last_message

# User Story n°4 : Fourniture d'un Bolus de Correction
def test_correction_bolus_calculation(setup_simulator):
    simulator = setup_simulator
    simulator.patient.glucose_level = 250
    simulator.run(5)  # Run for 5 minutes to trigger a correction bolus
    assert "Bolus de correction administré :" in simulator.pump.last_message

# User Story n°5 : Mesure de la Glycémie en Continu
def test_continuous_glucose_measurement(setup_simulator):
    simulator = setup_simulator
    simulator.run(30)  # Run for 30 minutes
    assert len(simulator.cgm.glucose_history) > 0
    assert "Glycémie mesurée :" in simulator.cgm.last_message

# User Story n°6 : Alerte des Patients par le PDM
def test_high_glucose_alert(setup_simulator):
    simulator = setup_simulator
    simulator.patient.glucose_level = 300
    simulator.pdm.check_glucose_limits(simulator.patient.glucose_level)
    assert "Alerte : glycémie critique de 300 mg/dL" in simulator.pdm.last_alert

# User Story n°6 : Alerte des Patients par le PDM
def test_low_battery_alert(setup_simulator):
    simulator = setup_simulator
    simulator.pump.battery_level = 10
    simulator.pdm.check_pump_status()
    assert "Alerte : Batterie faible, niveau actuel à 10%" in simulator.pdm.last_alert

# User Story n°7 : Historique des Doses et Glycémie
def test_glucose_history(setup_simulator):
    simulator = setup_simulator
    start_date = datetime(2024, 10, 1)
    for i in range(7):
        date = start_date + timedelta(days=i)
        glucose = 110 + i * 10
        simulator.pdm.record_glucose(date, glucose)
    
    history = simulator.pdm.get_glucose_history(start_date, start_date + timedelta(days=6))
    assert len(history) == 7
    assert history[0]['glucose'] == 110
    assert history[-1]['glucose'] == 170
    assert "Historique de glycémie consulté avec succès" in simulator.pdm.last_message

# User Story n°7 : Historique des Doses et Glycémie
def test_insulin_dose_history(setup_simulator):
    simulator = setup_simulator
    start_date = datetime(2024, 10, 1)
    for i in range(7):
        date = start_date + timedelta(days=i)
        dose = 25 + i
        simulator.pdm.record_insulin_dose(date, dose)
    
    history = simulator.pdm.get_insulin_dose_history(start_date, start_date + timedelta(days=6))
    assert len(history) == 7
    assert history[0]['dose'] == 25
    assert history[-1]['dose'] == 31
    assert "Historique des doses d'insuline consulté avec succès" in simulator.pdm.last_message

# User Story n°8 : Gestion des Modes Personnalisables
def test_configure_sport_mode(setup_simulator):
    simulator = setup_simulator
    sport_mode = {
        "name": "Sport",
        "basal_rate_adjustment": 0.8,  # 20% reduction
        "icr_adjustment": 1.2,  # 20% increase
        "isf_adjustment": 1.2,  # 20% increase
    }
    message = simulator.pdm.configure_personalized_mode("Sport", sport_mode)
    assert message == "Mode personnalisé 'Sport' configuré"
    assert "Sport" in simulator.pdm.personalized_modes

# User Story n°8 : Gestion des Modes Personnalisables
def test_activate_sport_mode(setup_simulator):
    simulator = setup_simulator
    sport_mode = {
        "name": "Sport",
        "basal_rate_adjustment": 0.8,
        "icr_adjustment": 1.2,
        "isf_adjustment": 1.2,
    }
    simulator.pdm.configure_personalized_mode("Sport", sport_mode)
    message = simulator.pdm.activate_personalized_mode("Sport")
    assert message == "Mode personnalisé 'Sport' activé"
    assert simulator.pdm.active_mode == "Sport"

# User Story n°9 : Implémentation d'une Boucle Fermée Automatisée
def test_closed_loop_adjustment(setup_simulator):
    simulator = setup_simulator
    simulator.patient.glucose_level = 150
    simulator.run(5)  # Run for 5 minutes
    assert "Taux basal ajusté :" in simulator.controller.last_message

# Enabler Story n°10 : Simulation et Tests des Composants
def test_simulation_duration(setup_simulator):
    simulator = setup_simulator
    simulator.run(24 * 60)  # Run for 24 hours
    assert simulator.simulation_time == 24 * 60
    assert "Simulation terminée, résultats disponibles" in simulator.last_message

# Enabler Story n°10 : Simulation et Tests des Composants
def test_event_logging(setup_simulator):
    simulator = setup_simulator
    simulator.run(60)  # Run for 1 hour
    assert len(simulator.event_log) > 0
    assert any("administration d'insuline" in event for event in simulator.event_log)

# Enabler Story n°10 : Simulation et Tests des Composants
def test_glucose_value_logging(setup_simulator):
    simulator = setup_simulator
    simulator.run(60)  # Run for 1 hour
    assert len(simulator.glucose_log) == 60

# Enabler Story n°10 : Simulation et Tests des Composants
def test_final_log_generation(setup_simulator):
    simulator = setup_simulator
    simulator.run(24 * 60)  # Run for 24 hours
    final_log = simulator.generate_final_log()
    assert "Événements" in final_log
    assert "Valeurs de glycémie" in final_log
    assert "Doses d'insuline administrées" in final_log