# Funcionalidades do Cofre de Senhas Seguro

Guia completo de cada funcionalidade do projeto, onde esta no codigo e como funciona.

---

## NOVIDADES DA VERSAO ATUAL (resumo)

A interface foi totalmente redesenhada e o servico ganhou suporte a multiplos tipos de itens.
O fluxo central (criacao, login, criptografia AES-256-GCM + Argon2id) **continua o mesmo** — as
secoes 1 a 4 deste documento ainda descrevem corretamente a inicializacao, criacao e login.

### O que mudou desde o redesign

**Multiplos tipos de itens** (`vault.py`)
- O cofre agora guarda 6 tipos: `senha`, `cartao`, `documento`, `nota`, `wifi`, `licenca`
- Cada tipo tem seus proprios campos editaveis (definidos em `CAMPOS_EDITAVEIS_POR_TIPO`)
- Cada tipo tem campos sensiveis proprios (em `CAMPOS_SENSIVEIS_POR_TIPO`) que ficam mascarados
- API generica nova: `listar_itens()`, `adicionar_item()`, `editar_item()`, `excluir_item()`,
  `obter_item()`, `revelar_campo()`, `alternar_favorito()`, `contar_por_tipo()`
- API legada (`listar_credenciais`, `adicionar_credencial`, etc) mantida para compatibilidade

**Visual moderno com `ttkbootstrap`** (`gui.py`)
- Paleta propria estilo GitHub Dark (definida em `PALETA_ESCURA` / `PALETA_CLARA`)
- Tema escuro por padrao, alternavel para tema claro com `Ctrl+T`
- Tela split (hero decorativo + formulario) na criacao e login
- Indicador de forca de senha em tempo real com cor (vermelho → verde)
- Faixa de acento colorida no topo da janela (decorativa)

**Tela principal redesenhada** (`TelaPrincipal` em `gui.py`)
- **Sidebar** com 8 filtros: Todos, Favoritos + os 6 tipos. Cada item ativo destaca com a
  cor do tipo no texto + barra indicadora colorida + fundo elevado
- **Dashboard de stats** no topo: 6 tiles clicaveis com contagem por tipo e cor de identidade
- **Busca global** estilo barra com icone, atalho `Ctrl+F`
- **Cards** com badge colorido contendo o icone, divisor sutil, rotulo do tipo embaixo do
  titulo, e botao de "copiar usuario / SSID / e-mail" direto no card (sem precisar abrir detalhes)
- **Estado vazio** rico: badge circular gigante na cor do tipo, sugestoes de uso, botao
  "Adicionar agora" e dica do atalho
- **Scrollbar auto-hide**: so aparece quando ha mais conteudo do que cabe na tela
- **Scroll reseta ao topo** a cada troca de filtro (evita cards "sumidos")

**Diálogos repaginados**
- Formulario de novo/editar item: header colorido com a cor do tipo, seletor visual de tipo
  (grid de 6 botoes coloridos), campos uppercase estilo "label", barra de forca de senha
  durante o cadastro, gerador de senha integrado (botao ✨)
- Detalhes do item: cabecalho colorido + cards de cada campo com botoes 👁 (revelar)
  e 📋 (copiar). **Revelar nao pede mais a senha mestra** — sessao ja autenticada
- Gerador de senhas (`Ctrl+G`): caixa de senha em destaque, slider para tamanho, toggles
  para classes de caracteres (maiusculas, minusculas, numeros, especiais)
- Configuracoes (`Ctrl+,`): notebook com 3 abas — Seguranca (trocar senha mestra/keyfile),
  Exportar/Importar, Informacoes do cofre

**Atalhos de teclado (`F1` mostra o guia completo)**
- `Ctrl+N` → novo item
- `Ctrl+F` → focar busca (Esc dentro limpa)
- `Ctrl+L` → bloquear cofre (logout)
- `Ctrl+T` → alternar tema escuro/claro
- `Ctrl+,` → configuracoes
- `Ctrl+G` → gerador de senhas
- `Ctrl+0` → mostrar todos / `Ctrl+1..6` → filtrar por tipo
- `Ctrl+Shift+F` → so favoritos
- `F5` → recarregar lista
- `F1` → janela com todos os atalhos
- Em formularios: `Ctrl+S` salva, `Esc` cancela, `Ctrl+Z/Y/A/C/V/X` em campos de texto
- Em detalhes: `Ctrl+E` editar, `Delete` excluir

