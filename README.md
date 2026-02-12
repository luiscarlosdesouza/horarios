# Sistema de Horários

Sistema para gerenciamento e visualização de horários de aulas, importando dados de CSV e integrando com autenticação USP (Senha Única).

## Instalação

1.  Crie um ambiente virtual: `python3 -m venv .venv`
2.  Ative o ambiente: `source .venv/bin/activate`
3.  Instale as dependências: `pip install -r requirements.txt`
4.  Configure as variáveis de ambiente: `cp .env-example .env` e edite o arquivo `.env`.
5.  Inicialize o banco de dados: `flask db upgrade`
6.  Execute a aplicação: `flask run --port 5001`

## Estrutura

-   `app.py`: Ponto de entrada da aplicação.
-   `config.py`: Configurações do projeto.
-   `models.py`: Modelos do banco de dados.
-   `views.py`: Rotas e visualizações.
-   `templates/`: Templates HTML.
