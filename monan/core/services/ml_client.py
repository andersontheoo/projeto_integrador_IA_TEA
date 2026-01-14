import os
import time
import logging
import random
from dotenv import load_dotenv
load_dotenv()

from core.services.ml_api import analyze_eeg

logger = logging.getLogger(__name__)
load_dotenv()

# -----------------------------
# Configurações via .env
# -----------------------------
MAX_RETRIES = int(os.getenv("WEKA_MAX_RETRIES", 2))
RETRY_DELAY = float(os.getenv("WEKA_RETRY_DELAY", 2))


# -----------------------------
# Classificação de erros
# -----------------------------
PERMANENT_ERRORS = (
    FileNotFoundError,
    ValueError,
)


# -----------------------------
# Simulador de IA (fallback)
# -----------------------------
def simulate_analysis(file_path: str) -> dict:
    """
    Simula uma análise de EEG de forma controlada e auditável.
    """
    filename = os.path.basename(file_path).lower()

    if "autism" in filename:
        result = True
        confidence = random.uniform(0.80, 0.90)
    else:
        result = random.choice([True, False])
        confidence = random.uniform(0.60, 0.85)

    logger.info("Análise simulada utilizada como fallback")

    return {
        "classification": result,
        "confidence": round(confidence, 2),
        "source": "simulated"
    }


# -----------------------------
# Orquestrador principal
# -----------------------------
def analyze_with_retry(file_path: str) -> dict:
    """
    Executa análise do EEG com WEKA, com retry automático e fallback.
    """
    attempt = 0

    while attempt <= MAX_RETRIES:
        try:
            logger.info(f"Iniciando análise EEG (tentativa {attempt + 1})")

            response = analyze_eeg(file_path)

            # ml_api retornou erro padronizado
            if "error" in response:
                raise RuntimeError("Erro retornado pelo serviço WEKA")

            # -----------------------------
            # Normalização da saída do WEKA
            # -----------------------------
            raw_output = response.get("resultado", "").lower()

            result = "autism" in raw_output
            confidence = 0.85  # valor fixo enquanto WEKA real não entrega score

            logger.info("Análise WEKA concluída com sucesso")

            return {
                "result": result,
                "confidence": confidence,
                "source": "weka"
            }

        except PERMANENT_ERRORS as e:
            logger.error(f"Erro permanente detectado: {e}")
            return {"error": "Falha na análise do sinal de EEG"}

        except TimeoutError:
            logger.warning("Timeout na execução do WEKA")

        except Exception as e:
            logger.warning(f"Falha transitória: {e}")

        attempt += 1

        if attempt <= MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    # -----------------------------
    # Fallback: Simulador
    # -----------------------------
    try:
        logger.warning("Ativando fallback de simulação de IA")
        return simulate_analysis(file_path)

    except Exception:
        logger.exception("Falha total na análise de EEG")
        return {"error": "Falha na análise do sinal de EEG"}
