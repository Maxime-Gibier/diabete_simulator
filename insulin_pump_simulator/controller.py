from .insulin_pump import InsulinPump
from .cgm import CGM
from .patient import Patient

class ClosedLoopController:
    def __init__(self, target_glucose):
        self.target_glucose = target_glucose
        self.pump = InsulinPump()
        self.cgm = CGM()

    def adjust_basal_rate(self, current_glucose: float) -> float:
        difference = current_glucose - self.target_glucose
        adjustment = round(difference / self.pump.config.insulin_sensitivity_factor, 2)
        new_basal_rate = round(self.pump.config.basal_rates[0] + adjustment / 24, 2)  # Ajuster le taux basal sur 24 heures
        self.pump.config.basal_rates = [new_basal_rate] * 24  # Mettre à jour tous les taux basaux
        self.pump.last_message = f"Ajustement calculé : {adjustment} U d'insuline"
        return adjustment

    def control_loop(self, patient: Patient) -> None:
        current_glucose = self.cgm.measure_glucose(patient)
        adjustment = self.adjust_basal_rate(current_glucose)
        self.pump.deliver_basal(int(adjustment))
        
        if current_glucose > 250:
            self.pump.add_alarm("High glucose alert")
        elif current_glucose < 70:
            self.pump.add_alarm("Low glucose alert")