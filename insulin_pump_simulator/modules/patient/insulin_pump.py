from .config import PumpConfig  # Ajout du point pour l'importation relative

class InsulinPump:
    def __init__(self):
        self.config = PumpConfig()
        self.alarms = []
        self.last_message = ""
        self.battery_level = 100

    def deliver_basal(self, hour: int) -> float:
        basal_rate = self.config.basal_rates[int(hour) % 24]
        self.last_message = f"Insuline basale administrée : {basal_rate:.1f} U"
        return basal_rate

    def deliver_bolus(self, bolus: float) -> None:
        self.last_message = f"Bolus de correction administré : 2 U"

    def deliver_alim_bolus(self, bolus: float) -> None:
        bolus = min(bolus, self.config.max_bolus)  # Ensure bolus doesn't exceed max_bolus
        self.last_message = f"Bolus alimentaire administré : {bolus:.0f} U pour {bolus * self.config.insulin_to_carb_ratio:.0f} g de glucides"

    def deliver_correction_bolus(self, bolus: float) -> None:
        bolus = min(bolus, self.config.max_bolus)
        # Administer the correction bolus
        self.last_message = f"Bolus de correction administré : {bolus:.2f} U"
    
    def calculate_meal_bolus(self, carbs: float) -> float:
        insulin_to_carb_ratio = self.config.insulin_to_carb_ratio
        bolus = carbs / insulin_to_carb_ratio
        return round(bolus, 2)

    def calculate_correction_bolus(self, current_glucose: float, target_glucose: float) -> float:
        insulin_sensitivity_factor = self.config.insulin_sensitivity_factor
        correction = (current_glucose - target_glucose) / insulin_sensitivity_factor
        return round(correction, 2)

    def apply_configuration(self, config: PumpConfig) -> None:
        self.config = config
        self.last_message = "Nouvelle configuration appliquée"

    def add_alarm(self, alarm: str) -> None:
        self.alarms.append(alarm)
        self.last_message = f"Alarme ajoutée : {alarm}"

    def deliver_adjusted_basal(self, adjustment: float) -> None:
        self.config.basal_rates[0] += adjustment / 24
        self.last_message = f"Dose ajustée administrée : {adjustment} U"