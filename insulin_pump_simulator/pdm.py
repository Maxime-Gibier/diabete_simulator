from insulin_pump_simulator.insulin_pump import InsulinPump
from insulin_pump_simulator.controller import ClosedLoopController
from insulin_pump_simulator.config import PumpConfig
from typing import Dict
import json

class PDM:
    def __init__(self, target_glucose: float):
        with open('data/sample_input_data.json', 'r') as file:
            data = json.load(file)

        self.pump = InsulinPump()
        self.target_glucose = target_glucose
        self.config = PumpConfig()
        self.controller = ClosedLoopController(self.target_glucose)
        self.history = {
            'glucose': data['history']['glucose_history'],
            'insulin_dose': data['history']['insulin_dose_history']
        }
        self.last_message = ""

    def set_meal(self, carbs: float) -> None:
        bolus = self.pump.calculate_meal_bolus(carbs)
        self.pump.deliver_bolus(bolus)
        print(f"Bolus de repas administré : {bolus} U")

    def set_target_glucose(self, target: float) -> None:
        self.target_glucose = target
        self.controller.target_glucose = target
        print(f"Glycémie cible ajustée à {target} mg/dL")

    def apply_new_config(self, config: PumpConfig) -> None:
        self.pump.apply_configuration(config)
        self.config = config

    def add_alarm(self, alarm: str) -> None:
        self.pump.add_alarm(alarm)

    def view_glucose_history(self) -> None:
        self.last_message = "Historique de glycémie consulté avec succès"
        return self.history['glucose']
    
    def view_insulin_dose_history(self) -> None:
        self.last_message = "Historique de glycémie consulté avec succès"
        return self.history['insulin_dose']

    def set_mode(self, mode: str, config: Dict) -> None:
        self.config.modes[mode] = config
        self.pump.config.active_mode = mode
        self.pump.apply_configuration(self.pump.config.modes[mode])
        self.last_message = f"Mode '{mode}' configuré avec succès"

    def check_battery_level(self) -> None:
        if self.pump.battery_level < 20:
            self.add_alarm("Low battery alert")
            self.pump.last_message = f"Alerte : Batterie faible, niveau actuel à {self.pump.battery_level} %"
        return self.pump.last_message, self.pump.alarms
    
    def get_mode(self) -> str:
        return self.pump.config.active_mode, f"Mode '{self.pump.config.active_mode}' est actuellement actif"

    def activate_mode(self, mode: str) -> None:
        if mode in self.config.modes:
            self.pump.config.active_mode = mode
            self.apply_configuration(self.config.modes[mode])
            self.pump.last_message = f"Mode '{mode}' activé avec succès"
        else:
            raise ValueError(f"Mode {mode} not found")
        
    def apply_configuration(self, config) -> None:
        if config["basal_rate_adjustment"] is not None:
            self.pump.config.basal_rates = [round(rate * config["basal_rate_adjustment"], 2) for rate in self.pump.config.basal_rates]
        self.last_message = "Nouvelle configuration appliquée"