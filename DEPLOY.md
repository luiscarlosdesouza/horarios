# Guia de Deploy e Desenvolvimento

## 1. Ambiente de Produção (Servidor)

Este guia descreve os passos para colocar o sistema Horários em produção.

### Pré-requisitos
-   Docker e Docker Compose instalados.
-   Git instalado.
-   Acesso à Internet.

### Passos para Deploy

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
    Crie o arquivo `.env` na raiz do projeto com as credenciais de produção.
    **Nota:** Para produção, o `USP_CALLBACK_ID` deve ser **66**.
    
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
    Execute o Docker Compose:
    ```bash
    sudo docker-compose up --build -d
    ```

4.  **Inicialização do Banco de Dados (Primeira Vez):**
    ```bash
    # Cria estrutura do banco
    sudo docker-compose exec web flask db upgrade
    
    # Cria usuário admin (se configurado no .env)
    sudo docker-compose exec web python create_admin.py
    ```

---

## 2. Ambiente de Desenvolvimento (Local / Home Office)

Para continuar o desenvolvimento em casa:

### Pré-requisitos
-   Docker Desktop ou Docker Engine + Compose.
-   Git.

### Configuração Inicial

1.  **Clonar o Repositório:**
    ```bash
    git clone https://github.com/luiscarlosdesouza/horarios.git
    cd horarios
    ```

2.  **Configurar `.env`:**
    Crie um arquivo `.env` baseado no exemplo acima, mas pode usar credenciais de teste.
    **Importante:** Para rodar localmente (localhost), o `USP_CALLBACK_ID` geralmente é diferente (ex: **64** ou outro configurado para 127.0.0.1).

3.  **Rodar o Projeto:**
    ```bash
    # Subir o container (o código fonte é mapeado, então edições locais funcionam na hora)
    docker-compose up -d
    ```
    Acesse em: `http://localhost:5001`

4.  **Aplicar Migrações (Banco Novo):**
    ```bash
    docker-compose exec web flask db upgrade
    docker-compose exec web python create_admin.py
    ```

### Comandos Úteis

-   **Ver logs:** `docker-compose logs -f web`
-   **Reiniciar serviço:** `docker-compose restart web`
-   **Parar tudo:** `docker-compose down`
-   **Instalar nova dependência:** 
    1. Adicione ao `requirements.txt`.
    2. Rode `docker-compose up --build -d`.

### Backup e Restauração de Dados

Se quiser levar os dados do servidor para casa:

1.  **Backup (no servidor):**
    ```bash
    # Copia o banco SQLite do container para a pasta local
    docker-compose cp web:/app/instance/horarios.db ./horarios_backup.db
    # ou se estiver mapeado na máquina local:
    cp instance/horarios.db ~/Desktop/horarios_backup.db
    ```
    Baixe o arquivo `horarios_backup.db` via SCP/SFTP.

2.  **Restaurar (em casa):**
    Coloque o arquivo na pasta `instance/` local:
    ```bash
    mkdir -p instance
    mv horarios_backup.db instance/horarios.db
    ```
    Reinicie o container.
