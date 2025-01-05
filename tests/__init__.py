# This file is intentionally left almost empty.
# It's used to mark the 'tests' directory as a Python package.

import pytest

# Define any fixtures or configurations that should be available to all tests
@pytest.fixture(scope="session")
def global_test_config():
    return {
        "simulation_duration": 24 * 60,  # 24 hours in minutes
        "time_step": 5,  # 5 minutes
        "default_glucose_target": 100,  # mg/dL
    }

# Uncomment these imports as you create the corresponding modules
from insulin_pump_simulator.modules.patient import Patient
from insulin_pump_simulator.modules.patient.insulin_pump import InsulinPump
from insulin_pump_simulator.modules.patient.cgm import CGM
from insulin_pump_simulator.modules.patient.controller import ClosedLoopController as Controller
from insulin_pump_simulator.modules.patient.pdm import PDM
from insulin_pump_simulator.modules.patient.simulator import Simulator
