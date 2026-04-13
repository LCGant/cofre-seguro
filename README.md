# Cofre de Senhas Seguro

Projeto acadêmico desenvolvido para a disciplina de **Programação de Computadores**.

O sistema implementa um cofre local em Python com interface gráfica moderna usando `ttkbootstrap`, autenticação por senha mestra, criptografia dos dados em disco e gerenciamento de **seis tipos de itens**: senhas, cartões, documentos, notas seguras, redes Wi-Fi e licenças de software.

## Objetivo

O objetivo do projeto é demonstrar a construção de uma aplicação desktop local com:

- interface gráfica moderna em `Tkinter + ttkbootstrap` (tema escuro/claro)
- organização modular do código
- persistência em arquivo local
- proteção de dados sensíveis com criptografia
- autenticação com mitigação contra tentativas repetidas de acesso
- suporte a múltiplos tipos de itens protegidos

## Tipos de itens suportados

| Tipo        | Ícone | Campos principais                                              |
|-------------|:-----:|----------------------------------------------------------------|
| Senha       | 🔒    | título, login, senha, observação                               |
| Cartão      | 💳    | título, número, titular, validade, CVV, bandeira, cor          |
| Documento   | 📄    | título, tipo (RG/CPF/CNH…), número, órgão, datas               |
| Nota segura | 📝    | título, conteúdo (texto livre)                                 |
| Wi-Fi       | 📶    | SSID, senha, tipo de segurança                                 |
| Licença     | 🔑    | software, chave, e-mail, data de compra, validade              |

## Funcionalidades

- criação de senha mestra no primeiro uso (com indicador de força em tempo real)
- login no cofre local (tela split com painel decorativo)
- suporte opcional a `keyfile`
- cadastro, edição e exclusão de itens de qualquer tipo
- **barra lateral (sidebar)** com filtros por categoria e contagem de itens
- **cards coloridos** por tipo na tela principal
- **busca global** em todos os itens
- **favoritos** (★) com filtro dedicado
- revelação de campos sensíveis (senha, CVV, chave) com reautenticação
- cópia para a área de transferência com **limpeza automática em 30s**
- **bloqueio automático** por inatividade após 5 minutos
- gerador de senhas fortes com slider de tamanho e toggles de classes
- alternância entre **tema escuro e claro**
- exportação/importação de credenciais em pacote criptografado
- atualização da segurança com nova senha mestra e/ou `keyfile`

## Segurança implementada

O projeto foi pensado para um cenário **local/offline**, dentro do escopo acadêmico.

Medidas adotadas:

- senha mestra nunca salva em texto puro
- verificação da senha com KDF forte
- criptografia autenticada dos dados do cofre
- armazenamento de `salt` aleatório
- uso de `secrets` para geração segura
- atraso progressivo após falhas de login
- bloqueio temporário após múltiplas tentativas incorretas
- reautenticação para ações sensíveis

Tecnologias de proteção usadas no projeto atual:

- `Argon2id` para derivação/verificação da senha mestra
- `AES-256-GCM` para criptografia autenticada dos dados
- `keyfile` opcional como segundo fator local de desbloqueio

Limite importante:

- o sistema reduz ataques dentro do aplicativo, mas não elimina totalmente risco de ataque offline se alguém copiar o arquivo criptografado do cofre

## Estrutura do projeto

```text
projeto_senhas/
├── cofre_seguro/
│   ├── __init__.py
│   ├── gui.py
│   ├── security.py
│   ├── storage.py
│   └── vault.py
├── docs/
│   ├── fluxograma_complexo.md
│   └── fluxograma_simples.md
├── main.py
├── requirements.txt
└── cofre_seguro_dados.json
```

## Arquitetura

- [main.py](main.py): ponto de entrada da aplicação
- [cofre_seguro/gui.py](cofre_seguro/gui.py): interface Tkinter
- [cofre_seguro/security.py](cofre_seguro/security.py): KDF, criptografia e geração segura
- [cofre_seguro/storage.py](cofre_seguro/storage.py): leitura e gravação do arquivo local
- [cofre_seguro/vault.py](cofre_seguro/vault.py): regras de negócio do cofre

## Execução

### 1. Criar ambiente virtual

```bash
python -m venv .venv
```

### 2. Ativar ambiente virtual

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

Observação:

- `Tkinter` faz parte da biblioteca padrão do Python
- `ttkbootstrap` é instalado automaticamente pelo `requirements.txt` (responsável pelo visual moderno)
- em algumas distribuições Linux, pode ser necessário instalar o pacote do sistema caso o módulo `tkinter` não venha disponível

### 4. Executar a aplicação

```bash
python main.py
```

Também é possível definir outro caminho para o arquivo do cofre:

```bash
python main.py --arquivo meu_cofre.json
```

## Fluxogramas

Os fluxogramas do projeto estão em:

- [docs/fluxograma_simples.md](docs/fluxograma_simples.md)
- [docs/fluxograma_complexo.md](docs/fluxograma_complexo.md)

Eles foram elaborados a partir do fluxo implementado no código atual.

## Escopo acadêmico

Este projeto foi desenvolvido com foco em aprendizado e demonstração de conceitos de:

- programação em Python
- modularização
- interface gráfica desktop
- persistência de dados
- segurança aplicada a software local

Não é um produto comercial nem uma solução auditada para uso crítico em produção.

## Autor

**LCGant**

Projeto acadêmico da disciplina de **Programação de Computadores**.