**Mouse**
- Roda do mouse: rolagem normal
- **Botao do meio + arrastar**: scroll-drag estilo visualizador de PDF (cursor vira ✥)
- Funciona em todas as listas e modais

**Seguranca aplicada na UI**
- **Bloqueio automatico apos 5 minutos** sem atividade (qualquer clique ou tecla reseta o timer)
- **Limpeza automatica do clipboard** 30 segundos apos copiar valor sensivel
- **Re-renderizacao da tela atual** ao trocar tema (preserva autenticacao em vez de voltar pro login)

**Otimizacoes internas** (`vault.py`)
- **Cache em memoria** do arquivo do cofre — evita reler o JSON do disco a cada chamada
  da UI (`obter_resumo_seguranca`, `cofre_requer_keyfile`, etc). Invalidado em todas as
  escritas via wrapper `_salvar_arquivo`
- Helper `_aplicar_migracao_legada` extrai a unica fonte de verdade da migracao de cofres
  antigos (campo `servico` → `titulo`, default de `tipo` e `favorito`)

---

## 1. INICIALIZACAO DO PROGRAMA

**Arquivo:** `main.py` (linha 47)

Quando voce roda o programa, ele faz 3 coisas:
- Cria o gerenciador de arquivos (`GerenciadorArquivoCofre`) — responsavel por ler e salvar o arquivo JSON
- Cria o servico do cofre (`ServicoCofre`) — responsavel por toda a logica (login, criptografia, CRUD)
- Abre a janela grafica (`iniciar_interface`) — a interface que o usuario ve

---

## 2. VERIFICACAO: JA EXISTE UM COFRE?

**Arquivo:** `gui.py` → metodo `_mostrar_tela_inicial` (linha 320, classe `AplicacaoCofre`)

O programa verifica se ja existe um arquivo de cofre salvo no disco:
- **NAO existe** → abre a Tela de Criacao (passo 3)
- **SIM existe** → abre a Tela de Login (passo 4)

Por baixo, chama `storage.py` → `existe_cofre()` (linha 43) que simplesmente verifica se o arquivo JSON existe.

---

## 3. TELA DE CRIACAO (primeiro uso)

**Arquivo:** `gui.py` → classe `TelaCriacaoMestra` (linha 379)

E a tela que aparece na primeira vez que o programa roda. O usuario preenche:
- Senha mestra (minimo 12 caracteres, com maiuscula, minuscula, numero e especial)
- Confirmacao da senha
- Keyfile opcional (um arquivo extra de seguranca)

### O que acontece ao clicar "Criar Cofre Seguro":

**Metodo:** `gui.py` → `_criar_cofre()` (linha 610)

1. Valida se as senhas coincidem
2. Valida a forca da senha → `security.py` → `validar_forca_senha_mestra()`
3. Se a senha for fraca → mostra erro e volta pra tela
4. Se a senha for forte → chama `vault.py` → `criar_cofre()` (linha 158) que:
   - Gera 2 salts aleatorios (numeros aleatorios para seguranca)
   - Cria um hash da senha com Argon2id (para verificar no login)
   - Deriva uma chave AES-256 da senha (para criptografar)
   - Criptografa os dados (vazios no inicio) com AES-256-GCM
   - Salva tudo no arquivo JSON via `storage.py` → `salvar()` (linha 78)
5. Redireciona para a Tela de Login

---

## 4. TELA DE LOGIN

**Arquivo:** `gui.py` → classe `TelaLogin` (linha 668)

O usuario digita a senha mestra (e keyfile, se configurado).

### O que acontece ao clicar "Entrar no Cofre":

**Metodo:** `gui.py` → `_tentar_login()` (linha 866) → chama `vault.py` → `tentar_login()` (linha 211)

