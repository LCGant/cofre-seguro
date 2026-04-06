# Importa a funcionalidade de "annotations" que permite usar tipos mais modernos no Python
# (por exemplo, usar "str | None" em vez de "Optional[str]")
from __future__ import annotations

# Importa o módulo "secrets" que gera valores aleatórios seguros (usado para criar senhas e tokens)
import secrets
# Importa o módulo "tkinter" que é a biblioteca padrão do Python para criar janelas e interfaces gráficas
import tkinter as tk
# Importa a classe "datetime" que trabalha com datas e horários
from datetime import datetime
# Importa submódulos do tkinter:
# - filedialog: abre janelas para o usuário escolher ou salvar arquivos no computador
# - messagebox: mostra caixinhas de aviso, erro ou confirmação na tela
# - simpledialog: mostra uma janelinha simples pedindo que o usuário digite algo
# - ttk: versão mais moderna e bonita dos componentes visuais do tkinter
from tkinter import filedialog, messagebox, simpledialog, ttk

# Importa a função que verifica se a senha mestra é forte o suficiente (do nosso próprio módulo de segurança)
from .security import validar_forca_senha_mestra
# Importa a classe ServicoCofre que faz toda a lógica de guardar, ler e proteger as senhas
from .vault import ServicoCofre


# Define a classe AplicacaoCofre, que herda de tk.Tk (a janela principal do tkinter)
# Herdar de tk.Tk significa que essa classe É uma janela, com todos os poderes de uma janela
class AplicacaoCofre(tk.Tk):
    """Janela principal responsável por alternar telas da aplicação."""

    # Método __init__ é o "construtor" — é chamado automaticamente quando criamos um objeto dessa classe
    # O parâmetro "servico" recebe o ServicoCofre que cuida da lógica das senhas
    # "-> None" significa que esse método não retorna nenhum valor
    def __init__(self, servico: ServicoCofre) -> None:
        """Configura janela base, estilo visual e fluxo inicial."""
        # super().__init__() chama o construtor da classe pai (tk.Tk) para criar a janela de verdade
        super().__init__()
        # Guarda o serviço do cofre como atributo do objeto para usar em outros métodos
        self.servico = servico
        # Define o título que aparece na barra superior da janela
        self.title("Cofre de Senhas Seguro")
        # Define o tamanho inicial da janela: 1160 pixels de largura por 760 de altura
        self.geometry("1160x760")
        # Define o tamanho mínimo da janela (o usuário não pode diminuir mais que isso)
        self.minsize(960, 620)
        # Define a cor de fundo da janela (um bege claro "#f6f1e8")
        self.configure(background="#f6f1e8")
        # Define o que acontece quando o usuário clica no "X" para fechar a janela:
        # em vez de fechar direto, chama nosso método que limpa dados sensíveis antes
        self.protocol("WM_DELETE_WINDOW", self._encerrar_aplicacao)

        # Chama o método que configura as cores, fontes e estilos visuais de toda a interface
        self._configurar_estilo()
        # Cria um frame (uma "caixa" invisível) que serve de container para todas as telas
        # style="App.TFrame" aplica o estilo visual definido, padding=18 coloca 18 pixels de espaço interno
        self._container = ttk.Frame(self, style="App.TFrame", padding=18)
        # pack() posiciona o container na janela
        # fill="both" faz o container preencher todo o espaço disponível (horizontal e vertical)
        # expand=True faz o container crescer quando a janela é redimensionada
        self._container.pack(fill="both", expand=True)

        # Variável que guarda qual tela está sendo exibida no momento (começa sem nenhuma)
        self._frame_atual: ttk.Frame | None = None
        # Mostra a primeira tela (login ou criação, dependendo se o cofre já existe)
        self._mostrar_tela_inicial()

    # Método que define todas as cores, fontes e aparências dos elementos visuais
    def _configurar_estilo(self) -> None:
        """Define tema e estilos ttk da interface."""
        # Cria um objeto de estilo vinculado a esta janela
        estilo = ttk.Style(self)
        # Usa o tema "clam" que é um dos temas visuais disponíveis no ttk (visual limpo e moderno)
        estilo.theme_use("clam")

        # --- Estilos de Frames (caixas/containers) ---

        # Estilo do frame principal do app — fundo bege claro
        estilo.configure("App.TFrame", background="#f6f1e8")
        # Estilo de "cartão" — fundo quase branco, com borda fina sólida ao redor
        estilo.configure(
            "Card.TFrame",
            background="#fffdf8",  # Cor de fundo branco levemente amarelado
            borderwidth=1,        # Espessura da borda: 1 pixel
            relief="solid",       # Tipo da borda: linha sólida
        )
        # Estilo do painel de segurança — fundo verde escuro para destacar informações importantes
        estilo.configure("Painel.TFrame", background="#173b36")

        # --- Estilos de Labels (textos estáticos na tela) ---

        # Estilo para títulos grandes — fundo bege, texto verde escuro, fonte grande e negrito
        estilo.configure(
            "Titulo.TLabel",
            background="#f6f1e8",    # Cor de fundo bege
            foreground="#173b36",    # Cor do texto verde escuro
            font=("Segoe UI", 24, "bold"),  # Fonte Segoe UI, tamanho 24, negrito
        )
        # Estilo para subtítulos — fundo bege, texto cinza esverdeado, fonte menor
        estilo.configure(
            "Subtitulo.TLabel",
            background="#f6f1e8",    # Cor de fundo bege
            foreground="#5d685f",    # Cor do texto cinza esverdeado
            font=("Segoe UI", 11),  # Fonte tamanho 11, sem negrito
        )
        # Estilo para rótulos de campos de formulário — negrito para destacar o nome do campo
        estilo.configure(
            "Campo.TLabel",
            background="#f6f1e8",
            foreground="#1f3736",
            font=("Segoe UI", 10, "bold"),
        )
        # Estilo para rótulos de campos dentro de cartões (fundo branco em vez de bege)
        estilo.configure(
            "CampoCard.TLabel",
            background="#fffdf8",
            foreground="#1f3736",
            font=("Segoe UI", 10, "bold"),
        )
        # Estilo para textos normais — sem negrito, cor verde acinzentado
        estilo.configure(
            "Texto.TLabel",
            background="#f6f1e8",
            foreground="#324746",
            font=("Segoe UI", 10),
        )
        # Estilo para textos normais dentro de cartões (fundo branco)
        estilo.configure(
            "TextoCard.TLabel",
            background="#fffdf8",
            foreground="#324746",
            font=("Segoe UI", 10),
        )
        # Estilo para títulos dentro de cartões — negrito, tamanho 11
        estilo.configure(
            "TituloCard.TLabel",
            background="#fffdf8",
            foreground="#173b36",
            font=("Segoe UI", 11, "bold"),
        )
        # Estilo para títulos grandes dentro de diálogos/janelas popup — fonte grande
        estilo.configure(
            "TituloDialogo.TLabel",
            background="#fffdf8",
            foreground="#173b36",
            font=("Segoe UI", 24, "bold"),
        )
        # Estilo para subtítulos dentro de cartões — cinza, sem negrito
        estilo.configure(
            "SubtituloCard.TLabel",
            background="#fffdf8",
            foreground="#5d685f",
            font=("Segoe UI", 11),
        )
        # Estilo para badges (etiquetas pequenas) — fundo verde escuro, texto claro, fonte pequena
        # padding=(10, 4) coloca 10 pixels de espaço nas laterais e 4 pixels em cima e embaixo
        estilo.configure(
            "Badge.TLabel",
            background="#173b36",
            foreground="#f8f4eb",
            font=("Segoe UI", 9, "bold"),
            padding=(10, 4),
        )
        # Estilo para textos de destaque — fundo escuro com texto claro (usado no painel de segurança)
        estilo.configure(
            "Destaque.TLabel",
            background="#173b36",
            foreground="#f8f4eb",
            font=("Segoe UI", 10, "bold"),
        )

        # --- Estilos de Botões ---

        # Estilo do botão primário (ação principal) — fundo verde escuro, texto branco, negrito
        # padding=(14, 9) coloca 14 pixels de espaço horizontal e 9 vertical dentro do botão
        # borderwidth=0 remove a borda, focuscolor="none" remove o contorno de foco
        estilo.configure(
            "Primario.TButton",
            background="#173b36",
            foreground="#fffdf8",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 9),
            borderwidth=0,
            focuscolor="none",
        )
        # Estilo do botão secundário (ação secundária) — fundo bege, texto escuro, sem negrito
        estilo.configure(
            "Secundario.TButton",
            background="#eadfc9",
            foreground="#173b36",
            font=("Segoe UI", 10),
            padding=(12, 8),
            borderwidth=0,
            focuscolor="none",
        )
        # Define as cores do botão primário quando o mouse passa por cima, quando é clicado ou desabilitado
        # "active" = mouse em cima, "pressed" = clicado, "disabled" = desativado/cinza
        estilo.map(
            "Primario.TButton",
            background=[
                ("active", "#12312d"),    # Cor quando o mouse está em cima (verde mais escuro)
                ("pressed", "#102a27"),   # Cor quando o botão é pressionado (verde ainda mais escuro)
                ("disabled", "#aab9b4"),  # Cor quando o botão está desativado (cinza)
            ],
            foreground=[("disabled", "#f2ede4")],  # Cor do texto quando desativado
        )
        # Define as cores do botão secundário nos mesmos estados
        estilo.map(
            "Secundario.TButton",
            background=[
                ("active", "#dcccad"),    # Mouse em cima — bege mais escuro
                ("pressed", "#d3c09d"),   # Clicado — bege ainda mais escuro
                ("disabled", "#ece4d5"),  # Desativado — bege bem claro
            ],
            foreground=[
                ("active", "#173b36"),    # Texto quando mouse em cima — verde escuro
                ("disabled", "#8a8a84"),  # Texto quando desativado — cinza
            ],
        )

        # --- Estilos de Checkbuttons (caixas de seleção com "tique") ---

        # Estilo padrão do checkbutton — fundo bege
        estilo.configure(
            "TCheckbutton",
            background="#f6f1e8",
            foreground="#1f3736",
            font=("Segoe UI", 10),
        )
        # Estilo do checkbutton dentro de cartões — fundo branco
        estilo.configure(
            "Card.TCheckbutton",
            background="#fffdf8",
            foreground="#1f3736",
            font=("Segoe UI", 10),
        )

        # --- Estilos de Entry (campos de texto onde o usuário digita) ---

        # Estilo do campo de entrada — fundo branco, texto escuro
        # insertcolor é a cor do cursor que pisca dentro do campo
        # padding=8 coloca 8 pixels de espaço interno no campo
        estilo.configure(
            "TEntry",
            fieldbackground="#fffdf8",
            foreground="#1f3736",
            insertcolor="#1f3736",
            padding=8,
            borderwidth=1,
        )
        # Quando o campo está em foco (selecionado para digitar), a borda fica verde escuro
        estilo.map(
            "TEntry",
            bordercolor=[("focus", "#173b36")],
            lightcolor=[("focus", "#173b36")],
            darkcolor=[("focus", "#173b36")],
        )

        # --- Estilos de Spinbox (campo numérico com setinhas para aumentar/diminuir) ---

        # Estilo do spinbox — fundo branco, setas de tamanho 14 pixels
        estilo.configure(
            "TSpinbox",
            fieldbackground="#fffdf8",
            foreground="#1f3736",
            arrowsize=14,
            padding=6,
        )
        # Borda verde escuro quando o spinbox está em foco
        estilo.map(
            "TSpinbox",
            bordercolor=[("focus", "#173b36")],
            lightcolor=[("focus", "#173b36")],
            darkcolor=[("focus", "#173b36")],
        )

        # --- Estilos de LabelFrame (caixa com título na borda) ---

        # Estilo do contorno do LabelFrame — fundo branco, borda sólida
        estilo.configure(
            "TLabelframe",
            background="#fffdf8",
            borderwidth=1,
            relief="solid",
        )
        # Estilo do texto do título que aparece na borda do LabelFrame
        estilo.configure(
            "TLabelframe.Label",
            background="#fffdf8",
            foreground="#173b36",
            font=("Segoe UI", 10, "bold"),
        )

        # --- Estilos de Treeview (tabela com linhas e colunas para mostrar dados) ---

        # Estilo das células da tabela — fundo branco, texto escuro, altura da linha 32 pixels
        estilo.configure(
            "Treeview",
            background="#fffdf8",
            fieldbackground="#fffdf8",
            foreground="#243938",
            font=("Segoe UI", 10),
            rowheight=32,
            borderwidth=0,
        )
        # Estilo do cabeçalho da tabela (a linha com os nomes das colunas) — fundo bege escuro, negrito
        # padding=(8, 9) coloca espaço interno no cabeçalho
        estilo.configure(
            "Treeview.Heading",
            background="#efe4d0",
            foreground="#173b36",
            font=("Segoe UI", 10, "bold"),
            padding=(8, 9),
        )
        # Quando uma linha da tabela é selecionada, ela fica com fundo verde claro e texto escuro
        estilo.map(
            "Treeview",
            background=[("selected", "#d8e4df")],
            foreground=[("selected", "#173b36")],
        )

    # Método que decide qual tela mostrar primeiro (criação do cofre ou login)
    def _mostrar_tela_inicial(self) -> None:
        """Decide entre fluxo de primeiro uso e login normal."""
        # Se o cofre já existe no disco, mostra a tela de login
        if self.servico.existe_cofre():
            self.mostrar_tela_login()
        # Se não existe, mostra a tela para criar o cofre pela primeira vez
        else:
            self.mostrar_tela_criacao()

    # Método que troca a tela exibida na janela — remove a tela atual e coloca a nova
    # O parâmetro "classe_tela" recebe o tipo da tela que queremos mostrar
    def _trocar_tela(self, classe_tela: type[ttk.Frame]) -> None:
        """Substitui o frame exibido no container principal."""
        # Se já existe uma tela sendo exibida, destrói ela (remove da janela)
        if self._frame_atual is not None:
            self._frame_atual.destroy()
        # Cria uma nova instância da tela desejada, passando o container e o app como parâmetros
        self._frame_atual = classe_tela(self._container, self)
        # Posiciona a nova tela preenchendo todo o espaço do container
        # fill="both" = preenche largura e altura, expand=True = cresce junto com a janela
        self._frame_atual.pack(fill="both", expand=True)

    # Método para mostrar a tela de criação da senha mestra (primeiro uso)
    def mostrar_tela_criacao(self) -> None:
        """Exibe tela para criação inicial da senha mestra."""
        self._trocar_tela(TelaCriacaoMestra)

    # Método para mostrar a tela de login (digitar senha para entrar)
    def mostrar_tela_login(self) -> None:
        """Exibe tela de autenticação por senha mestra."""
        self._trocar_tela(TelaLogin)

    # Método para mostrar a tela principal do cofre (onde ficam as senhas salvas)
    def mostrar_tela_principal(self) -> None:
        """Exibe área principal do cofre após login bem-sucedido."""
        self._trocar_tela(TelaPrincipal)

    # Método que fecha o aplicativo de forma segura, limpando dados sensíveis da memória
    def _encerrar_aplicacao(self) -> None:
        """Finaliza app limpando sessão para reduzir exposição em memória."""
        # Encerra a sessão do cofre (limpa senhas da memória por segurança)
        self.servico.encerrar_sessao()
        # Destrói a janela e fecha o programa
        self.destroy()


