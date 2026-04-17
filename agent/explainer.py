from models.baseline_builder import get_baseline

def generate_explanation(machine_id: str, reading: dict, features: dict, risk: dict) -> str:
    baseline = get_baseline(machine_id)
    reasons = []

    # Map generic names to specific fields if necessary or use directly
    vib = reading.get("vibration_mm_s", reading.get("vibration", 0))
    vib_mean = baseline.get("vib_mean", 0)
    if vib_mean > 0 and vib > vib_mean * 1.5:
        reasons.append(f"Vibration increased significantly ({vib:.2f} vs baseline {vib_mean:.2f})")

    temp = reading.get("temperature_C", reading.get("temperature", 0))
    temp_mean = baseline.get("temp_mean", 0)
    if temp_mean > 0 and temp > temp_mean * 1.2:
        reasons.append(f"Temperature above baseline ({temp:.2f} vs baseline {temp_mean:.2f})")
        
    rpm = reading.get("rpm", 0)
    rpm_mean = baseline.get("rpm_mean", 0)
    if rpm_mean > 0 and rpm < rpm_mean * 0.8:
        reasons.append(f"RPM dropped significantly below normal")
        
    current = reading.get("current_A", reading.get("current", 0))
    current_mean = baseline.get("current_mean", 0)
    if current_mean > 0 and current > current_mean * 1.3:
        reasons.append(f"Power current spike detected")

    # Simple fallback reasoning
    if not reasons:
        reasons.append("Anomalous pattern detected across multiple sensors")

    explanation = ", ".join(reasons)

    # Add the explanation as the 'reason' string in the risk dict
    risk['reason'] = explanation
    return explanation