1. **Verifica bloqueio** — se o cofre esta bloqueado por tentativas erradas, mostra contagem regressiva
2. **Verifica a senha** — usa Argon2id para derivar o hash e compara com o salvo (comparacao em tempo constante para seguranca)
3. **Se ACERTOU:**
   - Descriptografa os dados com AES-256-GCM
   - Guarda a chave na memoria da sessao
   - Abre a Area Principal
4. **Se ERROU:**
   - 1a falha → espera 1 segundo
   - 2a falha → espera 2 segundos
   - 3a falha → espera 4 segundos
   - 4a falha → espera 8 segundos
   - 5a falha → BLOQUEIA por 30 segundos
   - Bloqueios seguintes aumentam ate 300 segundos (5 minutos)

A contagem regressiva na tela e controlada por `gui.py` → `_iniciar_contagem()` (linha 920).

---

## 5. AREA PRINCIPAL (apos login)

**Arquivo:** `gui.py` → classe `TelaPrincipal` (linha 988)

E a tela principal com a tabela de credenciais e todos os botoes. Tem 10 funcionalidades:

---

### 5.1 BUSCAR CREDENCIAIS

**Botao:** Campo de texto "Buscar servico"
**Codigo:** `gui.py` → `_carregar_credenciais()` (linha 1221) → `vault.py` → `listar_credenciais()` (linha 401)

- A busca acontece em tempo real: cada tecla digitada filtra a tabela
- Procura no nome do servico, login e observacao
- Retorna as credenciais SEM mostrar as senhas

---

### 5.2 NOVA CREDENCIAL

**Botao:** "Nova credencial"
**Codigo:** `gui.py` → `_nova_credencial()` (linha 1269) → abre `DialogoCredencial` (linha 1668) → `vault.py` → `adicionar_credencial()` (linha 465)

- Abre uma janela modal com campos: Servico, Usuario/E-mail, Senha, Observacao
- Tem um gerador de senha forte embutido (8 a 64 caracteres)
- Valida campos obrigatorios e duplicidade (mesmo servico + mesmo login)
- Ao salvar, criptografa tudo e grava no arquivo

---

### 5.3 EDITAR CREDENCIAL

**Botao:** "Editar" (ou duplo clique na linha)
**Codigo:** `gui.py` → `_editar_credencial()` (linha 1280) → abre `DialogoCredencial` (linha 1668) → `vault.py` → `editar_credencial()` (linha 515)

- Abre a mesma janela modal, preenchida com os dados atuais
- Permite alterar qualquer campo
- Valida duplicidade ignorando a propria credencial

---

### 5.4 EXCLUIR CREDENCIAL

**Botao:** "Excluir"
**Codigo:** `gui.py` → `_excluir_credencial()` (linha 1311) → `vault.py` → `excluir_credencial()` (linha 563)

- Pede confirmacao antes de excluir ("Deseja realmente excluir?")
- Remove a credencial da lista e recriptografa o cofre

---

### 5.5 REVELAR SENHA

**Botao:** "Revelar senha"
**Codigo:** `gui.py` → `_revelar_senha()` (linha 1353) → `vault.py` → `revelar_senha()` (linha 597)

- Pede a senha mestra novamente (reautenticacao para seguranca)
- Se a senha mestra estiver correta, mostra a senha da credencial em um popup
- Se estiver errada, mostra erro

---

### 5.6 COPIAR SENHA

**Botao:** "Copiar senha"
**Codigo:** `gui.py` → `_copiar_senha()` (linha 1382) → `vault.py` → `revelar_senha()` (linha 597)

- Tambem pede reautenticacao
- Copia a senha para a area de transferencia (Ctrl+V)
- LIMPA AUTOMATICAMENTE apos 20 segundos por seguranca (`_limpar_clipboard_se_necessario`, linha 1427)
- Usa um token interno para verificar se a senha no clipboard ainda e a mesma

---

### 5.7 EXPORTAR CREDENCIAIS

**Botao:** "Exportar"
**Codigo:** `gui.py` → `_exportar_credenciais()` (linha 1479) → `vault.py` → `exportar_credenciais()` (linha 615)

