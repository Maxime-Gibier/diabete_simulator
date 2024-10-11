import json

with open('data/sample_input_data.json', 'r') as file:
    data = json.load(file)
    patient_data = data['basal_insulin_administration']

class Patient:
    def __init__(self, initial_glucose = patient_data["initial_glucose"], insulin_sensitivity = patient_data["cgm_correction"]["insulin_sensitivity_factor"], carb_sensitivity = 1):
        self.initial_glucose = initial_glucose
        self.glucose_level = initial_glucose
        self.insulin_sensitivity = insulin_sensitivity
        self.carb_sensitivity = carb_sensitivity

    def update_glucose_level(self, insulin=0, carbs=0):
        insulin_effect = insulin * self.insulin_sensitivity
        carb_effect = carbs * self.carb_sensitivity

        # Appliquons d'abord l'effet des glucides, puis celui de l'insuline
        self.glucose_level += carb_effect
        self.glucose_level -= insulin_effect
        
        # Assurons-nous que le niveau de glucose ne descend pas en dessous de 0
        self.glucose_level = max(0, self.glucose_level)

    def add_carbs(self, carbs):
        self.update_glucose_level(carbs=carbs)