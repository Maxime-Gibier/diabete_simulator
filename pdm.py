class PDM:
    def __init__(self, pump):
        self.pump = pump
        self.last_alert = ""  # Ajout de l'attribut last_alert

    def check_glucose_limits(self, glucose):
        if glucose > 250:
            self.last_alert = f"Alerte : glycémie critique de {glucose} mg/dL"
        elif glucose < 70:
            self.last_alert = f"Alerte : glycémie basse de {glucose} mg/dL"
        else:
            self.last_alert = ""

    def check_pump_status(self):
        if self.pump.battery_level < 20:
            self.last_alert = f"Alerte : Batterie faible, niveau actuel à {self.pump.battery_level}%"
        elif self.pump.is_occluded:
            self.last_alert = "Alerte : Obstruction détectée dans le système de délivrance d'insuline"
        else:
            self.last_alert = ""

    # Autres méthodes de la classe PDM...