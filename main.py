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

from fastapi import FastAPI, HTTPException

app = FastAPI()

dicionario_livros = {}

@app.get("/livros")
def get_livros():
    if not dicionario_livros:
        return {"message": "Esse livro nao existe!"}
    else:
        return {"livros": dicionario_livros}


#id do livro
#nome do livros
#autor do livro
#ano de lancamento do livro

@app.post("/adiciona")
def post_livros(id_livro: int, nome_livro: str, autor_livro: str, ano_livro: int ):
    if id_livro in dicionario_livros:
        raise HTTPException(status_code=400, detail="Esse livro ja esta cadastrado.")
    else:
        dicionario_livros[id_livro] = {"nome_livro": nome_livro,"autor_livro": autor_livro, "ano_livro": ano_livro}
        return {"message": " O livro foi adiconado com sucesso"}

@app.put("/atualiza/{id_livro}")
def put_livros(id_livro: int, nome_livro: str, autor_livro: str, ano_livro: int):
    meu_livro = dicionario_livros.get(id_livro)
    if not meu_livro:
        raise HTTPException(status_code = 404, detail="Esse livro nao foi encontrado")
    else:
        if nome_livro:
            meu_livro["nome_livro"] = nome_livro
        if autor_livro:
            meu_livro["autor_livro"] = autor_livro
        if ano_livro:
            meu_livro["ano_livro"] = ano_livro

        return {"message": "As informacoes do seu livro foram atualizadas com sucesso!"}

@app.delete("/deletar/{id_livros}")
def delete_livro(id_livros: int):
    if id_livros not in dicionario_livros:
        raise HTTPException(status_code = 404, detail= "Esse livro nao foi encontado")
    else:
        del dicionario_livros[id_livros]

        return {"message": "Seu livro foi deletado com sucesso!"}
    
