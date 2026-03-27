# 🍽️ Sabor do Brasil — Cofre Gastronômico

O **Sabor do Brasil** é uma aplicação web interativa para compartilhamento de receitas típicas. O projeto utiliza **Python (Flask)** no backend e uma interface moderna com **HTML5/CSS3** e **JavaScript Vanilla**, implementando um sistema completo de permissões, interações sociais e persistência de dados em JSON.

---

## 🏗️ Arquitetura do Sistema (MVC)

O projeto foi estruturado seguindo o padrão **Model-View-Controller**, separando a lógica de dados da interface do usuário:

### 📂 Estrutura de Pastas

```text
📁 sabor-do-brasil/
├── 📄 app.py                # Ponto de entrada da aplicação
├── 📄 usuarios.json         # Banco de dados (JSON)
├── 📁 controllers/          # Lógica de rotas e regras de negócio
│   ├── 📄 main_controller.py
│   └── 📄 receitas_controller.py
├── 📁 models/               # Manipulação de dados e arquivos
│   └── 📄 usuario.py
├── 📁 static/               # Arquivos estáticos (CSS)
│   └── 📄 style.css
├── 📁 templates/            # Interfaces (Jinja2/HTML)
│   └── 📄 index.html
└── 📁 utils/                # Funções auxiliares (Segurança/Validação)
    └── 📄 validacoes.py

    -----------------------------------------------------------------------------------

    🛠️ Descrição dos Componentes
1. Backend (Python/Flask)
app.py: Configura o servidor Flask, define a chave de segurança para sessões e registra os Blueprints. Garante que o arquivo de dados usuarios.json esteja presente antes da inicialização.

controllers/main_controller.py: Gerencia o fluxo de autenticação (Login/Cadastro) e as rotas de exclusão. Implementa a lógica de perfil (Admin vs. Comum).

controllers/receitas_controller.py: Foca nas interações de conteúdo. Gerencia a criação de receitas, o sistema de curtidas (toggle) e a adição de comentários.

models/usuario.py: Camada de persistência. Contém as funções ler_dados() e salvar_dados(), centralizando o acesso ao sistema de arquivos para evitar conflitos.

utils/validacoes.py: (Referenciado nos controllers) Contém a lógica de hash de senhas e verificações de permissão (ex: se o usuário logado é dono do comentário que tenta editar).

2. Frontend (HTML/CSS/JS)
index.html: Página principal que utiliza o motor de templates Jinja2 para renderizar receitas e comentários dinamicamente.

Logic.js (Embutido): Controla a abertura de modais, chamadas de API via fetch e o Minijogo da Velha contra IA.

style.css: Design responsivo com variáveis CSS. Utiliza a paleta oficial:

--laranja: #D97014 (Cor primária/gastronômica)

--erro: #FF0000 (Feedback visual de validação)

🎮 Funcionalidades Principais
🔐 Autenticação Segura: Senhas são criptografadas antes de serem salvas. O login é mantido via session do Flask.

⚔️ Desafio Admin: Para habilitar o campo de "Chave de Administrador" no cadastro, o usuário deve vencer a IA em uma partida de Jogo da Velha integrada ao modal.

❤️ Interação Social: Usuários logados podem curtir receitas (com atualização em tempo real no contador) e postar comentários.

🛡️ Controle de Acesso:

Comum: Pode gerenciar apenas suas próprias interações.

Admin: Possui "Poder de Moderador", podendo excluir qualquer comentário ou receita do sistema.

📍 Feedback de Erro: Campos obrigatórios ou credenciais inválidas ativam bordas vermelhas e mensagens de alerta dinâmicas.

  -----------------------------------------------------------------------------------

Como Executar o Projeto:
Clone o repositório:

git clone [https://github.com/seu-usuario/sabor-do-brasil.git](https://github.com/seu-usuario/sabor-do-brasil.git)

Instale as dependências:
pip install flask

Inicie a aplicação:
python app.py

Acesse no navegador:
http://127.0.0.1:8000