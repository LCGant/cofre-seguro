from __future__ import annotations

import secrets
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog, ttk

from .security import validar_forca_senha_mestra
from .vault import ServicoCofre


class AplicacaoCofre(tk.Tk):
    """Janela principal responsável por alternar telas da aplicação."""

    def __init__(self, servico: ServicoCofre) -> None:
        """Configura janela base, estilo visual e fluxo inicial."""
        super().__init__()
        self.servico = servico
        self.title("Cofre de Senhas Seguro")
        self.geometry("1160x760")
        self.minsize(960, 620)
        self.configure(background="#f6f1e8")
        self.protocol("WM_DELETE_WINDOW", self._encerrar_aplicacao)

        self._configurar_estilo()
        self._container = ttk.Frame(self, style="App.TFrame", padding=18)
        self._container.pack(fill="both", expand=True)

        self._frame_atual: ttk.Frame | None = None
        self._mostrar_tela_inicial()

    def _configurar_estilo(self) -> None:
        """Define tema e estilos ttk da interface."""
        estilo = ttk.Style(self)
        estilo.theme_use("clam")

        estilo.configure("App.TFrame", background="#f6f1e8")
        estilo.configure(
            "Card.TFrame",
            background="#fffdf8",
            borderwidth=1,
            relief="solid",
        )
        estilo.configure("Painel.TFrame", background="#173b36")
        estilo.configure(
            "Titulo.TLabel",
            background="#f6f1e8",
            foreground="#173b36",
            font=("Segoe UI", 24, "bold"),
        )
        estilo.configure(
            "Subtitulo.TLabel",
            background="#f6f1e8",
            foreground="#5d685f",
            font=("Segoe UI", 11),
        )
        estilo.configure(
            "Campo.TLabel",
            background="#f6f1e8",
            foreground="#1f3736",
            font=("Segoe UI", 10, "bold"),
        )
        estilo.configure(
            "CampoCard.TLabel",
            background="#fffdf8",
            foreground="#1f3736",
            font=("Segoe UI", 10, "bold"),
        )
        estilo.configure(
            "Texto.TLabel",
            background="#f6f1e8",
            foreground="#324746",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "TextoCard.TLabel",
            background="#fffdf8",
            foreground="#324746",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "TituloCard.TLabel",
            background="#fffdf8",
            foreground="#173b36",
            font=("Segoe UI", 11, "bold"),
        )
        estilo.configure(
            "TituloDialogo.TLabel",
            background="#fffdf8",
            foreground="#173b36",
            font=("Segoe UI", 24, "bold"),
        )
        estilo.configure(
            "SubtituloCard.TLabel",
            background="#fffdf8",
            foreground="#5d685f",
            font=("Segoe UI", 11),
        )
        estilo.configure(
            "Badge.TLabel",
            background="#173b36",
            foreground="#f8f4eb",
            font=("Segoe UI", 9, "bold"),
            padding=(10, 4),
        )
        estilo.configure(
            "Destaque.TLabel",
            background="#173b36",
            foreground="#f8f4eb",
            font=("Segoe UI", 10, "bold"),
        )
        estilo.configure(
            "Primario.TButton",
            background="#173b36",
            foreground="#fffdf8",
            font=("Segoe UI", 10, "bold"),
            padding=(14, 9),
            borderwidth=0,
            focuscolor="none",
        )
        estilo.configure(
            "Secundario.TButton",
            background="#eadfc9",
            foreground="#173b36",
            font=("Segoe UI", 10),
            padding=(12, 8),
            borderwidth=0,
            focuscolor="none",
        )
        estilo.map(
            "Primario.TButton",
            background=[
                ("active", "#12312d"),
                ("pressed", "#102a27"),
                ("disabled", "#aab9b4"),
            ],
            foreground=[("disabled", "#f2ede4")],
        )
        estilo.map(
            "Secundario.TButton",
            background=[
                ("active", "#dcccad"),
                ("pressed", "#d3c09d"),
                ("disabled", "#ece4d5"),
            ],
            foreground=[
                ("active", "#173b36"),
                ("disabled", "#8a8a84"),
            ],
        )
        estilo.configure(
            "TCheckbutton",
            background="#f6f1e8",
            foreground="#1f3736",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Card.TCheckbutton",
            background="#fffdf8",
            foreground="#1f3736",
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "TEntry",
            fieldbackground="#fffdf8",
            foreground="#1f3736",
            insertcolor="#1f3736",
            padding=8,
            borderwidth=1,
        )
        estilo.map(
            "TEntry",
            bordercolor=[("focus", "#173b36")],
            lightcolor=[("focus", "#173b36")],
            darkcolor=[("focus", "#173b36")],
        )
        estilo.configure(
            "TSpinbox",
            fieldbackground="#fffdf8",
            foreground="#1f3736",
            arrowsize=14,
            padding=6,
        )
        estilo.map(
            "TSpinbox",
            bordercolor=[("focus", "#173b36")],
            lightcolor=[("focus", "#173b36")],
            darkcolor=[("focus", "#173b36")],
        )
        estilo.configure(
            "TLabelframe",
            background="#fffdf8",
            borderwidth=1,
            relief="solid",
        )
        estilo.configure(
            "TLabelframe.Label",
            background="#fffdf8",
            foreground="#173b36",
            font=("Segoe UI", 10, "bold"),
        )
        estilo.configure(
            "Treeview",
            background="#fffdf8",
            fieldbackground="#fffdf8",
            foreground="#243938",
            font=("Segoe UI", 10),
            rowheight=32,
            borderwidth=0,
        )
        estilo.configure(
            "Treeview.Heading",
            background="#efe4d0",
            foreground="#173b36",
            font=("Segoe UI", 10, "bold"),
            padding=(8, 9),
        )
        estilo.map(
            "Treeview",
            background=[("selected", "#d8e4df")],
            foreground=[("selected", "#173b36")],
        )

    def _mostrar_tela_inicial(self) -> None:
        """Decide entre fluxo de primeiro uso e login normal."""
        if self.servico.existe_cofre():
            self.mostrar_tela_login()
        else:
            self.mostrar_tela_criacao()

    def _trocar_tela(self, classe_tela: type[ttk.Frame]) -> None:
        """Substitui o frame exibido no container principal."""
        if self._frame_atual is not None:
            self._frame_atual.destroy()
        self._frame_atual = classe_tela(self._container, self)
        self._frame_atual.pack(fill="both", expand=True)

    def mostrar_tela_criacao(self) -> None:
        """Exibe tela para criação inicial da senha mestra."""
        self._trocar_tela(TelaCriacaoMestra)

    def mostrar_tela_login(self) -> None:
        """Exibe tela de autenticação por senha mestra."""
        self._trocar_tela(TelaLogin)

    def mostrar_tela_principal(self) -> None:
        """Exibe área principal do cofre após login bem-sucedido."""
        self._trocar_tela(TelaPrincipal)

    def _encerrar_aplicacao(self) -> None:
        """Finaliza app limpando sessão para reduzir exposição em memória."""
        self.servico.encerrar_sessao()
        self.destroy()


