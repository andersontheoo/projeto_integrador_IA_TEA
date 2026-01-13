import os
import random
import logging

logger = logging.getLogger(__name__)

def simulate_eeg_analysis(file_path: str) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError("Arquivo EEG não encontrado")

    filename = os.path.basename(file_path).lower()

    if "autism" in filename:
        result = True
        confidence = random.uniform(0.80, 0.90)
    else:
        result = random.choice([True, False])
        confidence = random.uniform(0.60, 0.85)

    logger.info("Simulação de IA executada")

    return {
        "result": result,
        "confidence": round(confidence, 2),
        "source": "simulated"
    }
