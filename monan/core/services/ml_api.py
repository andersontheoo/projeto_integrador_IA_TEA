# core/services/ml_api.py

import subprocess
import logging
import os

logger = logging.getLogger(__name__)

WEKA_TIMEOUT = 60


def analyze_eeg(file_path: str) -> dict:
    """
    Executa a análise de um arquivo EEG usando WEKA.

    Responsabilidade única:
    - Chamar o WEKA
    - Retornar o resultado bruto
    - Levantar exceção em caso de erro
    """

    # Validação básica
    if not os.path.exists(file_path):
        raise FileNotFoundError("Arquivo EEG não encontrado")

    command = [
        "java",
        "-jar",
        "weka.jar",
        file_path
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=WEKA_TIMEOUT,
            check=True
        )

        return {
            "status": "success",
            "resultado": result.stdout.strip()
        }

    except subprocess.TimeoutExpired as e:
        logger.error("Timeout ao executar o WEKA", exc_info=True)
        raise RuntimeError("Timeout na execução do WEKA") from e

    except subprocess.CalledProcessError as e:
        logger.error("Erro retornado pelo WEKA", exc_info=True)
        raise RuntimeError(f"Erro no WEKA: {e.stderr}") from e

    except Exception as e:
        logger.exception("Erro inesperado ao executar WEKA")
        raise RuntimeError("Erro inesperado na análise de EEG") from e
    
        
