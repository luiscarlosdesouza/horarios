# Guia de Deploy - Servidor de Produção

Este guia descreve os passos para colocar o sistema Horários em produção.

## Pré-requisitos no Servidor
-   Docker e Docker Compose instalados.
-   Git instalado.
-   Acesso à Internet.

## Passos para Deploy

1.  **Preparar Diretório e Clonar:**
    Acesse o servidor via SSH, crie o diretório `/sistemas` e clone o projeto:
    ```bash
    sudo mkdir -p /sistemas
    sudo chown $USER:$USER /sistemas
    cd /sistemas
    git clone https://github.com/luiscarlosdesouza/horarios.git
    cd horarios
    ```

2.  **Configurar Variáveis de Ambiente:**
    Crie o arquivo `.env` na raiz do projeto (`/sistemas/horarios`) com as credenciais de produção.
    **Nota:** Para produção, o `USP_CALLBACK_ID` deve ser **66**.
    
    Use o comando `nano .env` e cole o conteúdo:

    ```ini
    SECRET_KEY=sua_chave_secreta_super_segura_producao
    
    # Credenciais do Admin
    ADMIN_USERNAME=admin
    ADMIN_EMAIL=admin@ime.usp.br
    ADMIN_PASSWORD=SuaSenhaForteAqui
    
    # E-mail (IME-USP)
    EMAIL_USER=apoio
    EMAIL_PASSWORD=sua_senha_email
    EMAIL_SMTP_SERVER=smtp.ime.usp.br
    EMAIL_SMTP_PORT=587
    EMAIL_TO=admin@ime.usp.br
    
    # OAuth Google
    GOOGLE_CLIENT_ID=seu_client_id_google
    GOOGLE_CLIENT_SECRET=seu_client_secret_google
    
    # OAuth USP
    USP_CLIENT_KEY=seu_key_usp
    USP_CLIENT_SECRET=seu_secret_usp
    USP_CALLBACK_ID=66 
    
    # Timezone
    TZ=America/Sao_Paulo
    ```

3.  **Subir a Aplicação:**
    Execute o Docker Compose para construir e iniciar o container:
    ```bash
    sudo docker-compose up --build -d
    ```

4.  **Verificar Status:**
    Verifique se o container está rodando (deve estar "Up"):
    ```bash
    sudo docker ps
    ```

5.  **Inicialização do Banco de Dados (Apenas na 1ª Instalação):**
    Como as migrações automáticas foram desativadas para evitar erros em bancos vazios, execute os comandos abaixo manualmente para criar a estrutura:

    ```bash
    # 1. Gera o arquivo de migração inicial
    sudo docker-compose exec web flask db migrate -m "Initial schema"
    
    # 2. Aplica a migração (cria as tabelas)
    sudo docker-compose exec web flask db upgrade
    
    # 3. Cria o usuário admin
    sudo docker-compose exec web python create_admin.py
    ```

6.  **Importar Dados Iniciais:**
    -   Acesse o sistema no navegador (porta 5001 ou configure um proxy reverso Nginx para porta 80/443).
    -   Faça login como Admin.
    -   Vá em "Consultas" -> "Importar Dados".
    -   Faça o upload do arquivo CSV `todos_horarios.csv`.

## Atualizações Futuras
Para atualizar o sistema com novas modificações do GitHub:

1.  Entre na pasta do projeto: `cd horarios`
2.  Baixe as atualizações: `git pull origin main`
3.  Reconstrua o container: `sudo docker-compose up --build -d`
4.  Aplique eventuais novas migrações: `sudo docker-compose exec web flask db upgrade`
