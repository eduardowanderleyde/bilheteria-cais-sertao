# 🎫 Sistema de Bilheteria - Museu Cais do Sertão

Sistema completo de gestão de bilheteria **Web** (FastAPI + HTMX) com interface moderna e responsiva, preparado para produção.

## 🚀 Características

- ✅ **Interface web moderna** com FastAPI + HTMX
- ✅ **Banco PostgreSQL** (produção) / SQLite (desenvolvimento)
- ✅ **Autenticação** segura com bcrypt e sessões
- ✅ **Sistema de papéis** (admin, gestora, bilheteira)
- ✅ **Relatórios avançados** com exportação CSV/Excel
- ✅ **Design responsivo** com Tailwind CSS
- ✅ **Auditoria completa** com logs de ações
- ✅ **Deploy automático** no Render
- ✅ **Validação robusta** com Pydantic

## 📋 Pré-requisitos

- Python 3.8 ou superior
- PostgreSQL (para produção) ou SQLite (desenvolvimento)

## 🛠️ Instalação

### Desenvolvimento Local

1. **Clone o repositório**
```bash
git clone https://github.com/eduardowanderleyde/bilheteria-cais-sertao.git
cd bilheteria-cais-sertao
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure o ambiente**
```bash
# Copie o arquivo de configuração
cp config.example .env

# Edite o arquivo .env e defina valores SEGUROS:
# IMPORTANTE: Substitua TODOS os valores CHANGE_ME
# 
# Exemplo de geração de SECRET_KEY segura:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
```

4. **Execute o setup inicial**
```bash
python seed_admin.py
```

5. **Execute a aplicação**
```bash
uvicorn app.main:app --reload
```

6. **Acesse o sistema**
- **URL:** http://127.0.0.1:8000
- **Usuários:** Conforme configurado no arquivo `.env`
  - Admin: definido em `ADMIN_USERNAME` e `ADMIN_PASSWORD`
  - Gestora: `gestora1` (se `GESTORA_PASSWORD` foi definido)
  - Bilheteiras: `bilheteira1`, `bilheteira2` (se `BILHETEIRA_PASSWORD` foi definido)

### Deploy em Produção (Render)

1. **Conecte seu repositório** ao Render
2. **Configure as variáveis de ambiente (OBRIGATÓRIO):**
   - `DATABASE_URL` (automático com PostgreSQL)
   - `SECRET_KEY` - Gere um valor seguro com: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - `ADMIN_USERNAME` - Nome do usuário administrador
   - `ADMIN_PASSWORD` - Senha segura (mínimo 8 caracteres)
   - `GESTORA_PASSWORD` (opcional) - Senha para usuárias gestoras
   - `BILHETEIRA_PASSWORD` (opcional) - Senha para bilheteiras
3. **Deploy automático** - o sistema criará as tabelas e usuários automaticamente

## 🎯 Funcionalidades

### Vendas Individuais
- Venda de ingressos (inteira, meia, gratuita)
- Motivos de desconto para meia/gratuidade
- Dados opcionais (nome, UF, cidade, observação)
- Forma de pagamento (crédito, débito, PIX)

### Vendas em Grupo
- Visitas agendadas e espontâneas
- Metadados da instituição
- Controle de ofício oficial
- Dados do responsável e localização

### Relatórios
- **Por UF:** Pessoas e receita por estado
- **Por motivos:** Descontos aplicados
- **Por forma de pagamento:** Análise financeira
- **Relatório diário:** Resumo completo em Excel

### Administração
- **Admin/Gestora:** Acesso total (incluindo exclusões)
- **Bilheteira:** Acesso limitado (sem exclusões)
- **Auditoria:** Log completo de todas as ações
- **Soft delete:** Exclusões seguras com rastreamento

## 🔐 Segurança

- **Autenticação:** Sessões seguras com cookies HTTP-only
- **Autorização:** Controle de acesso baseado em papéis
- **CSRF:** Proteção contra ataques cross-site
- **Validação:** Entrada de dados validada com Pydantic
- **Auditoria:** Log de todas as ações dos usuários

## 📊 Estrutura do Banco

### Tabelas Principais
- `users` - Usuários e papéis
- `orders` - Cabeçalho dos pedidos
- `order_items` - Itens dos pedidos (ingressos)
- `groups` - Metadados de visitas em grupo
- `order_events` - Log de auditoria

### Migração de Dados
```bash
# Migrar dados do sistema antigo
python migrate_legacy_data.py
```

## 🧪 Testes

```bash
# Instalar dependências de teste
pip install pytest

# Executar testes
python test_basic.py
```

## 📁 Estrutura do Projeto

```
bilheteria-cais/
├── app/
│   ├── __init__.py
│   ├── main.py          # Aplicação principal
│   ├── db.py            # Configuração do banco
│   ├── models.py        # Modelos SQLAlchemy
│   ├── schemas.py       # Schemas Pydantic
│   ├── auth.py          # Autenticação e autorização
│   ├── routes/          # Rotas da aplicação
│   └── services/        # Serviços de negócio
├── templates/           # Templates HTML
├── static/             # Arquivos estáticos
├── alembic/            # Migrações do banco
├── requirements.txt    # Dependências Python
├── render.yaml         # Configuração do Render
├── Procfile           # Comando de execução
└── seed_admin.py      # Script de criação de usuários
```

## 🚀 Deploy

### Render (Recomendado)
1. Conecte o repositório ao Render
2. Configure as variáveis de ambiente
3. Deploy automático com PostgreSQL

### Outras Plataformas
- **Heroku:** Use o Procfile
- **Railway:** Configure DATABASE_URL
- **DigitalOcean:** Use o render.yaml como referência

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```bash
# Banco de dados
DATABASE_URL=postgresql://user:pass@host:port/db

# Segurança - OBRIGATÓRIO
# Gere com: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=<valor_gerado_aleatoriamente_32+_caracteres>

# Usuário admin - OBRIGATÓRIO
ADMIN_USERNAME=seu_usuario_admin
ADMIN_PASSWORD=SuaSenhaForte123!

# Usuários opcionais (deixe vazio para não criar)
GESTORA_PASSWORD=
BILHETEIRA_PASSWORD=

# Aplicação
DEBUG=False
HOST=0.0.0.0
PORT=8000
SECURE_COOKIES=True
ENV=production
```

### Backup e Restauração
```bash
# Backup do PostgreSQL
pg_dump $DATABASE_URL > backup.sql

# Restauração
psql $DATABASE_URL < backup.sql
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs da aplicação
2. Consulte a documentação do FastAPI
3. Abra uma issue no GitHub

## 📄 Licença

Este projeto é de uso interno do Museu Cais do Sertão.

---

**Desenvolvido com ❤️ para o Museu Cais do Sertão**