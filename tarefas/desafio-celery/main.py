
from fastapi import FastAPI

from celery_app import calcular_soma, calcular_fatorial

app = FastAPI()


@app.post("/soma")
def executar_soma(a: int, b: int):
    tarefa = calcular_soma.delay(a, b)

    return {
        "task_id": tarefa.id,
        "status": "Soma enviada"
    }


@app.post("/fatorial")
def executar_fatorial(a: int):
    tarefa = calcular_fatorial.delay(a)

    return {
        "task_id": tarefa.id,
        "status": "Fatorial enviado"
    }
