# Guia de Limpeza Completa do Repositório

## ⚠️ ATENÇÃO: Este processo reescreve o histórico Git permanentemente!

### Pré-requisitos

1. **Instalar git-filter-repo:**
   ```bash
   pip install git-filter-repo
   ```

2. **Avisar a equipe** que todos terão que re-clonar após a operação.

3. **Fazer backup** do repositório atual (opcional, mas recomendado).

### Passo 1: Executar Limpeza Automática

```bash
python clean_repo_complete.py --confirm
```

Este script irá:
- Clonar o repositório espelhado
- Remover arquivos com credenciais do histórico
- Enviar o histórico limpo de volta

### Passo 2: Re-clonar o Repositório

```bash
cd C:\Users\Eduardo\Documents
git clone https://github.com/eduardowanderleyde/bilheteria-cais-sertao.git
cd bilheteria-cais-sertao
```

### Passo 3: Adicionar Arquivos Limpos

```bash
# Copiar arquivos sanitizados
copy seed_admin_clean.py seed_admin.py
copy setup_env_clean.py setup_env.py
copy test_login_clean.py test_login.py
copy run_server_clean.py run_server.py

# Copiar .env.example
copy env_example_complete.txt .env.example
```

### Passo 4: Configurar Ambiente

```bash
# Copiar exemplo para .env
copy .env.example .env

# Editar .env com suas credenciais seguras
notepad .env
```

### Passo 5: Commit e Push

```bash
git add seed_admin.py setup_env.py test_login.py run_server.py .env.example
git commit -m "chore(security): re-add sanitized files (env vars only)"
git push origin main
```

### Passo 6: Para Outros Clones Existentes

Cada clone precisa sincronizar com o histórico reescrito:

```bash
git fetch --all
git reset --hard origin/main
git clean -fdx
```

Ou simplesmente re-clonar:

```bash
rm -rf bilheteria-cais-sertao
git clone https://github.com/eduardowanderleyde/bilheteria-cais-sertao.git
```

## Arquivos que Serão Removidos do Histórico

- `seed_admin.py` (versão com credenciais hardcoded)
- `test_login.py` (versão com credenciais hardcoded)
- `run_server.py` (versão com SECRET_KEY hardcoded)
- `setup_env.py` (versão com credenciais hardcoded)

## Arquivos que Serão Re-adicionados (Limpos)

- `seed_admin.py` (usa variáveis de ambiente)
- `test_login.py` (usa variáveis de ambiente)
- `run_server.py` (gera SECRET_KEY automaticamente)
- `setup_env.py` (usa variáveis de ambiente)

## Verificação Final

Após a limpeza, verifique:

1. **GitGuardian** não deve mais detectar segredos
2. **Todos os scripts** usam variáveis de ambiente
3. **Arquivo .env** está no .gitignore
4. **Hook pre-commit** está ativo

## Credenciais que DEVEM ser Revogadas

- `18091992123`
- `***REMOVED***`
- `gestora123`
- `bilheteira123`
- `***REMOVED***`
- `funcionario1`
- `***REMOVED***` / `Januario 76` / `Januario72`
- `af5463df1a2dfa7ef04c91d89779a943f3a775469d26e18fa8cc2f5789bd55ab`

## Suporte

Se algo der errado, você pode:

1. **Restaurar do backup** (se fez)
2. **Re-clonar** do repositório remoto
3. **Contatar a equipe** para sincronizar

---

**Lembre-se:** Este processo é irreversível e afeta todos os desenvolvedores!
