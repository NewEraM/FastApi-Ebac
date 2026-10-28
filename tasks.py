
from celery_app import celery_app


@celery_app.task(name="tasks.somar")
def somar(a, b):
    return a + b


@celery_app.task(name="tasks.fatorial")
def fatorial(n):
    if n < 0:
        raise ValueError("O número deve ser maior ou igual a zero")

    resultado = 1
    for i in range(2, n + 1):
        resultado *= i

    return resultado
