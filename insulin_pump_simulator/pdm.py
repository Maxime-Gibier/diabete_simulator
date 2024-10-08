from .insulin_pump import InsulinPump
from .controller import ClosedLoopController
from .config import PumpConfig
from datetime import datetime, timedelta

class PDM:
    def __init__(self, pump):
        self.pump = pump
        self.last_alert = ""
        self.last_message = ""
        self.personalized_modes = {}
        self.active_mode = None
        self.glucose_history = []
        self.insulin_dose_history = []
        self.history = []

    def configure_basal_rates(self, basal_rates):
        self.pump.config.basal_rates = basal_rates
        return "Taux basaux configurés avec succès"

    def configure_insulin_to_carb_ratio(self, icr):
        self.pump.config.insulin_to_carb_ratio = icr
        return "Ratio insuline/glucides configuré avec succès"

    def configure_insulin_sensitivity_factor(self, isf):
        self.pump.config.insulin_sensitivity_factor = isf
        return "Facteur de sensibilité à l'insuline configuré avec succès"

    def configure_max_bolus(self, max_bolus):
        self.pump.config.max_bolus = max_bolus
        return "Dose maximale de bolus configurée avec succès"

    def enter_carbs(self, carbs):
        bolus = self.calculate_meal_bolus(carbs)
        self.pump.deliver_bolus(bolus)
        self.last_message = f"Bolus de repas calculé et administré : {bolus} U"
        return bolus

    def calculate_correction_bolus(self, current_glucose, target_glucose):
        bolus = self.pump.calculate_correction_bolus(current_glucose, target_glucose)
        self.history.append(f"Correction bolus calculated: {bolus} U")
        return bolus

    def deliver_bolus(self, amount):
        self.pump.deliver_bolus(amount)
        self.last_message = f"Dose ajustée administrée : {amount:.2f} U"
        self.record_insulin_dose(datetime.now(), amount)

    def get_history(self):
        return self.history

    def configure_personalized_mode(self, mode_name, mode_params):
        self.personalized_modes[mode_name] = mode_params
        return f"Mode personnalisé '{mode_name}' configuré"

    def activate_personalized_mode(self, mode_name):
        if mode_name in self.personalized_modes:
            self.active_mode = mode_name
            mode = self.personalized_modes[mode_name]
            self._adjust_pump_settings(mode)
            return f"Mode personnalisé '{mode_name}' activé"
        else:
            raise ValueError(f"Mode {mode_name} not found")

    def deactivate_personalized_mode(self):
        if self.active_mode:
            self._reset_pump_settings()
            self.active_mode = None
            return "Mode personnalisé désactivé"

    def _adjust_pump_settings(self, mode):
        # Implémentez l'ajustement des paramètres de la pompe ici
        pass

    def _reset_pump_settings(self):
        # Implémentez la réinitialisation des paramètres de la pompe ici
        pass

    def calculate_meal_bolus(self, carbs):
        insulin_to_carb_ratio = self.pump.config.insulin_to_carb_ratio
        bolus = carbs / insulin_to_carb_ratio
        bolus = round(bolus, 1)
        self.last_message = f"Bolus alimentaire calculé : {bolus:.1f} U"
        self.record_insulin_dose(datetime.now(), bolus)
        return bolus

    def administer_meal_bolus(self, carbs):
        bolus = self.calculate_meal_bolus(carbs)
        self.pump.deliver_bolus(bolus)
        self.last_message = f"Bolus de repas administré : {bolus} U"
        return bolus

    def confirm_bolus_administration(self, bolus):
        self.pump.deliver_bolus(bolus)
        self.last_message = f"Bolus de correction de {bolus:.2f} U administré et enregistré"

    def record_glucose(self, date, glucose):
        self.glucose_history.append({"date": date, "glucose": glucose})

    def record_insulin_dose(self, date, dose):
        self.insulin_dose_history.append({"date": date, "dose": dose})

    def check_glucose_limits(self, glucose):
        if glucose > 250:
            self.last_alert = f"Alerte : glycémie critique de {glucose} mg/dL"
        elif glucose < 70:
            self.last_alert = f"Alerte : glycémie basse de {glucose} mg/dL"
        else:
            self.last_alert = ""
        print(f"check_glucose_limits called, last_alert: {self.last_alert}")  # Ligne de débogage

    def check_pump_status(self):
        if self.pump.battery_level < 20:
            self.last_alert = f"Alerte : Batterie faible, niveau actuel à {self.pump.battery_level}%"
        elif self.pump.is_occluded:
            self.last_alert = "Alerte : Obstruction détectée dans le système de délivrance d'insuline"
        else:
            self.last_alert = ""
        print(f"check_pump_status called, last_alert: {self.last_alert}")  # Ligne de débogage

    def get_glucose_history(self, start_date, end_date):
        history = [entry for entry in self.glucose_history if start_date <= entry['date'] <= end_date]
        self.last_message = "Historique de glycémie consulté avec succès"
        return history

    def get_insulin_dose_history(self, start_date=None, end_date=None):
        if start_date is None and end_date is None:
            history = self.insulin_dose_history
        else:
            if start_date is None:
                start_date = datetime.min
            if end_date is None:
                end_date = datetime.max
            history = [entry for entry in self.insulin_dose_history if start_date <= entry['date'] <= end_date]
        self.last_message = "Historique des doses d'insuline consulté avec succès"
        return history