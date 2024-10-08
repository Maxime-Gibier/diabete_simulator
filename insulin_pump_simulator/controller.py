from .insulin_pump import InsulinPump
from .cgm import CGM
from .patient import Patient

class ClosedLoopController:
    def __init__(self, target_glucose, pump, cgm):
        self.target_glucose = target_glucose
        self.pump = pump
        self.cgm = cgm
        self.last_message = ""

    def calculate_insulin_adjustment(self, glucose):
        difference = glucose - self.target_glucose
        adjustment = difference / self.pump.config.insulin_sensitivity_factor
        adjustment = round(adjustment, 2)
        self.last_message = f"Ajustement calculé : {adjustment} U d'insuline"
        return adjustment

    def adjust_basal_rate(self, current_glucose: float) -> float:
        difference = current_glucose - self.target_glucose
        adjustment = difference / self.pump.config.insulin_sensitivity_factor
        new_basal_rate = self.pump.get_basal_rate(0) + adjustment / 24  # Ajuster le taux basal sur 24 heures
        self.pump.config.basal_rates = [new_basal_rate] * 24  # Mettre à jour tous les taux basaux
        self.last_message = f"Taux basal ajusté : {new_basal_rate:.2f} U/h"
        return adjustment

    def calculate_correction_bolus(self, current_glucose: float) -> float:
        difference = current_glucose - self.target_glucose
        correction_bolus = difference / self.pump.config.insulin_sensitivity_factor
        correction_bolus = max(0, correction_bolus)  # Ensure non-negative bolus
        self.last_message = f"Bolus de correction calculé : {correction_bolus:.2f} U"
        return round(correction_bolus, 2)

    def control_loop(self, patient: Patient):
        current_glucose = self.cgm.measure_glucose(patient)
        adjustment = self.adjust_basal_rate(current_glucose)
        self.pump.deliver_basal(int(adjustment))
        
        if current_glucose > 250:
            self.pump.add_alarm("High glucose alert")
        elif current_glucose < 70:
            self.pump.add_alarm("Low glucose alert")