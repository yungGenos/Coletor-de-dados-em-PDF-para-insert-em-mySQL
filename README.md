# Sistema de Coleta de Dados - Protótipo Melhorado

## 📋 Descrição
Sistema web profissional para coleta de dados de usuários com upload seguro de PDF e extração de texto.
Os dados são salvos em logs estruturados (JSON) com backup automático e validações robustas.

## 🚀 Funcionalidades

### ✅ Implementadas
- **Formulário dinâmico** com validação em tempo real
- **Upload seguro de PDF** com validação de integridade
- **Extração inteligente de texto** com tratamento de erros por página
- **Interface responsiva** com design moderno e acessível
- **Salvamento em logs** estruturados com backup automático
- **Visualização avançada** de dados coletados
- **Validação robusta** no frontend e backend
- **Logging estruturado** para auditoria e debugging
- **API de estatísticas** para monitoramento
- **Tratamento de erros** profissional

### 🎨 Interface
- **Design moderno** com gradientes e animações
- **Formulário responsivo** em duas colunas em desktop
- **Validação visual** em tempo real
- **Feedback imediato** de erros e sucessos
- **Loading states** durante processamento
- **Layout 100% responsivo** para todos os dispositivos

## 📁 Estrutura do Projeto
```
prototipo de iterceptação de dados/
├── app.py                    # Aplicação Flask principal (melhorada)
├── start.py                  # Script de inicialização com verificações
├── requirements.txt          # Dependências Python com versões fixas
├── .env.example             # Exemplo de configurações
├── templates/
│   ├── index.html           # Página principal (reescrita)
│   └── visualizar.html      # Página de visualização (atualizada)
├── uploads/                 # Pasta para arquivos PDF (auto-criada)
├── backups/                 # Pasta para backups diários (auto-criada)
├── dados_coletados.json     # Arquivo de dados estruturados
└── sistema_logs.log         # Logs detalhados do sistema
```

## 🛠️ Instalação e Execução

### Método 1: Script Automático (Recomendado)
```bash
python start.py
```

### Método 2: Manual
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar o sistema
python app.py
```

### 3. Acessar no navegador
```
http://localhost:5000
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente
Copie `.env.example` para `.env` e configure:
```bash
FLASK_ENV=development          # ou production
SECRET_KEY=sua_chave_secreta   # MUDE para produção!
MAX_FILE_SIZE=16777216         # Tamanho máximo do arquivo em bytes
```

## 📊 Fluxo do Sistema Melhorado

1. **Verificação inicial** do sistema e dependências
2. **Usuário acessa** a página principal (`/`)
3. **Preenche formulário** com validação em tempo real
4. **Anexa PDF** (opcional) com validação de integridade
5. **Sistema valida** dados no frontend e backend
6. **Processa PDF** página por página com tratamento de erros
7. **Salva dados** com backup automático e logging
8. **Exibe confirmação** com ID único e informações detalhadas
9. **Permite visualização** avançada em `/visualizar`

## � Melhorias de Segurança

### Validações Implementadas
- **Sanitização** de nomes de arquivos
- **Validação de integridade** de PDFs
- **Limite de páginas** (máximo 100 por PDF)
- **Validação de tamanho** de campos obrigatórios
- **Logging de atividades** para auditoria
- **Tratamento de exceções** em todos os pontos

### Dados Coletados para Auditoria
- **IP do usuário** que fez o upload
- **User-Agent** do navegador
- **Timestamp detalhado** de criação
- **Informações do arquivo** (nome original, tamanho, etc.)

## 📝 Formato dos Dados Salvos (Atualizado)

```json
{
  "timestamp": "2025-07-22T10:30:45.123456",
  "id": "uuid-gerado-automaticamente",
  "created_at": "2025-07-22 10:30:45",
  "version": "1.0",
  "data": {
    "formulario": {
      "criado_por": "Nome do Criador",
      "nome": "Nome da Pessoa",
      "responsavel": "Nome do Responsável",
      "observacoes": "Observações opcionais"
    },
    "pdf_content": "--- Página 1 ---\nTexto extraído...",
    "arquivo": {
      "nome_original": "documento.pdf",
      "nome_salvo": "20250722_103045_documento.pdf",
      "tamanho": 1048576,
      "caminho": "uploads/20250722_103045_documento.pdf"
    },
    "status": "processado",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  }
}
```

## 📱 Responsividade Aprimorada

### Desktop (1200px+)
- Formulário em duas colunas para Nome e Responsável
- Layout otimizado para produtividade

### Tablet (768px-1199px)
- Adaptação automática do layout
- Botões e campos otimizados para touch

### Mobile (até 767px)
- Formulário em coluna única
- Interface totalmente touch-friendly

## 🎯 Recursos Avançados

### API Endpoints
- `GET /api/stats` - Estatísticas do sistema
- `POST /upload` - Upload com validação robusta
- `GET /visualizar` - Interface de visualização

### Logging Estruturado
```python
2025-07-22 10:30:45 - app - INFO - Dados salvos com ID: abc123...
2025-07-22 10:30:46 - app - WARNING - PDF com 50 páginas processado
```

### Backup Automático
- Backup diário automático dos dados
- Rotação de logs para evitar crescimento excessivo
- Arquivo de configuração para personalização

## 🚀 Próximos Passos

1. **Integração com banco de dados** (SQLite/PostgreSQL)
2. **Sistema de autenticação** JWT
3. **Dashboard analytics** com gráficos em tempo real
4. **Export de dados** (Excel/CSV/PDF)
5. **API REST** completa com OpenAPI
6. **Notificações** via email/webhooks
7. **Containerização** com Docker

## � Monitoramento

### Estatísticas Disponíveis
- Total de registros processados
- Total de PDFs carregados
- Uptime do sistema
- Logs de erro e performance

### Comandos Úteis
```bash
# Ver logs em tempo real
tail -f sistema_logs.log

# Verificar estatísticas via API
curl http://localhost:5000/api/stats

# Verificar integridade dos dados
python -c "import json; [json.loads(line) for line in open('dados_coletados.json')]"
```

---

**Desenvolvido com foco em qualidade, segurança e escalabilidade**
