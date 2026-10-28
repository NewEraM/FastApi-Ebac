# API basica de livros

# GET,POST, PUT, DELETE

 
#POST - add novos livros
#GET - Buscar dados livros
#PUT - Atualizar info dos livros
#DELETE - deletar info dos livros

#CRUD - 
# Create 
# Read 
# Uptade 
# Delete

#Vamos acessar nosso end-point
#vamos acessar os PATHS do nosso ENDPOINT

#PATHS ou rotas - caminhos que vamos acessar para cada metodo
#Querry strings - parametros que passamos na URL

#documentacao swagger -> Documentar os endpoints da nossa aplicacao (da nossa API)

# Aceesa minha documetacao swagger nesse endpoint -> ........

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import os
import redis
import json
from fastapi import BackgroundTasks
from tasks import fatorial, somar
from celery_app import celery_app
from celery.result import AsyncResult
from dotenv import load_dotenv

load_dotenv()
#Criar banco de dados dentro do python

from sqlalchemy import  create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

import asyncio
#Variavel de hambiente
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
#add redis


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

redis_client = redis.Redis(host=REDIS_HOST,port=REDIS_PORT, db=0, decode_responses=True)


#_______________________________________________________________________________
app = FastAPI(
    title="API de livros",
    description="API para gerenciar catalogo de livros",
    version="1.0.0",
    contact={
        "name":"Guilherme Muniz",
        "email":"muniz_157@outlook.com"
    }
)

#Variavel de hambiente
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")


security = HTTPBasic()

dicionario_livros = {}

#Criar nossa table e adcionar nossas colunas com os parametros necessarios

class LivroDB(Base):
    __tablename__ = "Livros"
    id = Column(Integer, primary_key=True,index = True)
    nome_livro = Column(String, index = True)
    autor_livro = Column(String, index = True)
    ano_livro = Column(Integer)

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

Base.metadata.create_all(bind=engine)

def salvar_livro_redis(livro_id: int, livro: Livro):
    redis_client.set(f"livro:{livro_id}",json.dumps(livro.model_dump()))    

def deletar_livro_redis(livro_id: int):
    redis_client.delete(f"livro:{livro_id}")


def sessao_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Funcao com responsabilidade para fazer a autenticacao  do usuario
def autenticar_meu_user(credentials:HTTPBasicCredentials = Depends(security)):
   is_username_correct = secrets.compare_digest(credentials.username, USER)
   is_password_correct = secrets.compare_digest(credentials.password, PASSWORD)

   if not (is_username_correct and is_password_correct):
       raise HTTPException(
           status_code = 401,
           detail= "Usuario ou senha incorretos",
           headers={"WWW-Authenticate":"Basic"}
       )

async def chamadas_externas_1():
    await asyncio.sleep(2)
    return "Resultado chamada externa 1"

async def chamadas_externas_2():
    await asyncio.sleep(2)
    return "Resultado chamada externa 2"

async def chamadas_externas_3():
    await asyncio.sleep(2)
    return "Resultado chamada externa 3"

@app.get("/chamadas-externas")
async def chamadas_externas():
    tarefa1 = asyncio.create_task(chamadas_externas_1())
    tarefa2 = asyncio.create_task(chamadas_externas_2())
    tarefa3 = asyncio.create_task(chamadas_externas_3())

    resultado1 = await tarefa1
    resultado2 = await tarefa2
    resultado3 = await tarefa3

    return {
        "mensagem": "Todas as chamadas nas API's foram concluidas com sucesso!",
        "resultado": [resultado1, resultado2, resultado3]
    }

@app.post("/calcular/soma")
def calcular_soma(a: int, b: int):
    tarefa = somar.delay(a, b)

    redis_client.lpush("tarefas_ids", tarefa.id)

    return {
        "task_id": tarefa.id,
        "status": "PENDING"
    }

@app.post("/calcular/fatorial")
def calcular_fatorial(n: int):
    tarefa = fatorial.delay(n)
    redis_client.lpush("tarefas_id", tarefa.id)
    redis_client.ltrim("tarefas_id", 0, 49)

    return {
        "task_id": tarefa.id,
        "message": "Tarefa de fatorial enviada para execucao."
    }


