from flask import Blueprint, render_template, request, jsonify, session
from models.usuario import ler_dados, salvar_dados
from utils.validacoes import hash_senha, verificar_senha

main_bp = Blueprint('main', __name__)

# Chave secreta do adm
CHAVE_MESTRA_ADMIN = "123"

@main_bp.route("/")
def index():
    
    dados = ler_dados()
    usuario_logado = session.get("usuario")
    return render_template("index.html", receitas=dados["receitas"], usuario=usuario_logado)


@main_bp.route("/cadastrar", methods=["POST"])
def cadastrar():
   
    corpo = request.get_json()
    nickname = corpo.get("nickname", "").strip()
    senha = corpo.get("senha", "").strip()
    chave_enviada = corpo.get("chave_admin", "").strip()

    if not nickname or not senha:
        return jsonify({"erro": "Preencha todos os campos"}), 400

    dados = ler_dados()

    perfil_final = "admin" if chave_enviada == CHAVE_MESTRA_ADMIN else "comum"

    for usuario in dados["usuarios"]:
        if usuario["nickname"].lower() == nickname.lower():
            return jsonify({"erro": "Nickname já está em uso"}), 409

    novo_usuario = {
        "id": dados["proximo_usuario_id"],
        "nickname": nickname,
        "senha": hash_senha(senha),
        "perfil": perfil_final
    }

    dados["usuarios"].append(novo_usuario)
  
    dados["proximo_usuario_id"] += 1
   
    salvar_dados(dados)
   
    return jsonify({"mensagem": "Cadastro realizado com sucesso!"}), 201


@main_bp.route("/login", methods=["POST"])
def login():
   
    corpo = request.get_json()
    nickname = corpo.get("nickname", "").strip()
    senha = corpo.get("senha", "").strip()

    if not nickname or not senha:
        return jsonify({"erro": "Preencha todos os campos"}), 400

    dados = ler_dados()
    usuario_encontrado = None

    for usuario in dados["usuarios"]:
        if usuario["nickname"].lower() == nickname.lower():
            usuario_encontrado = usuario
            break

    if usuario_encontrado is None or not verificar_senha(senha, usuario_encontrado["senha"]):
        return jsonify({"erro": "Usuário ou senha incorreto"}), 401

    session["usuario"]  = {
        "id": usuario_encontrado["id"],
        "nickname": usuario_encontrado["nickname"],
        "perfil": usuario_encontrado["perfil"]
    }

    return jsonify({"mensagem": "Login realizado!", "usuario": session["usuario"]})


@main_bp.route("/logout", methods=["POST"])
def logout():

    session.pop("usuario", None)
    return jsonify({"mensagem": "Logout realizado com sucesso!"})


@main_bp.route("/status")
def status():
  
    return jsonify({"usuario_logado": session.get("usuario")})

@main_bp.route("/receitas/deletar/<int:id>", methods=["DELETE"])
def deletar_receita(id):
  
    usuario_logado = session.get("usuario")
    if not usuario_logado:
        return jsonify({"erro": "Acesso negado"}), 401

    dados = ler_dados()
    receita_encontrada = None
    
    for r in dados["receitas"]:
        if r["id"] == id:
            receita_encontrada = r
            break

    if not receita_encontrada:
        return jsonify({"erro": "Receita não encontrada"}), 404

    if usuario_logado["perfil"] == "admin" or usuario_logado["nickname"] == receita_encontrada.get("autor_nickname"):
        
        dados["receitas"] = [r for r in dados["receitas"] if r["id"] != id]
        salvar_dados(dados)
        return jsonify({"mensagem": "Receita excluída com sucesso!"}), 200

    return jsonify({"erro": "Sem permissão para excluir esta receita"}), 403


@main_bp.route("/comentario/<int:id>", methods=["DELETE"])
def excluir_comentario(id):
   
    usuario_logado = session.get("usuario")
    if not usuario_logado:
        return jsonify({"erro": "Acesso negado"}), 401

    dados = ler_dados()
    alterou = False

    for receita in dados["receitas"]:
        lista_original = receita.get("comentarios", [])
        
        comentario_alvo = next((c for c in lista_original if c["id"] == id), None)
        
        if comentario_alvo:
      
            if usuario_logado["perfil"] == "admin" or usuario_logado["id"] == comentario_alvo.get("autor_id"):
                receita["comentarios"] = [c for c in lista_original if c["id"] != id]
                alterou = True
                break
            else:
                return jsonify({"erro": "Sem permissão para excluir este comentário"}), 403

    if alterou:
        salvar_dados(dados)
        return jsonify({"mensagem": "Comentário excluído!"}), 200
    
    return jsonify({"erro": "Comentário não encontrado"}), 404

@main_bp.route("/comentario/editar/<int:id>", methods=["PUT"])
def editar_comentario(id):
  
    usuario_logado = session.get("usuario")
    if not usuario_logado:
        return jsonify({"erro": "Acesso negado"}), 401

    corpo = request.get_json()
    novo_texto = corpo.get("texto", "").strip()

    if not novo_texto:
        return jsonify({"erro": "O comentário não pode estar vazio"}), 400

    dados = ler_dados()
    alterou = False

    for receita in dados["receitas"]:
        for comentario in receita.get("comentarios", []):
            if comentario["id"] == id:
         
                if usuario_logado["perfil"] == "admin" or usuario_logado["id"] == comentario.get("autor_id"):
                    comentario["texto"] = novo_texto
                    alterou = True
                    break
                else:
                    return jsonify({"erro": "Você não tem permissão para editar este comentário"}), 403
        if alterou: break

    if alterou:
        salvar_dados(dados)
        return jsonify({"mensagem": "Comentário atualizado com sucesso!"}), 200
    
    return jsonify({"erro": "Comentário não encontrado"}), 404