def configurar_colunas_expansiveis(frame: tk.Widget, total_colunas: int, grupo: str) -> None:
    """Configura colunas com expansão horizontal e largura uniforme."""
    for indice in range(total_colunas):
        frame.columnconfigure(indice, weight=1, uniform=grupo)


class TelaCriacaoMestra(ttk.Frame):
    """Tela de primeiro uso para criação da senha mestra inicial."""

    def __init__(self, parent: ttk.Frame, app: AplicacaoCofre) -> None:
        """Monta interface de configuração inicial do cofre."""
        super().__init__(parent, style="App.TFrame")
        self.app = app
        self.var_senha = tk.StringVar()
        self.var_confirmacao = tk.StringVar()
        self.var_usar_keyfile = tk.BooleanVar(value=False)
        self.var_keyfile = tk.StringVar()
        self._montar_interface()
        self._atualizar_estado_keyfile()

    def _montar_interface(self) -> None:
        """Renderiza campos e ações de criação da senha mestra."""
        cabecalho = ttk.Frame(self, style="App.TFrame")
        cabecalho.pack(fill="x", pady=(10, 18))

        ttk.Label(cabecalho, text="COFRE LOCAL", style="Badge.TLabel").pack(anchor="w", pady=(0, 10))
        ttk.Label(cabecalho, text="Configuração Inicial", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            cabecalho,
            text="Crie a senha mestra do cofre e, se quiser, ative um keyfile local.",
            style="Subtitulo.TLabel",
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        cartao = ttk.Frame(self, style="Card.TFrame", padding=18)
        cartao.pack(fill="x", pady=(0, 16))

        ttk.Label(cartao, text="Senha mestra", style="CampoCard.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 14),
            pady=(0, 10),
        )
        ttk.Entry(
            cartao,
            textvariable=self.var_senha,
            show="*",
            width=42,
            font=("Segoe UI", 11),
        ).grid(row=0, column=1, columnspan=3, sticky="w", pady=(0, 10))

        ttk.Label(cartao, text="Confirmar senha", style="CampoCard.TLabel").grid(
            row=1,
            column=0,
            sticky="w",
            padx=(0, 14),
            pady=(0, 10),
        )
        ttk.Entry(
            cartao,
            textvariable=self.var_confirmacao,
            show="*",
            width=42,
            font=("Segoe UI", 11),
        ).grid(row=1, column=1, columnspan=3, sticky="w", pady=(0, 10))

        ttk.Checkbutton(
            cartao,
            text="Exigir keyfile local no desbloqueio",
            variable=self.var_usar_keyfile,
            style="Card.TCheckbutton",
            command=self._atualizar_estado_keyfile,
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 10))

        ttk.Label(cartao, text="Keyfile", style="CampoCard.TLabel").grid(
            row=3,
            column=0,
            sticky="w",
            padx=(0, 14),
            pady=(0, 10),
        )
        self._entrada_keyfile = ttk.Entry(
            cartao,
            textvariable=self.var_keyfile,
            width=52,
            font=("Segoe UI", 10),
        )
        self._entrada_keyfile.grid(row=3, column=1, sticky="we", pady=(0, 10))

        self._botao_keyfile = ttk.Button(
            cartao,
            text="Selecionar",
            style="Secundario.TButton",
            command=self._selecionar_keyfile,
        )
        self._botao_keyfile.grid(row=3, column=2, sticky="w", padx=(8, 8), pady=(0, 10))

        self._botao_gerar_keyfile = ttk.Button(
            cartao,
            text="Gerar keyfile",
            style="Secundario.TButton",
            command=self._gerar_keyfile,
        )
        self._botao_gerar_keyfile.grid(row=3, column=3, sticky="w", pady=(0, 10))

        cartao.columnconfigure(1, weight=1)

        botoes = ttk.Frame(self, style="App.TFrame")
        botoes.pack(fill="x", pady=(4, 0))
        configurar_colunas_expansiveis(botoes, 2, "acoes_criacao")

        ttk.Button(
            botoes,
            text="Criar Cofre Seguro",
            style="Primario.TButton",
            command=self._criar_cofre,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            botoes,
            text="Fechar",
            style="Secundario.TButton",
            command=self.app._encerrar_aplicacao,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _atualizar_estado_keyfile(self) -> None:
        """Habilita ou desabilita os controles de keyfile conforme a escolha do usuário."""
        estado = "normal" if self.var_usar_keyfile.get() else "disabled"
        self._entrada_keyfile.configure(state=estado)
        self._botao_keyfile.state(["!disabled"] if estado == "normal" else ["disabled"])
        self._botao_gerar_keyfile.state(["!disabled"] if estado == "normal" else ["disabled"])

    def _selecionar_keyfile(self) -> None:
        """Permite selecionar um keyfile existente no disco."""
        caminho = filedialog.askopenfilename(
            parent=self,
            title="Selecionar keyfile",
        )
        if caminho:
            self.var_keyfile.set(caminho)

    def _gerar_keyfile(self) -> None:
        """Gera um novo keyfile dedicado e grava no caminho escolhido pelo usuário."""
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar keyfile",
            defaultextension=".key",
            initialfile="cofre_seguro.key",
        )
        if not caminho:
            return

        try:
            self.app.servico.criar_keyfile(caminho)
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível gerar o keyfile: {exc}")
            return

        self.var_keyfile.set(caminho)
        messagebox.showinfo(
            "Keyfile criado",
            "Keyfile criado com sucesso. Guarde esse arquivo em local seguro.",
        )

    def _criar_cofre(self) -> None:
        """Valida entradas e cria o cofre inicial com senha mestra e keyfile opcional."""
        senha = self.var_senha.get()
        confirmacao = self.var_confirmacao.get()
        usar_keyfile = self.var_usar_keyfile.get()
        caminho_keyfile = self.var_keyfile.get().strip() or None

        if not senha or not confirmacao:
            messagebox.showwarning("Campos obrigatórios", "Preencha e confirme a senha mestra.")
            return

        if senha != confirmacao:
            messagebox.showerror("Validação", "As senhas informadas não coincidem.")
            return

        senha_valida, mensagem_forca = validar_forca_senha_mestra(senha)
        if not senha_valida:
            messagebox.showerror("Senha mestra fraca", mensagem_forca)
            return

        if usar_keyfile and not caminho_keyfile:
            messagebox.showwarning(
                "Keyfile obrigatório",
                "Ative um keyfile apenas se você realmente selecionou ou gerou esse arquivo.",
            )
            return

        try:
            self.app.servico.criar_cofre(
                senha,
                caminho_keyfile=caminho_keyfile if usar_keyfile else None,
            )
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível criar o cofre: {exc}")
            return

        self.var_senha.set("")
        self.var_confirmacao.set("")
        self.var_keyfile.set("")
        self.var_usar_keyfile.set(False)
        self._atualizar_estado_keyfile()
        messagebox.showinfo("Sucesso", "Cofre criado com sucesso. Faça login para continuar.")
        self.app.mostrar_tela_login()


