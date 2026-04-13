# Permite usar recursos modernos de tipagem em versões mais antigas do Python
from __future__ import annotations

# Importa módulos padrão que serão usados pela interface
import tkinter as tk                            # Biblioteca padrão de janelas
from tkinter import filedialog, messagebox      # Diálogos de arquivo e mensagem
from typing import Any, Callable                # Tipos usados nas anotações

# Importa o ttkbootstrap (dá temas modernos ao Tkinter)
import ttkbootstrap as tb
from ttkbootstrap.constants import (
    BOTH, LEFT, RIGHT, X, Y, W, E, N, S, NSEW, EW, NS, CENTER,
    PRIMARY, SECONDARY, SUCCESS, INFO, WARNING, DANGER, LIGHT, DARK,
    OUTLINE, SOLID,
)

# Importa nossos próprios módulos
from .security import validar_forca_senha_mestra
from .vault import (
    CAMPOS_EDITAVEIS_POR_TIPO,
    CAMPOS_OBRIGATORIOS_POR_TIPO,
    ServicoCofre,
    TIPOS_SUPORTADOS,
)


# ============================================================================
# PALETA DE CORES — inspirada no GitHub Dark, mais moderna e com acentos vivos
# ============================================================================

# Duas paletas completas — cada uma definida em seu próprio dicionário
# Isso permite alternar entre tema escuro e claro garantindo que TUDO muda junto

# ---------------- PALETA ESCURA (inspirada no GitHub Dark) ----------------
PALETA_ESCURA: dict[str, Any] = {
    # Fundos em camadas (do mais escuro ao mais claro)
    "BG_BASE":         "#0d1117",  # Fundo da janela principal (mais profundo)
    "BG_SIDEBAR":      "#010409",  # Fundo da barra lateral (quase preto)
    "BG_SURFACE":      "#161b22",  # Painéis elevados (cards, tiles)
    "BG_SURFACE_HOVER":"#1f2731",  # Card/tile quando o mouse passa por cima
    "BG_ELEVATED":     "#21262d",  # Inputs, botões e entradas de texto
    "BG_STATS":        "#0d1424",  # Faixa do dashboard de stats
    "BG_HEADER":       "#010409",  # Faixa superior fininha (acento decorativo)

    # Bordas
    "BORDER":          "#30363d",  # Borda visível
    "BORDER_MUTED":    "#21262d",  # Borda quase imperceptível
    "BORDER_HOVER":    "#8b949e",  # Borda em hover (destaque sutil)

    # Texto — hierarquia clara
    "TEXT_PRIMARY":    "#e6edf3",  # Texto principal
    "TEXT_SECONDARY":  "#8d96a7",  # Texto secundário
    "TEXT_MUTED":      "#6e7681",  # Texto bem discreto

    # Acentos — para botões/links e destaques globais
    "ACCENT_PRIMARY":  "#8957e5",
    "ACCENT_INFO":     "#58a6ff",
    "ACCENT_SUCCESS":  "#3fb950",
    "ACCENT_WARNING":  "#d29922",
    "ACCENT_DANGER":   "#f85149",

    # Cores por tipo — ajustadas para brilhar em fundo escuro
    "CORES_TIPO": {
        "senha":     "#58a6ff",  # Azul brilhante
        "cartao":    "#f0883e",  # Laranja vibrante
        "documento": "#3fb950",  # Verde limão
        "nota":      "#d2a8ff",  # Lavanda clara
        "wifi":      "#7ce38b",  # Menta
        "licenca":   "#ff7b72",  # Coral
    },

    "TEMA_TTK": "darkly",  # Tema base do ttkbootstrap que casa com essa paleta
}

# ---------------- PALETA CLARA (inspirada no GitHub Light) ----------------
PALETA_CLARA: dict[str, Any] = {
    # Fundos em camadas — no claro, "elevado" fica mais claro, não mais escuro
    "BG_BASE":         "#ffffff",  # Fundo principal (branco)
    "BG_SIDEBAR":      "#f2f4f7",  # Sidebar um pouco mais cinza que o fundo
    "BG_SURFACE":      "#ffffff",  # Cards brancos
    "BG_SURFACE_HOVER":"#eaeef2",  # Hover de card (cinza bem leve)
    "BG_ELEVATED":     "#f6f8fa",  # Inputs e botões secundários
    "BG_STATS":        "#f6f8fa",
    "BG_HEADER":       "#d0d7de",

    # Bordas mais visíveis no modo claro (sem elas, tudo some)
    "BORDER":          "#d0d7de",
    "BORDER_MUTED":    "#eaeef2",
    "BORDER_HOVER":    "#afb8c1",

    # Texto em tons escuros para ficar legível em fundo claro
    "TEXT_PRIMARY":    "#1f2328",
    "TEXT_SECONDARY":  "#656d76",
    "TEXT_MUTED":      "#8c959f",

    # Acentos levemente mais escuros (melhor contraste em fundo claro)
    "ACCENT_PRIMARY":  "#6639ba",
    "ACCENT_INFO":     "#0969da",
    "ACCENT_SUCCESS":  "#1a7f37",
    "ACCENT_WARNING":  "#9a6700",
    "ACCENT_DANGER":   "#cf222e",

    # Cores por tipo recalibradas para legibilidade em fundo branco
    "CORES_TIPO": {
        "senha":     "#0969da",  # Azul GitHub
        "cartao":    "#bc4c00",  # Laranja escuro
        "documento": "#1a7f37",  # Verde escuro
        "nota":      "#8250df",  # Roxo médio
        "wifi":      "#116329",  # Verde floresta
        "licenca":   "#cf222e",  # Vermelho carmim
    },

    "TEMA_TTK": "flatly",  # Tema claro do ttkbootstrap
}

# Variáveis globais de cor — inicializadas com a paleta escura
# A função _aplicar_paleta() no AplicacaoCofre troca esses valores ao alternar tema
BG_BASE          = PALETA_ESCURA["BG_BASE"]
BG_SIDEBAR       = PALETA_ESCURA["BG_SIDEBAR"]
BG_SURFACE       = PALETA_ESCURA["BG_SURFACE"]
BG_SURFACE_HOVER = PALETA_ESCURA["BG_SURFACE_HOVER"]
BG_ELEVATED      = PALETA_ESCURA["BG_ELEVATED"]
BG_STATS         = PALETA_ESCURA["BG_STATS"]
BG_HEADER        = PALETA_ESCURA["BG_HEADER"]
BORDER           = PALETA_ESCURA["BORDER"]
BORDER_MUTED     = PALETA_ESCURA["BORDER_MUTED"]
BORDER_HOVER     = PALETA_ESCURA["BORDER_HOVER"]
TEXT_PRIMARY     = PALETA_ESCURA["TEXT_PRIMARY"]
TEXT_SECONDARY   = PALETA_ESCURA["TEXT_SECONDARY"]
TEXT_MUTED       = PALETA_ESCURA["TEXT_MUTED"]
ACCENT_PRIMARY   = PALETA_ESCURA["ACCENT_PRIMARY"]
ACCENT_INFO      = PALETA_ESCURA["ACCENT_INFO"]
ACCENT_SUCCESS   = PALETA_ESCURA["ACCENT_SUCCESS"]
ACCENT_WARNING   = PALETA_ESCURA["ACCENT_WARNING"]
ACCENT_DANGER    = PALETA_ESCURA["ACCENT_DANGER"]
CORES_TIPO       = dict(PALETA_ESCURA["CORES_TIPO"])


# ============================================================================
# METADADOS DOS TIPOS DE ITEM (rótulos, ícones e cores)
# ============================================================================

METADADOS_TIPO: dict[str, dict[str, str]] = {
    "senha":     {"rotulo": "Senhas",     "icone": "🔒"},
    "cartao":    {"rotulo": "Cartões",    "icone": "💳"},
    "documento": {"rotulo": "Documentos", "icone": "📄"},
    "nota":      {"rotulo": "Notas",      "icone": "📝"},
    "wifi":      {"rotulo": "Wi-Fi",      "icone": "📶"},
    "licenca":   {"rotulo": "Licenças",   "icone": "🔑"},
}

# Tempo de inatividade (ms) antes de bloquear o cofre automaticamente
TEMPO_BLOQUEIO_AUTOMATICO_MS = 5 * 60 * 1000  # 5 minutos

# Fonte padrão do aplicativo (mesma família em toda a interface)
FONTE_PADRAO = "Segoe UI"
FONTE_MONO = "Consolas"


# ============================================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================================

# Calcula uma pontuação simples de força (0 a 100) para uma senha
def calcular_forca_senha(senha: str) -> tuple[int, str, str]:
    """Calcula pontuação (0-100), rótulo e cor hexadecimal da força da senha."""
    # Senha vazia = zero pontos
    if not senha:
        return 0, "Vazia", ACCENT_DANGER

    # Base: até 40 pontos por comprimento (4 pts por caractere, teto 40)
    pontos = min(len(senha) * 4, 40)
    # Cada classe de caracteres presente adiciona 15 pontos
    if any(c.islower() for c in senha):
        pontos += 15
    if any(c.isupper() for c in senha):
        pontos += 15
    if any(c.isdigit() for c in senha):
        pontos += 15
    if any(not c.isalnum() for c in senha):
        pontos += 15

    # Limita o resultado em 100 (máximo)
    pontos = min(pontos, 100)

    # Classifica em 4 níveis de força
    if pontos < 40:
        return pontos, "Fraca", ACCENT_DANGER
    if pontos < 65:
        return pontos, "Média", ACCENT_WARNING
    if pontos < 85:
        return pontos, "Boa", ACCENT_INFO
    return pontos, "Forte", ACCENT_SUCCESS


# Mascara número de cartão mostrando apenas os últimos 4 dígitos
def mascarar_numero_cartao(numero: str) -> str:
    """Oculta o número do cartão exibindo apenas os 4 dígitos finais."""
    limpo = numero.replace(" ", "").replace("-", "")
    if len(limpo) < 4:
        return "•" * len(limpo)
    return f"•••• •••• •••• {limpo[-4:]}"


# Cria uma máscara de pontinhos para campos sensíveis (senha, CVV, etc)
def mascarar_texto_sensivel(texto: str, tamanho_max: int = 12) -> str:
    """Gera máscara visual com pontinhos para campos sensíveis."""
    if not texto:
        return "(vazio)"
    return "•" * min(len(texto), tamanho_max)


# Habilita scroll-drag (botão do meio do mouse) num canvas — estilo visualizador PDF
# Usado em TODAS as áreas roláveis do app (lista principal + diálogos)
def _ligar_scroll_drag(canvas: tk.Canvas) -> None:
    """Liga o scroll por arrasto com o botão do meio do mouse ao canvas informado."""
    # scan_mark / scan_dragto são métodos nativos do tkinter para esse comportamento
    def iniciar(evento: tk.Event) -> None:
        """Marca a posição inicial do arrasto."""
        canvas.scan_mark(evento.x, evento.y)
        # Cursor vira "fleur" (as 4 setinhas) para indicar o modo de arrasto
        canvas.configure(cursor="fleur")

    def arrastar(evento: tk.Event) -> None:
        """Rola o canvas conforme o mouse move (gain=2 deixa mais responsivo)."""
        canvas.scan_dragto(evento.x, evento.y, gain=2)

    def parar(_evento: tk.Event) -> None:
        """Restaura o cursor ao soltar o botão do meio."""
        canvas.configure(cursor="")

    canvas.bind("<ButtonPress-2>", iniciar)
    canvas.bind("<B2-Motion>", arrastar)
    canvas.bind("<ButtonRelease-2>", parar)


# Habilita a rolagem com a rodinha do mouse sobre um canvas específico
# (tkinter não propaga MouseWheel automaticamente para canvases sem foco)
def _ligar_scroll_roda(canvas: tk.Canvas) -> None:
    """Liga a rolagem via roda do mouse ao canvas informado."""
    def rolar(evento: tk.Event) -> None:
        """Scroll com a roda do mouse — delta 120 = 1 unidade no Windows."""
        canvas.yview_scroll(int(-1 * (evento.delta / 120)), "units")

    # bind direto no canvas (não bind_all) para não conflitar com outros scrolls
    canvas.bind("<MouseWheel>", rolar)
    # Quando o mouse entra no canvas, ele passa a receber eventos de roda
    canvas.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", rolar))
    # Quando sai, remove o bind global para não rolar o canvas errado
    canvas.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))


# ============================================================================
# JANELA PRINCIPAL
# ============================================================================