# Função auxiliar (fora das classes) que configura várias colunas de um layout em grade
# para que todas tenham o mesmo tamanho e se expandam igualmente
def configurar_colunas_expansiveis(frame: tk.Widget, total_colunas: int, grupo: str) -> None:
    """Configura colunas com expansão horizontal e largura uniforme."""
    # Percorre cada coluna de 0 até total_colunas-1
    for indice in range(total_colunas):
        # weight=1 faz a coluna se expandir quando a janela cresce
        # uniform=grupo faz todas as colunas do mesmo grupo terem a mesma largura
        frame.columnconfigure(indice, weight=1, uniform=grupo)


# Classe da tela de criação da senha mestra (mostrada no primeiro uso do aplicativo)
# Herda de ttk.Frame — ou seja, é um "painel" que pode conter outros elementos visuais
class TelaCriacaoMestra(ttk.Frame):
    """Tela de primeiro uso para criação da senha mestra inicial."""

    # Construtor da tela — recebe o container pai e a referência para o app principal
    def __init__(self, parent: ttk.Frame, app: AplicacaoCofre) -> None:
        """Monta interface de configuração inicial do cofre."""
        # Chama o construtor do ttk.Frame para criar o painel com o estilo visual correto
        super().__init__(parent, style="App.TFrame")
        # Guarda a referência do aplicativo principal para poder trocar de tela depois
        self.app = app
        # Cria variáveis do tkinter que ficam conectadas aos campos de texto
        # Quando o usuário digita no campo, o valor é atualizado automaticamente na variável
        self.var_senha = tk.StringVar()         # Guarda a senha digitada pelo usuário
        self.var_confirmacao = tk.StringVar()    # Guarda a confirmação da senha
        self.var_usar_keyfile = tk.BooleanVar(value=False)  # Guarda se o usuário quer usar keyfile (começa desmarcado)
        self.var_keyfile = tk.StringVar()        # Guarda o caminho do arquivo keyfile
        # Chama o método que monta todos os elementos visuais na tela
        self._montar_interface()
        # Atualiza o estado dos controles de keyfile (habilitados ou desabilitados)
        self._atualizar_estado_keyfile()

    # Método que cria todos os elementos visuais da tela de criação
    def _montar_interface(self) -> None:
        """Renderiza campos e ações de criação da senha mestra."""
        # Cria um frame para o cabeçalho (título e subtítulo da tela)
        cabecalho = ttk.Frame(self, style="App.TFrame")
        # Posiciona o cabeçalho preenchendo a largura toda
        # fill="x" = preenche só na horizontal
        # pady=(10, 18) = 10 pixels de espaço acima e 18 abaixo do cabeçalho
        cabecalho.pack(fill="x", pady=(10, 18))

        # Cria um badge (etiqueta) escrito "COFRE LOCAL"
        # anchor="w" no pack() alinha o elemento à esquerda ("w" = west = oeste = esquerda)
        # pady=(0, 10) = 0 pixels acima e 10 abaixo
        ttk.Label(cabecalho, text="COFRE LOCAL", style="Badge.TLabel").pack(anchor="w", pady=(0, 10))
        # Cria o título principal da tela
        ttk.Label(cabecalho, text="Configuração Inicial", style="Titulo.TLabel").pack(anchor="w")
        # Cria o subtítulo explicativo
        # wraplength=900 faz o texto quebrar de linha automaticamente ao atingir 900 pixels
        # justify="left" alinha o texto à esquerda
        ttk.Label(
            cabecalho,
            text="Crie a senha mestra do cofre e, se quiser, ative um keyfile local.",
            style="Subtitulo.TLabel",
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        # Cria um cartão (caixa branca com borda) para os campos do formulário
        # padding=18 coloca 18 pixels de espaço interno em todos os lados
        cartao = ttk.Frame(self, style="Card.TFrame", padding=18)
        # fill="x" = preenche a largura toda, pady=(0, 16) = 16 pixels de espaço embaixo
        cartao.pack(fill="x", pady=(0, 16))

        # Cria o rótulo "Senha mestra" e posiciona na grade (linha 0, coluna 0)
        # grid() posiciona elementos em formato de tabela (linhas x colunas)
        # sticky="w" = gruda o elemento no lado esquerdo da célula
        # padx=(0, 14) = 0 pixels à esquerda e 14 à direita
        # pady=(0, 10) = 0 pixels acima e 10 abaixo
        ttk.Label(cartao, text="Senha mestra", style="CampoCard.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 14),
            pady=(0, 10),
        )
        # Cria o campo de texto para digitar a senha mestra
        # textvariable conecta o campo à variável var_senha (o que digitar vai para a variável)
        # show="*" mostra asteriscos em vez dos caracteres reais (para esconder a senha)
        # width=42 define a largura do campo em caracteres
        ttk.Entry(
            cartao,
            textvariable=self.var_senha,
            show="*",
            width=42,
            font=("Segoe UI", 11),
        # Posiciona na linha 0, coluna 1, ocupando 3 colunas (columnspan=3)
        ).grid(row=0, column=1, columnspan=3, sticky="w", pady=(0, 10))

        # Cria o rótulo "Confirmar senha" na linha 1, coluna 0
        ttk.Label(cartao, text="Confirmar senha", style="CampoCard.TLabel").grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 14),
            pady=(0, 10),
        )
        # Cria o campo para confirmar a senha (digitar a mesma senha de novo)
        ttk.Entry(
            cartao,
            textvariable=self.var_confirmacao,
            show="*",
            width=42,
            font=("Segoe UI", 11),
        ).grid(row=1, column=1, columnspan=3, sticky="w", pady=(0, 10))

        # Cria uma caixa de seleção (checkbox) para o usuário escolher se quer usar keyfile
        # variable conecta à variável booleana (True quando marcado, False quando desmarcado)
        # command define a função que é chamada quando o usuário clica no checkbox
        ttk.Checkbutton(
            cartao,
            text="Exigir keyfile local no desbloqueio",
            variable=self.var_usar_keyfile,
            style="Card.TCheckbutton",
            command=self._atualizar_estado_keyfile,
        # columnspan=4 faz ocupar todas as 4 colunas da grade
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 10))

        # Cria o rótulo "Keyfile" na linha 3
        ttk.Label(cartao, text="Keyfile", style="CampoCard.TLabel").grid(
            row=3,
            column=0,
            sticky="w",
            padx=(0, 14),
            pady=(0, 10),
        )
        # Cria o campo de texto para mostrar o caminho do keyfile selecionado
        # Guarda em self._entrada_keyfile para poder habilitar/desabilitar depois
        self._entrada_keyfile = ttk.Entry(
            cartao,
            textvariable=self.var_keyfile,
            width=52,
            font=("Segoe UI", 10),
        )
        # sticky="we" = estica o campo da esquerda (w=west) até a direita (e=east)
        self._entrada_keyfile.grid(row=3, column=1, sticky="we", pady=(0, 10))

        # Cria o botão "Selecionar" que abre uma janela para escolher um keyfile existente
        self._botao_keyfile = ttk.Button(
            cartao,
            text="Selecionar",
            style="Secundario.TButton",
            command=self._selecionar_keyfile,
        )
        # padx=(8, 8) = 8 pixels de espaço em cada lado do botão
        self._botao_keyfile.grid(row=3, column=2, sticky="w", padx=(8, 8), pady=(0, 10))

        # Cria o botão "Gerar keyfile" que cria um arquivo keyfile novo
        self._botao_gerar_keyfile = ttk.Button(
            cartao,
            text="Gerar keyfile",
            style="Secundario.TButton",
            command=self._gerar_keyfile,
        )
        self._botao_gerar_keyfile.grid(row=3, column=3, sticky="w", pady=(0, 10))

        # Faz a coluna 1 do cartão se expandir para preencher o espaço disponível
        # weight=1 significa que essa coluna "puxa" o espaço extra quando a janela cresce
        cartao.columnconfigure(1, weight=1)

        # Cria um frame para os botões de ação (Criar Cofre e Fechar)
        botoes = ttk.Frame(self, style="App.TFrame")
        # fill="x" = ocupa toda a largura, pady=(4, 0) = 4 pixels de espaço acima
        botoes.pack(fill="x", pady=(4, 0))
        # Configura 2 colunas com tamanhos iguais para os botões ficarem lado a lado
        configurar_colunas_expansiveis(botoes, 2, "acoes_criacao")

        # Cria o botão principal "Criar Cofre Seguro" que inicia o processo de criação
        ttk.Button(
            botoes,
            text="Criar Cofre Seguro",
            style="Primario.TButton",
            command=self._criar_cofre,
        # sticky="ew" = estica o botão de leste a oeste (preenche toda a largura da célula)
        # padx=(0, 6) = 0 pixels à esquerda e 6 à direita (espaço entre os botões)
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        # Cria o botão "Fechar" que encerra o aplicativo
        ttk.Button(
            botoes,
            text="Fechar",
            style="Secundario.TButton",
            command=self.app._encerrar_aplicacao,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    # Método que habilita ou desabilita os campos de keyfile dependendo do checkbox
    def _atualizar_estado_keyfile(self) -> None:
        """Habilita ou desabilita os controles de keyfile conforme a escolha do usuário."""
        # Se o checkbox está marcado, estado é "normal" (habilitado); senão, "disabled" (desabilitado)
        estado = "normal" if self.var_usar_keyfile.get() else "disabled"
        # Aplica o estado no campo de texto do keyfile
        self._entrada_keyfile.configure(state=estado)
        # Para botões ttk, usa-se .state() — "!disabled" = habilitado, "disabled" = desabilitado
        self._botao_keyfile.state(["!disabled"] if estado == "normal" else ["disabled"])
        self._botao_gerar_keyfile.state(["!disabled"] if estado == "normal" else ["disabled"])

    # Método que abre uma janela para o usuário escolher um keyfile já existente
    def _selecionar_keyfile(self) -> None:
        """Permite selecionar um keyfile existente no disco."""
        # Abre a janela de seleção de arquivo do sistema operacional
        caminho = filedialog.askopenfilename(
            parent=self,
            title="Selecionar keyfile",
        )
        # Se o usuário selecionou um arquivo (não cancelou), guarda o caminho na variável
        if caminho:
            self.var_keyfile.set(caminho)

    # Método que gera um novo arquivo keyfile e salva no disco
    def _gerar_keyfile(self) -> None:
        """Gera um novo keyfile dedicado e grava no caminho escolhido pelo usuário."""
        # Abre a janela de "Salvar como" para o usuário escolher onde salvar o keyfile
        # defaultextension=".key" adiciona a extensão .key automaticamente
        # initialfile define o nome sugerido para o arquivo
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar keyfile",
            defaultextension=".key",
            initialfile="cofre_seguro.key",
        )
        # Se o usuário cancelou a janela, não faz nada
        if not caminho:
            return

        # Tenta criar o keyfile usando o serviço do cofre
        try:
            self.app.servico.criar_keyfile(caminho)
        # Se ocorrer qualquer erro, mostra uma mensagem de erro ao usuário
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível gerar o keyfile: {exc}")
            return

        # Atualiza o campo de texto com o caminho do keyfile recém-criado
        self.var_keyfile.set(caminho)
        # Mostra mensagem de sucesso avisando para guardar o arquivo em local seguro
        messagebox.showinfo(
            "Keyfile criado",
            "Keyfile criado com sucesso. Guarde esse arquivo em local seguro.",
        )

    # Método que valida tudo e cria o cofre de senhas
    def _criar_cofre(self) -> None:
        """Valida entradas e cria o cofre inicial com senha mestra e keyfile opcional."""
        # Pega os valores digitados pelo usuário nos campos
        senha = self.var_senha.get()
        confirmacao = self.var_confirmacao.get()
        usar_keyfile = self.var_usar_keyfile.get()
        # strip() remove espaços em branco do início e fim; "or None" transforma string vazia em None
        caminho_keyfile = self.var_keyfile.get().strip() or None

        # Verifica se ambos os campos de senha foram preenchidos
        if not senha or not confirmacao:
            messagebox.showwarning("Campos obrigatórios", "Preencha e confirme a senha mestra.")
            return

        # Verifica se a senha e a confirmação são iguais
        if senha != confirmacao:
            messagebox.showerror("Validação", "As senhas informadas não coincidem.")
            return

        # Verifica se a senha é forte o suficiente (tamanho, complexidade, etc.)
        senha_valida, mensagem_forca = validar_forca_senha_mestra(senha)
        # Se a senha não for forte o suficiente, mostra o motivo e não prossegue
        if not senha_valida:
            messagebox.showerror("Senha mestra fraca", mensagem_forca)
            return

        # Se o usuário marcou "usar keyfile" mas não selecionou/gerou nenhum, avisa
        if usar_keyfile and not caminho_keyfile:
            messagebox.showwarning(
                "Keyfile obrigatório",
                "Ative um keyfile apenas se você realmente selecionou ou gerou esse arquivo.",
            )
            return

        # Tenta criar o cofre com a senha e o keyfile (se selecionado)
        try:
            self.app.servico.criar_cofre(
                senha,
                caminho_keyfile=caminho_keyfile if usar_keyfile else None,
            )
        # Se der erro na criação, mostra mensagem de erro
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível criar o cofre: {exc}")
            return

        # Limpa todos os campos do formulário por segurança (não deixa senhas na memória)
        self.var_senha.set("")
        self.var_confirmacao.set("")
        self.var_keyfile.set("")
        self.var_usar_keyfile.set(False)
        self._atualizar_estado_keyfile()
        # Mostra mensagem de sucesso e redireciona para a tela de login
        messagebox.showinfo("Sucesso", "Cofre criado com sucesso. Faça login para continuar.")
        self.app.mostrar_tela_login()


# Classe da tela de login — onde o usuário digita a senha mestra para acessar o cofre
# Herda de ttk.Frame (é um painel visual)
class TelaLogin(ttk.Frame):
    """Tela de autenticação com mitigação de força bruta e suporte a keyfile."""

    # Construtor — configura a tela de login com todos os seus campos e controles
    def __init__(self, parent: ttk.Frame, app: AplicacaoCofre) -> None:
        """Configura interface de login e controle de temporizadores."""
        # Cria o frame com estilo visual do app
        super().__init__(parent, style="App.TFrame")
        # Guarda referência do aplicativo
        self.app = app
        # Variável para a senha digitada
        self.var_senha = tk.StringVar()
        # Variável para o caminho do keyfile
        self.var_keyfile = tk.StringVar()
        # Identificador do timer de contagem regressiva (None = sem timer ativo)
        self._timer_id: str | None = None
        # Quantidade de segundos restantes no bloqueio/atraso
        self._segundos_restantes = 0
        # Texto que aparece antes da contagem (ex: "Bloqueio ativo." ou "Atraso progressivo.")
        self._prefixo_contagem = ""
        # Busca informações de segurança do cofre (tipo de criptografia, se usa keyfile, etc.)
        self._resumo = self.app.servico.obter_resumo_seguranca()
        # Monta toda a interface visual
        self._montar_interface()
        # Verifica se já existe um bloqueio ativo (de tentativas erradas anteriores)
        self._inicializar_bloqueio_existente()

    # Método que monta todos os elementos visuais da tela de login
    def _montar_interface(self) -> None:
        """Renderiza campos de autenticação e informações de proteção do cofre."""
        # Cria o cabeçalho com badge, título e subtítulo
        cabecalho = ttk.Frame(self, style="App.TFrame")
        # fill="x" preenche a largura, pady=(10, 16) = espaço acima e abaixo
        cabecalho.pack(fill="x", pady=(10, 16))

        # Badge "COFRE LOCAL" alinhado à esquerda
        ttk.Label(cabecalho, text="COFRE LOCAL", style="Badge.TLabel").pack(anchor="w", pady=(0, 10))
        # Título "Login no Cofre"
        ttk.Label(cabecalho, text="Login no Cofre", style="Titulo.TLabel").pack(anchor="w")
        # Subtítulo com instrução para o usuário
        ttk.Label(
            cabecalho,
            text="Digite a senha mestra para abrir o cofre local.",
            style="Subtitulo.TLabel",
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        # Cartão branco que mostra as informações de proteção do cofre
        cartao = ttk.Frame(self, style="Card.TFrame", padding=18)
        cartao.pack(fill="x", pady=(0, 16))

        # Título dentro do cartão: "Proteção detectada"
        # columnspan=2 faz o texto ocupar 2 colunas da grade
        ttk.Label(cartao, text="Proteção detectada", style="TituloCard.TLabel").grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 8),
        )
        # Mostra detalhes técnicos da proteção do cofre (tipo de criptografia, cifra, etc.)
        # Usa f-string para inserir os valores das variáveis dentro do texto
        ttk.Label(
            cartao,
            text=(
                f"KDF: {self._resumo['algoritmo_kdf']}  |  "
                f"Cifra: {self._resumo['algoritmo_cifra']}  |  "
                f"Formato: {self._resumo['status_formato']}  |  "
                f"Keyfile: {'Sim' if self._resumo['usa_keyfile'] else 'Não'}"
            ),
            style="TextoCard.TLabel",
            wraplength=860,
            justify="left",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))

        # Cria um frame separado para o formulário de login
        formulario = ttk.Frame(self, style="App.TFrame")
        # anchor="w" alinha o formulário à esquerda da tela
        formulario.pack(anchor="w", pady=(0, 10))

        # Rótulo "Senha mestra" ao lado esquerdo do campo
        ttk.Label(formulario, text="Senha mestra", style="Campo.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 14),
            pady=(0, 10),
        )
        # Campo de texto para digitar a senha (com asteriscos para esconder)
        # Guarda em self._entrada_senha para poder desabilitar durante o bloqueio
        self._entrada_senha = ttk.Entry(
            formulario,
            textvariable=self.var_senha,
            show="*",
            width=40,
            font=("Segoe UI", 11),
        )
        self._entrada_senha.grid(row=0, column=1, sticky="w", pady=(0, 10))
        # Coloca o foco (cursor) automaticamente neste campo ao abrir a tela
        self._entrada_senha.focus_set()

        # Lista de controles que serão desabilitados durante o bloqueio por tentativas erradas
        self._controles_temporizados: list[tk.Widget] = [self._entrada_senha]

        # Se o cofre usa keyfile, mostra campos adicionais para selecionar o arquivo
        if self._resumo["usa_keyfile"]:
            # Rótulo "Keyfile"
            ttk.Label(formulario, text="Keyfile", style="Campo.TLabel").grid(
                row=1,
                column=0,
                sticky="w",
                padx=(0, 14),
                pady=(0, 10),
            )
            # Campo de texto para o caminho do keyfile
            self._entrada_keyfile = ttk.Entry(
                formulario,
                textvariable=self.var_keyfile,
                width=46,
                font=("Segoe UI", 10),
            )
            # sticky="we" estica o campo horizontalmente
            self._entrada_keyfile.grid(row=1, column=1, sticky="we", pady=(0, 10))
            # Botão para abrir a janela de seleção de arquivo
            self._botao_keyfile = ttk.Button(
                formulario,
                text="Selecionar keyfile",
                style="Secundario.TButton",
                command=self._selecionar_keyfile,
            )
            self._botao_keyfile.grid(row=1, column=2, sticky="w", padx=(8, 0), pady=(0, 10))
            # Adiciona os novos controles à lista dos que serão bloqueados em tentativas erradas
            self._controles_temporizados.extend([self._entrada_keyfile, self._botao_keyfile])

        # Cria frame para os botões de ação
        botoes = ttk.Frame(self, style="App.TFrame")
        botoes.pack(fill="x", pady=(6, 10))
        # Configura 2 colunas iguais para os botões
        configurar_colunas_expansiveis(botoes, 2, "acoes_login")

        # Botão principal "Entrar no Cofre" que tenta fazer o login
        self._botao_login = ttk.Button(
            botoes,
            text="Entrar no Cofre",
            style="Primario.TButton",
            command=self._tentar_login,
        )
        # sticky="ew" = ocupa toda a largura da célula
        self._botao_login.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        # Adiciona o botão à lista dos que serão bloqueados durante atraso
        self._controles_temporizados.append(self._botao_login)

        # Botão "Fechar" que encerra o aplicativo
        ttk.Button(
            botoes,
            text="Fechar",
            style="Secundario.TButton",
            command=self.app._encerrar_aplicacao,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # Label de status que mostra mensagens como "Bloqueio ativo" ou "Nova tentativa liberada"
        self._label_status = ttk.Label(self, text="", style="Texto.TLabel")
        self._label_status.pack(anchor="w", pady=(6, 0))

        # Configura o atalho de teclado: pressionar Enter chama a função de login
        # bind() conecta um evento (tecla pressionada) a uma função
        self.bind("<Return>", self._executar_atalho_enter)

    # Método que abre janela para selecionar o keyfile do disco
    def _selecionar_keyfile(self) -> None:
        """Seleciona o keyfile necessário para o desbloqueio do cofre."""
        caminho = filedialog.askopenfilename(
            parent=self,
            title="Selecionar keyfile",
        )
        if caminho:
            self.var_keyfile.set(caminho)

    # Método que verifica se já existe um bloqueio ativo quando a tela abre
    def _inicializar_bloqueio_existente(self) -> None:
        """Ativa contagem visual caso o cofre já esteja bloqueado."""
        # Verifica quanto tempo falta para o bloqueio acabar
        restante = self.app.servico.tempo_restante_bloqueio()
        # Se ainda tem tempo restante, inicia a contagem regressiva visual
        if restante > 0:
            self._iniciar_contagem(restante, "Bloqueio ativo.")

    # Método chamado quando o usuário pressiona Enter — tenta fazer login se possível
    def _executar_atalho_enter(self, _: tk.Event) -> None:
        """Aciona login ao pressionar Enter quando possível."""
        # Se o botão de login está desabilitado (durante bloqueio), não faz nada
        if self._botao_login.instate(["disabled"]):
            return
        # Caso contrário, tenta fazer o login
        self._tentar_login()

    # Método principal de login — valida campos, tenta autenticar e trata erros
    def _tentar_login(self) -> None:
        """Executa autenticação, atraso progressivo e migração automática se necessário."""
        # Pega a senha digitada e o caminho do keyfile
        senha = self.var_senha.get()
        caminho_keyfile = self.var_keyfile.get().strip() or None

        # Verifica se a senha foi preenchida
        if not senha:
            messagebox.showwarning("Campo obrigatório", "Informe a senha mestra.")
            return

        # Se o cofre usa keyfile, verifica se o arquivo foi selecionado
        if self._resumo["usa_keyfile"] and not caminho_keyfile:
            messagebox.showwarning("Keyfile obrigatório", "Selecione o keyfile para continuar.")
            return

        # Tenta fazer login no serviço do cofre
        try:
            resultado = self.app.servico.tentar_login(
                senha,
                caminho_keyfile=caminho_keyfile,
            )
        # Se ocorrer um erro inesperado, mostra mensagem
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha no processo de login: {exc}")
            return
        # finally é executado sempre, mesmo se der erro — limpa a senha da memória
        finally:
            self.var_senha.set("")

        # Se o login foi bem-sucedido
        if resultado.sucesso:
            # Cancela qualquer contagem regressiva ativa
            self._cancelar_contagem()
            # Se houve migração automática, mostra a mensagem sobre a atualização
            if resultado.mensagem != "Login realizado com sucesso.":
                messagebox.showinfo("Proteção atualizada", resultado.mensagem)
            # Vai para a tela principal do cofre
            self.app.mostrar_tela_principal()
            return

        # Se o login falhou, mostra a mensagem de erro no label de status
        self._label_status.configure(text=resultado.mensagem)

        # Se existe um bloqueio por excesso de tentativas, inicia a contagem regressiva
        if resultado.bloqueio_restante > 0:
            self._iniciar_contagem(resultado.bloqueio_restante, "Bloqueio ativo.")
            return

        # Se existe um atraso progressivo (cada erro aumenta o tempo de espera)
        if resultado.atraso_segundos > 0:
            self._iniciar_contagem(resultado.atraso_segundos, "Atraso progressivo.")

    # Método que inicia a contagem regressiva visual e desabilita os controles
    def _iniciar_contagem(self, segundos: int, prefixo: str) -> None:
        """Desabilita login e atualiza contador regressivo na interface."""
        # Cancela qualquer contagem anterior que esteja rodando
        self._cancelar_contagem()
        # Define os segundos restantes (garante que não seja negativo)
        self._segundos_restantes = max(0, int(segundos))
        # Guarda o texto que aparece antes da contagem
        self._prefixo_contagem = prefixo
        # Desabilita todos os controles (campos e botões)
        self._definir_estado_controles("disabled")
        # Inicia a atualização visual da contagem
        self._atualizar_contagem()

    # Método que atualiza o texto da contagem regressiva a cada segundo
    def _atualizar_contagem(self) -> None:
        """Atualiza rótulo de tempo restante até liberar nova tentativa."""
        # Se a contagem chegou a zero, reabilita os controles
        if self._segundos_restantes <= 0:
            self._definir_estado_controles("normal")
            self._label_status.configure(text="Nova tentativa liberada.")
            self._timer_id = None
            # Coloca o foco de volta no campo de senha
            self._entrada_senha.focus_set()
            return

        # Atualiza o texto mostrando quantos segundos faltam
        self._label_status.configure(
            text=f"{self._prefixo_contagem} Aguarde {self._segundos_restantes} segundo(s)."
        )
        # Diminui 1 segundo
        self._segundos_restantes -= 1
        # Agenda a próxima atualização para daqui 1000 milissegundos (1 segundo)
        # self.after() é uma função do tkinter que executa algo depois de um tempo
        self._timer_id = self.after(1000, self._atualizar_contagem)

    # Método que habilita ou desabilita todos os controles que devem ser bloqueados
    def _definir_estado_controles(self, estado: str) -> None:
        """Aplica estado uniforme aos controles temporariamente bloqueados."""
        # Percorre todos os controles da lista
        for controle in self._controles_temporizados:
            # Botões ttk usam .state() com uma lista
            if isinstance(controle, ttk.Button):
                controle.state(["!disabled"] if estado == "normal" else ["disabled"])
            # Outros controles (Entry, etc.) usam .configure(state=...)
            else:
                controle.configure(state=estado)

    # Método que cancela o timer de contagem regressiva
    def _cancelar_contagem(self) -> None:
        """Cancela temporizador ativo quando necessário."""
        # Se existe um timer ativo, cancela ele
        if self._timer_id is not None:
            # after_cancel() cancela um agendamento feito com after()
            self.after_cancel(self._timer_id)
            self._timer_id = None
        # Zera os segundos restantes
        self._segundos_restantes = 0

    # Método destroy é chamado quando a tela é removida — limpa o timer antes
    def destroy(self) -> None:
        """Garante limpeza de timer ao destruir frame de login."""
        # Cancela qualquer timer ativo para evitar erros
        self._cancelar_contagem()
        # Chama o destroy da classe pai para realmente destruir o frame
        super().destroy()


# Classe da tela principal do cofre — onde o usuário vê e gerencia suas credenciais
class TelaPrincipal(ttk.Frame):
    """Área principal para gerenciamento completo das credenciais."""

    # Construtor — monta toda a interface principal com busca, tabela e botões
    def __init__(self, parent: ttk.Frame, app: AplicacaoCofre) -> None:
        """Constrói layout principal com busca, tabela, painel de proteção e ações."""
        # Cria o frame com estilo visual do app
        super().__init__(parent, style="App.TFrame")
        # Guarda referência do aplicativo principal
        self.app = app
        # Variável para o texto de busca/filtro de credenciais
        self.var_busca = tk.StringVar()
        # Token único para identificar a senha copiada na área de transferência
        self._token_clipboard = ""
        # Conteúdo real que foi copiado para a área de transferência
        self._conteudo_clipboard = ""
        # Monta todos os elementos visuais da tela
        self._montar_interface()
        # Atualiza o painel que mostra informações de segurança do cofre
        self._atualizar_painel_seguranca()
        # Carrega e mostra as credenciais salvas na tabela
        self._carregar_credenciais()

    # Método que monta toda a interface visual da tela principal
    def _montar_interface(self) -> None:
        """Renderiza controles da tela principal do cofre."""
        # Cria o cabeçalho com badge, título e subtítulo
        cabecalho = ttk.Frame(self, style="App.TFrame")
        cabecalho.pack(fill="x", pady=(8, 12))

        # Badge "COFRE LOCAL"
        ttk.Label(cabecalho, text="COFRE LOCAL", style="Badge.TLabel").pack(anchor="w", pady=(0, 10))
        # Título principal
        ttk.Label(cabecalho, text="Cofre de Senhas Seguro", style="Titulo.TLabel").pack(anchor="w")
        # Subtítulo
        ttk.Label(
            cabecalho,
            text="Gerencie suas credenciais locais.",
            style="Subtitulo.TLabel",
            wraplength=920,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        # Painel verde escuro que mostra as informações de segurança (tipo de criptografia, etc.)
        self._painel_seguranca = ttk.Frame(self, style="Painel.TFrame", padding=14)
        self._painel_seguranca.pack(fill="x", pady=(0, 12))

        # Label dentro do painel que mostra o texto com as informações de proteção
        self._label_resumo_seguranca = ttk.Label(
            self._painel_seguranca,
            text="",
            style="Destaque.TLabel",
            wraplength=980,
            justify="left",
        )
        self._label_resumo_seguranca.pack(anchor="w")

        # Barra de controles — cartão branco com busca e botões de ação
        barra_controles = ttk.Frame(self, style="Card.TFrame", padding=14)
        barra_controles.pack(fill="x", pady=(2, 8))

        # Linha de busca — contém o rótulo e o campo de pesquisa
        linha_busca = ttk.Frame(barra_controles, style="Card.TFrame")
        linha_busca.pack(fill="x", pady=(0, 10))
        # Faz a coluna 1 (campo de busca) se expandir
        linha_busca.columnconfigure(1, weight=1)

        # Rótulo "Buscar serviço"
        ttk.Label(linha_busca, text="Buscar serviço", style="CampoCard.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
        )
        # Campo de texto para digitar o termo de busca
        entrada_busca = ttk.Entry(
            linha_busca,
            textvariable=self.var_busca,
            width=30,
            font=("Segoe UI", 10),
        )
        # sticky="ew" = estica o campo horizontalmente, padx=(10, 0) = 10 pixels de espaço à esquerda
        entrada_busca.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        # Conecta o evento de soltar uma tecla ao método que recarrega a tabela filtrada
        # Assim a busca acontece em tempo real enquanto o usuário digita
        entrada_busca.bind("<KeyRelease>", lambda _: self._carregar_credenciais())

        # Grade de botões de ação (5 colunas, 2 linhas)
        grade_acoes = ttk.Frame(barra_controles, style="Card.TFrame")
        grade_acoes.pack(fill="x")
        # Configura 5 colunas com tamanhos iguais
        configurar_colunas_expansiveis(grade_acoes, 5, "acoes_principais")

        # Botão "Nova credencial" — abre formulário para adicionar uma nova senha
        ttk.Button(
            grade_acoes,
            text="Nova credencial",
            style="Primario.TButton",
            command=self._nova_credencial,
        # padx=4 = 4 pixels de espaço nas laterais, pady=4 = 4 pixels acima e abaixo
        ).grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        # Botão "Editar" — edita a credencial selecionada na tabela
        ttk.Button(
            grade_acoes,
            text="Editar",
            style="Secundario.TButton",
            command=self._editar_credencial,
        ).grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        # Botão "Excluir" — remove a credencial selecionada
        ttk.Button(
            grade_acoes,
            text="Excluir",
            style="Secundario.TButton",
            command=self._excluir_credencial,
        ).grid(row=0, column=2, sticky="ew", padx=4, pady=4)
        # Botão "Revelar senha" — mostra a senha da credencial selecionada
        ttk.Button(
            grade_acoes,
            text="Revelar senha",
            style="Secundario.TButton",
            command=self._revelar_senha,
        ).grid(row=0, column=3, sticky="ew", padx=4, pady=4)
        # Botão "Copiar senha" — copia a senha para a área de transferência
        ttk.Button(
            grade_acoes,
            text="Copiar senha",
            style="Secundario.TButton",
            command=self._copiar_senha,
        ).grid(row=0, column=4, sticky="ew", padx=4, pady=4)
        # Botão "Fortalecer cofre" — abre janela para trocar senha mestra e keyfile
        ttk.Button(
            grade_acoes,
            text="Fortalecer cofre",
            style="Secundario.TButton",
            command=self._fortalecer_cofre,
        ).grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        # Botão "Exportar" — salva as credenciais em arquivo protegido
        ttk.Button(
            grade_acoes,
            text="Exportar",
            style="Secundario.TButton",
            command=self._exportar_credenciais,
        ).grid(row=1, column=1, sticky="ew", padx=4, pady=4)
        # Botão "Importar" — carrega credenciais de um arquivo de backup
        ttk.Button(
            grade_acoes,
            text="Importar",
            style="Secundario.TButton",
            command=self._importar_credenciais,
        ).grid(row=1, column=2, sticky="ew", padx=4, pady=4)
        # Botão "Atualizar" — recarrega os dados da tabela e painel de segurança
        ttk.Button(
            grade_acoes,
            text="Atualizar",
            style="Secundario.TButton",
            command=self._atualizar_tela,
        ).grid(row=1, column=3, sticky="ew", padx=4, pady=4)
        # Botão "Sair" — encerra a sessão e volta para a tela de login
        ttk.Button(
            grade_acoes,
            text="Sair",
            style="Secundario.TButton",
            command=self._sair,
        ).grid(row=1, column=4, sticky="ew", padx=4, pady=4)

        # Frame que vai conter a tabela de credenciais
        tabela_frame = ttk.Frame(self, style="Card.TFrame", padding=10)
        # fill="both" = preenche largura e altura
        # expand=True = a tabela cresce quando a janela é redimensionada
        tabela_frame.pack(fill="both", expand=True, pady=(6, 8))

        # Define as colunas da tabela (cada uma é um campo da credencial)
        colunas = ("servico", "login", "observacao", "atualizado_em")
        # Cria a tabela (Treeview) com as colunas definidas
        # show="headings" mostra apenas os cabeçalhos das colunas (sem a coluna de árvore)
        # selectmode="browse" permite selecionar apenas uma linha por vez
        self._tabela = ttk.Treeview(
            tabela_frame,
            columns=colunas,
            show="headings",
            selectmode="browse",
        )

        # Define os títulos que aparecem no cabeçalho de cada coluna
        self._tabela.heading("servico", text="Serviço")
        self._tabela.heading("login", text="Usuário/E-mail")
        self._tabela.heading("observacao", text="Observação")
        self._tabela.heading("atualizado_em", text="Atualizado em")

        # Define a largura de cada coluna em pixels e o alinhamento do texto
        # anchor="w" = texto alinhado à esquerda (west), anchor="center" = centralizado
        self._tabela.column("servico", width=220, anchor="w")
        self._tabela.column("login", width=250, anchor="w")
        self._tabela.column("observacao", width=360, anchor="w")
        self._tabela.column("atualizado_em", width=180, anchor="center")

        # Cria uma barra de rolagem vertical para quando há muitas credenciais
        # orient="vertical" = barra vertical, command conecta à tabela
        barra_vertical = ttk.Scrollbar(tabela_frame, orient="vertical", command=self._tabela.yview)
        # Conecta a tabela à barra de rolagem (quando rolar a tabela, a barra se move junto)
        self._tabela.configure(yscrollcommand=barra_vertical.set)

        # Posiciona a tabela à esquerda, preenchendo todo o espaço disponível
        # side="left" = coloca à esquerda, fill="both" = preenche horizontal e vertical
        self._tabela.pack(side="left", fill="both", expand=True)
        # Posiciona a barra de rolagem à direita, preenchendo apenas na vertical
        # side="right" = coloca à direita, fill="y" = preenche só na vertical
        barra_vertical.pack(side="right", fill="y")

        # Conecta o duplo clique na tabela ao método de editar credencial
        # <Double-1> = duplo clique com o botão esquerdo do mouse
        self._tabela.bind("<Double-1>", lambda _: self._editar_credencial())

    # Método que atualiza o texto do painel de segurança com as informações atuais
    def _atualizar_painel_seguranca(self) -> None:
        """Atualiza o resumo visual das defesas ativas do cofre."""
        # Busca as informações atuais de segurança do cofre
        resumo = self.app.servico.obter_resumo_seguranca()
        # Monta o texto com as informações formatadas
        texto = (
            f"Proteção ativa: {resumo['algoritmo_kdf']} + {resumo['algoritmo_cifra']}  |  "
            f"Formato: {resumo['status_formato']}  |  "
            f"Keyfile: {'Ativado' if resumo['usa_keyfile'] else 'Desativado'}"
        )
        # Atualiza o texto do label no painel
        self._label_resumo_seguranca.configure(text=texto)

    # Método que recarrega tudo na tela (painel de segurança + tabela de credenciais)
    def _atualizar_tela(self) -> None:
        """Recarrega credenciais e resumo de segurança da interface principal."""
        self._atualizar_painel_seguranca()
        self._carregar_credenciais()

    # Método que busca as credenciais no cofre e preenche a tabela
    def _carregar_credenciais(self) -> None:
        """Atualiza tabela com credenciais filtradas pelo texto de busca."""
        # Tenta buscar as credenciais do cofre, filtrando pelo texto de busca
        try:
            credenciais = self.app.servico.listar_credenciais(self.var_busca.get())
        # Se a sessão expirou, redireciona para o login
        except PermissionError:
            messagebox.showwarning("Sessão", "Sua sessão foi encerrada. Faça login novamente.")
            self.app.mostrar_tela_login()
            return
        # Se ocorreu outro erro, mostra mensagem
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao carregar credenciais: {exc}")
            return

        # Limpa todas as linhas atuais da tabela antes de inserir os dados novos
        for item in self._tabela.get_children():
            self._tabela.delete(item)

        # Para cada credencial encontrada, insere uma nova linha na tabela
        for credencial in credenciais:
            # insert() adiciona uma linha — "" = raiz da árvore, "end" = no final
            # iid = identificador único da linha (usado para saber qual foi selecionada)
            # values = os valores que aparecem em cada coluna
            self._tabela.insert(
                "",
                "end",
                iid=credencial["id"],
                values=(
                    credencial["servico"],
                    credencial["login"],
                    credencial["observacao"],
                    self._formatar_data(credencial["atualizado_em"]),
                ),
            )

    # Método que retorna o ID da credencial selecionada na tabela (ou None se nenhuma)
    def _id_selecionado(self) -> str | None:
        """Retorna o identificador da linha selecionada na tabela."""
        # Pega a seleção atual da tabela (retorna uma tupla com os IDs selecionados)
        selecao = self._tabela.selection()
        # Se nenhuma linha está selecionada, retorna None
        if not selecao:
            return None
        # Retorna o primeiro (e único, pois o modo é "browse") ID selecionado
        return selecao[0]

    # Método que abre o formulário para cadastrar uma nova credencial
    def _nova_credencial(self) -> None:
        """Abre diálogo para cadastro de nova credencial."""
        # Cria e abre a janela de diálogo no modo "nova" (criação)
        dialogo = DialogoCredencial(self, self.app.servico, modo="nova")
        # Espera a janela do diálogo ser fechada antes de continuar
        self.wait_window(dialogo)
        # Se o usuário salvou a credencial, recarrega a tabela para mostrar a nova
        if dialogo.salvou:
            self._carregar_credenciais()

    # Método que abre o formulário para editar a credencial selecionada
    def _editar_credencial(self) -> None:
        """Abre diálogo de edição para a credencial selecionada."""
        # Pega o ID da credencial selecionada na tabela
        credencial_id = self._id_selecionado()
        # Se nenhuma está selecionada, avisa o usuário
        if not credencial_id:
            messagebox.showinfo("Seleção", "Selecione uma credencial para editar.")
            return

        # Busca os dados completos da credencial (incluindo a senha)
        credencial = self.app.servico.obter_credencial(credencial_id, incluir_senha=True)
        # Se não encontrou (pode ter sido excluída), mostra erro
        if credencial is None:
            messagebox.showerror("Erro", "Credencial não encontrada.")
            self._carregar_credenciais()
            return

        # Abre o diálogo no modo "edicao" com os dados da credencial
        dialogo = DialogoCredencial(
            self,
            self.app.servico,
            modo="edicao",
            credencial=credencial,
        )
        # Espera o diálogo fechar
        self.wait_window(dialogo)
        # Se salvou alterações, recarrega a tabela
        if dialogo.salvou:
            self._carregar_credenciais()

    # Método que exclui a credencial selecionada após confirmação do usuário
    def _excluir_credencial(self) -> None:
        """Exclui credencial selecionada após confirmação explícita."""
        # Pega o ID da credencial selecionada
        credencial_id = self._id_selecionado()
        if not credencial_id:
            messagebox.showinfo("Seleção", "Selecione uma credencial para excluir.")
            return

        # Busca os dados da credencial para mostrar no diálogo de confirmação
        credencial = self.app.servico.obter_credencial(credencial_id)
        if credencial is None:
            messagebox.showerror("Erro", "Credencial não encontrada.")
            self._carregar_credenciais()
            return

        # Pede confirmação ao usuário antes de excluir (mostra nome do serviço e login)
        # askyesno retorna True se o usuário clicou "Sim", False se clicou "Não"
        confirmar = messagebox.askyesno(
            "Confirmação",
            (
                "Deseja realmente excluir esta credencial?\n\n"
                f"Serviço: {credencial['servico']}\n"
                f"Usuário/E-mail: {credencial['login']}"
            ),
            icon="warning",
        )
        # Se o usuário não confirmou, cancela a exclusão
        if not confirmar:
            return

        # Tenta excluir a credencial do cofre
        try:
            self.app.servico.excluir_credencial(credencial_id)
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível excluir a credencial: {exc}")
            return

        # Mostra mensagem de sucesso e recarrega a tabela
        messagebox.showinfo("Sucesso", "Credencial excluída com sucesso.")
        self._carregar_credenciais()

    # Método que mostra a senha da credencial selecionada (pede reautenticação primeiro)
    def _revelar_senha(self) -> None:
        """Revela senha da credencial selecionada após reautenticação."""
        # Pega o ID da credencial selecionada
        credencial_id = self._id_selecionado()
        if not credencial_id:
            messagebox.showinfo("Seleção", "Selecione uma credencial para revelar a senha.")
            return

        # Pede a senha mestra para confirmar que é o dono do cofre
        senha_mestra = self._pedir_senha_mestra_acao()
        # Se o usuário cancelou, não faz nada
        if senha_mestra is None:
            return

        # Tenta revelar a senha usando o serviço do cofre
        try:
            senha = self.app.servico.revelar_senha(credencial_id, senha_mestra)
        # Se a senha mestra está errada
        except PermissionError:
            messagebox.showerror("Autenticação", "Senha mestra incorreta.")
            return
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível revelar a senha: {exc}")
            return

        # Mostra a senha em uma caixa de informação
        messagebox.showinfo("Senha da credencial", f"Senha: {senha}")

    # Método que copia a senha da credencial para a área de transferência (Ctrl+V)
    def _copiar_senha(self) -> None:
        """Copia senha para a área de transferência após reautenticação."""
        credencial_id = self._id_selecionado()
        if not credencial_id:
            messagebox.showinfo("Seleção", "Selecione uma credencial para copiar a senha.")
            return

        # Pede reautenticação com a senha mestra
        senha_mestra = self._pedir_senha_mestra_acao()
        if senha_mestra is None:
            return

        # Tenta obter a senha da credencial
        try:
            senha = self.app.servico.revelar_senha(credencial_id, senha_mestra)
        except PermissionError:
            messagebox.showerror("Autenticação", "Senha mestra incorreta.")
            return
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível copiar a senha: {exc}")
            return

        # Limpa a área de transferência (clipboard) atual
        self.clipboard_clear()
        # Coloca a senha na área de transferência (agora dá para colar com Ctrl+V)
        self.clipboard_append(senha)
        # Força a atualização visual da interface
        self.update_idletasks()

        # Cria um token único (código aleatório) para identificar esta cópia específica
        # Isso serve para saber se a senha ainda está no clipboard quando for limpar
        token = secrets.token_hex(8)
        self._token_clipboard = token
        self._conteudo_clipboard = senha
        # Agenda a limpeza automática do clipboard após 20 segundos (20000 milissegundos)
        # lambda cria uma função anônima que passa o token como parâmetro
        self.after(20000, lambda valor=token: self._limpar_clipboard_se_necessario(valor))

        # Avisa o usuário que a senha foi copiada e será apagada em 20 segundos
        messagebox.showinfo(
            "Senha copiada",
            "Senha copiada para a área de transferência por 20 segundos.",
        )

    # Método que limpa o clipboard automaticamente se a senha ainda estiver lá
    def _limpar_clipboard_se_necessario(self, token: str) -> None:
        """Limpa o clipboard se ainda contiver dado copiado por esta tela."""
        # Se o token não bate, significa que outra cópia foi feita depois — não limpa
        if token != self._token_clipboard:
            return
        # Tenta ler o conteúdo atual da área de transferência
        try:
            conteudo_atual = self.clipboard_get()
        # Se der erro ao ler o clipboard (pode estar vazio), não faz nada
        except tk.TclError:
            return
        # Se o conteúdo mudou (o usuário copiou outra coisa), não limpa
        if conteudo_atual != self._conteudo_clipboard:
            return
        # Se a senha ainda está no clipboard, limpa por segurança
        self.clipboard_clear()
        self.update_idletasks()
        # Reseta as variáveis de controle do clipboard
        self._conteudo_clipboard = ""
        self._token_clipboard = ""

    # Método auxiliar que pede a senha mestra ao usuário para confirmar ações sensíveis
    def _pedir_senha_mestra_acao(self) -> str | None:
        """Solicita senha mestra para confirmação de ação sensível."""
        # Abre um diálogo simples pedindo a senha (show="*" mostra asteriscos)
        senha_mestra = simpledialog.askstring(
            "Confirmação de segurança",
            "Digite a senha mestra para continuar:",
            show="*",
            parent=self,
        )
        # Se o usuário clicou "Cancelar", retorna None
        if senha_mestra is None:
            return None
        # Se o usuário deixou o campo vazio, avisa e retorna None
        if not senha_mestra:
            messagebox.showwarning("Validação", "A senha mestra não pode ficar vazia.")
            return None
        # Retorna a senha digitada
        return senha_mestra

    # Método que abre o diálogo para fortalecer o cofre (trocar senha mestra e keyfile)
    def _fortalecer_cofre(self) -> None:
        """Abre diálogo para alterar senha mestra e keyfile do cofre."""
        dialogo = DialogoSeguranca(self, self.app.servico)
        # Espera o diálogo fechar
        self.wait_window(dialogo)
        # Se o usuário aplicou alterações, atualiza a tela
        if dialogo.salvou:
            self._atualizar_tela()

    # Método que exporta as credenciais para um arquivo criptografado de backup
    def _exportar_credenciais(self) -> None:
        """Exporta as credenciais atuais para um pacote criptografado por senha própria."""
        # Abre janela para o usuário escolher onde salvar o arquivo de backup
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar credenciais",
            defaultextension=".json",
            initialfile="backup_cofre_seguro.json",
        )
        # Se cancelou, não faz nada
        if not caminho:
            return

        # Pede uma senha para proteger o arquivo exportado
        senha_exportacao = simpledialog.askstring(
            "Senha de exportação",
            (
                "Defina uma senha forte para proteger o arquivo exportado.\n"
                "Ela será necessária para importar esse backup depois."
            ),
            show="*",
            parent=self,
        )
        # Se cancelou, não faz nada
        if senha_exportacao is None:
            return

        # Pede para digitar a senha de novo (confirmação)
        confirmacao = simpledialog.askstring(
            "Confirmar senha de exportação",
            "Digite novamente a senha de exportação:",
            show="*",
            parent=self,
        )
        if confirmacao is None:
            return

        # Verifica se a senha e a confirmação são iguais
        if senha_exportacao != confirmacao:
            messagebox.showerror(
                "Validação",
                "A senha de exportação e a confirmação não coincidem.",
                parent=self,
            )
            return

        # Tenta exportar as credenciais para o arquivo escolhido
        try:
            resultado = self.app.servico.exportar_credenciais(caminho, senha_exportacao)
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível exportar as credenciais: {exc}")
            return

        # Mostra mensagem de sucesso com a quantidade de credenciais exportadas
        messagebox.showinfo(
            "Exportação concluída",
            (
                f"{resultado['quantidade']} credencial(is) exportada(s) com sucesso.\n\n"
                f"Arquivo: {resultado['arquivo']}"
            ),
        )

    # Método que importa credenciais de um arquivo de backup para o cofre
    def _importar_credenciais(self) -> None:
        """Importa credenciais de um pacote criptografado para o cofre atual."""
        # Abre janela para escolher o arquivo de backup
        # filetypes define os filtros de tipo de arquivo mostrados na janela
        caminho = filedialog.askopenfilename(
            parent=self,
            title="Importar credenciais",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        # Pede a senha que foi definida na exportação
        senha_importacao = simpledialog.askstring(
            "Senha de importação",
            "Digite a senha definida no arquivo exportado:",
            show="*",
            parent=self,
        )
        if senha_importacao is None:
            return

        # Pergunta se quer sobrescrever credenciais duplicadas (mesmo serviço e login)
        sobrescrever = messagebox.askyesno(
            "Duplicadas",
            (
                "Se uma credencial com o mesmo Serviço e Usuário/E-mail já existir,\n"
                "deseja sobrescrever os dados atuais com os dados importados?"
            ),
            parent=self,
        )

        # Tenta importar as credenciais do arquivo
        try:
            resultado = self.app.servico.importar_credenciais(
                caminho,
                senha_importacao,
                sobrescrever_duplicadas=sobrescrever,
            )
        # Se a senha está errada
        except PermissionError:
            messagebox.showerror("Autenticação", "Senha de importação incorreta.")
            return
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível importar as credenciais: {exc}")
            return

        # Atualiza a tela e mostra o resumo da importação
        self._atualizar_tela()
        messagebox.showinfo(
            "Importação concluída",
            (
                f"Inseridas: {resultado['inseridas']}\n"
                f"Atualizadas: {resultado['atualizadas']}\n"
                f"Ignoradas: {resultado['ignoradas']}"
            ),
        )

    # Método que encerra a sessão e volta para a tela de login
    def _sair(self) -> None:
        """Encerra sessão atual e retorna para tela de login."""
        # Limpa os dados de sessão (remove senha mestra da memória)
        self.app.servico.encerrar_sessao()
        # Volta para a tela de login
        self.app.mostrar_tela_login()

    # @staticmethod indica que este método não precisa de "self" — funciona sozinho, sem depender do objeto
    # É uma função utilitária que pode ser chamada sem criar uma instância da classe
    @staticmethod
    def _formatar_data(valor_iso: str) -> str:
        """Formata data ISO para exibição na tabela."""
        # Tenta converter a data do formato ISO (2024-01-15T14:30:00) para formato brasileiro (15/01/2024 14:30)
        try:
            return datetime.fromisoformat(valor_iso).strftime("%d/%m/%Y %H:%M")
        # Se der erro na conversão, retorna o valor original sem formatar
        except Exception:
            return valor_iso


# Classe base para janelas modais (janelas que bloqueiam a interação com a janela principal)
# Herda de tk.Toplevel — que é uma janela adicional (popup) do tkinter
class JanelaModalBase(tk.Toplevel):
    """Base para diálogos modais com ativação segura do grab no Tkinter."""

    # Construtor — cria a janela mas deixa ela escondida inicialmente
    def __init__(self, parent: tk.Widget) -> None:
        """Cria janela modal inicialmente oculta até ficar visível."""
        # Cria a janela Toplevel
        super().__init__(parent)
        # Esconde a janela temporariamente (ela vai aparecer depois)
        self.withdraw()
        # Faz essa janela estar vinculada à janela pai (aparece na frente dela)
        self.transient(parent)

    # Método que mostra a janela e ativa o comportamento modal (bloqueia a janela de trás)
    def ativar_modalidade(self) -> None:
        """Mostra a janela e aplica a captura modal quando estiver visível."""
        # Torna a janela visível
        self.deiconify()
        # Agenda a aplicação do grab (bloqueio modal) para o próximo ciclo da interface
        self.after(0, self._aplicar_modalidade_segura)

    # Método que aplica o "grab" (bloqueio modal) de forma segura
    # O grab impede que o usuário clique em qualquer outra janela até fechar esta
    def _aplicar_modalidade_segura(self) -> None:
        """Aplica comportamento modal apenas quando a janela está visível."""
        # Se a janela já foi fechada, não faz nada
        if not self.winfo_exists():
            return
        # Se a janela ainda não está totalmente visível, tenta novamente em 20ms
        if not self.winfo_viewable():
            self.after(20, self._aplicar_modalidade_segura)
            return
        # Tenta aplicar o grab (bloqueio modal) e forçar o foco nesta janela
        try:
            # grab_set() bloqueia interação com outras janelas
            self.grab_set()
            # focus_force() força o foco do teclado nesta janela
            self.focus_force()
        # Se der erro (raro, pode acontecer em situações de timing), tenta de novo
        except tk.TclError:
            self.after(20, self._aplicar_modalidade_segura)


# Classe do diálogo (janela popup) para criar ou editar uma credencial
# Herda de JanelaModalBase — ou seja, é uma janela modal que bloqueia a principal
class DialogoCredencial(JanelaModalBase):
    """Diálogo de cadastro e edição de credenciais do cofre."""

    # Construtor — recebe o modo ("nova" ou "edicao") e opcionalmente os dados da credencial
    def __init__(
        self,
        parent: tk.Widget,
        servico: ServicoCofre,
        modo: str,
        credencial: dict[str, str] | None = None,
    ) -> None:
        """Cria janela modal para edição de dados de uma credencial."""
        # Chama o construtor da JanelaModalBase que cria a janela escondida
        super().__init__(parent)
        # Guarda o serviço do cofre para salvar os dados depois
        self.servico = servico
        # Guarda o modo: "nova" para criação, "edicao" para editar existente
        self.modo = modo
        # Guarda os dados da credencial (vazio se for nova)
        self.credencial = credencial or {}
        # Flag que indica se o usuário salvou com sucesso (usada pela tela que abriu o diálogo)
        self.salvou = False

        # Cria variáveis conectadas aos campos do formulário
        # .get("servico", "") tenta pegar o valor "servico" do dicionário; se não existir, usa "" (vazio)
        self.var_servico = tk.StringVar(value=self.credencial.get("servico", ""))
        self.var_login = tk.StringVar(value=self.credencial.get("login", ""))
        self.var_senha = tk.StringVar(value=self.credencial.get("senha", ""))
        # Variável para o comprimento da senha gerada (padrão: 16 caracteres)
        self.var_tamanho = tk.IntVar(value=16)
        # Flag que indica se a senha está visível ou oculta (asteriscos)
        self._senha_visivel = False

        # Define o título da janela de acordo com o modo
        self.title("Nova credencial" if modo == "nova" else "Editar credencial")
        # Define o tamanho da janela
        self.geometry("580x450")
        self.minsize(560, 430)
        # Define a cor de fundo
        self.configure(background="#f6f1e8")
        # Monta todos os elementos visuais do formulário
        self._montar_interface()
        # Ativa o comportamento modal (bloqueia a janela de trás)
        self.ativar_modalidade()

    # Método que monta o formulário com todos os campos e botões
    def _montar_interface(self) -> None:
        """Renderiza formulário de credencial e botões de ação."""
        # Cria o frame principal do formulário com estilo de cartão
        frame = ttk.Frame(self, padding=18, style="Card.TFrame")
        # Preenche toda a janela
        frame.pack(fill="both", expand=True)

        # Título "Credencial" no topo do formulário
        # columnspan=3 faz o título ocupar 3 colunas da grade
        ttk.Label(frame, text="Credencial", style="TituloDialogo.TLabel").grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 14),
        )

        # Rótulo "Serviço" — nome do site ou aplicativo (ex: "Gmail", "Netflix")
        ttk.Label(frame, text="Serviço", style="CampoCard.TLabel").grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 8),
            padx=(0, 12),
        )
        # Campo de texto para digitar o nome do serviço
        # sticky="we" estica o campo de leste a oeste (preenche a largura)
        ttk.Entry(frame, textvariable=self.var_servico, width=42, font=("Segoe UI", 10)).grid(
            row=1,
            column=1,
            columnspan=2,
            sticky="we",
            pady=(0, 8),
        )

        # Rótulo "Usuário/E-mail" — o login que você usa naquele serviço
        ttk.Label(frame, text="Usuário/E-mail", style="CampoCard.TLabel").grid(
            row=2,
            column=0,
            sticky="w",
            pady=(0, 8),
            padx=(0, 12),
        )
        # Campo de texto para o login/e-mail
        ttk.Entry(frame, textvariable=self.var_login, width=42, font=("Segoe UI", 10)).grid(
            row=2,
            column=1,
            columnspan=2,
            sticky="we",
            pady=(0, 8),
        )

        # Rótulo "Senha"
        ttk.Label(frame, text="Senha", style="CampoCard.TLabel").grid(
            row=3,
            column=0,
            sticky="w",
            pady=(0, 8),
            padx=(0, 12),
        )
        # Campo de texto para a senha — show="*" mostra asteriscos
        # Guarda em self._entrada_senha para poder alterar a visibilidade depois
        self._entrada_senha = ttk.Entry(
            frame,
            textvariable=self.var_senha,
            show="*",
            width=34,
            font=("Segoe UI", 10),
        )
        self._entrada_senha.grid(row=3, column=1, sticky="we", pady=(0, 8))

        # Botão "Mostrar"/"Ocultar" que alterna a visibilidade da senha
        self._botao_visibilidade = ttk.Button(
            frame,
            text="Mostrar",
            style="Secundario.TButton",
            command=self._alternar_visibilidade_senha,
        )
        self._botao_visibilidade.grid(row=3, column=2, sticky="w", pady=(0, 8), padx=(8, 0))

        # Rótulo "Observação"
        # sticky="nw" = gruda no canto superior esquerdo (n=north=norte + w=west=oeste)
        ttk.Label(frame, text="Observação", style="CampoCard.TLabel").grid(
            row=4,
            column=0,
            sticky="nw",
            pady=(0, 8),
            padx=(0, 12),
        )
        # Campo de texto multilinha (Text) para observações/notas
        # height=5 define 5 linhas visíveis, bd=1 = borda de 1 pixel
        self._campo_observacao = tk.Text(
            frame,
            width=40,
            height=5,
            font=("Segoe UI", 10),
            bd=1,
            relief="solid",
        )
        self._campo_observacao.grid(row=4, column=1, columnspan=2, sticky="we", pady=(0, 8))
        # Se a credencial já tem observação (modo edição), preenche o campo
        # "1.0" significa "linha 1, caractere 0" — é o início do campo Text
        if self.credencial.get("observacao"):
            self._campo_observacao.insert("1.0", self.credencial["observacao"])

        # Cria um LabelFrame (caixa com título na borda) para o gerador de senhas
        gerador = ttk.LabelFrame(frame, text="Gerador de senha forte", padding=10)
        # sticky="we" estica horizontalmente
        gerador.grid(row=5, column=0, columnspan=3, sticky="we", pady=(10, 14))

        # Rótulo "Comprimento" dentro do gerador
        ttk.Label(gerador, text="Comprimento", style="TextoCard.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 8),
        )
        # Spinbox para escolher o comprimento da senha (de 8 a 64 caracteres)
        # O usuário pode usar as setinhas ou digitar o número
        ttk.Spinbox(
            gerador,
            from_=8,       # Valor mínimo: 8
            to=64,         # Valor máximo: 64
            textvariable=self.var_tamanho,
            width=8,
            font=("Segoe UI", 10),
        ).grid(row=0, column=1, sticky="w", padx=(0, 12))

        # Botão que gera uma senha forte aleatória com o comprimento escolhido
        ttk.Button(
            gerador,
            text="Gerar senha",
            style="Secundario.TButton",
            command=self._gerar_senha,
        ).grid(row=0, column=2, sticky="w")

        # Frame para os botões de ação do formulário (Salvar e Cancelar)
        acoes = ttk.Frame(frame, style="Card.TFrame")
        # sticky="ew" estica horizontalmente para os botões ocuparem toda a largura
        acoes.grid(row=6, column=0, columnspan=3, sticky="ew")
        # Configura 2 colunas iguais para os botões
        configurar_colunas_expansiveis(acoes, 2, "acoes_credencial")

        # Botão "Salvar" que grava a credencial no cofre
        ttk.Button(
            acoes,
            text="Salvar",
            style="Primario.TButton",
            command=self._salvar,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        # Botão "Cancelar" que fecha o diálogo sem salvar
        # command=self.destroy fecha/destrói a janela
        ttk.Button(
            acoes,
            text="Cancelar",
            style="Secundario.TButton",
            command=self.destroy,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # Faz a coluna 1 se expandir (o campo de texto cresce junto com a janela)
        frame.columnconfigure(1, weight=1)
        # Atalho: pressionar Enter salva o formulário
        self.bind("<Return>", self._atalho_salvar)

    # Método chamado quando o usuário pressiona Enter — atalho para salvar
    def _atalho_salvar(self, _: tk.Event) -> None:
        """Salva dados usando atalho Enter no diálogo."""
        self._salvar()

    # Método que gera uma senha forte aleatória e coloca no campo de senha
    def _gerar_senha(self) -> None:
        """Gera senha forte com secrets e aplica no campo de senha."""
        try:
            # Pega o comprimento desejado do spinbox
            tamanho = int(self.var_tamanho.get())
            # Gera a senha usando o serviço do cofre (que usa o módulo secrets internamente)
            senha = self.servico.gerar_senha(tamanho)
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível gerar a senha: {exc}", parent=self)
            return

        # Coloca a senha gerada no campo de texto
        self.var_senha.set(senha)
        # Torna a senha visível para o usuário poder ver o que foi gerado
        self._definir_visibilidade_senha(True)

    # Método que alterna entre mostrar e ocultar a senha no campo
    def _alternar_visibilidade_senha(self) -> None:
        """Alterna a visualização da senha no formulário da credencial."""
        # Inverte o estado: se estava visível fica oculta, e vice-versa
        self._definir_visibilidade_senha(not self._senha_visivel)

    # Método que define se a senha está visível ou oculta
    def _definir_visibilidade_senha(self, visivel: bool) -> None:
        """Aplica estado de visibilidade da senha no campo do formulário."""
        # Atualiza a flag
        self._senha_visivel = visivel
        # Se visível, show="" mostra os caracteres reais; se oculta, show="*" mostra asteriscos
        self._entrada_senha.configure(show="" if visivel else "*")
        # Atualiza o texto do botão
        self._botao_visibilidade.configure(text="Ocultar" if visivel else "Mostrar")

    # Método que valida o formulário e salva a credencial no cofre
    def _salvar(self) -> None:
        """Valida formulário e persiste nova credencial ou edição."""
        # Pega os valores dos campos (strip() remove espaços em branco no início e fim)
        servico = self.var_servico.get().strip()
        login = self.var_login.get().strip()
        senha = self.var_senha.get()
        # Pega o texto da observação — "1.0" = início do texto, "end" = até o final
        observacao = self._campo_observacao.get("1.0", "end").strip()

        # Verifica se todos os campos obrigatórios estão preenchidos
        if not servico or not login or not senha:
            messagebox.showwarning(
                "Campos obrigatórios",
                "Preencha Serviço, Usuário/E-mail e Senha.",
                parent=self,
            )
            return

        # Tenta salvar a credencial
        try:
            # Se é uma nova credencial, adiciona
            if self.modo == "nova":
                self.servico.adicionar_credencial(servico, login, senha, observacao)
            # Se é edição, atualiza a credencial existente usando seu ID
            else:
                self.servico.editar_credencial(
                    self.credencial["id"],
                    servico,
                    login,
                    senha,
                    observacao,
                )
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível salvar a credencial: {exc}", parent=self)
            return

        # Marca que salvou com sucesso (a tela que abriu este diálogo vai checar isso)
        self.salvou = True
        # Fecha a janela do diálogo
        self.destroy()


# Classe do diálogo para fortalecer a segurança do cofre (trocar senha e keyfile)
# Herda de JanelaModalBase — é uma janela popup modal
class DialogoSeguranca(JanelaModalBase):
    """Diálogo para fortalecer o cofre com nova senha mestra e keyfile opcional."""

    # Construtor — configura a janela de reconfiguração de segurança
    def __init__(self, parent: tk.Widget, servico: ServicoCofre) -> None:
        """Cria a janela modal de reconfiguração de segurança do cofre."""
        # Cria a janela modal escondida
        super().__init__(parent)
        # Guarda o serviço do cofre
        self.servico = servico
        # Flag que indica se as alterações foram aplicadas com sucesso
        self.salvou = False
        # Busca o resumo de segurança atual (para saber se já usa keyfile, etc.)
        self._resumo = self.servico.obter_resumo_seguranca()

        # Cria variáveis para os campos do formulário
        self.var_senha_atual = tk.StringVar()    # Senha mestra atual (para confirmar identidade)
        self.var_nova_senha = tk.StringVar()     # Nova senha mestra desejada
        self.var_confirmacao = tk.StringVar()    # Confirmação da nova senha
        # Checkbox de keyfile — começa marcado se o cofre já usa keyfile
        self.var_usar_keyfile = tk.BooleanVar(value=bool(self._resumo["usa_keyfile"]))
        self.var_keyfile = tk.StringVar()        # Caminho do novo keyfile

        # Configura a janela
        self.title("Fortalecer cofre")
        self.geometry("700x430")
        self.minsize(640, 410)
        self.configure(background="#f6f1e8")
        # Monta a interface visual
        self._montar_interface()
        # Atualiza os controles de keyfile (habilitados/desabilitados)
        self._atualizar_estado_keyfile()
        # Ativa o comportamento modal
        self.ativar_modalidade()

    # Método que monta o formulário de reconfiguração de segurança
    def _montar_interface(self) -> None:
        """Renderiza o formulário de reconfiguração de segurança."""
        # Frame principal com estilo de cartão
        frame = ttk.Frame(self, padding=18, style="Card.TFrame")
        frame.pack(fill="both", expand=True)

        # Badge "AJUSTE DE SEGURANÇA" no topo
        ttk.Label(frame, text="AJUSTE DE SEGURANÇA", style="Badge.TLabel").grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(0, 10),
        )
        # Título grande "Fortalecer cofre"
        ttk.Label(frame, text="Fortalecer cofre", style="TituloDialogo.TLabel").grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(0, 10),
        )
        # Subtítulo explicativo
        ttk.Label(
            frame,
            text="Troque a senha mestra e ajuste o uso de keyfile quando precisar.",
            style="SubtituloCard.TLabel",
            wraplength=620,
            justify="left",
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(0, 16))

        # Campo "Senha mestra atual" — necessário para confirmar a identidade do usuário
        ttk.Label(frame, text="Senha mestra atual", style="CampoCard.TLabel").grid(
            row=3,
            column=0,
            sticky="w",
            pady=(0, 10),
            padx=(0, 12),
        )
        ttk.Entry(
            frame,
            textvariable=self.var_senha_atual,
            show="*",
            width=34,
            font=("Segoe UI", 10),
        # columnspan=3 faz o campo ocupar 3 colunas, sticky="we" estica horizontalmente
        ).grid(row=3, column=1, columnspan=3, sticky="we", pady=(0, 10))

        # Campo "Nova senha mestra" — a senha que vai substituir a atual
        ttk.Label(frame, text="Nova senha mestra", style="CampoCard.TLabel").grid(
            row=4,
            column=0,
            sticky="w",
            pady=(0, 10),
            padx=(0, 12),
        )
        ttk.Entry(
            frame,
            textvariable=self.var_nova_senha,
            show="*",
            width=34,
            font=("Segoe UI", 10),
        ).grid(row=4, column=1, columnspan=3, sticky="we", pady=(0, 10))

        # Campo "Confirmar nova senha" — digitar de novo para evitar erros de digitação
        ttk.Label(frame, text="Confirmar nova senha", style="CampoCard.TLabel").grid(
            row=5,
            column=0,
            sticky="w",
            pady=(0, 10),
            padx=(0, 12),
        )
        ttk.Entry(
            frame,
            textvariable=self.var_confirmacao,
            show="*",
            width=34,
            font=("Segoe UI", 10),
        ).grid(row=5, column=1, columnspan=3, sticky="we", pady=(0, 10))

        # Checkbox para manter ou ativar/desativar a proteção por keyfile
        ttk.Checkbutton(
            frame,
            text="Manter cofre protegido com keyfile",
            variable=self.var_usar_keyfile,
            style="Card.TCheckbutton",
            command=self._atualizar_estado_keyfile,
        ).grid(row=6, column=0, columnspan=4, sticky="w", pady=(8, 10))

        # Campo "Novo keyfile" — caminho do novo arquivo keyfile
        ttk.Label(frame, text="Novo keyfile", style="CampoCard.TLabel").grid(
            row=7,
            column=0,
            sticky="w",
            pady=(0, 10),
            padx=(0, 12),
        )
        # Campo de texto para o caminho do keyfile
        self._entrada_keyfile = ttk.Entry(
            frame,
            textvariable=self.var_keyfile,
            width=42,
            font=("Segoe UI", 10),
        )
        self._entrada_keyfile.grid(row=7, column=1, sticky="we", pady=(0, 10))

        # Botão para selecionar um keyfile existente no disco
        self._botao_keyfile = ttk.Button(
            frame,
            text="Selecionar",
            style="Secundario.TButton",
            command=self._selecionar_keyfile,
        )
        self._botao_keyfile.grid(row=7, column=2, sticky="w", padx=(8, 8), pady=(0, 10))

        # Botão para gerar um novo keyfile
        self._botao_gerar_keyfile = ttk.Button(
            frame,
            text="Gerar keyfile",
            style="Secundario.TButton",
            command=self._gerar_keyfile,
        )
        self._botao_gerar_keyfile.grid(row=7, column=3, sticky="w", pady=(0, 10))

        # Frame para os botões de ação (Aplicar e Cancelar)
        acoes = ttk.Frame(frame, style="Card.TFrame")
        acoes.grid(row=8, column=0, columnspan=4, sticky="ew", pady=(18, 0))
        # Configura 2 colunas iguais para os botões
        configurar_colunas_expansiveis(acoes, 2, "acoes_seguranca")

        # Botão "Aplicar" que salva as alterações de segurança
        ttk.Button(
            acoes,
            text="Aplicar",
            style="Primario.TButton",
            command=self._aplicar,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        # Botão "Cancelar" que fecha a janela sem aplicar nada
        ttk.Button(
            acoes,
            text="Cancelar",
            style="Secundario.TButton",
            command=self.destroy,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        # Faz a coluna 1 se expandir (campos de texto crescem com a janela)
        frame.columnconfigure(1, weight=1)

    # Método que habilita/desabilita os controles de keyfile baseado no checkbox
    def _atualizar_estado_keyfile(self) -> None:
        """Habilita os controles de keyfile quando essa proteção estiver marcada."""
        # Se o checkbox está marcado: "normal" (habilitado); senão: "disabled" (desabilitado)
        estado = "normal" if self.var_usar_keyfile.get() else "disabled"
        self._entrada_keyfile.configure(state=estado)
        self._botao_keyfile.state(["!disabled"] if estado == "normal" else ["disabled"])
        self._botao_gerar_keyfile.state(["!disabled"] if estado == "normal" else ["disabled"])

    # Método que abre janela para selecionar um keyfile existente
    def _selecionar_keyfile(self) -> None:
        """Seleciona um keyfile existente para ativar ou substituir a proteção."""
        caminho = filedialog.askopenfilename(
            parent=self,
            title="Selecionar keyfile",
        )
        if caminho:
            self.var_keyfile.set(caminho)

    # Método que gera um novo keyfile e salva no disco
    def _gerar_keyfile(self) -> None:
        """Gera um novo keyfile em disco para reforçar o cofre atual."""
        # Abre janela "Salvar como" com nome sugerido
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar keyfile",
            defaultextension=".key",
            initialfile="cofre_seguro_novo.key",
        )
        if not caminho:
            return

        # Tenta criar o keyfile
        try:
            self.servico.criar_keyfile(caminho)
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível gerar o keyfile: {exc}", parent=self)
            return

        # Atualiza o campo com o caminho do keyfile criado
        self.var_keyfile.set(caminho)
        messagebox.showinfo(
            "Keyfile criado",
            "Novo keyfile criado com sucesso. Guarde esse arquivo antes de aplicar a alteração.",
            parent=self,
        )

    # Método que valida tudo e aplica as novas configurações de segurança
    def _aplicar(self) -> None:
        """Valida o formulário e aplica a nova configuração de segurança do cofre."""
        # Pega os valores dos campos
        senha_atual = self.var_senha_atual.get()
        nova_senha = self.var_nova_senha.get()
        confirmacao = self.var_confirmacao.get()
        usar_keyfile = self.var_usar_keyfile.get()
        caminho_keyfile = self.var_keyfile.get().strip() or None

        # Verifica se a senha atual foi informada (obrigatória para autorizar a mudança)
        if not senha_atual:
            messagebox.showwarning(
                "Campo obrigatório",
                "Informe a senha mestra atual para autorizar a alteração.",
                parent=self,
            )
            return

        # Se o usuário digitou uma nova senha, valida ela
        if nova_senha or confirmacao:
            # Verifica se a nova senha e a confirmação são iguais
            if nova_senha != confirmacao:
                messagebox.showerror(
                    "Validação",
                    "A nova senha mestra e a confirmação não coincidem.",
                    parent=self,
                )
                return

            # Verifica se a nova senha é forte o suficiente
            senha_valida, mensagem = validar_forca_senha_mestra(nova_senha)
            if not senha_valida:
                messagebox.showerror("Senha mestra fraca", mensagem, parent=self)
                return

        # Se nada foi alterado (sem nova senha e keyfile igual), avisa o usuário
        if not nova_senha and usar_keyfile == bool(self._resumo["usa_keyfile"]) and not caminho_keyfile:
            messagebox.showinfo(
                "Sem alterações",
                "Nenhuma alteração foi informada para aplicar.",
                parent=self,
            )
            return

        # Se quer ativar keyfile mas não selecionou/gerou nenhum arquivo
        if usar_keyfile and not self._resumo["usa_keyfile"] and not caminho_keyfile:
            messagebox.showwarning(
                "Keyfile obrigatório",
                "Selecione ou gere um keyfile para ativar essa proteção.",
                parent=self,
            )
            return

        # Tenta aplicar as alterações de segurança no cofre
        try:
            mensagem = self.servico.reconfigurar_seguranca(
                senha_mestra_atual=senha_atual,
                nova_senha_mestra=nova_senha or None,  # "or None" transforma "" em None
                usar_keyfile=usar_keyfile,
                caminho_keyfile=caminho_keyfile,
            )
        # Se a senha atual está errada
        except PermissionError:
            messagebox.showerror("Autenticação", "Senha mestra atual incorreta.", parent=self)
            return
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível aplicar a alteração: {exc}", parent=self)
            return

        # Marca que as alterações foram aplicadas com sucesso
        self.salvou = True
        # Mostra mensagem de sucesso com o resumo das mudanças
        messagebox.showinfo("Segurança atualizada", mensagem, parent=self)
        # Fecha a janela do diálogo
        self.destroy()


# Função que inicia toda a interface gráfica do aplicativo
# É o "ponto de entrada" da interface — chamada pelo programa principal
def iniciar_interface(servico: ServicoCofre) -> None:
    """Inicia o loop principal da interface Tkinter do cofre."""
    # Cria a janela principal do aplicativo, passando o serviço do cofre
    app = AplicacaoCofre(servico)
    # Inicia o loop principal do tkinter — fica rodando até a janela ser fechada
    # mainloop() é o que mantém a janela aberta e respondendo a cliques e digitação
    app.mainloop()
