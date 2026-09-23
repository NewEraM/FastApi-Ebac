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


app = FastAPI(
    title="API de livros",
    description="API para gerenciar catalogo de livros",
    version="1.0.0",
    contact={
        "name":"Guilherme Muniz",
        "email":"muniz_157@outlook.com"
    }
)

USER = "admin"
PASSWORD = "admin"


security = HTTPBasic()

dicionario_livros = {}

class Livro(BaseModel):
    nome_livro: str
    autor_livro: str
    ano_livro: int

def autenticar_meu_user(credentials:HTTPBasicCredentials = Depends(security)):
   is_username_correct = secrets.compare_digest(credentials.username, USER)
   is_password_correct = secrets.compare_digest(credentials.password, PASSWORD)

   if not (is_username_correct and is_password_correct):
       raise HTTPException(
           status_code = 401,
           detail= "Usuario ou senha incorretos",
           headers={"WWW-Autheticate":"Basic"}
       )


@app.get("/livros")
def get_livros(page: int = 1, limit: int = 10,  credentials: HTTPBasicCredentials = Depends(autenticar_meu_user)):
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code =400, detail="Page ou limit estao com valores invalidos"
        )
    if not dicionario_livros:
        return {"message":"Nao existe nenhum livro!!"}

    livros_ordenados = sorted(dicionario_livros.items(), key =lambda x: x[0])
    
    start = (page - 1)  * limit
    end = start + limit

    livros_paginados = [
        {"id": id_livro, "nome_livro": livro_data["nome_livro"], "autor_livro": livro_data["autor_livro"], "ano_livro": livro_data["ano_livro"]}
        for id_livro, livro_data in livros_ordenados[start:end]
    ]

    return [
        "page", page,
        "limit", limit,
        "total", len(dicionario_livros),
        "livros", livros_paginados
    ]

#id do livro
#nome do livros
#autor do livro
#ano de lancamento do livro

#Nao mais .dict() e agora .model_dump()

@app.post("/adiciona")
def post_livros(id_livro: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_meu_user) ):
    if id_livro in dicionario_livros:
        raise HTTPException(status_code=400, detail="Esse livro ja esta cadastrado.")
    else:
        dicionario_livros[id_livro] = livro.model_dump()
        return {"message": " O livro foi adiconado com sucesso"}

@app.put("/atualiza/{id_livro}")
def put_livros(id_livro: int, livro: Livro, credentials: HTTPBasicCredentials = Depends(autenticar_meu_user)):
    meu_livro = dicionario_livros.get(id_livro)
    if not meu_livro:
        raise HTTPException(status_code = 404, detail="Esse livro nao foi encontrado")
    else:
        dicionario_livros[id_livro] = livro.model_dump()
        return {"message": "As informacoes do seu livro foram atualizadas com sucesso!"}

@app.delete("/deletar/{id_livros}")
def delete_livro(id_livros: int, credentials: HTTPBasicCredentials = Depends(autenticar_meu_user)):
    if id_livros not in dicionario_livros:
        raise HTTPException(status_code = 400, detail= "Esse livro nao foi encontado")
    else:
        del dicionario_livros[id_livros]

        return {"message": "Seu livro foi deletado com sucesso!"}
    