class AplicacaoCofre(tb.Window):
    """Janela principal que alterna entre telas de login, criação e cofre."""

    # Construtor da janela
    def __init__(self, servico: ServicoCofre) -> None:
        """Inicializa janela com tema escuro customizado e paleta própria."""
        # Começa com tema "darkly" como base — vamos customizar depois
        super().__init__(themename="darkly")

        # Guarda o serviço do cofre (lógica de negócio)
        self.servico = servico
        # Identifica se o tema atual é escuro (para alternar depois)
        self._modo_escuro = True
        # Título na barra superior da janela
        self.title("Cofre Seguro")
        # Dimensões iniciais generosas
        self.geometry("1320x820")
        # Tamanho mínimo
        self.minsize(1080, 680)
        # Cor de fundo da janela raiz (por trás de tudo)
        self.configure(bg=BG_BASE)

        # Aplica nossa customização de estilos (cores personalizadas)
        self._aplicar_estilos_customizados()

        # Faixa fininha colorida no topo da janela (acento decorativo)
        # Dá identidade visual imediata e ajuda a diferenciar a janela do SO
        self._top_accent = tk.Frame(self, bg=ACCENT_PRIMARY, height=3)
        self._top_accent.pack(side="top", fill=X)

        # Container central onde as telas serão desenhadas
        self._container = tk.Frame(self, bg=BG_BASE)
        self._container.pack(fill=BOTH, expand=True)

        # Guarda referência para a tela ativa
        self._frame_atual: tk.Widget | None = None

        # Timer para bloqueio automático por inatividade
        self._timer_bloqueio: str | None = None

        # Quando clicar no X da janela, encerra sessão antes de fechar
        self.protocol("WM_DELETE_WINDOW", self._encerrar_aplicacao)

        # Registra os atalhos de teclado globais da aplicação
        self._configurar_atalhos_globais()

        # Mostra a primeira tela (login ou criação)
        self._mostrar_tela_inicial()

    # Registra todos os atalhos de teclado globais da aplicação
    def _configurar_atalhos_globais(self) -> None:
        """Registra atalhos globais de teclado (funcionam em qualquer lugar)."""
        # F1: mostrar tela de ajuda com lista de atalhos
        self.bind_all("<F1>", lambda _e: self._mostrar_ajuda_atalhos())

        # Ctrl+T: alternar tema escuro/claro (funciona sempre)
        self.bind_all("<Control-t>", lambda _e: self._atalho_tema())
        self.bind_all("<Control-T>", lambda _e: self._atalho_tema())

        # Ctrl+N: novo item (só na tela principal)
        self.bind_all("<Control-n>", self._atalho_novo_item)
        self.bind_all("<Control-N>", self._atalho_novo_item)

        # Ctrl+F: focar caixa de busca
        self.bind_all("<Control-f>", self._atalho_focar_busca)
        self.bind_all("<Control-F>", self._atalho_focar_busca)

        # Ctrl+L: bloquear (fazer logout)
        self.bind_all("<Control-l>", self._atalho_logout)
        self.bind_all("<Control-L>", self._atalho_logout)

        # Ctrl+,: abrir configurações
        self.bind_all("<Control-comma>", self._atalho_configuracoes)

        # F5: recarregar lista de itens
        self.bind_all("<F5>", self._atalho_recarregar)

        # Ctrl+0..6: filtros rápidos da sidebar
        self.bind_all("<Control-Key-0>", lambda _e: self._atalho_filtrar("todos"))
        # Mapeia Ctrl+1..6 para cada tipo de item na ordem definida
        for idx, tipo in enumerate(TIPOS_SUPORTADOS, start=1):
            self.bind_all(
                f"<Control-Key-{idx}>",
                lambda _e, t=tipo: self._atalho_filtrar(t),
            )

        # Ctrl+Shift+F: filtrar só favoritos
        self.bind_all("<Control-Shift-F>", lambda _e: self._atalho_filtrar("favoritos"))
        self.bind_all("<Control-Shift-f>", lambda _e: self._atalho_filtrar("favoritos"))

        # Ctrl+G: abrir gerador de senhas (em qualquer tela autenticada)
        self.bind_all("<Control-g>", self._atalho_gerador)
        self.bind_all("<Control-G>", self._atalho_gerador)

    # Helpers dos atalhos (cada um faz uma ação quando o atalho é pressionado)

    # Ctrl+T — alterna tema
    def _atalho_tema(self) -> str:
        """Alterna tema e pára propagação do evento."""
        self.alternar_tema()
        return "break"

    # Ctrl+N — novo item (só funciona na tela principal)
    def _atalho_novo_item(self, _evento: Any = None) -> str:
        """Abre formulário de novo item se estiver na tela principal."""
        if isinstance(self._frame_atual, TelaPrincipal):
            self._frame_atual._criar_novo_item()
        return "break"

    # Ctrl+F — foca no campo de busca
    def _atalho_focar_busca(self, _evento: Any = None) -> str:
        """Coloca o foco na caixa de busca global."""
        if isinstance(self._frame_atual, TelaPrincipal):
            self._frame_atual._focar_busca()
        return "break"

    # Ctrl+L — bloqueia o cofre
    def _atalho_logout(self, _evento: Any = None) -> str:
        """Faz logout se o usuário estiver autenticado."""
        if self.servico.esta_autenticado():
            self.fazer_logout()
        return "break"

    # Ctrl+, — abre configurações
    def _atalho_configuracoes(self, _evento: Any = None) -> str:
        """Abre o diálogo de configurações se estiver na tela principal."""
        if isinstance(self._frame_atual, TelaPrincipal):
            self._frame_atual._abrir_configuracoes()
        return "break"

    # F5 — recarrega a lista de itens
    def _atalho_recarregar(self, _evento: Any = None) -> str:
        """Recarrega os cards na tela principal."""
        if isinstance(self._frame_atual, TelaPrincipal):
            self._frame_atual._recarregar_itens()
        return "break"

    # Ctrl+0-6 — filtra por categoria
    def _atalho_filtrar(self, chave: str) -> str:
        """Troca o filtro ativo pela chave informada (tipo ou 'todos'/'favoritos')."""
        if isinstance(self._frame_atual, TelaPrincipal):
            self._frame_atual._mudar_filtro(chave)
        return "break"

    # Ctrl+G — gerador de senhas standalone
    def _atalho_gerador(self, _evento: Any = None) -> str:
        """Abre o gerador de senhas em modo standalone (ignora o resultado)."""
        if self.servico.esta_autenticado():
            DialogoGeradorSenha(self, callback_resultado=lambda _s: None)
        return "break"

    # F1 — mostra a janela de ajuda com todos os atalhos
    def _mostrar_ajuda_atalhos(self) -> str:
        """Abre o diálogo com a lista de atalhos do aplicativo."""
        DialogoAtalhos(self)
        return "break"

    # Configura estilos ttk personalizados com a nossa paleta
    def _aplicar_estilos_customizados(self) -> None:
        """Sobrepõe estilos do ttk para aplicar a paleta customizada do projeto."""
        estilo = self.style

        # Cor de fundo padrão de Frames (herdada em várias situações)
        estilo.configure("TFrame", background=BG_BASE)
        # Cor de fundo padrão de Labels
        estilo.configure("TLabel", background=BG_BASE, foreground=TEXT_PRIMARY)
        # Entradas de texto com fundo elevado e texto claro
        estilo.configure(
            "TEntry",
            fieldbackground=BG_ELEVATED,
            foreground=TEXT_PRIMARY,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            insertcolor=TEXT_PRIMARY,
        )

        # Estilo "Sidebar" — fundo mais escuro que a janela principal
        estilo.configure("Sidebar.TFrame", background=BG_SIDEBAR)
        estilo.configure(
            "Sidebar.TLabel",
            background=BG_SIDEBAR,
            foreground=TEXT_SECONDARY,
        )
        estilo.configure(
            "SidebarTitle.TLabel",
            background=BG_SIDEBAR,
            foreground=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 14, "bold"),
        )
        estilo.configure(
            "SidebarSection.TLabel",
            background=BG_SIDEBAR,
            foreground=TEXT_MUTED,
            font=(FONTE_PADRAO, 9, "bold"),
        )

        # Estilo "Stats" — fundo azulado escuro para a barra de estatísticas
        estilo.configure("Stats.TFrame", background=BG_STATS)

        # Estilo "Surface" — para painéis elevados (cards)
        estilo.configure("Surface.TFrame", background=BG_SURFACE)

        # Estilos de título e subtítulo da área principal
        estilo.configure(
            "HeroTitle.TLabel",
            background=BG_BASE,
            foreground=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 24, "bold"),
        )
        estilo.configure(
            "Subtitle.TLabel",
            background=BG_BASE,
            foreground=TEXT_SECONDARY,
            font=(FONTE_PADRAO, 10),
        )
        estilo.configure(
            "Muted.TLabel",
            background=BG_BASE,
            foreground=TEXT_MUTED,
            font=(FONTE_PADRAO, 9),
        )

        # Estilos de botão — usamos as variantes do ttkbootstrap com cores padrão
        # mas ajustamos um pouco o padding para parecer mais refinado
        estilo.configure("TButton", padding=(12, 8))

    # Mostra a tela apropriada conforme o estado do cofre
    def _mostrar_tela_inicial(self) -> None:
        """Escolhe entre login (cofre existe) ou criação (primeiro uso)."""
        if self.servico.existe_cofre():
            self.trocar_para_login()
        else:
            self.trocar_para_criacao()

    # Substitui a tela atual por uma nova
    def _trocar_frame(self, novo_frame: tk.Widget) -> None:
        """Destrói a tela atual e exibe a nova ocupando toda a janela."""
        if self._frame_atual is not None:
            self._frame_atual.destroy()
        novo_frame.pack(fill=BOTH, expand=True)
        self._frame_atual = novo_frame

    # Exibe a tela de criação do cofre
    def trocar_para_criacao(self) -> None:
        """Mostra a tela de criação de cofre (primeiro uso)."""
        self._trocar_frame(TelaCriacaoMestra(self._container, self))

    # Exibe a tela de login
    def trocar_para_login(self) -> None:
        """Mostra a tela de login."""
        self._trocar_frame(TelaLogin(self._container, self))

    # Exibe a tela principal do cofre após login
    def trocar_para_principal(self) -> None:
        """Mostra a tela principal (dashboard) após login bem-sucedido."""
        self._trocar_frame(TelaPrincipal(self._container, self))
        # Inicia o timer de bloqueio automático
        self._reiniciar_timer_bloqueio()

    # Alterna entre tema escuro e claro
    def alternar_tema(self) -> None:
        """Alterna entre tema escuro e claro aplicando a paleta e redesenhando."""
        # Inverte o modo atual e aplica a paleta correspondente
        self._modo_escuro = not self._modo_escuro
        paleta = PALETA_ESCURA if self._modo_escuro else PALETA_CLARA
        self._aplicar_paleta(paleta)

        # Re-renderiza a tela atual PRESERVANDO o estado (não volta pro login)
        tipo_tela = type(self._frame_atual).__name__ if self._frame_atual else ""
        if tipo_tela == "TelaPrincipal":
            self.trocar_para_principal()
        elif tipo_tela == "TelaLogin":
            self.trocar_para_login()
        elif tipo_tela == "TelaCriacaoMestra":
            self.trocar_para_criacao()
        else:
            self._mostrar_tela_inicial()

    # Aplica uma paleta completa ao aplicativo
    def _aplicar_paleta(self, paleta: dict[str, Any]) -> None:
        """Copia as cores da paleta para as variáveis globais e reconfigura estilos."""
        # "global" torna explícito que estamos atualizando as variáveis do módulo
        global BG_BASE, BG_SIDEBAR, BG_SURFACE, BG_SURFACE_HOVER
        global BG_ELEVATED, BG_STATS, BG_HEADER
        global BORDER, BORDER_MUTED, BORDER_HOVER
        global TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED
        global ACCENT_PRIMARY, ACCENT_INFO, ACCENT_SUCCESS, ACCENT_WARNING, ACCENT_DANGER
        global CORES_TIPO

        # Troca o tema base do ttkbootstrap para combinar com a paleta
        self.style.theme_use(paleta["TEMA_TTK"])

        # Copia cada cor para a variável global correspondente
        BG_BASE          = paleta["BG_BASE"]
        BG_SIDEBAR       = paleta["BG_SIDEBAR"]
        BG_SURFACE       = paleta["BG_SURFACE"]
        BG_SURFACE_HOVER = paleta["BG_SURFACE_HOVER"]
        BG_ELEVATED      = paleta["BG_ELEVATED"]
        BG_STATS         = paleta["BG_STATS"]
        BG_HEADER        = paleta["BG_HEADER"]
        BORDER           = paleta["BORDER"]
        BORDER_MUTED     = paleta["BORDER_MUTED"]
        BORDER_HOVER     = paleta["BORDER_HOVER"]
        TEXT_PRIMARY     = paleta["TEXT_PRIMARY"]
        TEXT_SECONDARY   = paleta["TEXT_SECONDARY"]
        TEXT_MUTED       = paleta["TEXT_MUTED"]
        ACCENT_PRIMARY   = paleta["ACCENT_PRIMARY"]
        ACCENT_INFO      = paleta["ACCENT_INFO"]
        ACCENT_SUCCESS   = paleta["ACCENT_SUCCESS"]
        ACCENT_WARNING   = paleta["ACCENT_WARNING"]
        ACCENT_DANGER    = paleta["ACCENT_DANGER"]
        # Precisamos de uma cópia do dict de cores por tipo para evitar aliasing
        CORES_TIPO       = dict(paleta["CORES_TIPO"])

        # Reaplica as cores na janela raiz e no container principal
        self.configure(bg=BG_BASE)
        self._container.configure(bg=BG_BASE)
        # A faixa decorativa do topo também precisa atualizar de cor
        if hasattr(self, "_top_accent"):
            self._top_accent.configure(bg=ACCENT_PRIMARY)
        self._aplicar_estilos_customizados()

    # Faz logout: limpa a sessão e volta ao login
    def fazer_logout(self, mensagem: str | None = None) -> None:
        """Encerra a sessão e volta para a tela de login."""
        self._cancelar_timer_bloqueio()
        self.servico.encerrar_sessao()
        self.trocar_para_login()
        if mensagem:
            messagebox.showinfo("Sessão encerrada", mensagem)

    # Reinicia o timer de bloqueio automático
    def _reiniciar_timer_bloqueio(self) -> None:
        """Reinicia o contador de inatividade e agenda novo bloqueio."""
        self._cancelar_timer_bloqueio()
        self._timer_bloqueio = self.after(
            TEMPO_BLOQUEIO_AUTOMATICO_MS,
            self._bloquear_por_inatividade,
        )

    # Cancela o timer de bloqueio
    def _cancelar_timer_bloqueio(self) -> None:
        """Cancela o timer de bloqueio automático, se estiver ativo."""
        if self._timer_bloqueio is not None:
            self.after_cancel(self._timer_bloqueio)
            self._timer_bloqueio = None

    # Bloqueia automaticamente após inatividade
    def _bloquear_por_inatividade(self) -> None:
        """Dispara o bloqueio automático após tempo de inatividade."""
        self._timer_bloqueio = None
        if self.servico.esta_autenticado():
            self.fazer_logout(
                "O cofre foi bloqueado automaticamente após 5 minutos sem atividade."
            )

    # Registra atividade do usuário para resetar o timer
    def registrar_atividade(self) -> None:
        """Reinicia o contador de inatividade ao detectar uso do app."""
        if self.servico.esta_autenticado():
            self._reiniciar_timer_bloqueio()

    # Encerra a aplicação de forma segura
    def _encerrar_aplicacao(self) -> None:
        """Encerra app garantindo limpeza da sessão e do timer."""
        self._cancelar_timer_bloqueio()
        if self.servico.esta_autenticado():
            self.servico.encerrar_sessao()
        self.destroy()


# ============================================================================
# HELPERS PARA CRIAR WIDGETS CUSTOMIZADOS
# ============================================================================


# Cria um Label do tkinter puro com cores e fonte customizadas
# Usado quando queremos controle total sobre o visual (sem depender do ttk)
def criar_label(
    pai: tk.Widget,
    texto: str,
    *,
    fg: str = TEXT_PRIMARY,
    bg: str | None = None,
    fonte: tuple = (FONTE_PADRAO, 10),
    **kwargs: Any,
) -> tk.Label:
    """Helper para criar um Label com cores personalizadas."""
    return tk.Label(
        pai,
        text=texto,
        fg=fg,
        bg=bg if bg is not None else BG_BASE,
        font=fonte,
        **kwargs,
    )


# Cria um Frame do tkinter puro com cor de fundo específica
def criar_frame(pai: tk.Widget, bg: str = BG_BASE, **kwargs: Any) -> tk.Frame:
    """Helper para criar um Frame com fundo personalizado."""
    return tk.Frame(pai, bg=bg, **kwargs)


# ============================================================================
# TELA — Criação do cofre (primeiro uso)
# ============================================================================


class TelaCriacaoMestra(tk.Frame):
    """Tela de criação inicial do cofre com senha mestra."""

    # Construtor
    def __init__(self, master: tk.Widget, app: AplicacaoCofre) -> None:
        """Monta a tela split de criação do cofre."""
        super().__init__(master, bg=BG_BASE)
        self.app = app
        self.var_senha = tk.StringVar()
        self.var_confirma = tk.StringVar()
        self.var_usar_keyfile = tk.BooleanVar(value=False)
        self.var_caminho_keyfile = tk.StringVar()
        self.var_forca = tk.IntVar(value=0)

        self._construir_interface()

    # Constrói a interface
    def _construir_interface(self) -> None:
        """Desenha layout em duas colunas: hero e formulário."""
        # Duas colunas iguais
        self.columnconfigure(0, weight=1, uniform="lados")
        self.columnconfigure(1, weight=1, uniform="lados")
        self.rowconfigure(0, weight=1)

        # ----- Lado esquerdo (hero decorativo) -----
        hero = tk.Frame(self, bg=BG_SIDEBAR)
        hero.grid(row=0, column=0, sticky=NSEW)
        hero.rowconfigure(0, weight=1)
        hero.rowconfigure(2, weight=1)
        hero.columnconfigure(0, weight=1)

        # Círculo com emoji grande (centro visual)
        emoji_container = criar_frame(hero, bg=BG_SIDEBAR)
        emoji_container.grid(row=0, column=0, sticky=S)

        criar_label(
            emoji_container,
            "🔐",
            fg=ACCENT_PRIMARY,
            bg=BG_SIDEBAR,
            fonte=("Segoe UI Emoji", 100),
        ).pack()

        # Bloco de textos centrais
        textos = criar_frame(hero, bg=BG_SIDEBAR)
        textos.grid(row=1, column=0, pady=(30, 20))

        criar_label(
            textos,
            "Cofre Seguro",
            fg=TEXT_PRIMARY,
            bg=BG_SIDEBAR,
            fonte=(FONTE_PADRAO, 34, "bold"),
        ).pack()

        criar_label(
            textos,
            "Suas senhas, cartões e documentos",
            fg=TEXT_SECONDARY,
            bg=BG_SIDEBAR,
            fonte=(FONTE_PADRAO, 13),
        ).pack(pady=(10, 0))
        criar_label(
            textos,
            "protegidos com criptografia forte.",
            fg=TEXT_SECONDARY,
            bg=BG_SIDEBAR,
            fonte=(FONTE_PADRAO, 13),
        ).pack()

        # Lista de recursos — cada um num "pill" visual
        destaques_frame = criar_frame(hero, bg=BG_SIDEBAR)
        destaques_frame.grid(row=2, column=0, sticky=N, pady=(30, 0))

        destaques = [
            ("🔒", "Criptografia AES-256-GCM"),
            ("🔑", "Derivação Argon2id"),
            ("🛡", "Bloqueio automático"),
            ("✨", "6 tipos de itens"),
        ]
        for icone, texto in destaques:
            linha = criar_frame(destaques_frame, bg=BG_SIDEBAR)
            linha.pack(anchor=W, pady=5)
            criar_label(
                linha, icone, bg=BG_SIDEBAR, fg=ACCENT_INFO,
                fonte=("Segoe UI Emoji", 13),
            ).pack(side=LEFT, padx=(0, 10))
            criar_label(
                linha, texto, bg=BG_SIDEBAR, fg=TEXT_SECONDARY,
                fonte=(FONTE_PADRAO, 11),
            ).pack(side=LEFT)

        # ----- Lado direito (formulário) -----
        form_wrapper = tk.Frame(self, bg=BG_BASE)
        form_wrapper.grid(row=0, column=1, sticky=NSEW)
        form_wrapper.rowconfigure(0, weight=1)
        form_wrapper.rowconfigure(2, weight=1)
        form_wrapper.columnconfigure(0, weight=1)

        form = tk.Frame(form_wrapper, bg=BG_BASE, padx=60)
        form.grid(row=1, column=0, sticky=EW)
        form.columnconfigure(0, weight=1)

        # Título do formulário
        criar_label(
            form, "Criar seu cofre",
            fg=TEXT_PRIMARY, fonte=(FONTE_PADRAO, 26, "bold"),
        ).grid(row=0, column=0, sticky=W)

        criar_label(
            form, "Escolha uma senha mestra forte. Ela não pode ser recuperada.",
            fg=TEXT_SECONDARY, fonte=(FONTE_PADRAO, 11),
        ).grid(row=1, column=0, sticky=W, pady=(4, 26))

        # Campo de senha mestra
        criar_label(
            form, "SENHA MESTRA",
            fg=TEXT_MUTED, fonte=(FONTE_PADRAO, 9, "bold"),
        ).grid(row=2, column=0, sticky=W, pady=(0, 6))

        entry_senha = tb.Entry(
            form,
            textvariable=self.var_senha,
            show="•",
            font=(FONTE_PADRAO, 11),
        )
        entry_senha.grid(row=3, column=0, sticky=EW, ipady=8)
        self.var_senha.trace_add("write", lambda *_: self._atualizar_forca())

        # Barra de força da senha (canvas customizado pra cor precisa)
        barra_frame = tk.Frame(form, bg=BG_BASE)
        barra_frame.grid(row=4, column=0, sticky=EW, pady=(10, 0))
        barra_frame.columnconfigure(0, weight=1)

        # Canvas como barra de força customizada
        self.canvas_forca = tk.Canvas(
            barra_frame, height=6, bg=BG_ELEVATED,
            highlightthickness=0, borderwidth=0,
        )
        self.canvas_forca.grid(row=0, column=0, sticky=EW)
        # Cria o preenchimento (vai crescer conforme força)
        self._retangulo_forca = self.canvas_forca.create_rectangle(
            0, 0, 0, 6, fill=ACCENT_DANGER, outline="",
        )

        self.lbl_forca = criar_label(
            barra_frame, "Força: —",
            fg=TEXT_MUTED, fonte=(FONTE_PADRAO, 10),
        )
        self.lbl_forca.grid(row=0, column=1, padx=(12, 0))

        # Confirmar senha
        criar_label(
            form, "CONFIRMAR SENHA",
            fg=TEXT_MUTED, fonte=(FONTE_PADRAO, 9, "bold"),
        ).grid(row=5, column=0, sticky=W, pady=(20, 6))

        tb.Entry(
            form,
            textvariable=self.var_confirma,
            show="•",
            font=(FONTE_PADRAO, 11),
        ).grid(row=6, column=0, sticky=EW, ipady=8)

        # Toggle keyfile
        tb.Checkbutton(
            form,
            text="   Usar arquivo-chave (segundo fator local)",
            variable=self.var_usar_keyfile,
            command=self._alternar_keyfile,
            bootstyle=f"{INFO}-round-toggle",
        ).grid(row=7, column=0, sticky=W, pady=(22, 0))

        # Seção do keyfile (começa escondida)
        self.frame_keyfile = tk.Frame(form, bg=BG_BASE)
        self.frame_keyfile.grid(row=8, column=0, sticky=EW, pady=(10, 0))
        self.frame_keyfile.columnconfigure(0, weight=1)

        tb.Entry(
            self.frame_keyfile,
            textvariable=self.var_caminho_keyfile,
            state="readonly",
            font=(FONTE_PADRAO, 10),
        ).grid(row=0, column=0, sticky=EW, ipady=4)

        tb.Button(
            self.frame_keyfile, text="Escolher",
            command=self._escolher_keyfile,
            bootstyle=(SECONDARY, OUTLINE),
        ).grid(row=0, column=1, padx=(6, 0))

        tb.Button(
            self.frame_keyfile, text="Gerar",
            command=self._gerar_keyfile,
            bootstyle=(INFO, OUTLINE),
        ).grid(row=0, column=2, padx=(6, 0))

        self.frame_keyfile.grid_remove()

        # Botão grande de criar cofre
        tb.Button(
            form, text="Criar cofre",
            command=self._criar_cofre,
            bootstyle=SUCCESS,
        ).grid(row=9, column=0, sticky=EW, pady=(28, 0), ipady=12)

        entry_senha.focus_set()

    # Atualiza barra de força em tempo real
    def _atualizar_forca(self) -> None:
        """Recalcula e redesenha a barra de força conforme digitação."""
        pontos, rotulo, cor = calcular_forca_senha(self.var_senha.get())
        self.var_forca.set(pontos)
        # Calcula a largura proporcional da barra (0% a 100%)
        largura_total = self.canvas_forca.winfo_width() or 300
        largura_preenchida = int(largura_total * pontos / 100)
        self.canvas_forca.coords(self._retangulo_forca, 0, 0, largura_preenchida, 6)
        self.canvas_forca.itemconfig(self._retangulo_forca, fill=cor)
        self.lbl_forca.configure(text=f"Força: {rotulo}", fg=cor)

    # Mostra/oculta seção do keyfile
    def _alternar_keyfile(self) -> None:
        """Mostra ou esconde controles de keyfile."""
        if self.var_usar_keyfile.get():
            self.frame_keyfile.grid()
        else:
            self.frame_keyfile.grid_remove()
            self.var_caminho_keyfile.set("")

    # Escolhe keyfile existente
    def _escolher_keyfile(self) -> None:
        """Abre diálogo para selecionar keyfile existente."""
        caminho = filedialog.askopenfilename(
            title="Selecionar keyfile",
            filetypes=[("Todos os arquivos", "*.*")],
        )
        if caminho:
            self.var_caminho_keyfile.set(caminho)

    # Gera novo keyfile aleatório
    def _gerar_keyfile(self) -> None:
        """Gera novo keyfile aleatório em local escolhido pelo usuário."""
        caminho = filedialog.asksaveasfilename(
            title="Salvar novo keyfile",
            defaultextension=".key",
            filetypes=[("Keyfile", "*.key"), ("Todos", "*.*")],
        )
        if not caminho:
            return
        try:
            self.app.servico.criar_keyfile(caminho)
        except Exception as exc:
            messagebox.showerror("Erro ao gerar keyfile", str(exc))
            return
        self.var_caminho_keyfile.set(caminho)
        messagebox.showinfo("Keyfile criado", "Arquivo-chave gerado com sucesso.")

    # Executa a criação do cofre
    def _criar_cofre(self) -> None:
        """Valida formulário e cria o cofre no disco."""
        senha = self.var_senha.get()
        confirma = self.var_confirma.get()

        if senha != confirma:
            messagebox.showerror("Senhas diferentes", "As senhas informadas não são iguais.")
            return
        ok, mensagem = validar_forca_senha_mestra(senha)
        if not ok:
            messagebox.showerror("Senha fraca", mensagem)
            return

        caminho_kf = None
        if self.var_usar_keyfile.get():
            caminho_kf = self.var_caminho_keyfile.get().strip() or None
            if not caminho_kf:
                messagebox.showerror("Keyfile ausente", "Selecione ou gere um arquivo-chave.")
                return

        try:
            self.app.servico.criar_cofre(senha, caminho_keyfile=caminho_kf)
        except Exception as exc:
            messagebox.showerror("Erro ao criar cofre", str(exc))
            return

        messagebox.showinfo(
            "Cofre criado",
            "Seu cofre foi criado com sucesso! Faça login para começar.",
        )
        self.app.trocar_para_login()


