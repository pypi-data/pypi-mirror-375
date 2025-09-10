class Battery:
    def __init__(self, capacity_kwh, max_charge_kw, max_discharge_kw, efficiency=0.95, soc_init=0.5):
        """
        Initialize the battery.

        Parameters:
        - capacity_kwh: Total energy capacity in kWh
        - max_charge_kw: Maximum charging power in kW
        - max_discharge_kw: Maximum discharging power in kW
        - efficiency: Round-trip efficiency (0 < eff ≤ 1)
        - soc_init: Initial state of charge (0 ≤ soc ≤ 1)
        """
        self.capacity = capacity_kwh
        self.max_charge = max_charge_kw
        self.max_discharge = max_discharge_kw
        self.efficiency = efficiency
        self.soc = soc_init  # State of charge as a fraction (0 to 1)

    def get_soc_kwh(self):
        return self.soc * self.capacity

    def step(self, power_request_kw, timestep_hours=1.0):
        """
        Simulate one time step of battery operation.

        Parameters:
        - power_request_kw: Power to charge (positive) or discharge (negative)
        - timestep_hours: Duration of the time step

        Returns:
        - actual_power_kw: Power actually charged/discharged
        - energy_exchanged_kwh: Energy in/out of battery (after efficiency)
        - soc: New state of charge
        """
        energy_request_kwh = power_request_kw * timestep_hours
        actual_energy_kwh = 0

        if power_request_kw > 0:
            # Charging
            max_charge_possible = min(self.max_charge * timestep_hours,
                                      (1 - self.soc) * self.capacity / self.efficiency)
            actual_energy_kwh = min(energy_request_kwh, max_charge_possible)
            self.soc += (actual_energy_kwh * self.efficiency) / self.capacity
        elif power_request_kw < 0:
            # Discharging
            max_discharge_possible = min(self.max_discharge * timestep_hours,
                                         self.soc * self.capacity)
            actual_energy_kwh = max(energy_request_kwh, -max_discharge_possible)
            self.soc += actual_energy_kwh / self.capacity  # Note: actual_energy_kwh is negative
            actual_energy_kwh *= self.efficiency  # Losses during discharge

        # Clamp SoC between 0 and 1
        self.soc = max(0.0, min(1.0, self.soc))

        return power_request_kw if actual_energy_kwh != 0 else 0.0, actual_energy_kwh, self.soc

    def __str__(self):
        return f"Battery SoC: {self.get_soc_kwh():.2f} kWh ({self.soc*100:.1f}%)"