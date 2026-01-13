import subprocess
import logging
import os

WEKA_TIMEOUT = 60

logger = logging.getLogger(__name__)

def analyze_with_retry(file_path: str) -> dict:
    """
    Executa a análise de um arquivo EEG usando WEKA.
    Retorna resultado ou erro padronizado.
    """
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(file_path):
            raise FileNotFoundError("Arquivo EEG não encontrado")

        # Comando básico para executar o WEKA
        command = [
            "java",
            "-jar",
            "weka.jar",
            file_path
        ]

        # Executa o processo com timeout
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

    except Exception:
        logger.exception("Erro ao analisar sinal de EEG")
        return {
            "error": "Falha na análise do sinal de EEG"
        }