# ============================================================================
# TELA — Login
# ============================================================================


class TelaLogin(tk.Frame):
    """Tela de login no cofre existente."""

    # Construtor
    def __init__(self, master: tk.Widget, app: AplicacaoCofre) -> None:
        """Inicializa a tela de login com visual split."""
        super().__init__(master, bg=BG_BASE)
        self.app = app
        self.var_senha = tk.StringVar()
        self.var_caminho_keyfile = tk.StringVar()
        self._btn_entrar: tb.Button | None = None
        self._timer_atraso: str | None = None

        self._construir_interface()

    # Constrói a interface
    def _construir_interface(self) -> None:
        """Desenha layout split: hero decorativo + formulário de login."""
        self.columnconfigure(0, weight=1, uniform="lados")
        self.columnconfigure(1, weight=1, uniform="lados")
        self.rowconfigure(0, weight=1)

        # ----- Lado esquerdo (hero) -----
        hero = tk.Frame(self, bg=BG_SIDEBAR)
        hero.grid(row=0, column=0, sticky=NSEW)
        hero.rowconfigure(0, weight=1)
        hero.rowconfigure(2, weight=1)
        hero.columnconfigure(0, weight=1)

        criar_label(
            hero, "🔐",
            fg=ACCENT_PRIMARY, bg=BG_SIDEBAR,
            fonte=("Segoe UI Emoji", 110),
        ).grid(row=0, column=0, sticky=S)

        textos = criar_frame(hero, bg=BG_SIDEBAR)
        textos.grid(row=1, column=0, pady=(30, 20))

        criar_label(
            textos, "Bem-vindo de volta",
            fg=TEXT_PRIMARY, bg=BG_SIDEBAR,
            fonte=(FONTE_PADRAO, 28, "bold"),
        ).pack()

        criar_label(
            textos, "Acesse seu cofre para continuar.",
            fg=TEXT_SECONDARY, bg=BG_SIDEBAR,
            fonte=(FONTE_PADRAO, 12),
        ).pack(pady=(8, 0))

        # Info de segurança ativa em um card discreto
        resumo = self.app.servico.obter_resumo_seguranca()
        card_seg = tk.Frame(hero, bg=BG_SURFACE, padx=24, pady=20,
                            highlightbackground=BORDER, highlightthickness=1)
        card_seg.grid(row=2, column=0, sticky=N, pady=(20, 0))

        criar_label(
            card_seg, "PROTEÇÃO ATIVA",
            fg=TEXT_MUTED, bg=BG_SURFACE,
            fonte=(FONTE_PADRAO, 9, "bold"),
        ).pack(anchor=W)
        # Linhas informativas
        for rotulo, valor in [
            ("KDF", resumo.get("algoritmo_kdf", "—")),
            ("Cifra", resumo.get("algoritmo_cifra", "—")),
        ]:
            linha = tk.Frame(card_seg, bg=BG_SURFACE)
            linha.pack(fill=X, pady=(8, 0))
            criar_label(
                linha, rotulo, fg=TEXT_SECONDARY, bg=BG_SURFACE,
                fonte=(FONTE_PADRAO, 10),
            ).pack(side=LEFT)
            criar_label(
                linha, valor, fg=TEXT_PRIMARY, bg=BG_SURFACE,
                fonte=(FONTE_MONO, 10),
            ).pack(side=RIGHT)

        if resumo.get("usa_keyfile"):
            criar_label(
                card_seg, "🔑  Keyfile obrigatório",
                fg=ACCENT_WARNING, bg=BG_SURFACE,
                fonte=("Segoe UI Emoji", 10),
            ).pack(anchor=W, pady=(10, 0))

        # ----- Lado direito (formulário) -----
        form_wrapper = tk.Frame(self, bg=BG_BASE)
        form_wrapper.grid(row=0, column=1, sticky=NSEW)
        form_wrapper.rowconfigure(0, weight=1)
        form_wrapper.rowconfigure(2, weight=1)
        form_wrapper.columnconfigure(0, weight=1)

        form = tk.Frame(form_wrapper, bg=BG_BASE, padx=60)
        form.grid(row=1, column=0, sticky=EW)
        form.columnconfigure(0, weight=1)

        criar_label(
            form, "Entrar",
            fg=TEXT_PRIMARY, fonte=(FONTE_PADRAO, 28, "bold"),
        ).grid(row=0, column=0, sticky=W)

        criar_label(
            form, "Digite sua senha mestra para acessar o cofre.",
            fg=TEXT_SECONDARY, fonte=(FONTE_PADRAO, 11),
        ).grid(row=1, column=0, sticky=W, pady=(4, 30))

        criar_label(
            form, "SENHA MESTRA",
            fg=TEXT_MUTED, fonte=(FONTE_PADRAO, 9, "bold"),
        ).grid(row=2, column=0, sticky=W, pady=(0, 6))

        entry_senha = tb.Entry(
            form, textvariable=self.var_senha,
            show="•", font=(FONTE_PADRAO, 11),
        )
        entry_senha.grid(row=3, column=0, sticky=EW, ipady=8)
        entry_senha.bind("<Return>", lambda _e: self._fazer_login())

        if self.app.servico.cofre_requer_keyfile():
            criar_label(
                form, "ARQUIVO-CHAVE",
                fg=TEXT_MUTED, fonte=(FONTE_PADRAO, 9, "bold"),
            ).grid(row=4, column=0, sticky=W, pady=(20, 6))

            frame_kf = tk.Frame(form, bg=BG_BASE)
            frame_kf.grid(row=5, column=0, sticky=EW)
            frame_kf.columnconfigure(0, weight=1)

            tb.Entry(
                frame_kf, textvariable=self.var_caminho_keyfile,
                state="readonly", font=(FONTE_PADRAO, 10),
            ).grid(row=0, column=0, sticky=EW, ipady=4)

            tb.Button(
                frame_kf, text="Escolher",
                command=self._escolher_keyfile,
                bootstyle=(SECONDARY, OUTLINE),
            ).grid(row=0, column=1, padx=(6, 0))

        # Mensagem de erro (começa invisível)
        self.lbl_mensagem = criar_label(
            form, "", fg=ACCENT_DANGER, fonte=(FONTE_PADRAO, 10),
            wraplength=400, justify="left",
        )
        self.lbl_mensagem.grid(row=6, column=0, sticky=W, pady=(15, 0))

        # Botão grande de entrar
        self._btn_entrar = tb.Button(
            form, text="Entrar no cofre",
            command=self._fazer_login,
            bootstyle=PRIMARY,
        )
        self._btn_entrar.grid(row=7, column=0, sticky=EW, pady=(15, 0), ipady=12)

        entry_senha.focus_set()

    # Escolhe keyfile
    def _escolher_keyfile(self) -> None:
        """Abre diálogo para selecionar keyfile no login."""
        caminho = filedialog.askopenfilename(
            title="Selecionar keyfile",
            filetypes=[("Todos os arquivos", "*.*")],
        )
        if caminho:
            self.var_caminho_keyfile.set(caminho)

    # Tenta fazer login
    def _fazer_login(self) -> None:
        """Executa tentativa de autenticação via serviço do cofre."""
        if self._btn_entrar is None or str(self._btn_entrar["state"]) == "disabled":
            return

        senha = self.var_senha.get()
        caminho_kf = self.var_caminho_keyfile.get().strip() or None

        try:
            resultado = self.app.servico.tentar_login(senha, caminho_keyfile=caminho_kf)
        except Exception as exc:
            self.lbl_mensagem.configure(text=str(exc))
            return

        if resultado.sucesso:
            self.lbl_mensagem.configure(text="")
            self.app.trocar_para_principal()
            return

        self.lbl_mensagem.configure(text=resultado.mensagem)
        segundos = max(resultado.atraso_segundos, resultado.bloqueio_restante)
        if segundos > 0:
            self._desabilitar_botao_por(segundos)

    # Desabilita botão temporariamente
    def _desabilitar_botao_por(self, segundos: int) -> None:
        """Desativa botão durante atraso de segurança pós-falha."""
        if self._btn_entrar is not None:
            self._btn_entrar.configure(state="disabled", text=f"Aguarde ({segundos}s)")
        self._tick_regressiva(segundos)

    # Contagem regressiva no botão
    def _tick_regressiva(self, segundos: int) -> None:
        """Atualiza contagem regressiva exibida no botão de login."""
        if segundos <= 0:
            if self._btn_entrar is not None:
                self._btn_entrar.configure(state="normal", text="Entrar no cofre")
            self._timer_atraso = None
            return
        if self._btn_entrar is not None:
            self._btn_entrar.configure(text=f"Aguarde ({segundos}s)")
        self._timer_atraso = self.after(1000, self._tick_regressiva, segundos - 1)


# ============================================================================
# TELA PRINCIPAL — dashboard com sidebar + stats + cards
# ============================================================================


