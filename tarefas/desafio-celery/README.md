
# Desafio Celery com FastAPI e Redis

## Objetivo

Desenvolver uma API FastAPI que envia tarefas assíncronas
para o Celery, utilizando o Redis como broker e backend.

As tarefas são:
- calcular_soma: soma dois números inteiros.
- calcular_fatorial: calcula o fatorial de um número inteiro
  não negativo.

As tarefas simulam demora com time.sleep(5).

## Tecnologias

- Python
- FastAPI
- Celery
- Redis
- Uvicorn

## Instalação

Crie e ative um ambiente virtual:

python -m venv .venv

No Windows PowerShell:

.\.venv\Scripts\Activate.ps1

Instale as dependências:

python -m pip install celery redis fastapi uvicorn

## Configuração do Redis

O Redis deve estar disponível em:

redis://localhost:6379/0

Verifique a conexão com:

redis-cli ping

A resposta esperada é PONG.

## Execução

### 1. Inicie o Redis

Inicie o serviço Redis conforme a instalação utilizada.

### 2. Inicie o Celery Worker

Em um terminal, execute:

celery -A celery_app:celery_app worker -l info --pool=solo

### 3. Inicie a API

Em outro terminal, execute:

uvicorn main:app --reload

A API estará disponível em http://127.0.0.1:8000.

A documentação interativa estará em:

http://127.0.0.1:8000/docs

## Testes

### Soma

POST /soma

Corpo JSON:

{
  "a": 10,
  "b": 20
}

Resultado esperado no worker: 30.

### Fatorial

POST /fatorial

Corpo JSON:

{
  "n": 5
}

Resultado esperado no worker: 120.

Os endpoints retornam o identificador da tarefa sem esperar
a conclusão do cálculo.

