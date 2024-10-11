from insulin_pump_simulator.patient import Patient
import json

with open('data/sample_input_data.json', 'r') as file:
    data = json.load(file)
    config = data['pump_configuration']

Patient = Patient()


class PumpConfig:
    def __init__(self, basal_rates: list[float] = config["basal_rates"], insulin_to_carb_ratio: float = config["insulin_to_carb_ratio"], max_bolus: float = config["max_bolus"], insulin_sensitivity_factor: float = Patient.insulin_sensitivity, modes: dict[str, dict] = config["personalized_modes"]):
        self.basal_rates: list[float] = basal_rates
        self.insulin_to_carb_ratio: float = insulin_to_carb_ratio
        self.insulin_sensitivity_factor: float = insulin_sensitivity_factor
        self.max_bolus: float = max_bolus
        self.modes: dict[str, dict] = modes if modes is not None else {}
        self.active_mode: str = "Day"

    def validate(self) -> bool:
        if len(self.basal_rates) != 24:
            raise ValueError("Basal rates must be defined for 24 hours")
        if self.insulin_to_carb_ratio <= 0:
            raise ValueError("Insulin to carb ratio must be positive")
        if self.insulin_sensitivity_factor is not None and self.insulin_sensitivity_factor <= 0:
            raise ValueError("Insulin sensitivity factor must be positive")
        if self.max_bolus <= 0:
            raise ValueError("Max bolus must be positive")
        return True