class TelaPrincipal(tk.Frame):
    """Tela principal do cofre: sidebar + dashboard de stats + grid de cards."""

    # Construtor
    def __init__(self, master: tk.Widget, app: AplicacaoCofre) -> None:
        """Monta toda a tela principal do cofre autenticado."""
        super().__init__(master, bg=BG_BASE)
        self.app = app
        self.var_busca = tk.StringVar()
        self.var_busca.trace_add("write", lambda *_: self._recarregar_itens())

        # Filtro atual: "todos", "favoritos" ou um tipo específico
        self._filtro_atual: str = "todos"
        # Referência aos botões da sidebar para destacar o ativo
        self._sidebar_containers: dict[str, tk.Frame] = {}
        self._sidebar_indicadores: dict[str, tk.Frame] = {}
        self._sidebar_rotulos: dict[str, tk.Label] = {}
        self._sidebar_contagens: dict[str, tk.Label] = {}
        # Referência aos tiles do dashboard
        self._stat_tiles: dict[str, dict[str, tk.Widget]] = {}

        self._construir_interface()
        self._recarregar_itens()

        # Registra eventos globais para o bloqueio automático
        self.bind_all("<Button-1>", lambda _e: self.app.registrar_atividade(), add="+")
        self.bind_all("<Key>", lambda _e: self.app.registrar_atividade(), add="+")

    # Constrói toda a interface
    def _construir_interface(self) -> None:
        """Desenha a estrutura principal: sidebar à esquerda, conteúdo à direita."""
        # Duas colunas: sidebar fixa 260px + conteúdo flexível
        self.columnconfigure(0, weight=0, minsize=260)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._construir_sidebar()

        # Área principal (conteúdo à direita)
        area = tk.Frame(self, bg=BG_BASE)
        area.grid(row=0, column=1, sticky=NSEW)
        # Linha 0 = header | Linha 1 = stats | Linha 2 = cards
        area.rowconfigure(2, weight=1)
        area.columnconfigure(0, weight=1)

        self._construir_header(area)
        self._construir_stats(area)
        self._construir_area_cards(area)

    # Sidebar (barra lateral esquerda)
    def _construir_sidebar(self) -> None:
        """Desenha a barra lateral com filtros e botão de novo item."""
        sidebar = tk.Frame(self, bg=BG_SIDEBAR)
        sidebar.grid(row=0, column=0, sticky=NSEW)
        sidebar.columnconfigure(0, weight=1)

        # Bloco superior (logo + categorias)
        topo = tk.Frame(sidebar, bg=BG_SIDEBAR, padx=20, pady=24)
        topo.pack(fill=X)
        topo.columnconfigure(0, weight=1)

        # Logo + nome
        logo_wrapper = tk.Frame(topo, bg=BG_SIDEBAR)
        logo_wrapper.pack(anchor=W, pady=(0, 22))

        criar_label(
            logo_wrapper, "🔐",
            fg=ACCENT_PRIMARY, bg=BG_SIDEBAR,
            fonte=("Segoe UI Emoji", 22),
        ).pack(side=LEFT, padx=(0, 10))

        criar_label(
            logo_wrapper, "Cofre Seguro",
            fg=TEXT_PRIMARY, bg=BG_SIDEBAR,
            fonte=(FONTE_PADRAO, 14, "bold"),
        ).pack(side=LEFT)

        # Título de seção
        criar_label(
            topo, "  GERAL",
            fg=TEXT_MUTED, bg=BG_SIDEBAR,
            fonte=(FONTE_PADRAO, 9, "bold"),
        ).pack(anchor=W, pady=(0, 6))

        # Filtros gerais
        for chave, emoji, rotulo in [
            ("todos", "📋", "Todos os itens"),
            ("favoritos", "⭐", "Favoritos"),
        ]:
            self._criar_botao_sidebar(topo, chave, emoji, rotulo)

        # Título de seção "CATEGORIAS"
        criar_label(
            topo, "  CATEGORIAS",
            fg=TEXT_MUTED, bg=BG_SIDEBAR,
            fonte=(FONTE_PADRAO, 9, "bold"),
        ).pack(anchor=W, pady=(16, 6))

        # Filtros por tipo
        for tipo in TIPOS_SUPORTADOS:
            meta = METADADOS_TIPO[tipo]
            self._criar_botao_sidebar(topo, tipo, meta["icone"], meta["rotulo"])

        # Botão grande de novo item
        tk.Frame(topo, bg=BG_SIDEBAR, height=20).pack()

        tb.Button(
            topo, text="  +   Novo item",
            command=self._criar_novo_item,
            bootstyle=PRIMARY,
        ).pack(fill=X, ipady=6, pady=(8, 0))

        # Rodapé da sidebar (ações + dica de atalhos)
        rodape = tk.Frame(sidebar, bg=BG_SIDEBAR, padx=20, pady=20)
        rodape.pack(side="bottom", fill=X)

        # Dica de atalhos (pequeno texto clicável que abre o diálogo de atalhos)
        dica = tk.Label(
            rodape, text="⌨  Pressione F1 para ver atalhos",
            bg=BG_SIDEBAR, fg=TEXT_MUTED,
            font=(FONTE_PADRAO, 9), cursor="hand2",
        )
        dica.pack(fill=X, pady=(0, 10))
        # Clique abre o diálogo de ajuda direto
        dica.bind("<Button-1>", lambda _e: self.app._mostrar_ajuda_atalhos())
        # Hover: texto ganha a cor de acento para mostrar que é clicável
        dica.bind("<Enter>", lambda _e: dica.configure(fg=ACCENT_INFO))
        dica.bind("<Leave>", lambda _e: dica.configure(fg=TEXT_MUTED))

        # Linha de botões (tema, config, sair)
        botoes = tk.Frame(rodape, bg=BG_SIDEBAR)
        botoes.pack(fill=X)
        botoes.columnconfigure(0, weight=1)
        botoes.columnconfigure(1, weight=1)
        botoes.columnconfigure(2, weight=1)

        # Cada botão tem uma dica (tooltip) com a descrição e o atalho
        self._criar_botao_com_dica(
            botoes, col=0, texto="🌓",
            comando=self.app.alternar_tema,
            estilo=(SECONDARY, OUTLINE),
            dica_texto="Alternar tema  (Ctrl+T)",
        )
        self._criar_botao_com_dica(
            botoes, col=1, texto="⚙",
            comando=self._abrir_configuracoes,
            estilo=(SECONDARY, OUTLINE),
            dica_texto="Configurações  (Ctrl+,)",
        )
        self._criar_botao_com_dica(
            botoes, col=2, texto="⎋",
            comando=lambda: self.app.fazer_logout(),
            estilo=(DANGER, OUTLINE),
            dica_texto="Bloquear cofre  (Ctrl+L)",
        )

    # Cria um botão do rodapé da sidebar com tooltip que aparece no hover
    def _criar_botao_com_dica(
        self,
        pai: tk.Widget,
        col: int,
        texto: str,
        comando: Callable,
        estilo: Any,
        dica_texto: str,
    ) -> None:
        """Cria botão com um tooltip simples que surge ao passar o mouse."""
        btn = tb.Button(pai, text=texto, command=comando, bootstyle=estilo)
        btn.grid(row=0, column=col, sticky=EW, padx=2, ipady=4)

        # Tooltip: janela minúscula que aparece no hover
        tooltip: dict[str, Any] = {"janela": None}

        def mostrar(_evento: Any) -> None:
            """Exibe a dica numa mini janela tooltip acima/abaixo do botão."""
            if tooltip["janela"] is not None:
                return
            # Calcula posição relativa ao botão
            x = btn.winfo_rootx() + btn.winfo_width() // 2
            y = btn.winfo_rooty() - 32
            tw = tk.Toplevel(btn)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x - 90}+{y}")
            tk.Label(
                tw, text=dica_texto,
                bg=BG_ELEVATED, fg=TEXT_PRIMARY,
                font=(FONTE_PADRAO, 9),
                padx=10, pady=5,
                highlightbackground=BORDER, highlightthickness=1,
            ).pack()
            tooltip["janela"] = tw

        def esconder(_evento: Any) -> None:
            """Fecha o tooltip ao sair o mouse."""
            if tooltip["janela"] is not None:
                tooltip["janela"].destroy()
                tooltip["janela"] = None

        btn.bind("<Enter>", mostrar)
        btn.bind("<Leave>", esconder)

    # Cria um botão de sidebar (com indicador ativo e contador)
    def _criar_botao_sidebar(
        self,
        pai: tk.Widget,
        chave: str,
        emoji: str,
        rotulo: str,
    ) -> None:
        """Cria botão customizado da sidebar com barra indicadora à esquerda."""
        # Container externo (linha inteira clicável)
        row = tk.Frame(pai, bg=BG_SIDEBAR, cursor="hand2")
        row.pack(fill=X, pady=1)

        # Barra de indicador ativo (4px colorida à esquerda — visível em ambos os temas)
        indicador = tk.Frame(row, bg=BG_SIDEBAR, width=4)
        indicador.pack(side=LEFT, fill=Y)

        # Conteúdo do botão (ícone + rótulo + contador)
        conteudo = tk.Frame(row, bg=BG_SIDEBAR)
        conteudo.pack(side=LEFT, fill=BOTH, expand=True, padx=(10, 12), pady=8)
        conteudo.columnconfigure(1, weight=1)

        lbl_emoji = tk.Label(
            conteudo, text=emoji, bg=BG_SIDEBAR, fg=TEXT_PRIMARY,
            font=("Segoe UI Emoji", 12),
        )
        lbl_emoji.grid(row=0, column=0, padx=(0, 10))

        lbl_rotulo = tk.Label(
            conteudo, text=rotulo, bg=BG_SIDEBAR, fg=TEXT_SECONDARY,
            font=(FONTE_PADRAO, 10), anchor=W,
        )
        lbl_rotulo.grid(row=0, column=1, sticky=EW)

        lbl_contagem = tk.Label(
            conteudo, text="0", bg=BG_SIDEBAR, fg=TEXT_MUTED,
            font=(FONTE_PADRAO, 9, "bold"),
        )
        lbl_contagem.grid(row=0, column=2)

        # Guarda referências para atualizar depois
        self._sidebar_containers[chave] = row
        self._sidebar_indicadores[chave] = indicador
        self._sidebar_rotulos[chave] = lbl_rotulo
        self._sidebar_contagens[chave] = lbl_contagem

        # Liga clique em todos os widgets filhos para ativar o filtro
        def ativar(_evento: Any = None, c: str = chave) -> None:
            self._mudar_filtro(c)

        # Sem efeito de hover na sidebar — evita confundir "passei o mouse"
        # com "está selecionado". A seleção é feita apenas no clique.
        # O cursor "hand2" já sinaliza que o item é clicável.
        for widget in (row, conteudo, lbl_emoji, lbl_rotulo, lbl_contagem):
            widget.bind("<Button-1>", ativar)

    # Cabeçalho com título + busca
    def _construir_header(self, pai: tk.Widget) -> None:
        """Desenha o cabeçalho com título dinâmico e caixa de busca."""
        header = tk.Frame(pai, bg=BG_BASE, padx=30, pady=24)
        header.grid(row=0, column=0, sticky=EW)
        header.columnconfigure(1, weight=1)

        # Título dinâmico + subtítulo
        titulo_wrapper = tk.Frame(header, bg=BG_BASE)
        titulo_wrapper.grid(row=0, column=0, sticky=W)

        self.lbl_titulo = criar_label(
            titulo_wrapper, "Todos os itens",
            fg=TEXT_PRIMARY, fonte=(FONTE_PADRAO, 24, "bold"),
        )
        self.lbl_titulo.pack(anchor=W)

        self.lbl_subtitulo = criar_label(
            titulo_wrapper, "Tudo que está guardado no seu cofre",
            fg=TEXT_SECONDARY, fonte=(FONTE_PADRAO, 11),
        )
        self.lbl_subtitulo.pack(anchor=W, pady=(4, 0))

        # Caixa de busca estilizada
        busca_wrapper = tk.Frame(
            header, bg=BG_ELEVATED,
            highlightbackground=BORDER, highlightthickness=1,
        )
        busca_wrapper.grid(row=0, column=1, sticky=E, padx=(40, 0))

        tk.Label(
            busca_wrapper, text="🔍",
            bg=BG_ELEVATED, fg=TEXT_MUTED,
            font=("Segoe UI Emoji", 12),
            padx=12, pady=6,
        ).pack(side=LEFT)

        self._entry_busca = tk.Entry(
            busca_wrapper,
            textvariable=self.var_busca,
            font=(FONTE_PADRAO, 11),
            bg=BG_ELEVATED, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            relief="flat", borderwidth=0,
            width=32,
        )
        self._entry_busca.pack(side=LEFT, padx=(0, 14), pady=6)

        # Esc dentro da busca limpa o texto (atalho útil)
        self._entry_busca.bind("<Escape>", lambda _e: self.var_busca.set(""))

    # Barra de stats com tiles por tipo
    def _construir_stats(self, pai: tk.Widget) -> None:
        """Desenha linha com tiles clicáveis mostrando contagem por tipo."""
        wrapper = tk.Frame(pai, bg=BG_BASE, padx=30)
        # pady zero no topo, 20 embaixo (dado via pack/grid, não no construtor)
        wrapper.grid(row=1, column=0, sticky=EW)

        # Configura 6 colunas de peso igual (uma por tipo)
        for i in range(len(TIPOS_SUPORTADOS)):
            wrapper.columnconfigure(i, weight=1, uniform="stats")

        # Cria um tile para cada tipo
        for idx, tipo in enumerate(TIPOS_SUPORTADOS):
            meta = METADADOS_TIPO[tipo]
            cor_tipo = CORES_TIPO[tipo]

            tile = tk.Frame(
                wrapper, bg=BG_SURFACE, cursor="hand2",
                highlightbackground=BORDER_MUTED, highlightthickness=1,
            )
            tile.grid(row=0, column=idx, sticky=EW, padx=(0, 10) if idx < 5 else 0)

            # Barra superior colorida (acento visual)
            barra_top = tk.Frame(tile, bg=cor_tipo, height=3)
            barra_top.pack(fill=X)

            # Conteúdo do tile
            conteudo = tk.Frame(tile, bg=BG_SURFACE, padx=16, pady=14)
            conteudo.pack(fill=BOTH, expand=True)

            # Linha superior: ícone + rótulo
            linha_top = tk.Frame(conteudo, bg=BG_SURFACE)
            linha_top.pack(fill=X)

            tk.Label(
                linha_top, text=meta["icone"],
                bg=BG_SURFACE, fg=cor_tipo,
                font=("Segoe UI Emoji", 14),
            ).pack(side=LEFT)

            tk.Label(
                linha_top, text=meta["rotulo"],
                bg=BG_SURFACE, fg=TEXT_SECONDARY,
                font=(FONTE_PADRAO, 10),
            ).pack(side=LEFT, padx=(8, 0))

            # Número grande de itens
            lbl_num = tk.Label(
                conteudo, text="0",
                bg=BG_SURFACE, fg=TEXT_PRIMARY,
                font=(FONTE_PADRAO, 22, "bold"),
            )
            lbl_num.pack(anchor=W, pady=(6, 0))

            # Guarda referência pra atualizar depois
            self._stat_tiles[tipo] = {
                "container": tile,
                "barra": barra_top,
                "conteudo": conteudo,
                "linha_top": linha_top,
                "numero": lbl_num,
            }

            # Liga clique para filtrar por aquele tipo
            # Sem eventos de hover — evita o efeito de "parece selecionado"
            # ao passar o mouse por cima. A seleção é só no clique.
            def ativar(_evento: Any = None, t: str = tipo) -> None:
                self._mudar_filtro(t)

            # Propaga só o clique para todos os filhos (sem Enter/Leave)
            for widget in tile.winfo_children() + [tile]:
                self._propagar_clique(widget, ativar)

    # Helper: propaga apenas o clique para um widget e todos os descendentes
    # (o mouse do usuário pode clicar em qualquer parte do tile, até um label interno)
    def _propagar_clique(self, widget: tk.Widget, on_click: Callable) -> None:
        """Liga o evento de clique ao widget e recursivamente a todos os filhos."""
        widget.bind("<Button-1>", on_click)
        for filho in widget.winfo_children():
            self._propagar_clique(filho, on_click)

    # Atualiza o estilo dos tiles do dashboard conforme o filtro ativo
    def _destacar_tile_ativo(self) -> None:
        """Destaca o tile do tipo selecionado e limpa o destaque dos demais.

        Ativo   → fundo BG_SURFACE_HOVER + borda grossa colorida com a cor do tipo
        Inativo → fundo BG_SURFACE + borda fina neutra
        """
        for tipo, refs in self._stat_tiles.items():
            container = refs["container"]
            if tipo == self._filtro_atual:
                # Estado ATIVO: fundo mais claro + borda colorida grossa
                cor_tipo = CORES_TIPO[tipo]
                container.configure(
                    bg=BG_SURFACE_HOVER,
                    highlightbackground=cor_tipo,
                    highlightthickness=2,
                )
                # Atualiza o fundo dos elementos internos para combinar
                for chave in ("conteudo", "linha_top", "numero"):
                    refs[chave].configure(bg=BG_SURFACE_HOVER)
                # Ícone + rótulo dentro da linha_top também precisam do novo fundo
                for filho in refs["linha_top"].winfo_children():
                    try:
                        filho.configure(bg=BG_SURFACE_HOVER)
                    except tk.TclError:
                        pass
            else:
                # Estado INATIVO: fundo normal + borda fina discreta
                container.configure(
                    bg=BG_SURFACE,
                    highlightbackground=BORDER_MUTED,
                    highlightthickness=1,
                )
                for chave in ("conteudo", "linha_top", "numero"):
                    refs[chave].configure(bg=BG_SURFACE)
                for filho in refs["linha_top"].winfo_children():
                    try:
                        filho.configure(bg=BG_SURFACE)
                    except tk.TclError:
                        pass

    # Área rolável com os cards
    def _construir_area_cards(self, pai: tk.Widget) -> None:
        """Cria a área rolável de cards dos itens."""
        wrapper = tk.Frame(pai, bg=BG_BASE, padx=30)
        # pady zero no topo, 20 embaixo (dado via pack/grid, não no construtor)
        wrapper.grid(row=2, column=0, sticky=NSEW)
        wrapper.rowconfigure(0, weight=1)
        wrapper.columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(
            wrapper, highlightthickness=0, borderwidth=0, bg=BG_BASE,
        )
        self._canvas.grid(row=0, column=0, sticky=NSEW)

        scroll_y = tb.Scrollbar(wrapper, orient="vertical", command=self._canvas.yview)
        scroll_y.grid(row=0, column=1, sticky=NS)
        self._canvas.configure(yscrollcommand=scroll_y.set)

        self._frame_cards = tk.Frame(self._canvas, bg=BG_BASE)
        self._janela_cards = self._canvas.create_window(
            (0, 0), window=self._frame_cards, anchor=tk.NW,
        )

        self._frame_cards.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )
        self._canvas.bind(
            "<Configure>",
            lambda e: self._canvas.itemconfigure(self._janela_cards, width=e.width),
        )
        # Liga a rolagem com rodinha e arrasto com botão do meio
        _ligar_scroll_roda(self._canvas)
        _ligar_scroll_drag(self._canvas)

    # Põe o foco no campo de busca (usado pelo atalho Ctrl+F)
    def _focar_busca(self) -> None:
        """Dá foco à caixa de busca e seleciona tudo que estiver escrito."""
        self._entry_busca.focus_set()
        self._entry_busca.select_range(0, tk.END)

    # Muda o filtro ativo
    def _mudar_filtro(self, chave: str) -> None:
        """Troca o filtro ativo e atualiza a tela."""
        self._filtro_atual = chave
        if chave == "todos":
            titulo = "Todos os itens"
            subtitulo = "Tudo que está guardado no seu cofre"
        elif chave == "favoritos":
            titulo = "⭐  Favoritos"
            subtitulo = "Seus itens mais importantes"
        else:
            meta = METADADOS_TIPO[chave]
            titulo = f"{meta['icone']}  {meta['rotulo']}"
            subtitulo = f"Todos os seus itens do tipo {meta['rotulo'].lower()}"
        self.lbl_titulo.configure(text=titulo)
        self.lbl_subtitulo.configure(text=subtitulo)
        self._recarregar_itens()

    # Recarrega os cards da tela
    def _recarregar_itens(self) -> None:
        """Recarrega cards e contadores conforme o filtro e a busca atuais."""
        self._atualizar_contadores()
        self._destacar_botao_ativo()
        # Sincroniza também os tiles do dashboard com o filtro ativo
        self._destacar_tile_ativo()

        # Limpa os cards anteriores
        for widget in self._frame_cards.winfo_children():
            widget.destroy()

        # Descobre parâmetros de busca conforme filtro
        apenas_favoritos = self._filtro_atual == "favoritos"
        tipo_filtro: str | None = None
        if self._filtro_atual in TIPOS_SUPORTADOS:
            tipo_filtro = self._filtro_atual

        try:
            itens = self.app.servico.listar_itens(
                tipo=tipo_filtro,
                filtro=self.var_busca.get(),
                apenas_favoritos=apenas_favoritos,
            )
        except Exception as exc:
            messagebox.showerror("Erro ao listar", str(exc))
            return

        if not itens:
            self._mostrar_estado_vazio()
            return

        # Grade de 3 colunas
        for i in range(3):
            self._frame_cards.columnconfigure(i, weight=1, uniform="cards")

        for i, item in enumerate(itens):
            linha = i // 3
            coluna = i % 3
            self._criar_card_item(item, linha, coluna)

    # Atualiza contadores (sidebar + dashboard)
    def _atualizar_contadores(self) -> None:
        """Atualiza números exibidos na sidebar e nos tiles de stats."""
        try:
            contagem = self.app.servico.contar_por_tipo()
        except Exception:
            contagem = {}

        try:
            total_favoritos = len(self.app.servico.listar_itens(apenas_favoritos=True))
        except Exception:
            total_favoritos = 0

        # Sidebar: totais por tipo + favoritos + todos
        total_todos = sum(contagem.values())
        self._sidebar_contagens["todos"].configure(text=str(total_todos))
        self._sidebar_contagens["favoritos"].configure(text=str(total_favoritos))
        for tipo in TIPOS_SUPORTADOS:
            self._sidebar_contagens[tipo].configure(text=str(contagem.get(tipo, 0)))

        # Dashboard (tiles): número grande por tipo
        for tipo in TIPOS_SUPORTADOS:
            self._stat_tiles[tipo]["numero"].configure(text=str(contagem.get(tipo, 0)))

    # Destaca o botão ativo da sidebar
    def _destacar_botao_ativo(self) -> None:
        """Destaca visualmente o filtro ativo e restaura os outros ao estado normal.

        Estratégia:
          • Item ATIVO  → fundo BG_SURFACE_HOVER (mais claro, visível no escuro)
                        + barra indicadora 4px colorida
                        + TEXTO com a cor do tipo (muito destaque)
                        + contagem também com a cor do tipo
          • Item INATIVO → fundo BG_SIDEBAR (limpo), texto secundário discreto
        """
        for chave in self._sidebar_containers:
            container = self._sidebar_containers[chave]
            indicador = self._sidebar_indicadores[chave]
            rotulo = self._sidebar_rotulos[chave]
            contagem = self._sidebar_contagens[chave]

            # Pega o frame "conteúdo" (último filho do container)
            conteudo = container.winfo_children()[-1]

            if chave == self._filtro_atual:
                # ---- ESTADO ATIVO ----
                # A cor do tipo é usada no texto e na barra indicadora; para
                # "todos"/"favoritos" uso o acento global do tema
                cor_ativa = CORES_TIPO.get(chave, ACCENT_PRIMARY)
                # Fundo mais claro (BG_SURFACE_HOVER) para destaque maior que BG_SURFACE
                container.configure(bg=BG_SURFACE_HOVER)
                conteudo.configure(bg=BG_SURFACE_HOVER)
                # Barra indicadora à esquerda com a cor do tipo
                indicador.configure(bg=cor_ativa)
                # Texto do rótulo: cor do tipo + negrito (dá grande destaque)
                rotulo.configure(
                    bg=BG_SURFACE_HOVER,
                    fg=cor_ativa,
                    font=(FONTE_PADRAO, 10, "bold"),
                )
                # Contagem também ganha a cor do tipo quando ativo
                contagem.configure(
                    bg=BG_SURFACE_HOVER,
                    fg=cor_ativa,
                    font=(FONTE_PADRAO, 10, "bold"),
                )
                # Atualiza fundo de todos os demais filhos (ícone, etc)
                for filho in conteudo.winfo_children():
                    if filho in (rotulo, contagem):
                        continue
                    try:
                        filho.configure(bg=BG_SURFACE_HOVER)
                    except tk.TclError:
                        pass
            else:
                # ---- ESTADO INATIVO ----
                container.configure(bg=BG_SIDEBAR)
                conteudo.configure(bg=BG_SIDEBAR)
                # Indicador fica invisível (mesma cor do fundo)
                indicador.configure(bg=BG_SIDEBAR)
                # Texto volta ao cinza padrão, peso normal
                rotulo.configure(
                    bg=BG_SIDEBAR,
                    fg=TEXT_SECONDARY,
                    font=(FONTE_PADRAO, 10),
                )
                # Contagem também volta ao padrão discreto
                contagem.configure(
                    bg=BG_SIDEBAR,
                    fg=TEXT_MUTED,
                    font=(FONTE_PADRAO, 9, "bold"),
                )
                # Restaura fundo de todos os filhos (ícone, etc)
                for filho in conteudo.winfo_children():
                    if filho in (rotulo, contagem):
                        continue
                    try:
                        filho.configure(bg=BG_SIDEBAR)
                    except tk.TclError:
                        pass

    # Estado vazio
    def _mostrar_estado_vazio(self) -> None:
        """Desenha mensagem amigável quando não há itens para mostrar."""
        vazio = tk.Frame(self._frame_cards, bg=BG_BASE, padx=60, pady=80)
        vazio.pack(fill=BOTH, expand=True)

        if self.var_busca.get().strip():
            emoji = "🔍"
            titulo = "Nenhum resultado"
            desc = "Tente um termo diferente na busca."
        elif self._filtro_atual == "favoritos":
            emoji = "⭐"
            titulo = "Sem favoritos ainda"
            desc = "Clique na estrela de um item para marcá-lo como favorito."
        elif self._filtro_atual in TIPOS_SUPORTADOS:
            meta = METADADOS_TIPO[self._filtro_atual]
            emoji = meta["icone"]
            titulo = f"Nenhum item em {meta['rotulo']}"
            desc = "Clique em 'Novo item' para adicionar o primeiro."
        else:
            emoji = "📭"
            titulo = "Cofre vazio"
            desc = "Clique em 'Novo item' na barra lateral para começar."

        criar_label(
            vazio, emoji, fg=TEXT_MUTED, bg=BG_BASE,
            fonte=("Segoe UI Emoji", 56),
        ).pack(pady=(20, 10))
        criar_label(
            vazio, titulo, fg=TEXT_PRIMARY, bg=BG_BASE,
            fonte=(FONTE_PADRAO, 16, "bold"),
        ).pack()
        criar_label(
            vazio, desc, fg=TEXT_SECONDARY, bg=BG_BASE,
            fonte=(FONTE_PADRAO, 11),
        ).pack(pady=(6, 0))

    # Card visual moderno de cada item
    def _criar_card_item(self, item: dict[str, Any], linha: int, coluna: int) -> None:
        """Desenha um card visual moderno com barra de acento e hover."""
        tipo = item.get("tipo", "senha")
        meta = METADADOS_TIPO.get(tipo, METADADOS_TIPO["senha"])
        cor_tipo = CORES_TIPO.get(tipo, ACCENT_INFO)
        favorito = bool(item.get("favorito", False))

        # Card externo (recebe a borda sutil)
        card = tk.Frame(
            self._frame_cards, bg=BG_SURFACE, cursor="hand2",
            highlightbackground=BORDER_MUTED, highlightthickness=1,
        )
        card.grid(row=linha, column=coluna, padx=8, pady=8, sticky=NSEW, ipady=0)

        # Barra de acento à esquerda (4px da cor do tipo)
        barra = tk.Frame(card, bg=cor_tipo, width=4)
        barra.pack(side=LEFT, fill=Y)

        # Conteúdo principal do card
        conteudo = tk.Frame(card, bg=BG_SURFACE, padx=16, pady=14)
        conteudo.pack(side=LEFT, fill=BOTH, expand=True)

        # Linha 1: ícone + título + estrela
        linha1 = tk.Frame(conteudo, bg=BG_SURFACE)
        linha1.pack(fill=X)

        lbl_icone = tk.Label(
            linha1, text=meta["icone"], bg=BG_SURFACE, fg=cor_tipo,
            font=("Segoe UI Emoji", 20),
        )
        lbl_icone.pack(side=LEFT)

        lbl_titulo = tk.Label(
            linha1, text=item.get("titulo", "(sem título)"),
            bg=BG_SURFACE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 12, "bold"), anchor=W,
        )
        lbl_titulo.pack(side=LEFT, padx=(10, 0), fill=X, expand=True)

        # Estrela de favorito (clicável sem abrir detalhes)
        cor_estrela = ACCENT_WARNING if favorito else TEXT_MUTED
        lbl_fav = tk.Label(
            linha1, text="★" if favorito else "☆",
            bg=BG_SURFACE, fg=cor_estrela,
            font=(FONTE_PADRAO, 14), cursor="hand2",
        )
        lbl_fav.pack(side=RIGHT, padx=(6, 0))

        # Subtítulo (info específica do tipo)
        subtitulo = self._subtitulo_para_tipo(item)
        if subtitulo:
            lbl_sub = tk.Label(
                conteudo, text=subtitulo,
                bg=BG_SURFACE, fg=TEXT_SECONDARY,
                font=(FONTE_MONO if tipo in ("cartao", "wifi") else FONTE_PADRAO, 10),
                anchor=W,
            )
            lbl_sub.pack(fill=X, pady=(10, 0))
        else:
            lbl_sub = None

        # Chip do tipo (tag colorida pequena)
        chip_wrapper = tk.Frame(conteudo, bg=BG_SURFACE)
        chip_wrapper.pack(fill=X, pady=(14, 0))

        chip = tk.Label(
            chip_wrapper, text=meta["rotulo"].upper(),
            bg=BG_SURFACE, fg=cor_tipo,
            font=(FONTE_PADRAO, 8, "bold"), padx=8, pady=3,
            highlightbackground=cor_tipo, highlightthickness=1,
        )
        chip.pack(side=LEFT)

        # Liga clique para abrir detalhes em todos os filhos (exceto estrela)
        def abrir_detalhes(_evento: Any = None, i: dict = item) -> None:
            self._abrir_detalhes(i)

        def alternar_fav(_evento: Any = None, i: dict = item) -> None:
            self._alternar_favorito(i)

        def on_enter(_evento: Any = None) -> None:
            """Efeito de hover no card: fundo mais claro + borda destacada."""
            card.configure(bg=BG_SURFACE_HOVER, highlightbackground=cor_tipo)
            conteudo.configure(bg=BG_SURFACE_HOVER)
            linha1.configure(bg=BG_SURFACE_HOVER)
            lbl_icone.configure(bg=BG_SURFACE_HOVER)
            lbl_titulo.configure(bg=BG_SURFACE_HOVER)
            lbl_fav.configure(bg=BG_SURFACE_HOVER)
            chip_wrapper.configure(bg=BG_SURFACE_HOVER)
            chip.configure(bg=BG_SURFACE_HOVER)
            if lbl_sub is not None:
                lbl_sub.configure(bg=BG_SURFACE_HOVER)

        def on_leave(_evento: Any = None) -> None:
            """Remove o hover e volta às cores normais."""
            card.configure(bg=BG_SURFACE, highlightbackground=BORDER_MUTED)
            conteudo.configure(bg=BG_SURFACE)
            linha1.configure(bg=BG_SURFACE)
            lbl_icone.configure(bg=BG_SURFACE)
            lbl_titulo.configure(bg=BG_SURFACE)
            lbl_fav.configure(bg=BG_SURFACE)
            chip_wrapper.configure(bg=BG_SURFACE)
            chip.configure(bg=BG_SURFACE)
            if lbl_sub is not None:
                lbl_sub.configure(bg=BG_SURFACE)

        # Aplica binds a todos os widgets do card (exceto a estrela, que tem seu próprio)
        widgets_card = [card, conteudo, linha1, lbl_icone, lbl_titulo, chip_wrapper, chip]
        if lbl_sub is not None:
            widgets_card.append(lbl_sub)
        for w in widgets_card:
            w.bind("<Button-1>", abrir_detalhes)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        # A estrela tem clique próprio (alterna favorito, não abre detalhes)
        lbl_fav.bind("<Button-1>", alternar_fav)
        lbl_fav.bind("<Enter>", on_enter)
        lbl_fav.bind("<Leave>", on_leave)

    # Gera subtítulo informativo do card por tipo
    def _subtitulo_para_tipo(self, item: dict[str, Any]) -> str:
        """Retorna texto do subtítulo do card conforme o tipo do item."""
        tipo = item.get("tipo", "senha")
        if tipo == "senha":
            return str(item.get("login", ""))
        if tipo == "cartao":
            bandeira = item.get("bandeira", "")
            return f"{bandeira} • •••• •••• •••• ••••" if bandeira else "•••• •••• •••• ••••"
        if tipo == "documento":
            return str(item.get("tipo_documento", ""))
        if tipo == "nota":
            return "Conteúdo protegido"
        if tipo == "wifi":
            return f"Rede: {item.get('titulo', '')}"
        if tipo == "licenca":
            return "Chave protegida"
        return ""

    # Alterna favorito de um item
    def _alternar_favorito(self, item: dict[str, Any]) -> None:
        """Liga/desliga favorito e recarrega cards."""
        try:
            self.app.servico.alternar_favorito(str(item["id"]))
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))
            return
        self._recarregar_itens()

    # Abre detalhes de um item
    def _abrir_detalhes(self, item: dict[str, Any]) -> None:
        """Abre o diálogo de detalhes completos do item clicado."""
        DialogoDetalhesItem(self.app, item, callback_atualizar=self._recarregar_itens)

    # Abre formulário de novo item
    def _criar_novo_item(self) -> None:
        """Abre o formulário de criação de novo item."""
        tipo_inicial = (
            self._filtro_atual if self._filtro_atual in TIPOS_SUPORTADOS
            else "senha"
        )
        DialogoFormularioItem(
            self.app,
            tipo_inicial=tipo_inicial,
            item_existente=None,
            callback_sucesso=self._recarregar_itens,
        )

    # Abre configurações
    def _abrir_configuracoes(self) -> None:
        """Abre o diálogo de configurações."""
        DialogoConfiguracoes(self.app, callback_atualizar=self._recarregar_itens)


