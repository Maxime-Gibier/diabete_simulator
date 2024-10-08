import numpy as np

class Patient:
    def __init__(self, initial_glucose, insulin_sensitivity, carb_ratio):
        self.glucose_level = initial_glucose
        self.insulin_sensitivity = insulin_sensitivity
        self.carb_ratio = carb_ratio

    def update_glucose_level(self, insulin=0, carbs=0):
        insulin_effect = insulin * self.insulin_sensitivity
        carb_effect = carbs / self.carb_ratio * 10  # Multiplions par 10 pour un effet plus réaliste

        # Appliquons d'abord l'effet des glucides, puis celui de l'insuline
        self.glucose_level += carb_effect
        self.glucose_level -= insulin_effect
        
        # Ajoutons une petite variation aléatoire
        self.glucose_level += np.random.normal(0, 1)
        
        # Assurons-nous que le niveau de glucose ne descend pas en dessous de 0
        self.glucose_level = max(0, self.glucose_level)