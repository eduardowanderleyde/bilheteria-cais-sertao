# 📖 Manual de Uso - Sistema de Bilheteria

## 🎯 Visão Geral

O Sistema de Bilheteria do Museu Cais do Sertão permite:
- **Vender ingressos** (inteira, meia, gratuita)
- **Registrar dados** dos compradores
- **Gerar relatórios** de vendas
- **Exportar dados** para Excel

## 🚀 Primeiros Passos

### 1. Iniciar o Sistema

**Versão Desktop:**
```bash
python run_desktop.py
```

**Versão Web:**
```bash
python run_web.py
```
Acesse: http://127.0.0.1:8000

### 2. Fazer Login
- **Usuário:** `funcionario1`
- **Senha:** `123456`

## 🎫 Venda de Ingressos

### Tipos de Ingresso
- **Inteira:** R$ 10,00 (público geral)
- **Meia:** R$ 5,00 (estudantes, idosos)
- **Gratuita:** R$ 0,00 (crianças, grupos)

### Como Vender

1. **Selecione o tipo** de ingresso
2. **Digite a quantidade** (padrão: 1)
3. **Preencha dados opcionais:**
   - Nome do comprador
   - Estado (UF)
   - Cidade
   - Observação
4. **Clique em "Registrar Venda"**

### Campos Obrigatórios
- ✅ Tipo de ingresso
- ✅ Quantidade

### Campos Opcionais
- 📝 Nome do comprador
- 📝 Estado (UF)
- 📝 Cidade
- 📝 Observação

## 📊 Relatórios

### Acessar Relatórios
1. **Clique na aba "Relatórios"**
2. **Visualize o resumo** por dia
3. **Veja estatísticas** gerais

### Funcionalidades dos Relatórios
- **Resumo por dia** (últimos 30 dias)
- **Total de ingressos** vendidos
- **Faturamento total**
- **Dias com vendas**
- **Atualização automática**

### Exportar para Excel
1. **Clique em "Exportar Excel"**
2. **Escolha onde salvar** o arquivo
3. **Arquivo gerado** com dados detalhados

## 🔧 Funcionalidades Avançadas

### Atualizar Relatórios
- **Automático:** A cada 30 segundos
- **Manual:** Botão "Atualizar Relatórios"

### Imprimir Relatórios
- **Clique em "Imprimir"**
- **Use Ctrl+P** para imprimir a página

### Logout
- **Clique em "Sair"** no canto superior direito
- **Sistema retorna** à tela de login

## 📱 Interface Web vs Desktop

### Versão Web (Recomendada)
- ✅ **Interface moderna** com Tailwind CSS
- ✅ **Responsiva** (funciona em tablets)
- ✅ **Atualizações automáticas**
- ✅ **Pode ser acessada** de qualquer dispositivo na rede
- ✅ **Mesmo código** para web e desktop

### Versão Desktop
- ✅ **Interface nativa** do Windows
- ✅ **Não precisa** de navegador
- ✅ **Funciona offline**
- ✅ **Mais simples** de instalar

## 💾 Banco de Dados

### Localização
- **Arquivo:** `bilheteria.db`
- **Tipo:** SQLite
- **Backup:** Simplesmente copie o arquivo

### Estrutura
- **Tabela `users`:** Usuários do sistema
- **Tabela `sales`:** Vendas registradas

### Backup Automático
```bash
# Criar backup
copy bilheteria.db backup_%date%.db

# Restaurar backup
copy backup_20240101.db bilheteria.db
```

## 🔐 Segurança

### Autenticação
- **Senhas** com hash bcrypt
- **Sessão** por token
- **Logout automático** em caso de erro

### Dados
- **Validação** de todos os inputs
- **Sanitização** de dados
- **Prevenção** de SQL injection

## 📈 Performance

### Otimizações
- **WAL mode** ativado no SQLite
- **Índices** nas colunas principais
- **Consultas otimizadas**
- **Suporta milhões** de registros

### Monitoramento
- **Logs** no console (versão desktop)
- **Logs** no terminal (versão web)
- **API docs** em `/docs` (versão web)

## 🚨 Solução de Problemas

### Erro: "Usuário/senha inválidos"
**Solução:**
- Verifique se digitou corretamente
- Usuário: `funcionario1`
- Senha: `123456`

### Erro: "Quantidade deve ser maior que zero"
**Solução:**
- Digite uma quantidade válida (1 ou mais)
- Use apenas números

### Erro: "Erro ao salvar venda"
**Solução:**
- Verifique se o banco de dados existe
- Reinicie a aplicação
- Verifique os logs de erro

### Erro: "Não há vendas para exportar"
**Solução:**
- Registre algumas vendas primeiro
- Verifique se há dados no banco

### Erro: "Port 8000 already in use" (Web)
**Solução:**
- Feche outras aplicações na porta 8000
- Ou altere a porta em `run_web.py`

## 📋 Dicas de Uso

### Para Caixas
1. **Sempre verifique** o tipo de ingresso
2. **Confirme a quantidade** antes de registrar
3. **Preencha o nome** quando possível
4. **Use observações** para casos especiais

### Para Gerentes
1. **Monitore os relatórios** regularmente
2. **Faça backup** do banco semanalmente
3. **Exporte relatórios** mensalmente
4. **Verifique estatísticas** diariamente

### Para TI
1. **Monitore logs** de erro
2. **Faça backup** antes de atualizações
3. **Teste** em ambiente de desenvolvimento
4. **Documente** mudanças

## 🔄 Atualizações

### Atualizar Sistema
1. **Pare a aplicação**
2. **Faça backup** do banco
3. **Substitua arquivos** antigos
4. **Reinicie** a aplicação

### Atualizar Dependências
```bash
pip install -r requirements.txt --upgrade
```

## 📞 Suporte Técnico

### Logs de Erro
- **Desktop:** Console da aplicação
- **Web:** Terminal do servidor

### Documentação da API
- **Acesse:** http://127.0.0.1:8000/docs
- **Visualize** todas as rotas disponíveis
- **Teste** endpoints diretamente

### Arquivos de Configuração
- **Banco:** `bilheteria.db`
- **Logs:** Console/Terminal
- **Config:** Código fonte

---

**🎉 Sistema pronto para uso! Boas vendas!**