# ============================================================================
# BASE — Diálogo modal reutilizável
# ============================================================================


class JanelaModalBase(tk.Toplevel):
    """Base para janelas modais (formulários e configurações)."""

    # Construtor
    def __init__(
        self,
        app: AplicacaoCofre,
        titulo: str,
        largura: int = 580,
        altura: int = 640,
    ) -> None:
        """Configura janela modal centralizada."""
        super().__init__(app)
        self.app = app
        self.title(titulo)
        self.configure(bg=BG_BASE)
        self.transient(app)
        self.grab_set()
        self.resizable(True, True)
        self.minsize(460, 400)

        # Centraliza relativo à janela principal
        self.update_idletasks()
        app.update_idletasks()
        x = app.winfo_x() + (app.winfo_width() // 2) - (largura // 2)
        y = app.winfo_y() + (app.winfo_height() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

        # ESC fecha o diálogo
        self.bind("<Escape>", lambda _e: self.destroy())


# ============================================================================
# DIÁLOGO — Formulário de item (criação e edição)
# ============================================================================


class DialogoFormularioItem(JanelaModalBase):
    """Diálogo para criar ou editar um item do cofre."""

    # Construtor
    def __init__(
        self,
        app: AplicacaoCofre,
        tipo_inicial: str,
        item_existente: dict[str, Any] | None,
        callback_sucesso: Callable[[], None],
    ) -> None:
        """Inicializa formulário modal para criação ou edição de item."""
        if item_existente:
            tipo_inicial = item_existente.get("tipo", tipo_inicial)

        meta = METADADOS_TIPO[tipo_inicial]
        modo = "Editar" if item_existente else "Novo"
        nome_tipo = meta["rotulo"].rstrip("s") if meta["rotulo"].endswith("s") else meta["rotulo"]
        super().__init__(app, titulo=f"{modo} {nome_tipo}", largura=620, altura=720)

        self.tipo = tipo_inicial
        self.item_existente: dict[str, Any] | None = None
        if item_existente:
            self.item_existente = self.app.servico.obter_item(
                str(item_existente["id"]),
                incluir_sensiveis=True,
            )
        self.callback_sucesso = callback_sucesso
        self.widgets_campo: dict[str, Any] = {}

        self._construir_interface()

    # Constrói a interface
    def _construir_interface(self) -> None:
        """Desenha formulário com header colorido e campos dinâmicos."""
        # Container principal
        root = tk.Frame(self, bg=BG_BASE)
        root.pack(fill=BOTH, expand=True)

        # Header colorido com ícone gigante
        self._construir_header(root)

        # Corpo do formulário (área rolável)
        corpo_wrapper = tk.Frame(root, bg=BG_BASE, padx=24, pady=20)
        corpo_wrapper.pack(fill=BOTH, expand=True)

        canvas = tk.Canvas(corpo_wrapper, bg=BG_BASE, highlightthickness=0)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)

        scroll = tb.Scrollbar(corpo_wrapper, orient="vertical", command=canvas.yview)
        scroll.pack(side=RIGHT, fill=Y)
        canvas.configure(yscrollcommand=scroll.set)

        self.frame_campos = tk.Frame(canvas, bg=BG_BASE)
        janela = canvas.create_window((0, 0), window=self.frame_campos, anchor=tk.NW)
        self.frame_campos.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(janela, width=e.width),
        )
        # Liga scroll com rodinha e arrasto com botão do meio
        _ligar_scroll_roda(canvas)
        _ligar_scroll_drag(canvas)

        if self.item_existente is None:
            self._construir_seletor_tipo()

        self._construir_campos_do_tipo()

        # Rodapé com botões
        rodape = tk.Frame(root, bg=BG_BASE, padx=24, pady=18)
        rodape.pack(fill=X)

        tb.Button(
            rodape, text="Cancelar",
            command=self.destroy,
            bootstyle=(SECONDARY, OUTLINE),
        ).pack(side=RIGHT, ipady=6)

        tb.Button(
            rodape, text="Salvar (Ctrl+S)",
            command=self._salvar,
            bootstyle=SUCCESS,
        ).pack(side=RIGHT, ipady=6, padx=(0, 8))

        # Atalho de teclado: Ctrl+S salva o item direto
        self.bind("<Control-s>", lambda _e: self._salvar())
        self.bind("<Control-S>", lambda _e: self._salvar())

    # Liga atalhos extras a um widget Text (Ctrl+A para selecionar tudo)
    def _ligar_atalhos_texto(self, widget: tk.Text) -> None:
        """Adiciona Ctrl+A ao widget Text (os demais já vêm nativos do tkinter)."""
        # Ctrl+A seleciona todo o conteúdo
        def selecionar_tudo(_evento: Any) -> str:
            widget.tag_add("sel", "1.0", "end-1c")
            widget.mark_set("insert", "end-1c")
            return "break"
        widget.bind("<Control-a>", selecionar_tudo)
        widget.bind("<Control-A>", selecionar_tudo)

    # Cabeçalho colorido do diálogo
    def _construir_header(self, pai: tk.Widget) -> None:
        """Desenha cabeçalho com cor do tipo e ícone grande."""
        meta = METADADOS_TIPO[self.tipo]
        cor_tipo = CORES_TIPO[self.tipo]

        # Barra superior colorida (3px)
        tk.Frame(pai, bg=cor_tipo, height=3).pack(fill=X)

        header = tk.Frame(pai, bg=BG_SURFACE, padx=24, pady=18)
        header.pack(fill=X)

        # Ícone dentro de círculo colorido (simulado com fundo)
        icone_wrapper = tk.Frame(header, bg=BG_SURFACE)
        icone_wrapper.pack(side=LEFT)

        tk.Label(
            icone_wrapper, text=meta["icone"],
            bg=BG_SURFACE, fg=cor_tipo,
            font=("Segoe UI Emoji", 30),
        ).pack()

        # Título + subtítulo
        titulo_wrapper = tk.Frame(header, bg=BG_SURFACE)
        titulo_wrapper.pack(side=LEFT, padx=(16, 0))

        texto_titulo = meta["rotulo"]
        if self.item_existente is not None:
            texto_titulo = f"Editar: {self.item_existente.get('titulo', '')}"
        tk.Label(
            titulo_wrapper, text=texto_titulo,
            bg=BG_SURFACE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 16, "bold"),
        ).pack(anchor=W)

        tk.Label(
            titulo_wrapper,
            text="Preencha os campos abaixo e clique em Salvar.",
            bg=BG_SURFACE, fg=TEXT_SECONDARY,
            font=(FONTE_PADRAO, 10),
        ).pack(anchor=W, pady=(2, 0))

    # Seletor visual de tipo
    def _construir_seletor_tipo(self) -> None:
        """Desenha botões grandes para selecionar tipo do novo item."""
        tk.Label(
            self.frame_campos, text="TIPO DE ITEM",
            bg=BG_BASE, fg=TEXT_MUTED,
            font=(FONTE_PADRAO, 9, "bold"),
        ).pack(anchor=W, pady=(0, 8))

        grid = tk.Frame(self.frame_campos, bg=BG_BASE)
        grid.pack(fill=X, pady=(0, 16))
        for i in range(3):
            grid.columnconfigure(i, weight=1, uniform="tipos")

        # Distribui 6 tipos em 2 linhas × 3 colunas
        for idx, (tipo, meta) in enumerate(METADADOS_TIPO.items()):
            cor_tipo = CORES_TIPO[tipo]
            linha = idx // 3
            coluna = idx % 3

            botao = tk.Frame(
                grid, bg=BG_SURFACE if tipo != self.tipo else BG_SURFACE_HOVER,
                cursor="hand2",
                highlightbackground=cor_tipo if tipo == self.tipo else BORDER_MUTED,
                highlightthickness=2 if tipo == self.tipo else 1,
            )
            botao.grid(row=linha, column=coluna, padx=4, pady=4, sticky=NSEW)

            # Ícone
            tk.Label(
                botao, text=meta["icone"],
                bg=botao["bg"], fg=cor_tipo,
                font=("Segoe UI Emoji", 20),
            ).pack(pady=(14, 4))

            # Rótulo
            tk.Label(
                botao, text=meta["rotulo"],
                bg=botao["bg"], fg=TEXT_PRIMARY,
                font=(FONTE_PADRAO, 10, "bold" if tipo == self.tipo else "normal"),
            ).pack(pady=(0, 14))

            # Clique
            def ativar(_evento: Any = None, t: str = tipo) -> None:
                self._trocar_tipo(t)

            for widget in [botao] + list(botao.winfo_children()):
                widget.bind("<Button-1>", ativar)

        # Divisor
        tk.Frame(self.frame_campos, bg=BORDER, height=1).pack(fill=X, pady=(8, 14))

    # Troca o tipo e recria campos
    def _trocar_tipo(self, novo_tipo: str) -> None:
        """Muda o tipo do item sendo criado e recarrega os campos."""
        self.tipo = novo_tipo
        for widget in self.frame_campos.winfo_children():
            widget.destroy()
        self.widgets_campo.clear()
        self._construir_seletor_tipo()
        self._construir_campos_do_tipo()

    # Constrói campos do tipo
    def _construir_campos_do_tipo(self) -> None:
        """Desenha campos específicos do tipo escolhido."""
        rotulos_amigaveis = {
            "titulo": "Título / Nome",
            "login": "Usuário / E-mail",
            "senha": "Senha",
            "observacao": "Observações",
            "numero": "Número",
            "titular": "Titular (nome no cartão)",
            "validade": "Validade (MM/AAAA)",
            "cvv": "CVV",
            "bandeira": "Bandeira",
            "cor": "Cor (hex ou nome)",
            "tipo_documento": "Tipo do documento",
            "nome_titular": "Nome do titular",
            "orgao_emissor": "Órgão emissor",
            "data_emissao": "Data de emissão",
            "conteudo": "Conteúdo",
            "tipo_seguranca": "Tipo de segurança",
            "chave": "Chave de licença",
            "email_licenca": "E-mail da licença",
            "data_compra": "Data de compra",
        }

        campos_tipo = CAMPOS_EDITAVEIS_POR_TIPO[self.tipo]
        campos_obrigatorios = CAMPOS_OBRIGATORIOS_POR_TIPO[self.tipo]

        for campo in campos_tipo:
            rotulo = rotulos_amigaveis.get(campo, campo.capitalize())
            obrig = campo in campos_obrigatorios

            # Rótulo uppercase "label"
            tk.Label(
                self.frame_campos,
                text=rotulo.upper() + (" *" if obrig else ""),
                bg=BG_BASE, fg=TEXT_MUTED,
                font=(FONTE_PADRAO, 9, "bold"),
            ).pack(anchor=W, pady=(14, 6))

            # Decide o widget conforme o campo
            if campo == "conteudo":
                widget = tk.Text(
                    self.frame_campos, height=7,
                    font=(FONTE_PADRAO, 10), wrap="word",
                    bg=BG_ELEVATED, fg=TEXT_PRIMARY,
                    insertbackground=TEXT_PRIMARY,
                    relief="flat", borderwidth=0,
                    highlightbackground=BORDER, highlightthickness=1,
                    padx=10, pady=8,
                    # undo=True habilita Ctrl+Z e Ctrl+Y no widget de texto
                    undo=True, maxundo=-1,
                )
                widget.pack(fill=X)
                if self.item_existente:
                    widget.insert("1.0", str(self.item_existente.get(campo, "")))
                # Liga atalhos de seleção (Ctrl+A) — não vem habilitado por padrão
                self._ligar_atalhos_texto(widget)
                self.widgets_campo[campo] = widget

            elif campo == "tipo_documento":
                var = tk.StringVar(value=str((self.item_existente or {}).get(campo, "")))
                combo = tb.Combobox(
                    self.frame_campos, textvariable=var,
                    values=["RG", "CPF", "CNH", "Passaporte", "Título de eleitor", "Outro"],
                    font=(FONTE_PADRAO, 10),
                )
                combo.pack(fill=X, ipady=5)
                self.widgets_campo[campo] = var

            elif campo == "bandeira":
                var = tk.StringVar(value=str((self.item_existente or {}).get(campo, "")))
                combo = tb.Combobox(
                    self.frame_campos, textvariable=var,
                    values=["Visa", "Mastercard", "Elo", "American Express", "Hipercard", "Outro"],
                    font=(FONTE_PADRAO, 10),
                )
                combo.pack(fill=X, ipady=5)
                self.widgets_campo[campo] = var

            elif campo == "tipo_seguranca":
                var = tk.StringVar(value=str((self.item_existente or {}).get(campo, "WPA2")))
                combo = tb.Combobox(
                    self.frame_campos, textvariable=var,
                    values=["WPA3", "WPA2", "WPA", "WEP", "Aberto"],
                    font=(FONTE_PADRAO, 10),
                )
                combo.pack(fill=X, ipady=5)
                self.widgets_campo[campo] = var

            elif campo in ("senha", "cvv", "chave"):
                self._criar_campo_sensivel(campo)

            elif campo == "observacao":
                widget = tk.Text(
                    self.frame_campos, height=3,
                    font=(FONTE_PADRAO, 10), wrap="word",
                    bg=BG_ELEVATED, fg=TEXT_PRIMARY,
                    insertbackground=TEXT_PRIMARY,
                    relief="flat", borderwidth=0,
                    highlightbackground=BORDER, highlightthickness=1,
                    padx=10, pady=8,
                    # undo=True habilita Ctrl+Z / Ctrl+Y no widget
                    undo=True, maxundo=-1,
                )
                widget.pack(fill=X)
                if self.item_existente:
                    widget.insert("1.0", str(self.item_existente.get(campo, "")))
                # Liga atalhos extras (Ctrl+A) que não vêm nativos
                self._ligar_atalhos_texto(widget)
                self.widgets_campo[campo] = widget

            else:
                var = tk.StringVar(value=str((self.item_existente or {}).get(campo, "")))
                tb.Entry(
                    self.frame_campos, textvariable=var,
                    font=(FONTE_PADRAO, 10),
                ).pack(fill=X, ipady=6)
                self.widgets_campo[campo] = var

    # Campo sensível com toggle e (se for senha) gerador + barra de força
    def _criar_campo_sensivel(self, campo: str) -> None:
        """Cria campo sensível com ícones de mostrar/ocultar e opções extras."""
        frame = tk.Frame(self.frame_campos, bg=BG_BASE)
        frame.pack(fill=X)
        frame.columnconfigure(0, weight=1)

        var = tk.StringVar(value=str((self.item_existente or {}).get(campo, "")))
        entry = tb.Entry(
            frame, textvariable=var, show="•",
            font=(FONTE_MONO, 10),
        )
        entry.grid(row=0, column=0, sticky=EW, ipady=6)

        estado = {"visivel": False}

        def alternar() -> None:
            """Alterna visibilidade do campo sensível."""
            estado["visivel"] = not estado["visivel"]
            entry.configure(show="" if estado["visivel"] else "•")
            btn.configure(text="🙈" if estado["visivel"] else "👁")

        btn = tb.Button(
            frame, text="👁", command=alternar,
            bootstyle=(SECONDARY, OUTLINE),
            width=3,
        )
        btn.grid(row=0, column=1, padx=(6, 0))

        if campo == "senha":
            tb.Button(
                frame, text="✨",
                command=lambda: self._gerar_senha_no_campo(var),
                bootstyle=(INFO, OUTLINE), width=3,
            ).grid(row=0, column=2, padx=(6, 0))

            # Barra de força (canvas customizado)
            barra_frame = tk.Frame(self.frame_campos, bg=BG_BASE)
            barra_frame.pack(fill=X, pady=(8, 0))
            barra_frame.columnconfigure(0, weight=1)

            canvas_bar = tk.Canvas(
                barra_frame, height=5, bg=BG_ELEVATED,
                highlightthickness=0,
            )
            canvas_bar.grid(row=0, column=0, sticky=EW)
            retangulo = canvas_bar.create_rectangle(0, 0, 0, 5, fill=ACCENT_DANGER, outline="")

            lbl_f = tk.Label(
                barra_frame, text="—",
                bg=BG_BASE, fg=TEXT_MUTED,
                font=(FONTE_PADRAO, 9),
            )
            lbl_f.grid(row=0, column=1, padx=(10, 0))

            def atualizar(*_args: Any) -> None:
                """Atualiza a barra ao digitar."""
                pts, rot, cor = calcular_forca_senha(var.get())
                largura = canvas_bar.winfo_width() or 200
                canvas_bar.coords(retangulo, 0, 0, int(largura * pts / 100), 5)
                canvas_bar.itemconfig(retangulo, fill=cor)
                lbl_f.configure(text=rot, fg=cor)

            var.trace_add("write", atualizar)
            atualizar()

        self.widgets_campo[campo] = var

    # Chama o gerador de senhas
    def _gerar_senha_no_campo(self, var: tk.StringVar) -> None:
        """Abre o gerador de senhas e aplica o resultado no campo."""
        DialogoGeradorSenha(self.app, callback_resultado=var.set)

    # Salva o item
    def _salvar(self) -> None:
        """Valida e envia o item para o cofre."""
        dados: dict[str, Any] = {}
        for campo, widget in self.widgets_campo.items():
            if isinstance(widget, tk.Text):
                dados[campo] = widget.get("1.0", "end").strip()
            elif isinstance(widget, tk.StringVar):
                dados[campo] = widget.get()

        try:
            if self.item_existente:
                self.app.servico.editar_item(str(self.item_existente["id"]), dados)
            else:
                self.app.servico.adicionar_item(self.tipo, dados)
        except Exception as exc:
            messagebox.showerror("Erro ao salvar", str(exc), parent=self)
            return

        self.callback_sucesso()
        self.destroy()


