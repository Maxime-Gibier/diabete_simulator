from datetime import datetime, timedelta
from .patient import Patient
from .insulin_pump import InsulinPump
from .cgm import CGM
from .controller import ClosedLoopController
from .pdm import PDM
from .config import PumpConfig

class Simulator:
    def __init__(self, duration: int):
        self.patient = Patient()
        self.pump = InsulinPump()
        self.cgm = CGM()
        self.controller = ClosedLoopController(self.pump)
        self.duration = duration
        self.event_log = []
        self.simulation_time = 0
        self.glucose_log = {}
        self.pdm = PDM(pump)
        self.start_time = datetime.now()

    def calculate_meal_bolus(self, carbs):
        bolus = self.pdm.calculate_meal_bolus(carbs)
        self.event_log.append(f"Bolus alimentaire calculé : {bolus:.1f} U")
        return bolus

    def run_simulation(self, duration: int):
        self.insulin_log = {}
        for _ in range(duration):
            self.simulation_time += 1
            glucose = self.cgm.measure_glucose(self.patient)
            self.glucose_log[self.simulation_time] = glucose
            adjustment = self.controller.adjust_basal_rate(glucose)
            basal_dose = self.pump.deliver_basal(self.simulation_time % 24)
            self.insulin_log[self.simulation_time] = basal_dose
            self.pdm.record_insulin_dose(datetime.now(), basal_dose)
            self.patient.update_glucose_level()
            self.event_log.append(f"Time {self.simulation_time}: Glucose {glucose:.2f}, Adjustment {adjustment:.2f}")
            if self.simulation_time % 60 == 0:  # Every hour
                self.event_log.append(f"Time {self.simulation_time}: administration d'insuline")
            self.event_log.append(f"Time {self.simulation_time}: mesure de glycémie")
            
            if glucose > 170:
                correction_bolus = self.controller.calculate_correction_bolus(glucose)
                self.pump.deliver_bolus(correction_bolus)
                self.insulin_log[self.simulation_time] += correction_bolus
                self.pdm.record_insulin_dose(datetime.now(), correction_bolus)
                self.event_log.append(f"Time {self.simulation_time}: Bolus de correction calculé : {correction_bolus:.2f} U")
            
            if self.simulation_time % 360 == 0:
                carbs = 60
                meal_bolus = self.calculate_meal_bolus(carbs)
                self.pump.deliver_bolus(meal_bolus)
                self.insulin_log[self.simulation_time] += meal_bolus
                self.pdm.record_insulin_dose(datetime.now(), meal_bolus)

        self.last_message = "Simulation terminée, résultats disponibles"

    def generate_final_log(self):
        events = ["Événements:"]
        events.extend(self.event_log)
        events.append("\nValeurs de glycémie:")
        for time, glucose in self.glucose_log.items():
            events.append(f"Time {time}: {glucose:.2f} mg/dL")
        events.append("\nDoses d'insuline administrées:")
        for time, dose in self.insulin_log.items():
            events.append(f"Time {time}: {dose:.2f} U")
        return "\n".join(events)

    def run_simulation(self):
        self.run(self.duration * 60)