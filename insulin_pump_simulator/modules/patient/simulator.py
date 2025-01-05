from .patient import Patient
from .insulin_pump import InsulinPump
from .cgm import CGM
from .controller import ClosedLoopController
from .pdm import PDM

class Simulator:
    def __init__(self, duration: int):
        self.patient = Patient()
        self.pump = InsulinPump()
        self.cgm = CGM()
        self.controller = ClosedLoopController(target_glucose=120)
        self.pdm = PDM(target_glucose=120)
        self.duration = duration

    def run_simulation(self) -> None:
        for hour in range(self.duration):
            for minute in range(0, 60, 5):  # Simulate every 5 minutes
                glucose = self.cgm.measure_glucose(self.patient)
                adjustment = self.controller.adjust_basal_rate(glucose[0])
                self.pump.deliver_adjusted_basal(adjustment)
                self.patient.update_glucose_level(insulin=adjustment)
                self.log_data()

    def log_data(self) -> None:
        # This method would be implemented to record simulation data
        # For example, writing to a file or storing in a database
        pass
