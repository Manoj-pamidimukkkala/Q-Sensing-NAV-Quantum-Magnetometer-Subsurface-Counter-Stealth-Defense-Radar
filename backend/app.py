from flask import Flask, jsonify, request
import numpy as np

app = Flask(__name__)

# Constants for NV Center Quantum Magnetometry
GYROMAGNETIC_RATIO = 28.02  # GHz / Tesla (Electron Spin Ratio)

@app.route('/api/magnetometer/readout', methods=['POST'])
def calculate_zeeman_split():
    """
    Calculates Zeeman frequency splitting based on local magnetic field B_z.
    f_res = f_0 ± gamma * B_z
    """
    data = request.json or {}
    b_field_tesla = data.get("b_field_nT", 450.0) * 1e-9  # convert nT to Tesla
    
    f_0 = 2.870  # Zero-field splitting in GHz
    delta_f = GYROMAGNETIC_RATIO * b_field_tesla
    
    f_minus = f_0 - delta_f
    f_plus = f_0 + delta_f
    
    return jsonify({
        "status": "OPERATIONAL",
        "zero_field_splitting_GHz": f_0,
        "measured_b_field_nT": data.get("b_field_nT", 450.0),
        "odmr_resonance_frequencies_GHz": [round(f_minus, 6), round(f_plus, 6)],
        "target_detected": True if data.get("b_field_nT", 450.0) > 200 else False
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)
