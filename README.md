# DIO Explorer 🚀

> Projeto desenvolvido durante o bootcamp **[IBM Bob: IA de Nível Empresarial para Desenvolvedores e Tech Leaders](https://web.dio.me/track/6c94a3da-1f22-45f6-be56-a2bad071ef51)** na plataforma [DIO](https://www.dio.me).

Um explorador de trilhas de aprendizado da DIO com interface no terminal (TUI), construído em Python com a biblioteca `curses`. Permite navegar, filtrar e acompanhar o progresso nas trilhas, realizar desafios de código e emitir certificados — tudo sem sair do terminal.

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| 📋 **Explorar trilhas** | Lista todas as 30 trilhas disponíveis com nível, tecnologia e badges |
| 🔍 **Filtrar por nome ou tecnologia** | Comando `/trilha [filtro]` para busca em tempo real |
| ⏵ **Acompanhar progresso** | Inicia e remove trilhas em andamento; estado persiste entre sessões |
| ⚔️ **Desafios de código** | Gera um desafio contextualizado ao nível e tecnologia da trilha |
| 🏆 **Concluir trilhas** | Marca uma trilha como concluída ao finalizar seu desafio |
| 🎓 **Emitir certificado** | Gera um certificado personalizado com nome, badges e código de verificação |
| 💾 **Persistência** | Progresso e certificados salvos em arquivos JSON locais |

---

## 🏗️ Arquitetura

O projeto segue o padrão **MVC (Model — View — Controller)** com uma camada de serviço intermediária, garantindo separação de responsabilidades e testabilidade.

```
dio_explorer/src/
├── model.py       # Model   — tipos de dados (TypedDicts) e repositórios
├── service.py     # Service — lógica de negócio (busca, progresso, desafios, certificados)
├── controller.py  # Controller — estado da aplicação e tratamento de eventos de teclado
├── view.py        # View   — toda a renderização curses (sem estado próprio)
└── tui.py         # Entrypoint — cabeamento das camadas e loop principal
```

### Diagrama de camadas

```
┌─────────────────────────────────────────────────────────────┐
│                         tui.py                              │
│              (entrypoint · loop de eventos)                 │
└───────┬──────────────────────────────────────┬─────────────┘
        │                                      │
        ▼                                      ▼
┌───────────────┐                    ┌──────────────────┐
│ controller.py │                    │    view.py       │
│  AppState     │◄── lê estado ──────│  draw_list()     │
│  Controller   │                    │  draw_detail()   │
└───────┬───────┘                    │  show_fullscreen │
        │ delega                     │  show_challenge  │
        ▼                            │  show_certificate│
┌───────────────┐                    └──────────────────┘
│  service.py   │
│ TrackService  │
│ ProgressSvc   │
│ ChallengeSvc  │
│ CertificateSvc│
└───────┬───────┘
        │ acessa
        ▼
┌───────────────┐
│   model.py    │
│ Track (dict)  │
│ TrackRepository│
│ ProgressRepo  │
└───────┬───────┘
        │ lê/grava
        ▼
┌───────────────────────────────────┐
│  dio_explorer/data/               │
│  ├── trilhas_dio.json             │
│  ├── progress.json                │
│  └── certificados-emitidos/       │
│      └── certificado_trilha_N.json│
└───────────────────────────────────┘
```

### Descrição das camadas

**`model.py` — Model**
- `Track` / `Promotion` / `Live` — TypedDicts que espelham o schema do JSON
- `TrackRepository` — carrega e expõe a lista de trilhas do arquivo JSON
- `ProgressRepository` — persiste os conjuntos `in_progress` e `completed` em `progress.json`

**`service.py` — Service Layer**
- `TrackService` — busca e filtragem de trilhas; retorna `SearchResult`
- `ProgressService` — lógica de negócio: iniciar, remover e concluir trilhas
- `ChallengeService` — gera texto de desafio contextualizado ao nível da trilha
- `CertificateService` — gera, persiste e recarrega certificados em JSON

**`controller.py` — Controller**
- `AppState` — dataclass com todo o estado reativo (trilhas visíveis, seleção, modo de comando, mensagens)
- `Controller` — recebe eventos de teclado, orquestra os serviços e atualiza o estado

**`view.py` — View**
- Funções puras de renderização curses; recebem dados como parâmetros, nunca armazenam estado
- `draw_list()`, `draw_detail()`, `draw_cmdbar()` — painéis do layout principal
- `show_fullscreen()`, `show_challenge()`, `show_certificate()` — telas de overlay
- Todas usam `win.noutrefresh()` + `curses.doupdate()` para renderização atômica

---

## 🗂️ Estrutura de arquivos

```
ibm-bob-dio-project/
├── README.md
├── AGENTS.md                        # Regras de desenvolvimento para agentes IA
├── pyproject.toml                   # Configuração do projeto e ruff
├── .venv/                           # Ambiente virtual (não versionado)
├── dio_explorer/
│   ├── src/
│   │   ├── tui.py                   # Entrypoint
│   │   ├── model.py                 # Model layer
│   │   ├── service.py               # Service layer
│   │   ├── controller.py            # Controller layer
│   │   └── view.py                  # View layer
│   ├── data/
│   │   ├── trilhas_dio.json         # Catálogo de 30 trilhas (somente leitura)
│   │   ├── progress.json            # Progresso do usuário (gerado em runtime)
│   │   └── certificados-emitidos/   # Certificados gerados (gerado em runtime)
│   ├── mcp/
│   │   └── server.py                # Servidor MCP (expõe ferramentas para agentes IA)
│   ├── docs/
│   │   └── mvc-refactor.md          # Documentação da arquitetura e roadmap de testes
│   └── commands/                    # Reservado
├── .bob/
│   ├── commands/                    # Comandos slash do Bob (/trilha, /desafio, /certificado)
│   └── skills/                      # Skills do Bob espelhando os comandos
```

---

## ⌨️ Comandos disponíveis na TUI

| Tecla / Comando | Ação |
|---|---|
| `↑` / `↓` | Navegar entre trilhas |
| `Enter` | Abrir detalhe completo da trilha selecionada |
| `/trilha [filtro]` | Filtrar trilhas por nome ou tecnologia |
| `/desafio` | Exibir somente trilhas em andamento |
| `/certificado` | Exibir somente trilhas concluídas |
| `Esc` | Limpar filtro / fechar overlay |
| `q` | Sair da aplicação |

**Na tela de detalhe (Enter):**

| Tecla | Condição | Ação |
|---|---|---|
| `S` | Qualquer trilha | Iniciar / remover do progresso |
| `D` | Trilha em andamento | Abrir desafio de código |
| `C` | Trilha concluída | Ver certificado |

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.12+
- [`uv`](https://github.com/astral-sh/uv) (gerenciador de pacotes)

### Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd ibm-bob-dio-project

# Crie o ambiente virtual e instale as dependências
uv venv
uv pip install --python .venv/bin/python "mcp[cli]>=2.3.0" ruff
```

### Executar a TUI

```bash
.venv/bin/python dio_explorer/src/tui.py
```

> **Importante:** execute sempre a partir da raiz do projeto para que os caminhos de dados sejam resolvidos corretamente.

---

## 🛠️ Desenvolvimento

### Lint e formatação

```bash
# Verificar
.venv/bin/ruff check dio_explorer/
.venv/bin/ruff format --check dio_explorer/

# Aplicar correções automáticas
.venv/bin/ruff check --fix dio_explorer/ && .venv/bin/ruff format dio_explorer/
```

### Validação de sintaxe

```bash
python3 -m py_compile dio_explorer/src/model.py \
                       dio_explorer/src/service.py \
                       dio_explorer/src/controller.py \
                       dio_explorer/src/view.py \
                       dio_explorer/src/tui.py
```

### Convenções de código

- **Idioma do código:** inglês (nomes de classes, métodos, variáveis, docstrings)
- **Idioma da UI:** português (textos exibidos ao usuário no terminal)
- **`model.py` e `controller.py` não importam `curses`** — são testáveis sem terminal
- **`view.py` nunca chama `win.refresh()`** — usa `win.noutrefresh()` + `curses.doupdate()`
- **`line-length = 100`** configurado no `pyproject.toml`

---

## 🤖 Servidor MCP

O projeto inclui um servidor [MCP (Model Context Protocol)](https://modelcontextprotocol.io) em `dio_explorer/mcp/server.py` que expõe as funcionalidades do DIO Explorer como ferramentas para agentes de IA (como o IBM Bob).

### Ferramentas disponíveis

| Ferramenta | Descrição |
|---|---|
| `list_tracks` | Lista todas as trilhas, com filtro opcional por nome ou tecnologia |
| `get_track` | Retorna detalhes completos de uma trilha pelo ID |
| `get_progress` | Retorna os IDs de trilhas em andamento e concluídas |
| `toggle_progress` | Inicia ou remove uma trilha do progresso |
| `generate_challenge` | Gera um desafio de código para uma trilha pelo ID |
| `complete_track` | Marca uma trilha como concluída (irreversível) |
| `get_certificate` | Carrega ou gera o certificado de uma trilha concluída |

### Como registrar no Bob

Adicione ao arquivo `mcp.json` do workspace (`.bob/mcp.json`):

```json
{
  "mcpServers": {
    "dio-explorer": {
      "command": ".venv/bin/python",
      "args": ["dio_explorer/mcp/server.py"]
    }
  }
}
```

> O servidor lê e grava os mesmos arquivos de dados da TUI (`progress.json`, `certificados-emitidos/`), portanto o estado é compartilhado entre as duas interfaces.

### Executar o servidor manualmente (para testes)

```bash
.venv/bin/python dio_explorer/mcp/server.py
```

O servidor usa transporte **stdio** — aguarda mensagens JSON-RPC na entrada padrão.

---

## 🎓 Sobre o bootcamp

Este projeto foi desenvolvido como parte do bootcamp **[IBM Bob: IA de Nível Empresarial para Desenvolvedores e Tech Leaders](https://web.dio.me/track/6c94a3da-1f22-45f6-be56-a2bad071ef51)** oferecido pela [DIO](https://www.dio.me) em parceria com a IBM.

O bootcamp explora o uso do **IBM Bob** como assistente de IA para engenharia de software, abordando desde arquitetura de aplicações até boas práticas de desenvolvimento com suporte de IA generativa.

---

## 📄 Licença

Projeto educacional — sem licença comercial.