# ============================================================================
# DIÁLOGO — Detalhes do item (visualização)
# ============================================================================


class DialogoDetalhesItem(JanelaModalBase):
    """Diálogo com detalhes completos do item e botões de revelar/editar."""

    # Construtor
    def __init__(
        self,
        app: AplicacaoCofre,
        item: dict[str, Any],
        callback_atualizar: Callable[[], None],
    ) -> None:
        """Inicializa o diálogo com os detalhes do item."""
        tipo = item.get("tipo", "senha")
        meta = METADADOS_TIPO.get(tipo, METADADOS_TIPO["senha"])
        super().__init__(
            app, titulo=f"{meta['icone']} {item.get('titulo', 'Detalhes')}",
            largura=600, altura=640,
        )
        self.item_id = str(item["id"])
        self.callback_atualizar = callback_atualizar
        self._campos_revelados: dict[str, str] = {}
        self._construir_interface()

    # Constrói a interface
    def _construir_interface(self) -> None:
        """Desenha cabeçalho colorido e lista de campos do item."""
        item = self.app.servico.obter_item(self.item_id, incluir_sensiveis=False)
        if item is None:
            messagebox.showerror("Erro", "Item não encontrado.", parent=self)
            self.destroy()
            return

        tipo = item.get("tipo", "senha")
        meta = METADADOS_TIPO.get(tipo, METADADOS_TIPO["senha"])
        cor_tipo = CORES_TIPO.get(tipo, ACCENT_INFO)

        # Container principal
        root = tk.Frame(self, bg=BG_BASE)
        root.pack(fill=BOTH, expand=True)

        # Barra superior colorida
        tk.Frame(root, bg=cor_tipo, height=3).pack(fill=X)

        # Header com ícone + título + chip de tipo
        header = tk.Frame(root, bg=BG_SURFACE, padx=24, pady=20)
        header.pack(fill=X)

        tk.Label(
            header, text=meta["icone"],
            bg=BG_SURFACE, fg=cor_tipo,
            font=("Segoe UI Emoji", 32),
        ).pack(side=LEFT)

        info = tk.Frame(header, bg=BG_SURFACE)
        info.pack(side=LEFT, padx=(16, 0), fill=X, expand=True)

        tk.Label(
            info, text=item.get("titulo", ""),
            bg=BG_SURFACE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 18, "bold"),
        ).pack(anchor=W)

        # Chip do tipo
        chip = tk.Label(
            info, text=meta["rotulo"].upper(),
            bg=BG_SURFACE, fg=cor_tipo,
            font=(FONTE_PADRAO, 9, "bold"),
            padx=8, pady=2,
            highlightbackground=cor_tipo, highlightthickness=1,
        )
        chip.pack(anchor=W, pady=(6, 0))

        # Corpo rolável com os campos
        corpo_wrapper = tk.Frame(root, bg=BG_BASE, padx=24, pady=20)
        corpo_wrapper.pack(fill=BOTH, expand=True)

        canvas = tk.Canvas(corpo_wrapper, bg=BG_BASE, highlightthickness=0)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scroll = tb.Scrollbar(corpo_wrapper, orient="vertical", command=canvas.yview)
        scroll.pack(side=RIGHT, fill=Y)
        canvas.configure(yscrollcommand=scroll.set)

        frame_campos = tk.Frame(canvas, bg=BG_BASE)
        janela = canvas.create_window((0, 0), window=frame_campos, anchor=tk.NW)
        frame_campos.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(janela, width=e.width),
        )
        # Liga scroll com rodinha e arrasto com botão do meio
        _ligar_scroll_roda(canvas)
        _ligar_scroll_drag(canvas)

        self._renderizar_campos(frame_campos, item, tipo)

        # Rodapé com botões
        rodape = tk.Frame(root, bg=BG_BASE, padx=24, pady=18)
        rodape.pack(fill=X)

        tb.Button(
            rodape, text="Excluir (Del)",
            command=self._excluir_item,
            bootstyle=(DANGER, OUTLINE),
        ).pack(side=RIGHT, ipady=4)

        tb.Button(
            rodape, text="Editar (Ctrl+E)",
            command=lambda: self._editar_item(item),
            bootstyle=PRIMARY,
        ).pack(side=RIGHT, ipady=4, padx=(0, 8))

        # Atalhos de teclado do diálogo de detalhes
        # Ctrl+E abre edição; Delete solicita exclusão
        self.bind("<Control-e>", lambda _e: self._editar_item(item))
        self.bind("<Control-E>", lambda _e: self._editar_item(item))
        self.bind("<Delete>", lambda _e: self._excluir_item())

    # Desenha cada campo como um "card" horizontal
    def _renderizar_campos(
        self,
        pai: tk.Widget,
        item: dict[str, Any],
        tipo: str,
    ) -> None:
        """Desenha cada campo do item como cartão com rótulo, valor e ações."""
        from .vault import CAMPOS_SENSIVEIS_POR_TIPO

        rotulos = {
            "titulo": "Título",
            "login": "Usuário / E-mail",
            "senha": "Senha",
            "observacao": "Observações",
            "numero": "Número",
            "titular": "Titular",
            "validade": "Validade",
            "cvv": "CVV",
            "bandeira": "Bandeira",
            "cor": "Cor",
            "tipo_documento": "Tipo",
            "nome_titular": "Titular",
            "orgao_emissor": "Órgão emissor",
            "data_emissao": "Data de emissão",
            "conteudo": "Conteúdo",
            "tipo_seguranca": "Segurança",
            "chave": "Chave",
            "email_licenca": "E-mail da licença",
            "data_compra": "Data de compra",
        }

        campos_sensiveis = CAMPOS_SENSIVEIS_POR_TIPO.get(tipo, ())
        campos_tipo = CAMPOS_EDITAVEIS_POR_TIPO[tipo]

        for campo in campos_tipo:
            valor = str(item.get(campo, ""))
            # Pula se vazio e não for sensível
            if not valor and campo not in campos_sensiveis:
                continue

            rotulo = rotulos.get(campo, campo.capitalize())

            # Card do campo
            card = tk.Frame(
                pai, bg=BG_SURFACE,
                highlightbackground=BORDER_MUTED, highlightthickness=1,
            )
            card.pack(fill=X, pady=4)

            conteudo = tk.Frame(card, bg=BG_SURFACE, padx=16, pady=12)
            conteudo.pack(fill=X)

            # Rótulo
            tk.Label(
                conteudo, text=rotulo.upper(),
                bg=BG_SURFACE, fg=TEXT_MUTED,
                font=(FONTE_PADRAO, 8, "bold"),
            ).pack(anchor=W)

            # Valor
            if campo in campos_sensiveis:
                self._renderizar_campo_sensivel(conteudo, campo, tipo)
            else:
                linha_valor = tk.Frame(conteudo, bg=BG_SURFACE)
                linha_valor.pack(fill=X, pady=(4, 0))

                tk.Label(
                    linha_valor, text=valor,
                    bg=BG_SURFACE, fg=TEXT_PRIMARY,
                    font=(FONTE_MONO if len(valor) > 30 else FONTE_PADRAO, 10),
                    anchor=W, justify="left", wraplength=420,
                ).pack(side=LEFT, fill=X, expand=True)

                tb.Button(
                    linha_valor, text="📋",
                    command=lambda v=valor: self._copiar(v),
                    bootstyle=(SECONDARY, OUTLINE), width=3,
                ).pack(side=RIGHT)

    # Renderiza campo sensível com botão revelar
    def _renderizar_campo_sensivel(
        self,
        pai: tk.Widget,
        campo: str,
        tipo: str,
    ) -> None:
        """Desenha campo sensível com máscara, botão revelar e botão copiar."""
        estado: dict[str, Any] = {"revelado": False, "valor": ""}
        mask_inicial = "•" * 16 if campo == "numero" else mascarar_texto_sensivel("xxxxxxxx")

        linha = tk.Frame(pai, bg=BG_SURFACE)
        linha.pack(fill=X, pady=(4, 0))

        var = tk.StringVar(value=mask_inicial)
        tk.Label(
            linha, textvariable=var,
            bg=BG_SURFACE, fg=TEXT_PRIMARY,
            font=(FONTE_MONO, 10), anchor=W,
            wraplength=420, justify="left",
        ).pack(side=LEFT, fill=X, expand=True)

        def revelar() -> None:
            """Alterna revelar/ocultar pedindo senha se necessário."""
            if estado["revelado"]:
                var.set(mask_inicial)
                estado["revelado"] = False
                btn_r.configure(text="👁")
                return
            senha = _pedir_senha_mestra(self, "Autenticar", "Digite sua senha mestra para revelar:")
            if senha is None:
                return
            try:
                valor = self.app.servico.revelar_campo(self.item_id, campo, senha)
            except PermissionError:
                messagebox.showerror("Erro", "Senha mestra incorreta.", parent=self)
                return
            except Exception as exc:
                messagebox.showerror("Erro", str(exc), parent=self)
                return
            if campo == "numero" and tipo == "cartao":
                valor = " ".join(valor[i:i+4] for i in range(0, len(valor), 4))
            var.set(valor)
            estado.update(revelado=True, valor=valor)
            btn_r.configure(text="🙈")

        def copiar() -> None:
            """Copia o valor sensível após autenticar."""
            if not estado["revelado"]:
                senha = _pedir_senha_mestra(self, "Autenticar", "Digite sua senha mestra para copiar:")
                if senha is None:
                    return
                try:
                    valor = self.app.servico.revelar_campo(self.item_id, campo, senha)
                except PermissionError:
                    messagebox.showerror("Erro", "Senha mestra incorreta.", parent=self)
                    return
                except Exception as exc:
                    messagebox.showerror("Erro", str(exc), parent=self)
                    return
                self._copiar(valor)
            else:
                self._copiar(str(estado.get("valor", "")))

        btn_r = tb.Button(
            linha, text="👁", command=revelar,
            bootstyle=(INFO, OUTLINE), width=3,
        )
        btn_r.pack(side=LEFT, padx=(6, 4))

        tb.Button(
            linha, text="📋", command=copiar,
            bootstyle=(SECONDARY, OUTLINE), width=3,
        ).pack(side=LEFT)

    # Copia com feedback visual
    def _copiar(self, texto: str) -> None:
        """Copia para o clipboard e agenda limpeza automática em 30s."""
        self.clipboard_clear()
        self.clipboard_append(texto)
        self.after(30000, self._limpar_clipboard_se_mesmo, texto)
        # Feedback visual no título
        titulo_orig = self.title()
        self.title(titulo_orig + "  ✓ Copiado")
        self.after(1500, lambda: self.title(titulo_orig))

    # Limpa clipboard se conteúdo ainda for o copiado
    def _limpar_clipboard_se_mesmo(self, texto: str) -> None:
        """Limpa clipboard após 30s se conteúdo não foi alterado."""
        try:
            atual = self.clipboard_get()
        except tk.TclError:
            return
        if atual == texto:
            self.clipboard_clear()

    # Edita o item
    def _editar_item(self, item: dict[str, Any]) -> None:
        """Abre o formulário de edição do item atual."""
        self.destroy()
        DialogoFormularioItem(
            self.app,
            tipo_inicial=item.get("tipo", "senha"),
            item_existente=item,
            callback_sucesso=self.callback_atualizar,
        )

    # Exclui o item
    def _excluir_item(self) -> None:
        """Confirma e exclui o item."""
        if not messagebox.askyesno(
            "Excluir item",
            "Tem certeza que deseja excluir este item? A ação não pode ser desfeita.",
            parent=self,
        ):
            return
        try:
            self.app.servico.excluir_item(self.item_id)
        except Exception as exc:
            messagebox.showerror("Erro", str(exc), parent=self)
            return
        self.callback_atualizar()
        self.destroy()