- Pede para escolher onde salvar o arquivo de backup
- Pede uma senha de exportacao (pode ser diferente da senha mestra)
- Cria um arquivo JSON criptografado independente do cofre
- Util para backup ou transferir credenciais para outro computador

---

### 5.8 IMPORTAR CREDENCIAIS

**Botao:** "Importar"
**Codigo:** `gui.py` → `_importar_credenciais()` (linha 1542) → `vault.py` → `importar_credenciais()` (linha 695)

- Seleciona um arquivo exportado anteriormente
- Pede a senha que foi usada na exportacao
- Pergunta se quer sobrescrever credenciais duplicadas
- Resultado mostra: quantas inseridas, atualizadas e ignoradas

---

### 5.9 FORTALECER COFRE

**Botao:** "Fortalecer cofre"
**Codigo:** `gui.py` → `_fortalecer_cofre()` (linha 1469) → abre `DialogoSeguranca` (linha 1962) → `vault.py` → `reconfigurar_seguranca()` (linha 798)

- Permite trocar a senha mestra
- Permite ativar/desativar/trocar o keyfile
- Pede a senha mestra atual para autorizar
- Recriptografa todo o cofre com as novas credenciais

---

### 5.10 SAIR

**Botao:** "Sair"
**Codigo:** `gui.py` → `_sair()` (linha 1601) → `vault.py` → `encerrar_sessao()` (linha 885)

- Sobrescreve todas as senhas na memoria com texto vazio ("")
- Anula as chaves de criptografia da sessao
- Volta para a Tela de Login

---

## MODULOS DE SUPORTE

### security.py — Criptografia

Contem todas as funcoes de seguranca do projeto. O fluxo de criptografia funciona em duas etapas:

#### Etapa 1: Argon2id — Transformar a senha em chave (KDF)

O problema: a senha que o usuario digita (ex: "MinhaSenh@123") e fraca demais para usar como chave de criptografia. Ela tem poucos bytes e padroes previsiveis. O algoritmo AES precisa de exatamente 32 bytes aleatorios e fortes.

O Argon2id resolve isso. Ele e um KDF (Key Derivation Function — funcao de derivacao de chave) que transforma a senha fraca em uma chave forte de 32 bytes.

**Por que Argon2id e nao outro algoritmo?**
- E o vencedor da competicao Password Hashing Competition (2015), ou seja, foi escolhido por especialistas em seguranca como o melhor algoritmo para proteger senhas
- Combina protecao contra dois tipos de ataque: Argon2i (resistente a ataques de canal lateral) e Argon2d (resistente a ataques com GPU). O "id" no nome significa que ele usa os dois
- Usa muita memoria RAM de proposito (64MB neste projeto). Isso significa que cada tentativa de adivinhar a senha precisa de 64MB, tornando ataques de forca bruta extremamente caros — um atacante precisaria de milhoes de GB de RAM para testar milhoes de senhas ao mesmo tempo
- E mais moderno e seguro que alternativas como bcrypt (2002) e scrypt (2009)

**Parametros usados no projeto** (definidos em `security.py`):
- `memory_cost = 65536` → usa 64MB de RAM por tentativa
- `iterations = 3` → processa a senha 3 vezes (mais lento = mais seguro)
- `lanes = 4` → usa 4 threads paralelas no processamento
- `dklen = 32` → gera uma chave de 32 bytes (256 bits)

#### Etapa 2: AES-256-GCM — Criptografar os dados

Depois que o Argon2id gera a chave de 32 bytes, o AES-256-GCM usa essa chave para criptografar as credenciais do usuario.

**Por que AES-256-GCM?**
- **AES (Advanced Encryption Standard)** e o padrao mundial de criptografia simetrica, usado por governos, bancos e militares. Foi adotado pelo NIST (Instituto Nacional de Padroes dos EUA) em 2001 e nunca foi quebrado
- **256** e o tamanho da chave em bits. Com 256 bits, existem 2^256 combinacoes possiveis — um numero tao grande que testar todas levaria mais tempo do que a idade do universo, mesmo com todos os computadores do mundo trabalhando juntos
- **GCM (Galois/Counter Mode)** e o modo de operacao que, alem de criptografar, tambem **autentica** os dados. Isso significa que se alguem alterar 1 byte do arquivo criptografado, a descriptografia falha automaticamente — o programa detecta que os dados foram adulterados
- E mais seguro que o modo antigo do projeto (Fernet), que usa AES-128-CBC sem autenticacao independente

