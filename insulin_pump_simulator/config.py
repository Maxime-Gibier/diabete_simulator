class PumpConfig:
    def __init__(self, basal_rates, insulin_to_carb_ratio, max_bolus, insulin_sensitivity_factor=None):
        self.basal_rates = basal_rates
        self.insulin_to_carb_ratio = insulin_to_carb_ratio
        self.insulin_sensitivity_factor = insulin_sensitivity_factor
        self.max_bolus = max_bolus

    def validate(self):
        if len(self.basal_rates) != 24:
            raise ValueError("Basal rates must be defined for 24 hours")
        if self.insulin_to_carb_ratio <= 0:
            raise ValueError("Insulin to carb ratio must be positive")
        if self.insulin_sensitivity_factor is not None and self.insulin_sensitivity_factor <= 0:
            raise ValueError("Insulin sensitivity factor must be positive")
        if self.max_bolus <= 0:
            raise ValueError("Max bolus must be positive")
        return True