# ============================================================================
# DIÁLOGO — Gerador de senha
# ============================================================================


class DialogoGeradorSenha(JanelaModalBase):
    """Diálogo para gerar senhas fortes com opções configuráveis."""

    def __init__(
        self,
        app: AplicacaoCofre,
        callback_resultado: Callable[[str], None],
    ) -> None:
        """Inicializa gerador de senhas com slider e toggles."""
        super().__init__(app, titulo="Gerador de senhas", largura=500, altura=460)
        self.callback_resultado = callback_resultado

        self.var_tamanho = tk.IntVar(value=16)
        # Variável auxiliar só para exibição (tk.Scale escreve float na IntVar e
        # o Label mostra "16.0" em vez de "16"; resolvemos usando uma StringVar
        # separada, atualizada no callback do slider com int(float(v)))
        self.var_tamanho_display = tk.StringVar(value="16")
        self.var_maiusculas = tk.BooleanVar(value=True)
        self.var_minusculas = tk.BooleanVar(value=True)
        self.var_numeros = tk.BooleanVar(value=True)
        self.var_especiais = tk.BooleanVar(value=True)
        self.var_senha_gerada = tk.StringVar()

        self._construir_interface()
        self._gerar()

    def _construir_interface(self) -> None:
        """Desenha a interface do gerador."""
        root = tk.Frame(self, bg=BG_BASE)
        root.pack(fill=BOTH, expand=True)

        # Barra superior roxa decorativa
        tk.Frame(root, bg=ACCENT_PRIMARY, height=3).pack(fill=X)

        conteudo = tk.Frame(root, bg=BG_BASE, padx=24, pady=20)
        conteudo.pack(fill=BOTH, expand=True)

        # Título
        tk.Label(
            conteudo, text="✨  Gerador de senhas",
            bg=BG_BASE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 18, "bold"),
        ).pack(anchor=W, pady=(0, 4))

        tk.Label(
            conteudo, text="Crie uma senha forte e aleatória com as opções abaixo.",
            bg=BG_BASE, fg=TEXT_SECONDARY,
            font=(FONTE_PADRAO, 10),
        ).pack(anchor=W, pady=(0, 16))

        # Caixa que mostra a senha gerada (destaque)
        caixa = tk.Frame(
            conteudo, bg=BG_SURFACE,
            highlightbackground=ACCENT_PRIMARY, highlightthickness=2,
        )
        caixa.pack(fill=X)

        caixa_interna = tk.Frame(caixa, bg=BG_SURFACE, padx=16, pady=14)
        caixa_interna.pack(fill=X)
        caixa_interna.columnconfigure(0, weight=1)

        entry = tk.Entry(
            caixa_interna, textvariable=self.var_senha_gerada,
            font=(FONTE_MONO, 14),
            bg=BG_SURFACE, fg=ACCENT_INFO,
            insertbackground=TEXT_PRIMARY,
            relief="flat", borderwidth=0,
            readonlybackground=BG_SURFACE, state="readonly",
        )
        entry.grid(row=0, column=0, sticky=EW)

        tb.Button(
            caixa_interna, text="🔄", command=self._gerar,
            bootstyle=(INFO, OUTLINE), width=3,
        ).grid(row=0, column=1, padx=(8, 0))

        # Slider de tamanho
        tk.Label(
            conteudo, text="TAMANHO",
            bg=BG_BASE, fg=TEXT_MUTED,
            font=(FONTE_PADRAO, 9, "bold"),
        ).pack(anchor=W, pady=(18, 6))

        slider_frame = tk.Frame(conteudo, bg=BG_BASE)
        slider_frame.pack(fill=X)
        slider_frame.columnconfigure(0, weight=1)

        # Callback do slider: força o valor a int e atualiza a variável de display
        def _slider_mudou(valor: str) -> None:
            """Arredonda o valor do slider e atualiza IntVar e display."""
            inteiro = int(float(valor))
            self.var_tamanho.set(inteiro)
            self.var_tamanho_display.set(str(inteiro))
            self._gerar()

        tb.Scale(
            slider_frame, from_=8, to=48,
            variable=self.var_tamanho,
            bootstyle=INFO,
            command=_slider_mudou,
        ).grid(row=0, column=0, sticky=EW)

        # Mostra o valor INTEIRO via StringVar dedicada (evita o "16.0")
        tk.Label(
            slider_frame, textvariable=self.var_tamanho_display,
            bg=BG_BASE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 11, "bold"), width=4,
        ).grid(row=0, column=1, padx=(12, 0))

        # Toggles
        tk.Label(
            conteudo, text="INCLUIR",
            bg=BG_BASE, fg=TEXT_MUTED,
            font=(FONTE_PADRAO, 9, "bold"),
        ).pack(anchor=W, pady=(18, 6))

        for texto, var in [
            ("Letras maiúsculas (A-Z)", self.var_maiusculas),
            ("Letras minúsculas (a-z)", self.var_minusculas),
            ("Números (0-9)", self.var_numeros),
            ("Símbolos especiais (!@#$…)", self.var_especiais),
        ]:
            tb.Checkbutton(
                conteudo, text="  " + texto, variable=var,
                command=self._gerar,
                bootstyle=f"{INFO}-round-toggle",
            ).pack(anchor=W, pady=3)

        # Rodapé
        rodape = tk.Frame(conteudo, bg=BG_BASE)
        rodape.pack(fill=X, pady=(24, 0))

        tb.Button(
            rodape, text="Cancelar", command=self.destroy,
            bootstyle=(SECONDARY, OUTLINE),
        ).pack(side=RIGHT, ipady=4, padx=(8, 0))

        tb.Button(
            rodape, text="Usar esta senha",
            command=self._usar_senha,
            bootstyle=SUCCESS,
        ).pack(side=RIGHT, ipady=4)

    def _gerar(self) -> None:
        """Gera nova senha com as opções atuais."""
        if not any([
            self.var_maiusculas.get(),
            self.var_minusculas.get(),
            self.var_numeros.get(),
            self.var_especiais.get(),
        ]):
            self.var_senha_gerada.set("(selecione ao menos um tipo)")
            return
        try:
            senha = self.app.servico.gerar_senha(
                comprimento=self.var_tamanho.get(),
                incluir_maiusculas=self.var_maiusculas.get(),
                incluir_minusculas=self.var_minusculas.get(),
                incluir_numeros=self.var_numeros.get(),
                incluir_especiais=self.var_especiais.get(),
            )
        except Exception as exc:
            self.var_senha_gerada.set(f"(erro: {exc})")
            return
        self.var_senha_gerada.set(senha)

    def _usar_senha(self) -> None:
        """Aplica a senha gerada e fecha o diálogo."""
        senha = self.var_senha_gerada.get()
        if senha and not senha.startswith("("):
            self.callback_resultado(senha)
        self.destroy()


# ============================================================================
# DIÁLOGO — Configurações
# ============================================================================