**Elementos de seguranca adicionais:**
- **Nonce** (12 bytes aleatorios): um "numero usado uma vez" que garante que criptografar os mesmos dados duas vezes gere resultados completamente diferentes. Sem ele, um atacante poderia comparar dados criptografados e encontrar padroes
- **AAD** ("Cofre de Senhas Seguro v2"): dado adicional autenticado. Vincula o texto criptografado a este projeto especifico — impede que alguem pegue dados criptografados de outro lugar e tente usar aqui

#### Salt — Garantir unicidade

O salt e um numero aleatorio de 16 bytes gerado toda vez que o cofre e criado ou reconfigurado.

**Por que usar salt?**
- Sem salt, a mesma senha sempre geraria a mesma chave. Um atacante poderia pre-calcular uma tabela gigante de "senha → chave" (chamada rainbow table) e comparar
- Com salt, a mesma senha gera chaves completamente diferentes em cada cofre. Tabelas pre-calculadas ficam inuteis

**Por que o projeto usa DOIS salts separados?**
- `salt_verificador` → usado para gerar o hash que confere se a senha esta correta
- `salt_criptografia` → usado para gerar a chave que criptografa os dados

Usar salts diferentes garante que as duas derivacoes sejam completamente independentes. Comprometer uma nao ajuda a descobrir a outra.

O salt NAO e segredo — ele e salvo em texto claro no arquivo JSON. Seu papel nao e ser secreto, e garantir que cada cofre tenha derivacoes unicas.

#### Comparacao em tempo constante (hmac.compare_digest)

Quando o programa verifica se a senha esta correta, ele compara o hash calculado com o hash salvo usando `hmac.compare_digest`. Essa funcao leva o mesmo tempo para comparar, independente de quantos bytes estao corretos.

**Por que isso importa?**
- Uma comparacao normal (==) para no primeiro byte diferente. Se o primeiro byte esta errado, retorna rapido. Se so o ultimo byte esta errado, demora mais
- Um atacante poderia medir esse tempo e descobrir a senha byte a byte (ataque de timing)
- O `hmac.compare_digest` sempre leva o mesmo tempo, eliminando esse tipo de ataque

#### Gerador de senhas fortes

Funcao `gerar_senha_forte()` que cria senhas aleatorias usando o modulo `secrets` do Python (criptograficamente seguro, diferente do `random` que e previsivel).

Garante que a senha tenha pelo menos um caractere de cada grupo selecionado (maiuscula, minuscula, numero, especial) e embaralha usando o algoritmo Fisher-Yates para que a posicao dos caracteres tambem seja aleatoria.

#### Formato legado (compatibilidade)

O projeto tambem suporta um formato antigo que usava:
- **scrypt** em vez de Argon2id para derivacao de chave
- **Fernet (AES-128-CBC)** em vez de AES-256-GCM para criptografia

Quando o usuario faz login em um cofre antigo, o programa **migra automaticamente** para o formato novo (mais seguro), de forma transparente.

---

### storage.py — Armazenamento

Classe `GerenciadorArquivoCofre` que cuida do arquivo JSON:

- **Escrita atomica** (`salvar()`, linha 78) → primeiro grava num arquivo temporario, depois substitui o original com `os.replace()`. Se o programa crashar no meio da gravacao, o arquivo original nao se corrompe porque a substituicao so acontece quando a gravacao esta completa
- **fsync** → forca o sistema operacional a gravar os dados no disco fisico antes de substituir o arquivo, evitando perda por cache
- **Permissao 600** (`os.chmod`) → configura o arquivo para que somente o dono possa ler e escrever. Outros usuarios do computador nao conseguem acessar
