
import time

from celery import Celery
from celery.utils.log import get_task_logger

# Redis será o broker e o backend dos resultados.
REDIS_URL = "redis://localhost:6379/0"

celery_app = Celery(
    "desafio",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

logger = get_task_logger(__name__)


@celery_app.task(name="calcular_soma")
def calcular_soma(numero1: int, numero2: int) -> int:
    """Simula uma tarefa demorada e retorna a soma."""
    logger.info("Iniciando soma: %s + %s", numero1, numero2)

    time.sleep(5)

    resultado = numero1 + numero2

    logger.info("Resultado da soma: %s", resultado)

    return resultado


@celery_app.task(name="calcular_fatorial")
def calcular_fatorial(numero: int) -> int:
    """Calcula o fatorial de forma iterativa."""
    if numero < 0:
        raise ValueError("O número deve ser maior ou igual a zero.")

    logger.info("Iniciando fatorial de %s", numero)

    time.sleep(5)

    resultado = 1

    for valor in range(2, numero + 1):
        resultado *= valor

    logger.info("Resultado do fatorial de %s: %s", numero, resultado)

    return resultado
