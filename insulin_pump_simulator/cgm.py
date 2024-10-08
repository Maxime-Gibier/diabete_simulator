import numpy as np
from .patient import Patient

class CGM:
    def __init__(self):
        self.last_message = ""
        self.glucose_history = []

    def measure_glucose(self, patient):
        glucose = patient.glucose_level
        self.last_message = f"Glycémie mesurée : {glucose:.1f} mg/dL"
        self.glucose_history.append(glucose)
        return glucose

    def get_glucose_history(self):
        return self.glucose_history