class DialogoConfiguracoes(JanelaModalBase):
    """Diálogo de configurações em abas."""

    def __init__(
        self,
        app: AplicacaoCofre,
        callback_atualizar: Callable[[], None],
    ) -> None:
        """Inicializa diálogo de configurações do cofre."""
        super().__init__(app, titulo="Configurações", largura=680, altura=660)
        self.callback_atualizar = callback_atualizar
        self._construir_interface()

    def _construir_interface(self) -> None:
        """Desenha abas de configurações."""
        root = tk.Frame(self, bg=BG_BASE)
        root.pack(fill=BOTH, expand=True)

        # Barra colorida superior
        tk.Frame(root, bg=ACCENT_INFO, height=3).pack(fill=X)

        # Título
        header = tk.Frame(root, bg=BG_BASE, padx=24, pady=16)
        header.pack(fill=X)

        tk.Label(
            header, text="⚙  Configurações",
            bg=BG_BASE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 18, "bold"),
        ).pack(anchor=W)

        # Notebook de abas
        notebook = tb.Notebook(root, bootstyle=PRIMARY)
        notebook.pack(fill=BOTH, expand=True, padx=24, pady=(0, 20))

        aba_seg = tk.Frame(notebook, bg=BG_BASE, padx=20, pady=18)
        notebook.add(aba_seg, text=" Segurança ")
        self._construir_aba_seguranca(aba_seg)

        aba_io = tk.Frame(notebook, bg=BG_BASE, padx=20, pady=18)
        notebook.add(aba_io, text=" Exportar / Importar ")
        self._construir_aba_io(aba_io)

        aba_info = tk.Frame(notebook, bg=BG_BASE, padx=20, pady=18)
        notebook.add(aba_info, text=" Informações ")
        self._construir_aba_info(aba_info)

    def _construir_aba_seguranca(self, pai: tk.Widget) -> None:
        """Desenha aba de segurança (trocar senha mestra e keyfile)."""
        tk.Label(
            pai, text="Alterar senha mestra",
            bg=BG_BASE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 13, "bold"),
        ).pack(anchor=W, pady=(0, 4))

        tk.Label(
            pai, text="Todas as alterações exigem a senha atual para confirmação.",
            bg=BG_BASE, fg=TEXT_SECONDARY, font=(FONTE_PADRAO, 10),
        ).pack(anchor=W, pady=(0, 14))

        var_atual = tk.StringVar()
        var_nova = tk.StringVar()
        var_confirma = tk.StringVar()
        var_usar_kf = tk.BooleanVar(value=self.app.servico.cofre_requer_keyfile())
        var_caminho_kf = tk.StringVar()

        tk.Label(pai, text="SENHA ATUAL *", bg=BG_BASE, fg=TEXT_MUTED,
                 font=(FONTE_PADRAO, 9, "bold")).pack(anchor=W, pady=(0, 4))
        tb.Entry(pai, textvariable=var_atual, show="•",
                 font=(FONTE_PADRAO, 10)).pack(fill=X, ipady=5)

        tk.Label(pai, text="NOVA SENHA (OPCIONAL)", bg=BG_BASE, fg=TEXT_MUTED,
                 font=(FONTE_PADRAO, 9, "bold")).pack(anchor=W, pady=(14, 4))
        tb.Entry(pai, textvariable=var_nova, show="•",
                 font=(FONTE_PADRAO, 10)).pack(fill=X, ipady=5)

        tk.Label(pai, text="CONFIRMAR NOVA SENHA", bg=BG_BASE, fg=TEXT_MUTED,
                 font=(FONTE_PADRAO, 9, "bold")).pack(anchor=W, pady=(14, 4))
        tb.Entry(pai, textvariable=var_confirma, show="•",
                 font=(FONTE_PADRAO, 10)).pack(fill=X, ipady=5)

        tb.Checkbutton(
            pai, text="  Usar arquivo-chave (keyfile)", variable=var_usar_kf,
            bootstyle=f"{INFO}-round-toggle",
        ).pack(anchor=W, pady=(16, 6))

        frame_kf = tk.Frame(pai, bg=BG_BASE)
        frame_kf.pack(fill=X)
        frame_kf.columnconfigure(0, weight=1)

        tb.Entry(frame_kf, textvariable=var_caminho_kf, state="readonly",
                 font=(FONTE_PADRAO, 10)).grid(row=0, column=0, sticky=EW, ipady=4)

        def escolher() -> None:
            caminho = filedialog.askopenfilename(title="Selecionar keyfile", parent=self)
            if caminho:
                var_caminho_kf.set(caminho)

        tb.Button(frame_kf, text="Escolher", command=escolher,
                  bootstyle=(SECONDARY, OUTLINE)).grid(row=0, column=1, padx=(6, 0))

        def aplicar() -> None:
            atual = var_atual.get()
            nova = var_nova.get()
            confirma = var_confirma.get()
            if not atual:
                messagebox.showerror("Erro", "Informe a senha atual.", parent=self)
                return
            if nova and nova != confirma:
                messagebox.showerror("Erro", "As senhas novas não batem.", parent=self)
                return
            try:
                msg = self.app.servico.reconfigurar_seguranca(
                    senha_mestra_atual=atual,
                    nova_senha_mestra=nova or None,
                    usar_keyfile=var_usar_kf.get(),
                    caminho_keyfile=var_caminho_kf.get() or None,
                )
            except Exception as exc:
                messagebox.showerror("Erro", str(exc), parent=self)
                return
            messagebox.showinfo("Sucesso", msg, parent=self)
            var_atual.set("")
            var_nova.set("")
            var_confirma.set("")

        tb.Button(
            pai, text="Aplicar alterações", command=aplicar,
            bootstyle=SUCCESS,
        ).pack(fill=X, pady=(22, 0), ipady=8)

    def _construir_aba_io(self, pai: tk.Widget) -> None:
        """Desenha aba de exportação/importação."""
        tk.Label(
            pai, text="Exportar credenciais",
            bg=BG_BASE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 13, "bold"),
        ).pack(anchor=W, pady=(0, 4))

        tk.Label(
            pai,
            text="Gera um arquivo criptografado com uma senha própria (apenas senhas).",
            bg=BG_BASE, fg=TEXT_SECONDARY, font=(FONTE_PADRAO, 10),
        ).pack(anchor=W, pady=(0, 10))

        def exportar() -> None:
            caminho = filedialog.asksaveasfilename(
                title="Salvar exportação",
                defaultextension=".json",
                filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
                parent=self,
            )
            if not caminho:
                return
            senha = _pedir_senha_mestra(
                self, "Senha de exportação",
                "Defina uma senha forte para proteger o arquivo exportado:",
            )
            if not senha:
                return
            try:
                r = self.app.servico.exportar_credenciais(caminho, senha)
            except Exception as exc:
                messagebox.showerror("Erro", str(exc), parent=self)
                return
            messagebox.showinfo(
                "Exportação concluída",
                f"{r['quantidade']} credenciais exportadas.", parent=self,
            )

        tb.Button(pai, text="📤  Exportar", command=exportar,
                  bootstyle=(PRIMARY, OUTLINE)).pack(fill=X, ipady=6, pady=(0, 20))

        tk.Frame(pai, bg=BORDER, height=1).pack(fill=X, pady=(0, 16))

        tk.Label(
            pai, text="Importar credenciais",
            bg=BG_BASE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 13, "bold"),
        ).pack(anchor=W, pady=(0, 4))

        tk.Label(
            pai, text="Adiciona senhas de um pacote exportado ao cofre atual.",
            bg=BG_BASE, fg=TEXT_SECONDARY, font=(FONTE_PADRAO, 10),
        ).pack(anchor=W, pady=(0, 10))

        var_sobrescrever = tk.BooleanVar(value=False)
        tb.Checkbutton(
            pai, text="  Sobrescrever duplicadas",
            variable=var_sobrescrever,
            bootstyle=f"{INFO}-round-toggle",
        ).pack(anchor=W, pady=(0, 10))

        def importar() -> None:
            caminho = filedialog.askopenfilename(
                title="Selecionar arquivo de importação",
                filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
                parent=self,
            )
            if not caminho:
                return
            senha = _pedir_senha_mestra(
                self, "Senha de importação",
                "Digite a senha do arquivo exportado:",
            )
            if not senha:
                return
            try:
                r = self.app.servico.importar_credenciais(
                    caminho, senha, sobrescrever_duplicadas=var_sobrescrever.get(),
                )
            except Exception as exc:
                messagebox.showerror("Erro", str(exc), parent=self)
                return
            messagebox.showinfo(
                "Importação concluída",
                f"Inseridas: {r['inseridas']}\nAtualizadas: {r['atualizadas']}\nIgnoradas: {r['ignoradas']}",
                parent=self,
            )
            self.callback_atualizar()

        tb.Button(pai, text="📥  Importar", command=importar,
                  bootstyle=(PRIMARY, OUTLINE)).pack(fill=X, ipady=6)

    def _construir_aba_info(self, pai: tk.Widget) -> None:
        """Desenha aba de informações do cofre e do app."""
        resumo = self.app.servico.obter_resumo_seguranca()

        tk.Label(
            pai, text="Informações do cofre",
            bg=BG_BASE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 13, "bold"),
        ).pack(anchor=W, pady=(0, 14))

        linhas = [
            ("Formato", resumo.get("status_formato", "—")),
            ("Versão", str(resumo.get("versao", 0))),
            ("Algoritmo KDF", resumo.get("algoritmo_kdf", "—")),
            ("Algoritmo de cifra", resumo.get("algoritmo_cifra", "—")),
            ("Keyfile ativo", "Sim" if resumo.get("usa_keyfile") else "Não"),
            ("Memória Argon2id", f"{resumo.get('memoria_argon2_mb', 0)} MB"),
        ]

        for rotulo, valor in linhas:
            card = tk.Frame(
                pai, bg=BG_SURFACE,
                highlightbackground=BORDER_MUTED, highlightthickness=1,
            )
            card.pack(fill=X, pady=3)

            linha = tk.Frame(card, bg=BG_SURFACE, padx=14, pady=10)
            linha.pack(fill=X)

            tk.Label(
                linha, text=rotulo, bg=BG_SURFACE, fg=TEXT_SECONDARY,
                font=(FONTE_PADRAO, 10),
            ).pack(side=LEFT)
            tk.Label(
                linha, text=valor, bg=BG_SURFACE, fg=ACCENT_INFO,
                font=(FONTE_MONO, 10),
            ).pack(side=RIGHT)

        tk.Frame(pai, bg=BORDER, height=1).pack(fill=X, pady=(18, 14))

        tk.Label(
            pai, text="🔐  Cofre Seguro",
            bg=BG_BASE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 12, "bold"),
        ).pack()
        tk.Label(
            pai, text="Projeto acadêmico — Programação de Computadores",
            bg=BG_BASE, fg=TEXT_MUTED,
            font=(FONTE_PADRAO, 9),
        ).pack()


# ============================================================================
# UTIL — Diálogo para pedir senha mestra
# ============================================================================


def _pedir_senha_mestra(
    parent: tk.Misc, titulo: str, mensagem: str,
) -> str | None:
    """Modal para pedir senha mestra (reautenticação); retorna None se cancelar."""
    resultado: list[str | None] = [None]

    dlg = tk.Toplevel(parent)
    dlg.title(titulo)
    dlg.configure(bg=BG_BASE)
    dlg.transient(parent)
    dlg.grab_set()
    dlg.resizable(False, False)

    parent.update_idletasks()
    largura, altura = 440, 200
    try:
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (largura // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (altura // 2)
    except Exception:
        x, y = 200, 200
    dlg.geometry(f"{largura}x{altura}+{x}+{y}")

    # Barra colorida superior
    tk.Frame(dlg, bg=ACCENT_PRIMARY, height=3).pack(fill=X)

    frame = tk.Frame(dlg, bg=BG_BASE, padx=24, pady=20)
    frame.pack(fill=BOTH, expand=True)

    tk.Label(
        frame, text="🔐", bg=BG_BASE, fg=ACCENT_PRIMARY,
        font=("Segoe UI Emoji", 24),
    ).pack(pady=(0, 6))

    tk.Label(
        frame, text=mensagem, bg=BG_BASE, fg=TEXT_PRIMARY,
        font=(FONTE_PADRAO, 10), wraplength=380, justify=CENTER,
    ).pack(pady=(0, 12))

    var = tk.StringVar()
    entry = tb.Entry(frame, textvariable=var, show="•", font=(FONTE_PADRAO, 11))
    entry.pack(fill=X, ipady=6)
    entry.focus_set()

    def confirmar(_e: Any = None) -> None:
        resultado[0] = var.get()
        dlg.destroy()

    def cancelar() -> None:
        resultado[0] = None
        dlg.destroy()

    entry.bind("<Return>", confirmar)
    dlg.bind("<Escape>", lambda _e: cancelar())

    rodape = tk.Frame(frame, bg=BG_BASE)
    rodape.pack(fill=X, pady=(14, 0))
    tb.Button(
        rodape, text="Cancelar", command=cancelar,
        bootstyle=(SECONDARY, OUTLINE),
    ).pack(side=RIGHT, padx=(8, 0), ipady=3)
    tb.Button(
        rodape, text="OK", command=confirmar,
        bootstyle=PRIMARY,
    ).pack(side=RIGHT, ipady=3)

    parent.wait_window(dlg)
    return resultado[0]


# ============================================================================
# DIÁLOGO — Atalhos de teclado (F1)
# ============================================================================


class DialogoAtalhos(JanelaModalBase):
    """Diálogo que exibe todos os atalhos de teclado do aplicativo."""

    # Construtor
    def __init__(self, app: AplicacaoCofre) -> None:
        """Monta a janela com a lista de atalhos organizada por seção."""
        super().__init__(app, titulo="Atalhos de teclado", largura=640, altura=640)
        self._construir_interface()

    # Constrói a interface
    def _construir_interface(self) -> None:
        """Desenha o conteúdo: header + seções + rodapé."""
        root = tk.Frame(self, bg=BG_BASE)
        root.pack(fill=BOTH, expand=True)

        # Barra colorida superior (acento decorativo)
        tk.Frame(root, bg=ACCENT_INFO, height=3).pack(fill=X)

        # Cabeçalho
        header = tk.Frame(root, bg=BG_BASE, padx=24, pady=18)
        header.pack(fill=X)

        tk.Label(
            header, text="⌨  Atalhos de teclado",
            bg=BG_BASE, fg=TEXT_PRIMARY,
            font=(FONTE_PADRAO, 18, "bold"),
        ).pack(anchor=W)

        tk.Label(
            header,
            text="Use o teclado para agilizar sua navegação pelo cofre.",
            bg=BG_BASE, fg=TEXT_SECONDARY,
            font=(FONTE_PADRAO, 10),
        ).pack(anchor=W, pady=(4, 0))

        # Área rolável para a lista de atalhos
        wrapper = tk.Frame(root, bg=BG_BASE, padx=24, pady=10)
        wrapper.pack(fill=BOTH, expand=True)

        canvas = tk.Canvas(wrapper, bg=BG_BASE, highlightthickness=0)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scroll = tb.Scrollbar(wrapper, orient="vertical", command=canvas.yview)
        scroll.pack(side=RIGHT, fill=Y)
        canvas.configure(yscrollcommand=scroll.set)

        interno = tk.Frame(canvas, bg=BG_BASE)
        janela = canvas.create_window((0, 0), window=interno, anchor=tk.NW)
        interno.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(janela, width=e.width),
        )
        # Liga scroll com rodinha e arrasto com botão do meio
        _ligar_scroll_roda(canvas)
        _ligar_scroll_drag(canvas)

        # Seções de atalhos (título + lista de (tecla, descrição))
        secoes: list[tuple[str, list[tuple[str, str]]]] = [
            ("🧭  Navegação", [
                ("Ctrl + N",          "Criar novo item"),
                ("Ctrl + F",          "Focar no campo de busca"),
                ("Ctrl + 0",          "Mostrar todos os itens"),
                ("Ctrl + 1 … 6",      "Filtrar por tipo (Senhas, Cartões, …)"),
                ("Ctrl + Shift + F",  "Filtrar só favoritos"),
                ("F5",                "Recarregar lista de itens"),
                ("Escape",             "Limpar busca / fechar diálogo"),
            ]),
            ("⚙  Aplicativo", [
                ("Ctrl + T",       "Alternar tema (claro/escuro)"),
                ("Ctrl + ,",       "Abrir configurações"),
                ("Ctrl + G",       "Abrir gerador de senhas"),
                ("Ctrl + L",       "Bloquear cofre (logout)"),
                ("F1",             "Mostrar esta janela de atalhos"),
            ]),
            ("📋  Ao ver um item", [
                ("Ctrl + E",       "Editar o item"),
                ("Delete",         "Excluir o item"),
                ("Clique em 👁",    "Revelar campo sensível (pede senha)"),
                ("Clique em 📋",    "Copiar valor para a área de transferência"),
            ]),
            ("💾  No formulário", [
                ("Ctrl + S",       "Salvar o item"),
                ("Escape",         "Cancelar / fechar"),
                ("Ctrl + Z",       "Desfazer digitação em campos de texto"),
                ("Ctrl + Y",       "Refazer digitação em campos de texto"),
                ("Ctrl + A",       "Selecionar todo o texto de um campo"),
                ("Ctrl + C / V / X", "Copiar / colar / recortar"),
            ]),
            ("🖱  Mouse", [
                ("Roda do mouse",       "Rolar a lista de itens"),
                ("Botão do meio + arrastar", "Rolar a lista arrastando (estilo PDF)"),
                ("Clique no card",      "Abrir detalhes do item"),
                ("Clique na ★ / ☆",     "Marcar/desmarcar como favorito"),
            ]),
        ]

        # Desenha cada seção
        for titulo_secao, atalhos in secoes:
            # Título da seção
            tk.Label(
                interno, text=titulo_secao,
                bg=BG_BASE, fg=ACCENT_INFO,
                font=(FONTE_PADRAO, 12, "bold"),
            ).pack(anchor=W, pady=(14, 8))

            # Card com os atalhos da seção
            card = tk.Frame(
                interno, bg=BG_SURFACE,
                highlightbackground=BORDER_MUTED, highlightthickness=1,
            )
            card.pack(fill=X)

            for tecla, desc in atalhos:
                linha = tk.Frame(card, bg=BG_SURFACE)
                linha.pack(fill=X, padx=16, pady=8)

                # "Chip" com a tecla (estilo badge monoespaçado)
                chip = tk.Label(
                    linha, text=f" {tecla} ",
                    bg=BG_ELEVATED, fg=TEXT_PRIMARY,
                    font=(FONTE_MONO, 9, "bold"),
                    padx=8, pady=3,
                    highlightbackground=BORDER, highlightthickness=1,
                )
                chip.pack(side=LEFT)

                # Descrição à direita
                tk.Label(
                    linha, text=desc,
                    bg=BG_SURFACE, fg=TEXT_SECONDARY,
                    font=(FONTE_PADRAO, 10),
                    anchor=W,
                ).pack(side=LEFT, padx=(14, 0), fill=X, expand=True)

        # Rodapé com botão Fechar
        rodape = tk.Frame(root, bg=BG_BASE, padx=24, pady=16)
        rodape.pack(fill=X)

        tb.Button(
            rodape, text="Fechar",
            command=self.destroy,
            bootstyle=PRIMARY,
        ).pack(side=RIGHT, ipady=4)


# ============================================================================
# FUNÇÃO DE ENTRADA
# ============================================================================


def iniciar_interface(servico: ServicoCofre) -> None:
    """Cria a janela principal e entra no loop da aplicação."""
    app = AplicacaoCofre(servico)
    app.mainloop()
