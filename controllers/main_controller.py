from flask import Blueprint, render_template, request, jsonify, session
from models.usuario import ler_dados, salvar_dados
from utils.validacoes import hash_senha, verificar_senha

main_bp = Blueprint('main', __name__)

# Chave secreta para criar contas de administrador
CHAVE_MESTRA_ADMIN = "123"

# =============================================================================
#   ROTAS DA APLICAÇÃO
# =============================================================================

@main_bp.route("/")
def index():
    """Rota principal — renderiza a página inicial com as receitas."""
    dados = ler_dados()
    usuario_logado = session.get("usuario")
    return render_template("index.html", receitas=dados["receitas"], usuario=usuario_logado)


@main_bp.route("/cadastrar", methods=["POST"])
def cadastrar():
    """
    Rota de cadastro de novo usuário.

    Recebe via JSON: { "nickname": "...", "senha": "..." }
    Retorna JSON com sucesso ou mensagem de erro.

    IMPORTANTE: A senha NUNCA deve ser salva em texto puro!
    Use a função hash_senha() que você implementou.
    """
    corpo = request.get_json()
    nickname = corpo.get("nickname", "").strip()
    senha = corpo.get("senha", "").strip()
    chave_enviada = corpo.get("chave_admin", "").strip()

    # Validação básica dos campos
    if not nickname or not senha:
        return jsonify({"erro": "Preencha todos os campos"}), 400

    dados = ler_dados()

    perfil_final = "admin" if chave_enviada == CHAVE_MESTRA_ADMIN else "comum"

    # Verifica se o nickname já existe
    for usuario in dados["usuarios"]:
        if usuario["nickname"].lower() == nickname.lower():
            return jsonify({"erro": "Nickname já está em uso"}), 409

    # Crie um dicionário novo_usuario
    novo_usuario = {
        "id": dados["proximo_usuario_id"],
        "nickname": nickname,
        "senha": hash_senha(senha),
        "perfil": perfil_final
    }
    # Adicione novo_usuario em dados["usuarios"]
    dados["usuarios"].append(novo_usuario)
    # Incremente dados["proximo_usuario_id"] em 1
    dados["proximo_usuario_id"] += 1
    # Chame salvar_dados(dados) para persistir
    salvar_dados(dados)
    # Retorne jsonify({"mensagem": "Cadastro realizado com sucesso!"})
    return jsonify({"mensagem": "Cadastro realizado com sucesso!"}), 201


@main_bp.route("/login", methods=["POST"])
def login():
    """
    Rota de autenticação.

    Recebe via JSON: { "nickname": "...", "senha": "..." }
    Em caso de sucesso, salva o usuário na sessão Flask.

    (Peso: 30% — Linguagem de Programação / estruturas condicionais)
    """
    corpo = request.get_json()
    nickname = corpo.get("nickname", "").strip()
    senha = corpo.get("senha", "").strip()

    if not nickname or not senha:
        return jsonify({"erro": "Preencha todos os campos"}), 400

    dados = ler_dados()
    usuario_encontrado = None

    # Busca o usuário pelo nickname (case-insensitive)
    for usuario in dados["usuarios"]:
        if usuario["nickname"].lower() == nickname.lower():
            usuario_encontrado = usuario
            break

    # verificar usuario e senha, se for None retorna erro 401
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
    """Remove o usuário da sessão (logout)."""
    session.pop("usuario", None)
    return jsonify({"mensagem": "Logout realizado com sucesso!"})


@main_bp.route("/status")
def status():
    """Rota utilitária — retorna o usuário da sessão atual (útil para debug)."""
    return jsonify({"usuario_logado": session.get("usuario")})

# =============================================================================
#   ROTAS DE EXCLUSÃO (RECEITAS E COMENTÁRIOS)
# =============================================================================

@main_bp.route("/receitas/deletar/<int:id>", methods=["DELETE"])
def deletar_receita(id):
    """Exclui uma receita se o usuário for admin ou o autor."""
    usuario_logado = session.get("usuario")
    if not usuario_logado:
        return jsonify({"erro": "Acesso negado"}), 401

    dados = ler_dados()
    receita_encontrada = None
    
    # Busca a receita para validar o autor
    for r in dados["receitas"]:
        if r["id"] == id:
            receita_encontrada = r
            break

    if not receita_encontrada:
        return jsonify({"erro": "Receita não encontrada"}), 404

    # Validação: Admin ou Dono da Receita (precisa que a receita tenha o campo 'autor_nickname')
    if usuario_logado["perfil"] == "admin" or usuario_logado["nickname"] == receita_encontrada.get("autor_nickname"):
        # Remove a receita da lista
        dados["receitas"] = [r for r in dados["receitas"] if r["id"] != id]
        salvar_dados(dados)
        return jsonify({"mensagem": "Receita excluída com sucesso!"}), 200

    return jsonify({"erro": "Sem permissão para excluir esta receita"}), 403


@main_bp.route("/comentario/<int:id>", methods=["DELETE"])
def excluir_comentario(id):
    """Exclui um comentário se o usuário for admin ou o autor."""
    usuario_logado = session.get("usuario")
    if not usuario_logado:
        return jsonify({"erro": "Acesso negado"}), 401

    dados = ler_dados()
    alterou = False

    # Percorre todas as receitas para achar o comentário dentro da lista de cada uma
    for receita in dados["receitas"]:
        lista_original = receita.get("comentarios", [])
        
        # Tenta encontrar o comentário para validar permissão
        comentario_alvo = next((c for c in lista_original if c["id"] == id), None)
        
        if comentario_alvo:
            # Validação: Admin ou Dono do Comentário
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
    """Edita o texto de um comentário se for o autor ou admin."""
    usuario_logado = session.get("usuario")
    if not usuario_logado:
        return jsonify({"erro": "Acesso negado"}), 401

    corpo = request.get_json()
    novo_texto = corpo.get("texto", "").strip()

    if not novo_texto:
        return jsonify({"erro": "O comentário não pode estar vazio"}), 400

    dados = ler_dados()
    alterou = False

    # Procura o comentário dentro de todas as receitas
    for receita in dados["receitas"]:
        for comentario in receita.get("comentarios", []):
            if comentario["id"] == id:
                # VALIDAÇÃO: Admin ou o próprio Autor (pelo ID)
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