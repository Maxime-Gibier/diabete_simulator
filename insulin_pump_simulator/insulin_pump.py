from .config import PumpConfig  # Ajout du point pour l'importation relative

class InsulinPump:
    def __init__(self, config):
        if isinstance(config, dict):
            self.config = PumpConfig(**config)
        else:
            self.config = config
        self.total_insulin_delivered = 0
        self.last_message = ""
        self.battery_level = 100
        self.is_occluded = False  # Ajout de l'attribut is_occluded

    def get_basal_rate(self, hour):
        return self.config.basal_rates[int(hour) % 24]  # Conversion en entier

    def deliver_basal(self, hour):
        basal_rate = self.get_basal_rate(hour)
        self.total_insulin_delivered += basal_rate
        self.last_message = f"Insuline basale administrée : {basal_rate:.1f} U"
        return basal_rate

    def deliver_bolus(self, dose):
        self.total_insulin_delivered += dose
        self.last_message = f"Bolus de correction administré : {dose:.2f} U"

    def calculate_meal_bolus(self, carbs):
        insulin_to_carb_ratio = self.config.insulin_to_carb_ratio
        bolus = carbs / insulin_to_carb_ratio
        return round(bolus, 2)

    def set_occlusion(self, status: bool):
        self.is_occluded = status
        if status:
            self.last_message = "Alerte : Occlusion détectée"

    def get_current_basal_rate(self):
        return self.config.basal_rates[0]  # Retourne le taux basal actuel (premier élément de la liste)