class TelaLogin(ttk.Frame):
    """Tela de autenticação com mitigação de força bruta e suporte a keyfile."""

    def __init__(self, parent: ttk.Frame, app: AplicacaoCofre) -> None:
        """Configura interface de login e controle de temporizadores."""
        super().__init__(parent, style="App.TFrame")
        self.app = app
        self.var_senha = tk.StringVar()
        self.var_keyfile = tk.StringVar()
        self._timer_id: str | None = None
        self._segundos_restantes = 0
        self._prefixo_contagem = ""
        self._resumo = self.app.servico.obter_resumo_seguranca()
        self._montar_interface()
        self._inicializar_bloqueio_existente()

    def _montar_interface(self) -> None:
        """Renderiza campos de autenticação e informações de proteção do cofre."""
        cabecalho = ttk.Frame(self, style="App.TFrame")
        cabecalho.pack(fill="x", pady=(10, 16))

        ttk.Label(cabecalho, text="COFRE LOCAL", style="Badge.TLabel").pack(anchor="w", pady=(0, 10))
        ttk.Label(cabecalho, text="Login no Cofre", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            cabecalho,
            text="Digite a senha mestra para abrir o cofre local.",
            style="Subtitulo.TLabel",
            wraplength=900,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        cartao = ttk.Frame(self, style="Card.TFrame", padding=18)
        cartao.pack(fill="x", pady=(0, 16))

        ttk.Label(cartao, text="Proteção detectada", style="TituloCard.TLabel").grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 8),
        )
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

        formulario = ttk.Frame(self, style="App.TFrame")
        formulario.pack(anchor="w", pady=(0, 10))

        ttk.Label(formulario, text="Senha mestra", style="Campo.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 14),
            pady=(0, 10),
        )
        self._entrada_senha = ttk.Entry(
            formulario,
            textvariable=self.var_senha,
            show="*",
            width=40,
            font=("Segoe UI", 11),
        )
        self._entrada_senha.grid(row=0, column=1, sticky="w", pady=(0, 10))
        self._entrada_senha.focus_set()

        self._controles_temporizados: list[tk.Widget] = [self._entrada_senha]

        if self._resumo["usa_keyfile"]:
            ttk.Label(formulario, text="Keyfile", style="Campo.TLabel").grid(
                row=1,
                column=0,
                sticky="w",
                padx=(0, 14),
                pady=(0, 10),
            )
            self._entrada_keyfile = ttk.Entry(
                formulario,
                textvariable=self.var_keyfile,
                width=46,
                font=("Segoe UI", 10),
            )
            self._entrada_keyfile.grid(row=1, column=1, sticky="we", pady=(0, 10))
            self._botao_keyfile = ttk.Button(
                formulario,
                text="Selecionar keyfile",
                style="Secundario.TButton",
                command=self._selecionar_keyfile,
            )
            self._botao_keyfile.grid(row=1, column=2, sticky="w", padx=(8, 0), pady=(0, 10))
            self._controles_temporizados.extend([self._entrada_keyfile, self._botao_keyfile])

        botoes = ttk.Frame(self, style="App.TFrame")
        botoes.pack(fill="x", pady=(6, 10))
        configurar_colunas_expansiveis(botoes, 2, "acoes_login")

        self._botao_login = ttk.Button(
            botoes,
            text="Entrar no Cofre",
            style="Primario.TButton",
            command=self._tentar_login,
        )
        self._botao_login.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self._controles_temporizados.append(self._botao_login)

        ttk.Button(
            botoes,
            text="Fechar",
            style="Secundario.TButton",
            command=self.app._encerrar_aplicacao,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self._label_status = ttk.Label(self, text="", style="Texto.TLabel")
        self._label_status.pack(anchor="w", pady=(6, 0))

        self.bind("<Return>", self._executar_atalho_enter)

    def _selecionar_keyfile(self) -> None:
        """Seleciona o keyfile necessário para o desbloqueio do cofre."""
        caminho = filedialog.askopenfilename(
            parent=self,
            title="Selecionar keyfile",
        )
        if caminho:
            self.var_keyfile.set(caminho)

    def _inicializar_bloqueio_existente(self) -> None:
        """Ativa contagem visual caso o cofre já esteja bloqueado."""
        restante = self.app.servico.tempo_restante_bloqueio()
        if restante > 0:
            self._iniciar_contagem(restante, "Bloqueio ativo.")

    def _executar_atalho_enter(self, _: tk.Event) -> None:
        """Aciona login ao pressionar Enter quando possível."""
        if self._botao_login.instate(["disabled"]):
            return
        self._tentar_login()

    def _tentar_login(self) -> None:
        """Executa autenticação, atraso progressivo e migração automática se necessário."""
        senha = self.var_senha.get()
        caminho_keyfile = self.var_keyfile.get().strip() or None

        if not senha:
            messagebox.showwarning("Campo obrigatório", "Informe a senha mestra.")
            return

        if self._resumo["usa_keyfile"] and not caminho_keyfile:
            messagebox.showwarning("Keyfile obrigatório", "Selecione o keyfile para continuar.")
            return

        try:
            resultado = self.app.servico.tentar_login(
                senha,
                caminho_keyfile=caminho_keyfile,
            )
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha no processo de login: {exc}")
            return
        finally:
            self.var_senha.set("")

        if resultado.sucesso:
            self._cancelar_contagem()
            if resultado.mensagem != "Login realizado com sucesso.":
                messagebox.showinfo("Proteção atualizada", resultado.mensagem)
            self.app.mostrar_tela_principal()
            return

        self._label_status.configure(text=resultado.mensagem)

        if resultado.bloqueio_restante > 0:
            self._iniciar_contagem(resultado.bloqueio_restante, "Bloqueio ativo.")
            return

        if resultado.atraso_segundos > 0:
            self._iniciar_contagem(resultado.atraso_segundos, "Atraso progressivo.")

    def _iniciar_contagem(self, segundos: int, prefixo: str) -> None:
        """Desabilita login e atualiza contador regressivo na interface."""
        self._cancelar_contagem()
        self._segundos_restantes = max(0, int(segundos))
        self._prefixo_contagem = prefixo
        self._definir_estado_controles("disabled")
        self._atualizar_contagem()

    def _atualizar_contagem(self) -> None:
        """Atualiza rótulo de tempo restante até liberar nova tentativa."""
        if self._segundos_restantes <= 0:
            self._definir_estado_controles("normal")
            self._label_status.configure(text="Nova tentativa liberada.")
            self._timer_id = None
            self._entrada_senha.focus_set()
            return

        self._label_status.configure(
            text=f"{self._prefixo_contagem} Aguarde {self._segundos_restantes} segundo(s)."
        )
        self._segundos_restantes -= 1
        self._timer_id = self.after(1000, self._atualizar_contagem)

    def _definir_estado_controles(self, estado: str) -> None:
        """Aplica estado uniforme aos controles temporariamente bloqueados."""
        for controle in self._controles_temporizados:
            if isinstance(controle, ttk.Button):
                controle.state(["!disabled"] if estado == "normal" else ["disabled"])
            else:
                controle.configure(state=estado)

    def _cancelar_contagem(self) -> None:
        """Cancela temporizador ativo quando necessário."""
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None
        self._segundos_restantes = 0

    def destroy(self) -> None:
        """Garante limpeza de timer ao destruir frame de login."""
        self._cancelar_contagem()
        super().destroy()


class TelaPrincipal(ttk.Frame):
    """Área principal para gerenciamento completo das credenciais."""

    def __init__(self, parent: ttk.Frame, app: AplicacaoCofre) -> None:
        """Constrói layout principal com busca, tabela, painel de proteção e ações."""
        super().__init__(parent, style="App.TFrame")
        self.app = app
        self.var_busca = tk.StringVar()
        self._token_clipboard = ""
        self._conteudo_clipboard = ""
        self._montar_interface()
        self._atualizar_painel_seguranca()
        self._carregar_credenciais()

    def _montar_interface(self) -> None:
        """Renderiza controles da tela principal do cofre."""
        cabecalho = ttk.Frame(self, style="App.TFrame")
        cabecalho.pack(fill="x", pady=(8, 12))

        ttk.Label(cabecalho, text="COFRE LOCAL", style="Badge.TLabel").pack(anchor="w", pady=(0, 10))
        ttk.Label(cabecalho, text="Cofre de Senhas Seguro", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(
            cabecalho,
            text="Gerencie suas credenciais locais.",
            style="Subtitulo.TLabel",
            wraplength=920,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        self._painel_seguranca = ttk.Frame(self, style="Painel.TFrame", padding=14)
        self._painel_seguranca.pack(fill="x", pady=(0, 12))

        self._label_resumo_seguranca = ttk.Label(
            self._painel_seguranca,
            text="",
            style="Destaque.TLabel",
            wraplength=980,
            justify="left",
        )
        self._label_resumo_seguranca.pack(anchor="w")

        barra_controles = ttk.Frame(self, style="Card.TFrame", padding=14)
        barra_controles.pack(fill="x", pady=(2, 8))

        linha_busca = ttk.Frame(barra_controles, style="Card.TFrame")
        linha_busca.pack(fill="x", pady=(0, 10))
        linha_busca.columnconfigure(1, weight=1)

        ttk.Label(linha_busca, text="Buscar serviço", style="CampoCard.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
        )
        entrada_busca = ttk.Entry(
            linha_busca,
            textvariable=self.var_busca,
            width=30,
            font=("Segoe UI", 10),
        )
        entrada_busca.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        entrada_busca.bind("<KeyRelease>", lambda _: self._carregar_credenciais())

        grade_acoes = ttk.Frame(barra_controles, style="Card.TFrame")
        grade_acoes.pack(fill="x")
        configurar_colunas_expansiveis(grade_acoes, 5, "acoes_principais")

        ttk.Button(
            grade_acoes,
            text="Nova credencial",
            style="Primario.TButton",
            command=self._nova_credencial,
        ).grid(row=0, column=0, sticky="ew", padx=4, pady=4)
        ttk.Button(
            grade_acoes,
            text="Editar",
            style="Secundario.TButton",
            command=self._editar_credencial,
        ).grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        ttk.Button(
            grade_acoes,
            text="Excluir",
            style="Secundario.TButton",
            command=self._excluir_credencial,
        ).grid(row=0, column=2, sticky="ew", padx=4, pady=4)
        ttk.Button(
            grade_acoes,
            text="Revelar senha",
            style="Secundario.TButton",
            command=self._revelar_senha,
        ).grid(row=0, column=3, sticky="ew", padx=4, pady=4)
        ttk.Button(
            grade_acoes,
            text="Copiar senha",
            style="Secundario.TButton",
            command=self._copiar_senha,
        ).grid(row=0, column=4, sticky="ew", padx=4, pady=4)
        ttk.Button(
            grade_acoes,
            text="Fortalecer cofre",
            style="Secundario.TButton",
            command=self._fortalecer_cofre,
        ).grid(row=1, column=0, sticky="ew", padx=4, pady=4)
        ttk.Button(
            grade_acoes,
            text="Exportar",
            style="Secundario.TButton",
            command=self._exportar_credenciais,
        ).grid(row=1, column=1, sticky="ew", padx=4, pady=4)
        ttk.Button(
            grade_acoes,
            text="Importar",
            style="Secundario.TButton",
            command=self._importar_credenciais,
        ).grid(row=1, column=2, sticky="ew", padx=4, pady=4)
        ttk.Button(
            grade_acoes,
            text="Atualizar",
            style="Secundario.TButton",
            command=self._atualizar_tela,
        ).grid(row=1, column=3, sticky="ew", padx=4, pady=4)
        ttk.Button(
            grade_acoes,
            text="Sair",
            style="Secundario.TButton",
            command=self._sair,
        ).grid(row=1, column=4, sticky="ew", padx=4, pady=4)

        tabela_frame = ttk.Frame(self, style="Card.TFrame", padding=10)
        tabela_frame.pack(fill="both", expand=True, pady=(6, 8))

        colunas = ("servico", "login", "observacao", "atualizado_em")
        self._tabela = ttk.Treeview(
            tabela_frame,
            columns=colunas,
            show="headings",
            selectmode="browse",
        )

        self._tabela.heading("servico", text="Serviço")
        self._tabela.heading("login", text="Usuário/E-mail")
        self._tabela.heading("observacao", text="Observação")
        self._tabela.heading("atualizado_em", text="Atualizado em")

        self._tabela.column("servico", width=220, anchor="w")
        self._tabela.column("login", width=250, anchor="w")
        self._tabela.column("observacao", width=360, anchor="w")
        self._tabela.column("atualizado_em", width=180, anchor="center")

        barra_vertical = ttk.Scrollbar(tabela_frame, orient="vertical", command=self._tabela.yview)
        self._tabela.configure(yscrollcommand=barra_vertical.set)

        self._tabela.pack(side="left", fill="both", expand=True)
        barra_vertical.pack(side="right", fill="y")

        self._tabela.bind("<Double-1>", lambda _: self._editar_credencial())

    def _atualizar_painel_seguranca(self) -> None:
        """Atualiza o resumo visual das defesas ativas do cofre."""
        resumo = self.app.servico.obter_resumo_seguranca()
        texto = (
            f"Proteção ativa: {resumo['algoritmo_kdf']} + {resumo['algoritmo_cifra']}  |  "
            f"Formato: {resumo['status_formato']}  |  "
            f"Keyfile: {'Ativado' if resumo['usa_keyfile'] else 'Desativado'}"
        )
        self._label_resumo_seguranca.configure(text=texto)

    def _atualizar_tela(self) -> None:
        """Recarrega credenciais e resumo de segurança da interface principal."""
        self._atualizar_painel_seguranca()
        self._carregar_credenciais()

    def _carregar_credenciais(self) -> None:
        """Atualiza tabela com credenciais filtradas pelo texto de busca."""
        try:
            credenciais = self.app.servico.listar_credenciais(self.var_busca.get())
        except PermissionError:
            messagebox.showwarning("Sessão", "Sua sessão foi encerrada. Faça login novamente.")
            self.app.mostrar_tela_login()
            return
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao carregar credenciais: {exc}")
            return

        for item in self._tabela.get_children():
            self._tabela.delete(item)

        for credencial in credenciais:
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

    def _id_selecionado(self) -> str | None:
        """Retorna o identificador da linha selecionada na tabela."""
        selecao = self._tabela.selection()
        if not selecao:
            return None
        return selecao[0]

    def _nova_credencial(self) -> None:
        """Abre diálogo para cadastro de nova credencial."""
        dialogo = DialogoCredencial(self, self.app.servico, modo="nova")
        self.wait_window(dialogo)
        if dialogo.salvou:
            self._carregar_credenciais()

    def _editar_credencial(self) -> None:
        """Abre diálogo de edição para a credencial selecionada."""
        credencial_id = self._id_selecionado()
        if not credencial_id:
            messagebox.showinfo("Seleção", "Selecione uma credencial para editar.")
            return

        credencial = self.app.servico.obter_credencial(credencial_id, incluir_senha=True)
        if credencial is None:
            messagebox.showerror("Erro", "Credencial não encontrada.")
            self._carregar_credenciais()
            return

        dialogo = DialogoCredencial(
            self,
            self.app.servico,
            modo="edicao",
            credencial=credencial,
        )
        self.wait_window(dialogo)
        if dialogo.salvou:
            self._carregar_credenciais()

    def _excluir_credencial(self) -> None:
        """Exclui credencial selecionada após confirmação explícita."""
        credencial_id = self._id_selecionado()
        if not credencial_id:
            messagebox.showinfo("Seleção", "Selecione uma credencial para excluir.")
            return

        credencial = self.app.servico.obter_credencial(credencial_id)
        if credencial is None:
            messagebox.showerror("Erro", "Credencial não encontrada.")
            self._carregar_credenciais()
            return

        confirmar = messagebox.askyesno(
            "Confirmação",
            (
                "Deseja realmente excluir esta credencial?\n\n"
                f"Serviço: {credencial['servico']}\n"
                f"Usuário/E-mail: {credencial['login']}"
            ),
            icon="warning",
        )
        if not confirmar:
            return

        try:
            self.app.servico.excluir_credencial(credencial_id)
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível excluir a credencial: {exc}")
            return

        messagebox.showinfo("Sucesso", "Credencial excluída com sucesso.")
        self._carregar_credenciais()

    def _revelar_senha(self) -> None:
        """Revela senha da credencial selecionada após reautenticação."""
        credencial_id = self._id_selecionado()
        if not credencial_id:
            messagebox.showinfo("Seleção", "Selecione uma credencial para revelar a senha.")
            return

        senha_mestra = self._pedir_senha_mestra_acao()
        if senha_mestra is None:
            return

        try:
            senha = self.app.servico.revelar_senha(credencial_id, senha_mestra)
        except PermissionError:
            messagebox.showerror("Autenticação", "Senha mestra incorreta.")
            return
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível revelar a senha: {exc}")
            return

        messagebox.showinfo("Senha da credencial", f"Senha: {senha}")

    def _copiar_senha(self) -> None:
        """Copia senha para a área de transferência após reautenticação."""
        credencial_id = self._id_selecionado()
        if not credencial_id:
            messagebox.showinfo("Seleção", "Selecione uma credencial para copiar a senha.")
            return

        senha_mestra = self._pedir_senha_mestra_acao()
        if senha_mestra is None:
            return

        try:
            senha = self.app.servico.revelar_senha(credencial_id, senha_mestra)
        except PermissionError:
            messagebox.showerror("Autenticação", "Senha mestra incorreta.")
            return
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível copiar a senha: {exc}")
            return

        self.clipboard_clear()
        self.clipboard_append(senha)
        self.update_idletasks()

        token = secrets.token_hex(8)
        self._token_clipboard = token
        self._conteudo_clipboard = senha
        self.after(20000, lambda valor=token: self._limpar_clipboard_se_necessario(valor))

        messagebox.showinfo(
            "Senha copiada",
            "Senha copiada para a área de transferência por 20 segundos.",
        )

    def _limpar_clipboard_se_necessario(self, token: str) -> None:
        """Limpa o clipboard se ainda contiver dado copiado por esta tela."""
        if token != self._token_clipboard:
            return
        try:
            conteudo_atual = self.clipboard_get()
        except tk.TclError:
            return
        if conteudo_atual != self._conteudo_clipboard:
            return
        self.clipboard_clear()
        self.update_idletasks()
        self._conteudo_clipboard = ""
        self._token_clipboard = ""

    def _pedir_senha_mestra_acao(self) -> str | None:
        """Solicita senha mestra para confirmação de ação sensível."""
        senha_mestra = simpledialog.askstring(
            "Confirmação de segurança",
            "Digite a senha mestra para continuar:",
            show="*",
            parent=self,
        )
        if senha_mestra is None:
            return None
        if not senha_mestra:
            messagebox.showwarning("Validação", "A senha mestra não pode ficar vazia.")
            return None
        return senha_mestra

    def _fortalecer_cofre(self) -> None:
        """Abre diálogo para alterar senha mestra e keyfile do cofre."""
        dialogo = DialogoSeguranca(self, self.app.servico)
        self.wait_window(dialogo)
        if dialogo.salvou:
            self._atualizar_tela()

    def _exportar_credenciais(self) -> None:
        """Exporta as credenciais atuais para um pacote criptografado por senha própria."""
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Exportar credenciais",
            defaultextension=".json",
            initialfile="backup_cofre_seguro.json",
        )
        if not caminho:
            return

        senha_exportacao = simpledialog.askstring(
            "Senha de exportação",
            (
                "Defina uma senha forte para proteger o arquivo exportado.\n"
                "Ela será necessária para importar esse backup depois."
            ),
            show="*",
            parent=self,
        )
        if senha_exportacao is None:
            return

        confirmacao = simpledialog.askstring(
            "Confirmar senha de exportação",
            "Digite novamente a senha de exportação:",
            show="*",
            parent=self,
        )
        if confirmacao is None:
            return

        if senha_exportacao != confirmacao:
            messagebox.showerror(
                "Validação",
                "A senha de exportação e a confirmação não coincidem.",
                parent=self,
            )
            return

        try:
            resultado = self.app.servico.exportar_credenciais(caminho, senha_exportacao)
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível exportar as credenciais: {exc}")
            return

        messagebox.showinfo(
            "Exportação concluída",
            (
                f"{resultado['quantidade']} credencial(is) exportada(s) com sucesso.\n\n"
                f"Arquivo: {resultado['arquivo']}"
            ),
        )

    def _importar_credenciais(self) -> None:
        """Importa credenciais de um pacote criptografado para o cofre atual."""
        caminho = filedialog.askopenfilename(
            parent=self,
            title="Importar credenciais",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        senha_importacao = simpledialog.askstring(
            "Senha de importação",
            "Digite a senha definida no arquivo exportado:",
            show="*",
            parent=self,
        )
        if senha_importacao is None:
            return

        sobrescrever = messagebox.askyesno(
            "Duplicadas",
            (
                "Se uma credencial com o mesmo Serviço e Usuário/E-mail já existir,\n"
                "deseja sobrescrever os dados atuais com os dados importados?"
            ),
            parent=self,
        )

        try:
            resultado = self.app.servico.importar_credenciais(
                caminho,
                senha_importacao,
                sobrescrever_duplicadas=sobrescrever,
            )
        except PermissionError:
            messagebox.showerror("Autenticação", "Senha de importação incorreta.")
            return
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível importar as credenciais: {exc}")
            return

        self._atualizar_tela()
        messagebox.showinfo(
            "Importação concluída",
            (
                f"Inseridas: {resultado['inseridas']}\n"
                f"Atualizadas: {resultado['atualizadas']}\n"
                f"Ignoradas: {resultado['ignoradas']}"
            ),
        )

    def _sair(self) -> None:
        """Encerra sessão atual e retorna para tela de login."""
        self.app.servico.encerrar_sessao()
        self.app.mostrar_tela_login()

    @staticmethod
    def _formatar_data(valor_iso: str) -> str:
        """Formata data ISO para exibição na tabela."""
        try:
            return datetime.fromisoformat(valor_iso).strftime("%d/%m/%Y %H:%M")
        except Exception:
            return valor_iso


class JanelaModalBase(tk.Toplevel):
    """Base para diálogos modais com ativação segura do grab no Tkinter."""

    def __init__(self, parent: tk.Widget) -> None:
        """Cria janela modal inicialmente oculta até ficar visível."""
        super().__init__(parent)
        self.withdraw()
        self.transient(parent)

    def ativar_modalidade(self) -> None:
        """Mostra a janela e aplica a captura modal quando estiver visível."""
        self.deiconify()
        self.after(0, self._aplicar_modalidade_segura)

    def _aplicar_modalidade_segura(self) -> None:
        """Aplica comportamento modal apenas quando a janela está visível."""
        if not self.winfo_exists():
            return
        if not self.winfo_viewable():
            self.after(20, self._aplicar_modalidade_segura)
            return
        try:
            self.grab_set()
            self.focus_force()
        except tk.TclError:
            self.after(20, self._aplicar_modalidade_segura)


class DialogoCredencial(JanelaModalBase):
    """Diálogo de cadastro e edição de credenciais do cofre."""

    def __init__(
        self,
        parent: tk.Widget,
        servico: ServicoCofre,
        modo: str,
        credencial: dict[str, str] | None = None,
    ) -> None:
        """Cria janela modal para edição de dados de uma credencial."""
        super().__init__(parent)
        self.servico = servico
        self.modo = modo
        self.credencial = credencial or {}
        self.salvou = False

        self.var_servico = tk.StringVar(value=self.credencial.get("servico", ""))
        self.var_login = tk.StringVar(value=self.credencial.get("login", ""))
        self.var_senha = tk.StringVar(value=self.credencial.get("senha", ""))
        self.var_tamanho = tk.IntVar(value=16)
        self._senha_visivel = False

        self.title("Nova credencial" if modo == "nova" else "Editar credencial")
        self.geometry("580x450")
        self.minsize(560, 430)
        self.configure(background="#f6f1e8")
        self._montar_interface()
        self.ativar_modalidade()

    def _montar_interface(self) -> None:
        """Renderiza formulário de credencial e botões de ação."""
        frame = ttk.Frame(self, padding=18, style="Card.TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Credencial", style="TituloDialogo.TLabel").grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 14),
        )

        ttk.Label(frame, text="Serviço", style="CampoCard.TLabel").grid(
            row=1,
            column=0,
            sticky="w",
            pady=(0, 8),
            padx=(0, 12),
        )
        ttk.Entry(frame, textvariable=self.var_servico, width=42, font=("Segoe UI", 10)).grid(
            row=1,
            column=1,
            columnspan=2,
            sticky="we",
            pady=(0, 8),
        )

        ttk.Label(frame, text="Usuário/E-mail", style="CampoCard.TLabel").grid(
            row=2,
            column=0,
            sticky="w",
            pady=(0, 8),
            padx=(0, 12),
        )
        ttk.Entry(frame, textvariable=self.var_login, width=42, font=("Segoe UI", 10)).grid(
            row=2,
            column=1,
            columnspan=2,
            sticky="we",
            pady=(0, 8),
        )

        ttk.Label(frame, text="Senha", style="CampoCard.TLabel").grid(
            row=3,
            column=0,
            sticky="w",
            pady=(0, 8),
            padx=(0, 12),
        )
        self._entrada_senha = ttk.Entry(
            frame,
            textvariable=self.var_senha,
            show="*",
            width=34,
            font=("Segoe UI", 10),
        )
        self._entrada_senha.grid(row=3, column=1, sticky="we", pady=(0, 8))

        self._botao_visibilidade = ttk.Button(
            frame,
            text="Mostrar",
            style="Secundario.TButton",
            command=self._alternar_visibilidade_senha,
        )
        self._botao_visibilidade.grid(row=3, column=2, sticky="w", pady=(0, 8), padx=(8, 0))

        ttk.Label(frame, text="Observação", style="CampoCard.TLabel").grid(
            row=4,
            column=0,
            sticky="nw",
            pady=(0, 8),
            padx=(0, 12),
        )
        self._campo_observacao = tk.Text(
            frame,
            width=40,
            height=5,
            font=("Segoe UI", 10),
            bd=1,
            relief="solid",
        )
        self._campo_observacao.grid(row=4, column=1, columnspan=2, sticky="we", pady=(0, 8))
        if self.credencial.get("observacao"):
            self._campo_observacao.insert("1.0", self.credencial["observacao"])

        gerador = ttk.LabelFrame(frame, text="Gerador de senha forte", padding=10)
        gerador.grid(row=5, column=0, columnspan=3, sticky="we", pady=(10, 14))

        ttk.Label(gerador, text="Comprimento", style="TextoCard.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 8),
        )
        ttk.Spinbox(
            gerador,
            from_=8,
            to=64,
            textvariable=self.var_tamanho,
            width=8,
            font=("Segoe UI", 10),
        ).grid(row=0, column=1, sticky="w", padx=(0, 12))

        ttk.Button(
            gerador,
            text="Gerar senha",
            style="Secundario.TButton",
            command=self._gerar_senha,
        ).grid(row=0, column=2, sticky="w")

        acoes = ttk.Frame(frame, style="Card.TFrame")
        acoes.grid(row=6, column=0, columnspan=3, sticky="ew")
        configurar_colunas_expansiveis(acoes, 2, "acoes_credencial")

        ttk.Button(
            acoes,
            text="Salvar",
            style="Primario.TButton",
            command=self._salvar,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            acoes,
            text="Cancelar",
            style="Secundario.TButton",
            command=self.destroy,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        frame.columnconfigure(1, weight=1)
        self.bind("<Return>", self._atalho_salvar)

    def _atalho_salvar(self, _: tk.Event) -> None:
        """Salva dados usando atalho Enter no diálogo."""
        self._salvar()

    def _gerar_senha(self) -> None:
        """Gera senha forte com secrets e aplica no campo de senha."""
        try:
            tamanho = int(self.var_tamanho.get())
            senha = self.servico.gerar_senha(tamanho)
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível gerar a senha: {exc}", parent=self)
            return

        self.var_senha.set(senha)
        self._definir_visibilidade_senha(True)

    def _alternar_visibilidade_senha(self) -> None:
        """Alterna a visualização da senha no formulário da credencial."""
        self._definir_visibilidade_senha(not self._senha_visivel)

    def _definir_visibilidade_senha(self, visivel: bool) -> None:
        """Aplica estado de visibilidade da senha no campo do formulário."""
        self._senha_visivel = visivel
        self._entrada_senha.configure(show="" if visivel else "*")
        self._botao_visibilidade.configure(text="Ocultar" if visivel else "Mostrar")

    def _salvar(self) -> None:
        """Valida formulário e persiste nova credencial ou edição."""
        servico = self.var_servico.get().strip()
        login = self.var_login.get().strip()
        senha = self.var_senha.get()
        observacao = self._campo_observacao.get("1.0", "end").strip()

        if not servico or not login or not senha:
            messagebox.showwarning(
                "Campos obrigatórios",
                "Preencha Serviço, Usuário/E-mail e Senha.",
                parent=self,
            )
            return

        try:
            if self.modo == "nova":
                self.servico.adicionar_credencial(servico, login, senha, observacao)
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

        self.salvou = True
        self.destroy()


class DialogoSeguranca(JanelaModalBase):
    """Diálogo para fortalecer o cofre com nova senha mestra e keyfile opcional."""

    def __init__(self, parent: tk.Widget, servico: ServicoCofre) -> None:
        """Cria a janela modal de reconfiguração de segurança do cofre."""
        super().__init__(parent)
        self.servico = servico
        self.salvou = False
        self._resumo = self.servico.obter_resumo_seguranca()

        self.var_senha_atual = tk.StringVar()
        self.var_nova_senha = tk.StringVar()
        self.var_confirmacao = tk.StringVar()
        self.var_usar_keyfile = tk.BooleanVar(value=bool(self._resumo["usa_keyfile"]))
        self.var_keyfile = tk.StringVar()

        self.title("Fortalecer cofre")
        self.geometry("700x430")
        self.minsize(640, 410)
        self.configure(background="#f6f1e8")
        self._montar_interface()
        self._atualizar_estado_keyfile()
        self.ativar_modalidade()

    def _montar_interface(self) -> None:
        """Renderiza o formulário de reconfiguração de segurança."""
        frame = ttk.Frame(self, padding=18, style="Card.TFrame")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="AJUSTE DE SEGURANÇA", style="Badge.TLabel").grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(0, 10),
        )
        ttk.Label(frame, text="Fortalecer cofre", style="TituloDialogo.TLabel").grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(0, 10),
        )
        ttk.Label(
            frame,
            text="Troque a senha mestra e ajuste o uso de keyfile quando precisar.",
            style="SubtituloCard.TLabel",
            wraplength=620,
            justify="left",
        ).grid(row=2, column=0, columnspan=4, sticky="w", pady=(0, 16))

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
        ).grid(row=3, column=1, columnspan=3, sticky="we", pady=(0, 10))

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

        ttk.Checkbutton(
            frame,
            text="Manter cofre protegido com keyfile",
            variable=self.var_usar_keyfile,
            style="Card.TCheckbutton",
            command=self._atualizar_estado_keyfile,
        ).grid(row=6, column=0, columnspan=4, sticky="w", pady=(8, 10))

        ttk.Label(frame, text="Novo keyfile", style="CampoCard.TLabel").grid(
            row=7,
            column=0,
            sticky="w",
            pady=(0, 10),
            padx=(0, 12),
        )
        self._entrada_keyfile = ttk.Entry(
            frame,
            textvariable=self.var_keyfile,
            width=42,
            font=("Segoe UI", 10),
        )
        self._entrada_keyfile.grid(row=7, column=1, sticky="we", pady=(0, 10))

        self._botao_keyfile = ttk.Button(
            frame,
            text="Selecionar",
            style="Secundario.TButton",
            command=self._selecionar_keyfile,
        )
        self._botao_keyfile.grid(row=7, column=2, sticky="w", padx=(8, 8), pady=(0, 10))

        self._botao_gerar_keyfile = ttk.Button(
            frame,
            text="Gerar keyfile",
            style="Secundario.TButton",
            command=self._gerar_keyfile,
        )
        self._botao_gerar_keyfile.grid(row=7, column=3, sticky="w", pady=(0, 10))

        acoes = ttk.Frame(frame, style="Card.TFrame")
        acoes.grid(row=8, column=0, columnspan=4, sticky="ew", pady=(18, 0))
        configurar_colunas_expansiveis(acoes, 2, "acoes_seguranca")

        ttk.Button(
            acoes,
            text="Aplicar",
            style="Primario.TButton",
            command=self._aplicar,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ttk.Button(
            acoes,
            text="Cancelar",
            style="Secundario.TButton",
            command=self.destroy,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        frame.columnconfigure(1, weight=1)

    def _atualizar_estado_keyfile(self) -> None:
        """Habilita os controles de keyfile quando essa proteção estiver marcada."""
        estado = "normal" if self.var_usar_keyfile.get() else "disabled"
        self._entrada_keyfile.configure(state=estado)
        self._botao_keyfile.state(["!disabled"] if estado == "normal" else ["disabled"])
        self._botao_gerar_keyfile.state(["!disabled"] if estado == "normal" else ["disabled"])

    def _selecionar_keyfile(self) -> None:
        """Seleciona um keyfile existente para ativar ou substituir a proteção."""
        caminho = filedialog.askopenfilename(
            parent=self,
            title="Selecionar keyfile",
        )
        if caminho:
            self.var_keyfile.set(caminho)

    def _gerar_keyfile(self) -> None:
        """Gera um novo keyfile em disco para reforçar o cofre atual."""
        caminho = filedialog.asksaveasfilename(
            parent=self,
            title="Salvar keyfile",
            defaultextension=".key",
            initialfile="cofre_seguro_novo.key",
        )
        if not caminho:
            return

        try:
            self.servico.criar_keyfile(caminho)
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível gerar o keyfile: {exc}", parent=self)
            return

        self.var_keyfile.set(caminho)
        messagebox.showinfo(
            "Keyfile criado",
            "Novo keyfile criado com sucesso. Guarde esse arquivo antes de aplicar a alteração.",
            parent=self,
        )

    def _aplicar(self) -> None:
        """Valida o formulário e aplica a nova configuração de segurança do cofre."""
        senha_atual = self.var_senha_atual.get()
        nova_senha = self.var_nova_senha.get()
        confirmacao = self.var_confirmacao.get()
        usar_keyfile = self.var_usar_keyfile.get()
        caminho_keyfile = self.var_keyfile.get().strip() or None

        if not senha_atual:
            messagebox.showwarning(
                "Campo obrigatório",
                "Informe a senha mestra atual para autorizar a alteração.",
                parent=self,
            )
            return

        if nova_senha or confirmacao:
            if nova_senha != confirmacao:
                messagebox.showerror(
                    "Validação",
                    "A nova senha mestra e a confirmação não coincidem.",
                    parent=self,
                )
                return

            senha_valida, mensagem = validar_forca_senha_mestra(nova_senha)
            if not senha_valida:
                messagebox.showerror("Senha mestra fraca", mensagem, parent=self)
                return

        if not nova_senha and usar_keyfile == bool(self._resumo["usa_keyfile"]) and not caminho_keyfile:
            messagebox.showinfo(
                "Sem alterações",
                "Nenhuma alteração foi informada para aplicar.",
                parent=self,
            )
            return

        if usar_keyfile and not self._resumo["usa_keyfile"] and not caminho_keyfile:
            messagebox.showwarning(
                "Keyfile obrigatório",
                "Selecione ou gere um keyfile para ativar essa proteção.",
                parent=self,
            )
            return

        try:
            mensagem = self.servico.reconfigurar_seguranca(
                senha_mestra_atual=senha_atual,
                nova_senha_mestra=nova_senha or None,
                usar_keyfile=usar_keyfile,
                caminho_keyfile=caminho_keyfile,
            )
        except PermissionError:
            messagebox.showerror("Autenticação", "Senha mestra atual incorreta.", parent=self)
            return
        except Exception as exc:
            messagebox.showerror("Erro", f"Não foi possível aplicar a alteração: {exc}", parent=self)
            return

        self.salvou = True
        messagebox.showinfo("Segurança atualizada", mensagem, parent=self)
        self.destroy()


def iniciar_interface(servico: ServicoCofre) -> None:
    """Inicia o loop principal da interface Tkinter do cofre."""
    app = AplicacaoCofre(servico)
    app.mainloop()