@app.get("/tarefas/recentes")
def listar_tarefas_recentes():
    ids = redis_client.lrange("tarefas_ids", 0, -1)
    tarefas = []

    for task_id in ids:
        resultado = AsyncResult(task_id, app=celery_app)
        tarefas.append({
            "task_id": task_id,
            "status" : resultado.status,
            "resultado": resultado.result if resultado.successful() else None
        })

    return {
        "tarefas": tarefas
    }


#chaves livros       
@app.get("/debug/redis")
def debug_redis():
    chaves = redis_client.keys("livros:*")
    livros = []

    for chave in chaves:
        valor = redis_client.get(chave)
        ttl = redis_client.ttl(chave)

        livros.append({"chave" : chave, "valor": json.loads(valor), "ttl": ttl})
    return livros


@app.get("/livros") #GET atualizado usando o metodo sqlalchemy (banco de dados)
def get_livros(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(sessao_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_meu_user)
):
    if page < 1 or  limit < 1:
        raise HTTPException(status_code=400, detail="Page e limit devem ser maiores que 0")

    cache_key = f"livros:page={page}&limit={limit}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    livros = db.query(LivroDB).offset((page - 1) * limit).limit(limit).all()

    if not livros:
        raise HTTPException(status_code=404, detail="Nenhum livro encontrado no banco de dados")

    total_livros = db.query(LivroDB).count()

    resposta ={
        "page": page,
        "limit": limit,
        "total_livros": total_livros,
        "livros": [
            {
                "id": livro.id,
                "nome_livro": livro.nome_livro,
                "autor_livro": livro.autor_livro,
                "ano_livro": livro.ano_livro
            }
            for livro in livros
        ]
    }
    redis_client.setex(cache_key, 60, json.dumps(resposta))
    return resposta

#id do livro
#nome do livros
#autor do livro
#ano de lancamento do livro

#Nao mais .dict() e agora .model_dump()

@app.post("/adiciona") #POST atualizado usando o metodo sqlalchemy (banco de dados)
async def post_livros(livro: Livro, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_meu_user) ):
    db_livro = db.query(LivroDB).filter(LivroDB.nome_livro == livro.nome_livro, LivroDB.autor_livro == livro.autor_livro).first()
    if db_livro:
        raise HTTPException(status_code = 400, detail = "Esse livro ja existe dentro do banco de dados")

    novo_livro = LivroDB(nome_livro = livro.nome_livro, autor_livro = livro.autor_livro, ano_livro = livro.ano_livro)
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)

    salvar_livro_redis(novo_livro.id, livro)

    return {"message": "O livro foi criado com sucesso!"}

@app.put("/atualiza/{id_livro}")#PUT atualizado usando o metodo sqlalchemy (banco de dados)
async def put_livros(id_livro: int, livro: Livro,db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_meu_user)):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()
    if not db_livro:
        raise HTTPException (status_code = 404, detail = "Este livro nao foi encontrado no seu banco de dados!")
    db_livro.nome_livro = livro.nome_livro
    db_livro.autor_livro = livro.autor_livro
    db_livro.ano_livro = livro.ano_livro

    db.commit()
    db.refresh(db_livro)

    salvar_livro_redis(db_livro.id, livro)

    return {"message": "O livro foi atualizado com sucesso!"}
    
@app.delete("/deletar/{id_livro}")
async def delete_livro(id_livro: int, db: Session = Depends(sessao_db), credentials: HTTPBasicCredentials = Depends(autenticar_meu_user)):
    db_livro = db.query(LivroDB).filter(LivroDB.id == id_livro).first()

    if not db_livro:
        raise HTTPException(status_code = 404, detail = "Este livro nao foi encontrado no seu banco de dados!")
    db.delete(db_livro)
    db.commit()

    deletar_livro_redis(id_livro)
    return {"message": "Seu livro foi deletado com sucesso!"}

#ACID
#ORM => Object Relational Mapping
# fastapi/ django / flask / node / express / nest.js / laravel / springboot => Frameworks Backends
# Vantagens -> a gente vai ganhar agilidade no desemvolvimento 
# desvantagens -> a gente perde  performace no banco de dados
