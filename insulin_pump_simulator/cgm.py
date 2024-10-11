import json
from insulin_pump_simulator.patient import Patient

with open('data/sample_input_data.json', 'r') as file:
    data = json.load(file)
    measurement_interval = data['continuous_glucose_measurement']['measurement_interval']
    glucose_critical_limit = data['patient_alerts']['glucose_limits']['upper_critical_limit']



class CGM:
    def __init__(self, measurement_interval: int = measurement_interval):
        self.measurement_interval = measurement_interval
        self.current_glucose = 0
        self.last_message = ""

    def measure_glucose(self, patient: Patient) -> float:
        from insulin_pump_simulator.pdm import PDM
        pdm = PDM(target_glucose=120)

        self.current_glucose = patient.glucose_level
        self.last_message = "Données de glycémie transmises au contrôleur"
        
        if self.current_glucose > glucose_critical_limit:
            pdm.add_alarm("High glucose alert")
            pdm.pump.last_message = f"Alerte : glycémie critique de {self.current_glucose} mg/dL"
        return self.current_glucose, pdm.pump.last_message, pdm.pump.alarms