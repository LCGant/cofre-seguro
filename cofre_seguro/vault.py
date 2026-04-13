# Permite usar recursos de versões futuras do Python nesta versão
from __future__ import annotations

# Importa a biblioteca para trabalhar com dados no formato JSON (formato de texto estruturado)
import json
# Importa funções matemáticas como arredondamento para cima
import math
# Importa a biblioteca para gerar valores aleatórios seguros (usados como identificadores únicos)
import secrets
# Importa a biblioteca para trabalhar com tempo (medir segundos, etc.)
import time
# Importa o decorador dataclass, que cria classes simples de dados automaticamente
from dataclasses import dataclass
# Importa ferramentas para trabalhar com datas e fusos horários
from datetime import datetime, timezone
# Importa a classe Path, que facilita trabalhar com caminhos de arquivos e pastas
from pathlib import Path
# Importa o tipo Any, que significa "qualquer tipo de dado" (usado em dicas de tipo)
from typing import Any

# Importa várias funções de segurança do nosso próprio módulo (arquivo security.py)
# Essas funções cuidam de criptografia, verificação de senha, geração de chaves, etc.
from .security import (
    VERSAO_COFRE_ATUAL,              # Número da versão mais recente do formato do cofre
    criar_registro_senha_mestra,     # Cria o registro seguro a partir da senha do usuário
    criptografar_objeto,             # Transforma dados legíveis em dados embaralhados (criptografados)
    descriptografar_objeto,          # Transforma dados embaralhados de volta em dados legíveis
    descriptografar_objeto_legado,   # Faz o mesmo, mas para o formato antigo do cofre
    gerar_chave_criptografia,        # Gera a chave usada para embaralhar/desembaralhar dados
    gerar_chave_fernet_legado,       # Gera chave no formato antigo (Fernet)
    gerar_conteudo_keyfile,          # Gera conteúdo aleatório para um arquivo-chave (keyfile)
    gerar_senha_forte,               # Gera uma senha aleatória e segura
    normalizar_segredo_keyfile,      # Padroniza o conteúdo do keyfile para uso interno
    validar_forca_senha_mestra,      # Verifica se a senha mestra é forte o suficiente
    verificar_senha_mestra,          # Confere se a senha mestra digitada está correta
)
# Importa o gerenciador que cuida de salvar e carregar o arquivo do cofre no disco
from .storage import GerenciadorArquivoCofre


# Lista com todos os tipos de item que o cofre aceita guardar
# Cada tipo tem campos diferentes, mas todos ficam criptografados igualmente
TIPOS_SUPORTADOS = ("senha", "cartao", "documento", "nota", "wifi", "licenca")

# Dicionário que diz quais campos são "sensíveis" (precisam reautenticação para exibir)
# Por exemplo, o CVV do cartão e a chave de licença são campos que não aparecem por padrão
CAMPOS_SENSIVEIS_POR_TIPO: dict[str, tuple[str, ...]] = {
    "senha": ("senha",),                # Só a senha é sensível
    "cartao": ("numero", "cvv"),        # Número do cartão e CVV são sensíveis
    "documento": ("numero",),           # Número do documento (RG, CPF, etc) é sensível
    "nota": ("conteudo",),              # Todo o conteúdo da nota é sensível
    "wifi": ("senha",),                 # Só a senha do WiFi é sensível
    "licenca": ("chave",),              # A chave da licença é sensível
}

# Dicionário que diz quais campos são obrigatórios em cada tipo de item
# Se o usuário deixar algum desses campos vazios, o cadastro é rejeitado
CAMPOS_OBRIGATORIOS_POR_TIPO: dict[str, tuple[str, ...]] = {
    "senha": ("titulo", "login", "senha"),
    "cartao": ("titulo", "numero", "validade"),
    "documento": ("titulo", "tipo_documento", "numero"),
    "nota": ("titulo", "conteudo"),
    "wifi": ("titulo", "senha"),
    "licenca": ("titulo", "chave"),
}

# Dicionário com todos os campos editáveis de cada tipo (usado para formulários e validação)
# Inclui tanto os obrigatórios quanto os opcionais, mas NÃO os metadados (id, datas, tipo)
CAMPOS_EDITAVEIS_POR_TIPO: dict[str, tuple[str, ...]] = {
    "senha": ("titulo", "login", "senha", "observacao"),
    "cartao": ("titulo", "numero", "titular", "validade", "cvv", "bandeira", "cor", "observacao"),
    "documento": (
        "titulo", "tipo_documento", "numero", "nome_titular",
        "orgao_emissor", "data_emissao", "validade", "observacao",
    ),
    "nota": ("titulo", "conteudo", "observacao"),
    "wifi": ("titulo", "senha", "tipo_seguranca", "observacao"),
    "licenca": (
        "titulo", "chave", "email_licenca", "data_compra",
        "validade", "observacao",
    ),
}


# @dataclass é um atalho do Python que cria automaticamente o __init__ e outros métodos
# slots=True faz a classe usar menos memória
@dataclass(slots=True)
class ResultadoLogin:
    """Representa o resultado da tentativa de autenticação no cofre."""

    # Indica se o login deu certo (True) ou errado (False)
    sucesso: bool
    # Mensagem explicando o que aconteceu (ex: "Login realizado com sucesso")
    mensagem: str
    # Quantos segundos o usuário deve esperar antes de tentar de novo (começa em 0)
    atraso_segundos: int = 0
    # Quantos segundos restam de bloqueio total, se o cofre estiver bloqueado (começa em 0)
    bloqueio_restante: int = 0


# Define a classe principal que gerencia todas as operações do cofre de senhas
class ServicoCofre:
    """Implementa regras do cofre, autenticação e operações de itens guardados."""

    # Configurações padrão de segurança contra tentativas de invasão por força bruta
    POLITICA_PADRAO = {
        "max_tentativas": 5,            # Máximo de tentativas erradas antes de bloquear
        "atraso_max_segundos": 8,       # Maior tempo de espera entre tentativas erradas
        "bloqueio_base_segundos": 30,   # Tempo base de bloqueio após muitas falhas
        "bloqueio_max_segundos": 300,   # Tempo máximo de bloqueio (5 minutos)
    }

    # Método especial que é chamado automaticamente quando criamos um novo ServicoCofre
    # Ele prepara o objeto com tudo que vai precisar para funcionar
    def __init__(self, armazenamento: GerenciadorArquivoCofre) -> None:
        """Inicializa o serviço com o gerenciador de persistência local."""
        # Guarda o gerenciador que sabe ler e gravar o arquivo do cofre
        self._armazenamento = armazenamento
        # Cache do conteúdo do arquivo de cofre — evita reler o JSON do disco
        # toda vez que a UI consulta resumo de segurança, status do keyfile, etc.
        # Invalidado em todas as escritas (_salvar_arquivo) e ao trocar de cofre.
        self._cache_arquivo: dict[str, Any] | None = None
        # Chave de criptografia da sessão atual (None = ninguém fez login ainda)
        self._chave_sessao: bytes | None = None
        # Dados do cofre descriptografados na memória (None = não carregado ainda)
        self._dados_cofre: dict[str, Any] | None = None
        # Segredo do keyfile usado na sessão atual (None = sem keyfile)
        self._segredo_keyfile_sessao: bytes | None = None

    # Verifica se já existe um arquivo de cofre salvo no computador
    def existe_cofre(self) -> bool:
        """Indica se já existe um cofre inicializado no disco."""
        return self._armazenamento.existe_cofre()

    # Verifica se o cofre exige um arquivo-chave (keyfile) além da senha
    def cofre_requer_keyfile(self) -> bool:
        """Informa se o cofre configurado exige keyfile para autenticação."""
        # Se não existe cofre, não precisa de keyfile
        if not self.existe_cofre():
            return False
        # Carrega os dados do arquivo do cofre
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        # Verifica dentro das configurações do KDF se o keyfile está ativado
        return bool(dados_arquivo.get("kdf", {}).get("usa_keyfile", False))

    # Retorna um resumo das configurações de segurança do cofre para mostrar na tela
    def obter_resumo_seguranca(self) -> dict[str, Any]:
        """Retorna metadados resumidos de proteção para exibição na interface."""
        # Se não existe cofre, retorna informações vazias/padrão
        if not self.existe_cofre():
            return {
                "configurado": False,
                "versao": 0,
                "algoritmo_kdf": "Não configurado",
                "algoritmo_cifra": "Não configurado",
                "usa_keyfile": False,
                "status_formato": "Sem cofre",
                "memoria_argon2_mb": 0,
            }

        # Carrega o arquivo do cofre do disco
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        # Pega as configurações de derivação de chave (KDF)
        kdf = dados_arquivo.get("kdf", {})
        # Verifica se o cofre usa o formato antigo (legado)
        formato_legado = self._arquivo_usa_formato_legado(dados_arquivo)
        # Obtém o nome do algoritmo de derivação de chave em formato amigável
        algoritmo_kdf = self._rotulo_kdf(kdf)
        # Obtém o nome do algoritmo de criptografia em formato amigável
        algoritmo_cifra = self._rotulo_cifra(dados_arquivo.get("dados_cofre_criptografados"))

        # Retorna um dicionário com todas as informações de segurança
        return {
            "configurado": True,
            "versao": int(dados_arquivo.get("versao", 1)),
            "algoritmo_kdf": algoritmo_kdf,
            "algoritmo_cifra": algoritmo_cifra,
            "usa_keyfile": bool(kdf.get("usa_keyfile", False)),
            "status_formato": "Legado" if formato_legado else "Atual",
            "memoria_argon2_mb": int(kdf.get("memory_cost", 0)) // 1024,
        }

    # Cria um novo arquivo-chave (keyfile) no caminho escolhido pelo usuário
    def criar_keyfile(self, caminho_destino: str | Path) -> Path:
        """Cria um keyfile aleatório em disco com permissão restrita quando possível."""
        # Converte o caminho em um objeto Path e resolve para caminho absoluto
        caminho = Path(caminho_destino).expanduser().resolve()
        # Cria as pastas necessárias caso não existam
        caminho.parent.mkdir(parents=True, exist_ok=True)
        # Se já existe um arquivo nesse local, não permite sobrescrever
        if caminho.exists():
            raise ValueError("Já existe um arquivo nesse caminho para o keyfile.")

        # Gera conteúdo aleatório e grava no arquivo
        caminho.write_bytes(gerar_conteudo_keyfile())
        # Tenta restringir as permissões do arquivo para que só o dono possa ler/escrever
        try:
            caminho.chmod(0o600)
        # Se o sistema não suportar essa operação (ex: Windows), ignora o erro
        except OSError:
            pass
        # Retorna o caminho completo do keyfile criado
        return caminho

    # Cria um cofre novo com senha mestra e, opcionalmente, um keyfile
    def criar_cofre(self, senha_mestra: str, caminho_keyfile: str | None = None) -> None:
        """Cria um novo cofre local com senha mestra e keyfile opcional."""
        # Se já existe um cofre, não permite criar outro no mesmo local
        if self.existe_cofre():
            raise ValueError("Já existe um cofre inicializado neste caminho.")

        # Verifica se a senha mestra é forte o suficiente
        senha_valida, mensagem = validar_forca_senha_mestra(senha_mestra)
        # Se a senha for fraca, mostra a mensagem de erro
        if not senha_valida:
            raise ValueError(mensagem)

        # Se o usuário escolheu usar keyfile, carrega o segredo dele; senão, fica sem
        segredo_keyfile = self._carregar_segredo_keyfile(caminho_keyfile) if caminho_keyfile else None
        # Cria o registro de verificação da senha mestra (hash seguro da senha)
        registro = criar_registro_senha_mestra(senha_mestra, segredo_keyfile=segredo_keyfile)
        # Gera a chave de criptografia a partir da senha e das configurações do KDF
        chave_aes = gerar_chave_criptografia(
            senha_mestra,
            registro["kdf"],
            segredo_keyfile=segredo_keyfile,
        )
        # Pega a data e hora atuais no formato ISO (padrão internacional)
        agora = self._agora_iso()
        # Cria a estrutura inicial do cofre, vazia, com a data de criação
        # "credenciais" é mantido como nome histórico do campo, mas agora guarda TODOS
        # os tipos de item (senha, cartão, documento, nota, wifi, licença)
        dados_cofre = {
            "credenciais": [],       # Lista vazia de itens (ainda não tem nenhum)
            "metadados": {
                "criado_em": agora,      # Quando o cofre foi criado
                "atualizado_em": agora,  # Quando foi a última atualização
            },
        }

        # Monta a estrutura completa do arquivo que será salvo no disco
        estrutura_arquivo = self._montar_estrutura_arquivo(
            registro=registro,
            dados_cofre=dados_cofre,
            chave_criptografia=chave_aes,
            controle_acesso={
                "falhas_consecutivas": 0,    # Nenhuma tentativa errada ainda
                "bloqueado_ate": 0.0,        # Sem bloqueio
                "bloqueios_aplicados": 0,    # Nenhum bloqueio aplicado ainda
            },
            politica_acesso=dict(self.POLITICA_PADRAO),  # Usa as regras padrão de segurança
            metadados_arquivo={
                "criado_em": agora,
                "atualizado_em": agora,
            },
        )
        # Salva tudo no arquivo do cofre
        self._salvar_arquivo(estrutura_arquivo)

    # Tenta fazer login no cofre com senha e, opcionalmente, keyfile
    def tentar_login(
        self,
        senha_mestra: str,
        caminho_keyfile: str | None = None,
    ) -> ResultadoLogin:
        """Valida login com atraso progressivo, keyfile opcional e migração legada."""
        # Carrega os dados salvos do arquivo do cofre
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        # Pega (ou cria) a seção de controle de acesso (tentativas, bloqueios)
        controle = dados_arquivo.setdefault("controle_acesso", {})
        # Obtém as regras de política de acesso (limites de tentativas, tempos, etc.)
        politica = self._politica_acesso(dados_arquivo)
        # Pega o momento atual em segundos (timestamp)
        agora_ts = time.time()

        # Verifica se o cofre está bloqueado por tentativas erradas demais
        bloqueado_ate = float(controle.get("bloqueado_ate", 0.0))
        # Se o bloqueio ainda não expirou, impede o login
        if bloqueado_ate > agora_ts:
            # Calcula quantos segundos faltam para o bloqueio acabar
            restante = math.ceil(bloqueado_ate - agora_ts)
            # Monta a mensagem informando sobre o bloqueio
            mensagem = (
                "Cofre temporariamente bloqueado por múltiplas falhas. "
                f"Tente novamente em {restante} segundo(s)."
            )
            # Retorna resultado de falha com informação do bloqueio
            return ResultadoLogin(
                sucesso=False,
                mensagem=mensagem,
                atraso_segundos=0,
                bloqueio_restante=restante,
            )

        # Inicializa o segredo do keyfile como vazio
        segredo_keyfile = None
        # Se o cofre exige keyfile, precisamos carregá-lo
        if bool(dados_arquivo.get("kdf", {}).get("usa_keyfile", False)):
            # Se o usuário não informou o keyfile, avisa que é obrigatório
            if not caminho_keyfile:
                raise ValueError("Este cofre exige um keyfile para concluir o login.")
            # Carrega o segredo do keyfile a partir do arquivo
            segredo_keyfile = self._carregar_segredo_keyfile(caminho_keyfile)

        # Verifica se a senha mestra digitada está correta
        senha_ok = verificar_senha_mestra(
            senha_mestra,
            dados_arquivo["kdf"],
            dados_arquivo["verificador_senha"],
            segredo_keyfile=segredo_keyfile,
        )

        # Se a senha está correta, prossegue com o login
        if senha_ok:
            # Verifica se o cofre usa o formato antigo (legado)
            formato_legado = self._arquivo_usa_formato_legado(dados_arquivo)
            # Descriptografa (desembaralha) os dados do cofre
            dados_cofre, chave_sessao = self._abrir_carga_criptografada(
                dados_arquivo,
                senha_mestra,
                segredo_keyfile,
            )
            # Verifica se os dados descriptografados são válidos (devem ser um dicionário)
            if not isinstance(dados_cofre, dict):
                raise ValueError("Estrutura interna do cofre inválida.")

            # Armazena os dados descriptografados na memória para uso durante a sessão
            self._dados_cofre = dados_cofre
            # Armazena a chave de criptografia da sessão
            self._chave_sessao = chave_sessao
            # Armazena o segredo do keyfile para uso durante a sessão
            self._segredo_keyfile_sessao = segredo_keyfile
            # Garante que a estrutura interna do cofre tem todos os campos necessários
            self._normalizar_estrutura_cofre()

            # Zera o contador de falhas consecutivas (login deu certo)
            controle["falhas_consecutivas"] = 0
            # Remove qualquer bloqueio ativo
            controle["bloqueado_ate"] = 0.0

            # Variável para saber se o cofre foi migrado para formato novo
            migrado = False
            # Se o cofre estava no formato antigo, tenta atualizar para o formato novo
            if formato_legado:
                migrado = self._migrar_arquivo_se_necessario(
                    dados_arquivo=dados_arquivo,
                    senha_mestra=senha_mestra,
                    dados_cofre=self._dados_cofre,
                    segredo_keyfile=segredo_keyfile,
                )

            # Se não houve migração, apenas atualiza a data e salva
            if not migrado:
                dados_arquivo.setdefault("metadados", {})["atualizado_em"] = self._agora_iso()
                self._salvar_arquivo(dados_arquivo)

            # Mensagem padrão de sucesso
            mensagem = "Login realizado com sucesso."
            # Se houve migração, adiciona informação extra na mensagem
            if migrado:
                mensagem = (
                    "Login realizado com sucesso. "
                    "O cofre foi atualizado automaticamente para proteção mais forte."
                )

            # Retorna resultado de sucesso
            return ResultadoLogin(True, mensagem)

        # --- A partir daqui, a senha estava errada ---

        # Conta mais uma falha consecutiva
        falhas = int(controle.get("falhas_consecutivas", 0)) + 1
        controle["falhas_consecutivas"] = falhas

        # Calcula o tempo de espera progressivo (dobra a cada tentativa errada)
        # Mas nunca passa do limite máximo configurado
        atraso = min(
            int(politica["atraso_max_segundos"]),
            2 ** max(0, falhas - 1),
        )

        # Inicializa o tempo de bloqueio como zero
        bloqueio_restante = 0
        # Mensagem informando que a senha estava errada e quanto tempo esperar
        mensagem = (
            "Credenciais de desbloqueio incorretas. "
            f"Aguarde {atraso} segundo(s) para tentar novamente."
        )

        # Se o número de falhas atingiu o limite máximo, aplica bloqueio total
        if falhas >= int(politica["max_tentativas"]):
            # Conta mais um bloqueio aplicado
            bloqueios_aplicados = int(controle.get("bloqueios_aplicados", 0)) + 1
            controle["bloqueios_aplicados"] = bloqueios_aplicados
            # Calcula a duração do bloqueio (aumenta a cada vez que é bloqueado)
            duracao_bloqueio = min(
                int(politica["bloqueio_max_segundos"]),
                int(politica["bloqueio_base_segundos"]) * bloqueios_aplicados,
            )
            # Define até quando o cofre fica bloqueado (momento atual + duração)
            controle["bloqueado_ate"] = agora_ts + duracao_bloqueio
            # Zera as falhas consecutivas (pois o bloqueio já foi aplicado)
            controle["falhas_consecutivas"] = 0
            # Remove o atraso simples, pois agora o bloqueio total está ativo
            atraso = 0
            # Informa o tempo de bloqueio restante
            bloqueio_restante = duracao_bloqueio
            # Mensagem informando que o cofre foi bloqueado
            mensagem = (
                "Limite de tentativas atingido. "
                f"Cofre bloqueado por {duracao_bloqueio} segundo(s)."
            )

        # Atualiza a data de modificação e salva o arquivo com as novas informações de controle
        dados_arquivo.setdefault("metadados", {})["atualizado_em"] = self._agora_iso()
        self._salvar_arquivo(dados_arquivo)

        # Retorna resultado de falha com informações de atraso e bloqueio
        return ResultadoLogin(
            sucesso=False,
            mensagem=mensagem,
            atraso_segundos=atraso,
            bloqueio_restante=bloqueio_restante,
        )

    # Verifica quantos segundos faltam para acabar um bloqueio que está ativo
    def tempo_restante_bloqueio(self) -> int:
        """Retorna quantos segundos faltam para o fim de um bloqueio ativo."""
        # Se não existe cofre, não há bloqueio
        if not self.existe_cofre():
            return 0
        # Carrega os dados do arquivo
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        # Pega o momento até quando o cofre está bloqueado
        bloqueado_ate = float(dados_arquivo.get("controle_acesso", {}).get("bloqueado_ate", 0.0))
        # Calcula quanto tempo falta
        restante = bloqueado_ate - time.time()
        # Se já passou do tempo de bloqueio, retorna 0
        if restante <= 0:
            return 0
        # Arredonda para cima e retorna os segundos restantes
        return math.ceil(restante)

    # Verifica se o usuário já fez login e tem uma sessão ativa
    def esta_autenticado(self) -> bool:
        """Indica se existe sessão autenticada com dados descriptografados."""
        # Só está autenticado se a chave da sessão e os dados do cofre existem
        return self._chave_sessao is not None and self._dados_cofre is not None

    # ========================================================================
    # API GENÉRICA DE ITENS — suporta os 6 tipos: senha, cartão, documento,
    # nota segura, wifi e licença. Todos os itens ficam guardados na mesma
    # lista interna, diferenciados pelo campo "tipo".
    # ========================================================================

    # Lista todos os itens do cofre (ou filtrados por tipo e termo de busca)
    # Os campos sensíveis (senha, cvv, etc) NÃO são retornados, por segurança
    def listar_itens(
        self,
        tipo: str | None = None,
        filtro: str = "",
        apenas_favoritos: bool = False,
    ) -> list[dict[str, Any]]:
        """Lista itens do cofre sem expor campos sensíveis."""
        # Garante que o usuário está logado antes de continuar
        self._garantir_sessao()
        # Remove espaços e converte o filtro para minúsculas para busca sem distinção de maiúsculas
        termo = filtro.strip().lower()
        # Lista que vai guardar os resultados finais
        saida: list[dict[str, Any]] = []

        # Percorre cada item guardado no cofre
        for item in self._dados_cofre.get("credenciais", []):
            # Normaliza o item para garantir que tem todos os campos padrão
            item_normalizado = self._normalizar_item(item)
            # Se foi pedido um tipo específico, e o item é de outro tipo, pula
            if tipo and item_normalizado["tipo"] != tipo:
                continue
            # Se foi pedido só favoritos, e este não é favorito, pula
            if apenas_favoritos and not item_normalizado.get("favorito", False):
                continue
            # Cria versão "pública" do item (sem campos sensíveis)
            item_publico = self._item_sem_sensiveis(item_normalizado)
            # Se tem termo de busca, verifica se aparece em algum campo visível
            if termo:
                # Monta um texto com todos os valores do item para buscar
                texto_busca = " ".join(str(valor) for valor in item_publico.values()).lower()
                # Se o termo não aparece, pula esse item
                if termo not in texto_busca:
                    continue
            # Adiciona o item sanitizado na lista de saída
            saida.append(item_publico)

        # Ordena: favoritos primeiro, depois por título alfabético
        saida.sort(key=lambda i: (not i.get("favorito", False), str(i.get("titulo", "")).lower()))
        # Retorna a lista final
        return saida

    # Obtém um item específico pelo ID, com opção de revelar campos sensíveis
    def obter_item(
        self,
        item_id: str,
        incluir_sensiveis: bool = False,
    ) -> dict[str, Any] | None:
        """Obtém um item específico pelo identificador interno."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Procura o item bruto pelo ID
        item_bruto = self._buscar_item_por_id(item_id)
        # Se não encontrou, retorna None (nada)
        if item_bruto is None:
            return None
        # Normaliza o item (garante campos padrão)
        item_normalizado = self._normalizar_item(item_bruto)
        # Se foi pedido para incluir campos sensíveis, retorna tudo
        if incluir_sensiveis:
            return dict(item_normalizado)
        # Caso contrário, retorna sem os campos sensíveis
        return self._item_sem_sensiveis(item_normalizado)

    # Conta quantos itens existem em cada tipo (usado para mostrar na sidebar)
    def contar_por_tipo(self) -> dict[str, int]:
        """Conta quantos itens existem em cada tipo para exibir na interface."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Cria um dicionário começando com zero para cada tipo suportado
        contagem = {tipo: 0 for tipo in TIPOS_SUPORTADOS}
        # Percorre cada item e conta pelo seu tipo
        for item in self._dados_cofre.get("credenciais", []):
            tipo_item = self._resolver_tipo(item)
            if tipo_item in contagem:
                contagem[tipo_item] += 1
        # Retorna o dicionário com a contagem de cada tipo
        return contagem

    # Adiciona um novo item de qualquer tipo suportado ao cofre
    def adicionar_item(self, tipo: str, dados: dict[str, Any]) -> str:
        """Adiciona um novo item de qualquer tipo suportado ao cofre."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Valida e normaliza os dados recebidos conforme o tipo informado
        dados_validos = self._validar_dados_item(tipo, dados)
        # Verifica se já existe item igual (mesmo tipo e mesmo título) para evitar duplicatas
        if self._item_duplicado(tipo, dados_validos["titulo"]):
            raise ValueError("Já existe um item desse tipo com o mesmo título.")

        # Pega a data e hora atuais
        agora = self._agora_iso()
        # Cria o novo item com ID único, tipo, favorito inicial False e datas
        novo_item: dict[str, Any] = {
            "id": secrets.token_hex(16),     # Identificador único aleatório (32 caracteres hex)
            "tipo": tipo,                     # Tipo do item (senha, cartao, etc)
            "favorito": False,                # Começa não favorito
            "criado_em": agora,               # Data de criação
            "atualizado_em": agora,           # Data da última atualização
        }
        # Copia todos os campos validados para o novo item
        novo_item.update(dados_validos)
        # Adiciona o item na lista interna do cofre
        self._dados_cofre["credenciais"].append(novo_item)
        # Criptografa e salva no disco
        self._persistir_cofre()
        # Retorna o ID gerado para quem chamou poder usar (abrir detalhes, etc)
        return novo_item["id"]

    # Edita um item existente, atualizando seus campos
    def editar_item(self, item_id: str, dados: dict[str, Any]) -> None:
        """Atualiza os dados de um item existente."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Procura o item pelo ID
        item = self._buscar_item_por_id(item_id)
        # Se não encontrou, lança erro
        if item is None:
            raise ValueError("Item não encontrado.")

        # Pega o tipo do item (normalizando, caso seja legado sem campo "tipo")
        tipo_item = self._resolver_tipo(item)
        # Valida os dados para o tipo deste item
        dados_validos = self._validar_dados_item(tipo_item, dados)
        # Verifica duplicata (ignora o próprio item sendo editado)
        if self._item_duplicado(tipo_item, dados_validos["titulo"], ignorar_id=item_id):
            raise ValueError("Já existe outro item desse tipo com o mesmo título.")

        # Garante que o campo "tipo" está presente no item (cofres legados podem não ter)
        item["tipo"] = tipo_item
        # Atualiza todos os campos editáveis
        for campo in CAMPOS_EDITAVEIS_POR_TIPO[tipo_item]:
            item[campo] = dados_validos.get(campo, item.get(campo, ""))
        # Atualiza a data de modificação
        item["atualizado_em"] = self._agora_iso()
        # Criptografa e salva no disco
        self._persistir_cofre()

    # Alterna (liga/desliga) o status de favorito de um item
    def alternar_favorito(self, item_id: str) -> bool:
        """Alterna o estado de favorito de um item e salva."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Procura o item pelo ID
        item = self._buscar_item_por_id(item_id)
        # Se não encontrou, lança erro
        if item is None:
            raise ValueError("Item não encontrado.")
        # Inverte o estado de favorito (True ↔ False)
        novo_estado = not bool(item.get("favorito", False))
        item["favorito"] = novo_estado
        # Atualiza a data de modificação
        item["atualizado_em"] = self._agora_iso()
        # Criptografa e salva no disco
        self._persistir_cofre()
        # Retorna o novo estado para a interface atualizar
        return novo_estado

    # Revela um campo sensível específico após reautenticação da senha mestra
    def revelar_campo(self, item_id: str, campo: str, senha_mestra: str) -> str:
        """Revela um campo sensível de um item após reautenticação."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Verifica a senha mestra antes de revelar qualquer coisa
        if not self.autenticar_acao_sensivel(senha_mestra):
            raise PermissionError("Falha de autenticação para revelar o campo solicitado.")
        # Procura o item pelo ID
        item = self._buscar_item_por_id(item_id)
        # Se não encontrou, lança erro
        if item is None:
            raise ValueError("Item não encontrado.")

        # Determina o tipo do item para descobrir quais campos são sensíveis
        tipo_item = self._resolver_tipo(item)
        # Lista de campos considerados sensíveis para este tipo
        campos_permitidos = CAMPOS_SENSIVEIS_POR_TIPO.get(tipo_item, ())
        # Só permite revelar campos que estão na lista de sensíveis (segurança extra)
        if campo not in campos_permitidos:
            raise ValueError("Campo solicitado não pode ser revelado desta forma.")
        # Retorna o valor do campo sensível como texto
        return str(item.get(campo, ""))

    # ========================================================================
    # API LEGADA (compatibilidade) — só para o tipo "senha". Mantida para não
    # quebrar código/chamadores antigos. Internamente usa a API genérica.
    # ========================================================================

    # Lista as credenciais (itens do tipo "senha") no formato antigo
    def listar_credenciais(self, filtro: str = "") -> list[dict[str, str]]:
        """Lista credenciais (apenas senhas) no formato legado."""
        # Busca apenas itens do tipo "senha"
        itens = self.listar_itens(tipo="senha", filtro=filtro)
        # Converte para o formato antigo que usa "servico" em vez de "titulo"
        saida: list[dict[str, str]] = []
        for item in itens:
            saida.append({
                "id": str(item.get("id", "")),
                "servico": str(item.get("titulo", "")),
                "login": str(item.get("login", "")),
                "observacao": str(item.get("observacao", "")),
                "atualizado_em": str(item.get("atualizado_em", "")),
            })
        # Retorna a lista no formato antigo
        return saida

    # Obtém uma credencial no formato antigo (compatibilidade)
    def obter_credencial(
        self,
        credencial_id: str,
        incluir_senha: bool = False,
    ) -> dict[str, str] | None:
        """Obtém credencial específica no formato legado."""
        # Busca o item completo
        item = self.obter_item(credencial_id, incluir_sensiveis=incluir_senha)
        # Se não encontrou, retorna None
        if item is None:
            return None
        # Se o tipo não é "senha", devolve None (compatibilidade: API legada só vê senhas)
        if item.get("tipo") != "senha":
            return None
        # Monta o dicionário no formato antigo
        resultado = {
            "id": str(item.get("id", "")),
            "servico": str(item.get("titulo", "")),
            "login": str(item.get("login", "")),
            "observacao": str(item.get("observacao", "")),
            "atualizado_em": str(item.get("atualizado_em", "")),
        }
        # Se foi pedida a senha, adiciona ao resultado
        if incluir_senha:
            resultado["senha"] = str(item.get("senha", ""))
        # Retorna no formato legado
        return resultado

    # Adiciona uma credencial (senha) pelo formato legado (servico/login/senha)
    def adicionar_credencial(
        self,
        servico: str,
        login: str,
        senha: str,
        observacao: str = "",
    ) -> str:
        """Adiciona nova credencial (formato legado)."""
        # Usa a API genérica adaptando "servico" para "titulo"
        return self.adicionar_item("senha", {
            "titulo": servico,
            "login": login,
            "senha": senha,
            "observacao": observacao,
        })

    # Edita uma credencial (senha) pelo formato legado
    def editar_credencial(
        self,
        credencial_id: str,
        servico: str,
        login: str,
        senha: str,
        observacao: str = "",
    ) -> None:
        """Atualiza credencial existente (formato legado)."""
        # Usa a API genérica adaptando campos
        self.editar_item(credencial_id, {
            "titulo": servico,
            "login": login,
            "senha": senha,
            "observacao": observacao,
        })

    # Remove um item do cofre (alias histórico: "excluir_credencial")
    def excluir_credencial(self, credencial_id: str) -> None:
        """Remove um item do cofre (alias mantido por compatibilidade)."""
        self.excluir_item(credencial_id)

    # Remove um item do cofre pelo ID (API nova)
    def excluir_item(self, item_id: str) -> None:
        """Remove um item do cofre e grava as alterações."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Pega a lista de itens atual
        itens = self._dados_cofre.get("credenciais", [])
        # Guarda o tamanho da lista antes de filtrar
        tamanho_antes = len(itens)
        # Cria uma nova lista SEM o item que queremos excluir
        itens_filtrados = [atual for atual in itens if atual.get("id") != item_id]

        # Se o tamanho não mudou, não encontrou o item para excluir
        if len(itens_filtrados) == tamanho_antes:
            raise ValueError("Item não encontrado.")

        # Substitui a lista pelo resultado filtrado
        self._dados_cofre["credenciais"] = itens_filtrados
        # Criptografa e salva no disco
        self._persistir_cofre()

    # Verifica a senha mestra para ações sensíveis (usado internamente e pela API)
    def autenticar_acao_sensivel(self, senha_mestra: str) -> bool:
        """Revalida a senha mestra para ações sensíveis usando a sessão atual."""
        # Carrega o arquivo do cofre
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        # Verifica se a senha mestra está correta e retorna True ou False
        return verificar_senha_mestra(
            senha_mestra,
            dados_arquivo["kdf"],
            dados_arquivo["verificador_senha"],
            segredo_keyfile=self._segredo_keyfile_sessao,
        )

    # Revela a senha de uma credencial (método legado; usa revelar_campo internamente)
    def revelar_senha(self, credencial_id: str, senha_mestra: str) -> str:
        """Revela a senha de uma credencial após autenticação (formato legado)."""
        return self.revelar_campo(credencial_id, "senha", senha_mestra)

    # Exporta (copia) credenciais para um arquivo separado, protegido por outra senha
    # Mantém compatibilidade: exporta APENAS itens do tipo "senha"
    def exportar_credenciais(
        self,
        caminho_destino: str | Path,
        senha_exportacao: str,
        credencial_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Exporta credenciais para um pacote criptografado independente do cofre atual."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Verifica se a senha de exportação é forte o suficiente
        senha_valida, mensagem = validar_forca_senha_mestra(senha_exportacao)
        # Se a senha for fraca, mostra erro
        if not senha_valida:
            raise ValueError(
                f"A senha de exportação precisa ser forte. {mensagem}"
            )

        # Resolve o caminho completo do arquivo de destino
        caminho_resolvido = Path(caminho_destino).expanduser().resolve()
        # Impede que a exportação sobrescreva o próprio cofre
        if caminho_resolvido == self._armazenamento.caminho:
            raise ValueError("Escolha outro arquivo; a exportação não pode sobrescrever o cofre atual.")

        # Pega todos os itens do cofre e filtra só os do tipo senha
        itens_fonte = [
            item for item in self._dados_cofre.get("credenciais", [])
            if self._resolver_tipo(item) == "senha"
        ]
        # Se foram informados IDs específicos, cria um conjunto para filtrar
        ids_filtrados = set(credencial_ids or [])
        # Lista que vai guardar os itens selecionados para exportação
        credenciais_exportadas: list[dict[str, Any]] = []

        # Percorre cada credencial do cofre
        for credencial in itens_fonte:
            # Se há filtro de IDs e esta credencial não está na lista, pula
            if ids_filtrados and str(credencial.get("id")) not in ids_filtrados:
                continue
            # Converte para formato legado (servico em vez de titulo) para compatibilidade
            credencial_legada = {
                "id": credencial.get("id"),
                "servico": credencial.get("titulo", credencial.get("servico", "")),
                "login": credencial.get("login", ""),
                "senha": credencial.get("senha", ""),
                "observacao": credencial.get("observacao", ""),
                "criado_em": credencial.get("criado_em", ""),
                "atualizado_em": credencial.get("atualizado_em", ""),
            }
            credenciais_exportadas.append(credencial_legada)

        # Se nenhuma credencial foi selecionada, mostra erro
        if not credenciais_exportadas:
            raise ValueError("Não há credenciais para exportar.")

        # Cria um novo registro de senha para proteger a exportação
        registro = criar_registro_senha_mestra(senha_exportacao)
        # Gera a chave de criptografia para a exportação
        chave_exportacao = gerar_chave_criptografia(senha_exportacao, registro["kdf"])
        # Pega a data e hora atuais
        agora = self._agora_iso()
        # Monta o pacote de exportação com tudo criptografado
        pacote = {
            "tipo": "exportacao_credenciais_cofre_seguro",
            "versao_exportacao": 1,
            "kdf": registro["kdf"],
            "verificador_senha": registro["verificador_senha"],
            "dados_exportados_criptografados": criptografar_objeto(
                {
                    "credenciais": credenciais_exportadas,
                    "metadados": {
                        "exportado_em": agora,
                        "quantidade_credenciais": len(credenciais_exportadas),
                    },
                },
                chave_exportacao,
            ),
            "metadados": {
                "exportado_em": agora,
                "quantidade_credenciais": len(credenciais_exportadas),
                "formato_origem": int(self.obter_resumo_seguranca()["versao"]),
            },
        }

        # Salva o pacote de exportação no arquivo de destino
        GerenciadorArquivoCofre(caminho_resolvido).salvar(pacote)
        # Retorna informações sobre a exportação (caminho e quantidade)
        return {
            "arquivo": str(caminho_resolvido),
            "quantidade": len(credenciais_exportadas),
        }

    # Importa credenciais de um arquivo de exportação para o cofre atual
    def importar_credenciais(
        self,
        caminho_origem: str | Path,
        senha_importacao: str,
        sobrescrever_duplicadas: bool = False,
    ) -> dict[str, int]:
        """Importa um pacote criptografado de credenciais para o cofre autenticado."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Carrega e valida o pacote de exportação do arquivo de origem
        pacote = self._carregar_pacote_exportacao(caminho_origem)

        # Verifica se a senha de importação está correta
        if not verificar_senha_mestra(
            senha_importacao,
            pacote["kdf"],
            pacote["verificador_senha"],
        ):
            raise PermissionError("Senha de importação incorreta.")

        # Gera a chave de criptografia a partir da senha de importação
        chave_importacao = gerar_chave_criptografia(senha_importacao, pacote["kdf"])
        # Descriptografa os dados exportados usando a chave
        carga = descriptografar_objeto(
            pacote["dados_exportados_criptografados"],
            chave_importacao,
        )
        # Verifica se os dados descriptografados são válidos
        if not isinstance(carga, dict):
            raise ValueError("Pacote de importação inválido.")

        # Pega a lista de credenciais do pacote
        credenciais = carga.get("credenciais", [])
        # Verifica se é realmente uma lista
        if not isinstance(credenciais, list):
            raise ValueError("Pacote de importação com lista de credenciais inválida.")

        # Contadores para saber o que aconteceu com cada credencial
        inseridas = 0     # Quantas credenciais novas foram adicionadas
        atualizadas = 0   # Quantas credenciais existentes foram atualizadas
        ignoradas = 0     # Quantas credenciais foram ignoradas (duplicadas ou inválidas)
        # Pega a data e hora atuais
        agora = self._agora_iso()

        # Percorre cada item (credencial) do pacote importado
        for item in credenciais:
            # Se o item não é um dicionário válido, ignora e conta como ignorado
            if not isinstance(item, dict):
                ignoradas += 1
                continue

            # Pega os campos (aceita tanto "servico" antigo quanto "titulo" novo)
            titulo = str(item.get("titulo", item.get("servico", ""))).strip()
            login = str(item.get("login", "")).strip()
            senha = str(item.get("senha", ""))
            observacao = str(item.get("observacao", "")).strip()

            # Se falta algum campo obrigatório, ignora esse item
            if not titulo or not login or not senha:
                ignoradas += 1
                continue

            # Procura item duplicado (mesmo título e mesmo login no tipo "senha")
            existente = self._buscar_item_senha_por_titulo_login(titulo, login)
            # Se já existe uma igual no cofre
            if existente is not None:
                # Se não foi pedido para sobrescrever duplicadas, ignora
                if not sobrescrever_duplicadas:
                    ignoradas += 1
                    continue
                # Se foi pedido para sobrescrever, atualiza os dados da existente
                existente["senha"] = senha
                existente["observacao"] = observacao
                existente["atualizado_em"] = agora
                atualizadas += 1
                continue

            # Se não existe, cria uma nova credencial do tipo "senha"
            novo_item = {
                "id": secrets.token_hex(16),
                "tipo": "senha",
                "favorito": False,
                "titulo": titulo,
                "login": login,
                "senha": senha,
                "observacao": observacao,
                "criado_em": str(item.get("criado_em", agora)),
                "atualizado_em": str(item.get("atualizado_em", agora)),
            }
            # Adiciona a nova credencial no cofre
            self._dados_cofre["credenciais"].append(novo_item)
            inseridas += 1

        # Se houve alguma inserção ou atualização, salva o cofre
        if inseridas or atualizadas:
            self._persistir_cofre()

        # Retorna o resumo da importação
        return {
            "inseridas": inseridas,
            "atualizadas": atualizadas,
            "ignoradas": ignoradas,
        }

    # Permite trocar a senha mestra, ativar/desativar keyfile e atualizar a criptografia
    def reconfigurar_seguranca(
        self,
        senha_mestra_atual: str,
        nova_senha_mestra: str | None = None,
        usar_keyfile: bool = False,
        caminho_keyfile: str | None = None,
    ) -> str:
        """Reconfigura senha mestra, keyfile e formato forte do cofre atual."""
        # Garante que o usuário está logado
        self._garantir_sessao()

        # Primeiro verifica se a senha mestra atual está correta
        if not self.autenticar_acao_sensivel(senha_mestra_atual):
            raise PermissionError("Senha mestra atual incorreta.")

        # Se o usuário informou nova senha, usa ela; senão, mantém a atual
        senha_destino = (nova_senha_mestra or "").strip() or senha_mestra_atual
        # Se há nova senha, verifica se ela é forte o suficiente
        if nova_senha_mestra:
            senha_valida, mensagem = validar_forca_senha_mestra(senha_destino)
            if not senha_valida:
                raise ValueError(mensagem)

        # Inicializa o segredo do keyfile como vazio
        segredo_keyfile_destino = None
        # Se o usuário quer usar keyfile
        if usar_keyfile:
            # Se informou um caminho para o keyfile, carrega dele
            if caminho_keyfile:
                segredo_keyfile_destino = self._carregar_segredo_keyfile(caminho_keyfile)
            # Se não informou caminho mas já tinha keyfile na sessão, reutiliza
            elif self._segredo_keyfile_sessao is not None:
                segredo_keyfile_destino = self._segredo_keyfile_sessao
            # Se não tem keyfile nenhum, mostra erro
            else:
                raise ValueError("Selecione ou gere um keyfile para ativar essa proteção.")

        # Cria novo registro de senha com as novas configurações
        registro = criar_registro_senha_mestra(
            senha_destino,
            segredo_keyfile=segredo_keyfile_destino,
        )
        # Gera nova chave de criptografia
        chave_criptografia = gerar_chave_criptografia(
            senha_destino,
            registro["kdf"],
            segredo_keyfile=segredo_keyfile_destino,
        )

        # Carrega o arquivo atual do cofre
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        # Pega os metadados existentes
        metadados_arquivo = dict(dados_arquivo.get("metadados", {}))
        # Registra quando a segurança foi atualizada
        metadados_arquivo["seguranca_atualizada_em"] = self._agora_iso()

        # Monta a nova estrutura do arquivo com as novas configurações de segurança
        estrutura_arquivo = self._montar_estrutura_arquivo(
            registro=registro,
            dados_cofre=self._dados_cofre,
            chave_criptografia=chave_criptografia,
            controle_acesso=dados_arquivo.get("controle_acesso"),
            politica_acesso=dados_arquivo.get("politica_acesso"),
            metadados_arquivo=metadados_arquivo,
        )
        # Salva o arquivo com as novas configurações
        self._salvar_arquivo(estrutura_arquivo)

        # Atualiza a sessão com a nova chave e keyfile
        self._chave_sessao = chave_criptografia
        self._segredo_keyfile_sessao = segredo_keyfile_destino

        # Retorna uma mensagem diferente dependendo do que foi alterado
        if nova_senha_mestra and usar_keyfile:
            return "Senha mestra e keyfile atualizados com sucesso."
        if nova_senha_mestra:
            return "Senha mestra atualizada com sucesso."
        if usar_keyfile:
            return "Proteção com keyfile aplicada ao cofre."
        return "Proteção com keyfile removida; o cofre segue protegido pela senha mestra."

    # Gera uma senha forte aleatória para o usuário usar em algum serviço
    def gerar_senha(
        self,
        comprimento: int = 16,
        incluir_maiusculas: bool = True,
        incluir_minusculas: bool = True,
        incluir_numeros: bool = True,
        incluir_especiais: bool = True,
    ) -> str:
        """Gera senha forte para preenchimento rápido no formulário."""
        # Encaminha todos os parâmetros para a função do módulo de segurança
        return gerar_senha_forte(
            comprimento=comprimento,
            incluir_maiusculas=incluir_maiusculas,
            incluir_minusculas=incluir_minusculas,
            incluir_numeros=incluir_numeros,
            incluir_especiais=incluir_especiais,
        )

    # Encerra a sessão atual, limpando todos os dados sensíveis da memória
    def encerrar_sessao(self) -> None:
        """Limpa referências de sessão para reduzir exposição em memória."""
        # Se existem dados do cofre na memória, apaga os campos sensíveis
        if isinstance(self._dados_cofre, dict):
            # Percorre cada item e zera seus campos sensíveis
            for item in self._dados_cofre.get("credenciais", []):
                tipo_item = self._resolver_tipo(item)
                # Limpa todos os campos sensíveis daquele tipo
                for campo_sensivel in CAMPOS_SENSIVEIS_POR_TIPO.get(tipo_item, ()):
                    if campo_sensivel in item:
                        item[campo_sensivel] = ""

        # Limpa todas as referências de sessão (dados, chave e keyfile)
        self._dados_cofre = None
        self._chave_sessao = None
        self._segredo_keyfile_sessao = None
        # Invalida o cache do arquivo: próxima sessão pode ser cofre diferente
        # (importante quando o usuário troca de cofre via --arquivo)
        self._cache_arquivo = None

    # ========================================================================
    # Métodos internos (privados) — usados apenas dentro desta classe
    # ========================================================================

    # Criptografa e salva os dados do cofre no arquivo
    def _persistir_cofre(self) -> None:
        """Criptografa e salva o estado atual do cofre em disco."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Carrega o arquivo atual do disco
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        # Pega a data e hora atuais
        agora = self._agora_iso()
        # Atualiza a data de modificação nos dados internos do cofre
        self._dados_cofre.setdefault("metadados", {})["atualizado_em"] = agora

        # Criptografa (embaralha) os dados do cofre com a chave da sessão
        carga_criptografada = criptografar_objeto(self._dados_cofre, self._chave_sessao)
        # Atualiza a versão do formato
        dados_arquivo["versao"] = VERSAO_COFRE_ATUAL
        # Substitui os dados criptografados antigos pelos novos
        dados_arquivo["dados_cofre_criptografados"] = carga_criptografada
        # Atualiza a data de modificação do arquivo
        dados_arquivo.setdefault("metadados", {})["atualizado_em"] = agora
        # Salva o arquivo atualizado no disco
        self._salvar_arquivo(dados_arquivo)

    # Descriptografa os dados do cofre, tratando formato atual e legado
    def _abrir_carga_criptografada(
        self,
        dados_arquivo: dict[str, Any],
        senha_mestra: str,
        segredo_keyfile: bytes | None,
    ) -> tuple[dict[str, Any], bytes | None]:
        """Abre os dados do cofre conforme o formato atual ou legado."""
        # Se o arquivo usa o formato antigo (legado), usa o método antigo
        if self._arquivo_usa_formato_legado(dados_arquivo):
            # Gera a chave no formato antigo (Fernet)
            chave_fernet = gerar_chave_fernet_legado(senha_mestra, dados_arquivo["kdf"])
            # Descriptografa usando o método antigo
            dados_cofre = descriptografar_objeto_legado(
                dados_arquivo["dados_cofre_criptografados"],
                chave_fernet,
            )
            # Retorna os dados (sem chave AES, pois é formato antigo)
            return dados_cofre, None

        # Se é formato atual, gera a chave AES moderna
        chave_aes = gerar_chave_criptografia(
            senha_mestra,
            dados_arquivo["kdf"],
            segredo_keyfile=segredo_keyfile,
        )
        # Descriptografa usando o método moderno
        dados_cofre = descriptografar_objeto(
            dados_arquivo["dados_cofre_criptografados"],
            chave_aes,
        )
        # Retorna os dados e a chave AES para uso na sessão
        return dados_cofre, chave_aes

    # Migra (atualiza) cofres no formato antigo para o formato moderno
    def _migrar_arquivo_se_necessario(
        self,
        dados_arquivo: dict[str, Any],
        senha_mestra: str,
        dados_cofre: dict[str, Any],
        segredo_keyfile: bytes | None,
    ) -> bool:
        """Migra cofres legados para Argon2id + AES-256-GCM ao abrir com sucesso."""
        # Se já está no formato atual, não precisa migrar
        if not self._arquivo_usa_formato_legado(dados_arquivo):
            return False

        # Cria novo registro de senha no formato moderno
        registro = criar_registro_senha_mestra(
            senha_mestra,
            segredo_keyfile=segredo_keyfile,
        )
        # Gera nova chave de criptografia no formato moderno
        chave_criptografia = gerar_chave_criptografia(
            senha_mestra,
            registro["kdf"],
            segredo_keyfile=segredo_keyfile,
        )

        # Pega os metadados do arquivo e adiciona informações sobre a migração
        metadados_arquivo = dict(dados_arquivo.get("metadados", {}))
        metadados_arquivo["migrado_em"] = self._agora_iso()
        metadados_arquivo["origem_migracao"] = f"versao_{dados_arquivo.get('versao', 1)}"

        # Monta a nova estrutura do arquivo no formato moderno
        estrutura_arquivo = self._montar_estrutura_arquivo(
            registro=registro,
            dados_cofre=dados_cofre,
            chave_criptografia=chave_criptografia,
            controle_acesso=dados_arquivo.get("controle_acesso"),
            politica_acesso=dados_arquivo.get("politica_acesso"),
            metadados_arquivo=metadados_arquivo,
        )
        # Salva o arquivo atualizado no disco
        self._salvar_arquivo(estrutura_arquivo)
        # Atualiza a chave da sessão para a nova chave
        self._chave_sessao = chave_criptografia
        # Retorna True indicando que a migração foi feita
        return True

    # Monta a estrutura completa do arquivo do cofre no formato mais recente
    def _montar_estrutura_arquivo(
        self,
        registro: dict[str, Any],
        dados_cofre: dict[str, Any],
        chave_criptografia: bytes,
        controle_acesso: dict[str, Any] | None,
        politica_acesso: dict[str, Any] | None,
        metadados_arquivo: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Monta a estrutura persistida do cofre no formato atual."""
        # Pega a data e hora atuais
        agora = self._agora_iso()
        # Copia os metadados ou cria um dicionário vazio se não existirem
        metadados = dict(metadados_arquivo or {})
        # Define a data de criação se ainda não existir
        metadados.setdefault("criado_em", agora)
        # Sempre atualiza a data de modificação
        metadados["atualizado_em"] = agora

        # Retorna a estrutura completa do arquivo
        return {
            "versao": VERSAO_COFRE_ATUAL,  # Versão do formato do cofre
            "kdf": registro["kdf"],        # Configurações de derivação de chave
            "verificador_senha": registro["verificador_senha"],
            "dados_cofre_criptografados": criptografar_objeto(dados_cofre, chave_criptografia),
            "controle_acesso": {
                "falhas_consecutivas": int((controle_acesso or {}).get("falhas_consecutivas", 0)),
                "bloqueado_ate": float((controle_acesso or {}).get("bloqueado_ate", 0.0)),
                "bloqueios_aplicados": int((controle_acesso or {}).get("bloqueios_aplicados", 0)),
            },
            "politica_acesso": dict(politica_acesso or self.POLITICA_PADRAO),
            "metadados": metadados,
        }

    # Procura um item (qualquer tipo) pelo identificador único
    def _buscar_item_por_id(self, item_id: str) -> dict[str, Any] | None:
        """Procura um item no cofre pelo identificador único."""
        # Percorre cada item do cofre
        for item in self._dados_cofre.get("credenciais", []):
            # Se o ID bate, retorna o item
            if item.get("id") == item_id:
                return item
        # Se não encontrou, retorna None
        return None

    # Procura item do tipo "senha" pelo par título + login (usado na importação)
    def _buscar_item_senha_por_titulo_login(
        self,
        titulo: str,
        login: str,
    ) -> dict[str, Any] | None:
        """Busca item tipo 'senha' pelo título e login (case-insensitive)."""
        # Normaliza busca para caixa baixa
        alvo_titulo = titulo.lower()
        alvo_login = login.lower()
        # Percorre todos os itens do cofre
        for item in self._dados_cofre.get("credenciais", []):
            # Só interessa itens de senha (ignora cartões, notas, etc)
            if self._resolver_tipo(item) != "senha":
                continue
            # Pega título (aceita campo legado "servico" se "titulo" não existir)
            titulo_atual = str(item.get("titulo", item.get("servico", ""))).lower()
            login_atual = str(item.get("login", "")).lower()
            # Se ambos batem, retorna o item encontrado
            if titulo_atual == alvo_titulo and login_atual == alvo_login:
                return item
        # Não encontrou
        return None

    # Verifica se já existe item duplicado (mesmo tipo + mesmo título)
    def _item_duplicado(
        self,
        tipo: str,
        titulo: str,
        ignorar_id: str | None = None,
    ) -> bool:
        """Valida duplicidade por tipo e título de forma case-insensitive."""
        # Normaliza para caixa baixa
        alvo = titulo.strip().lower()
        # Percorre todos os itens do cofre
        for item in self._dados_cofre.get("credenciais", []):
            # Se tem ID para ignorar (caso de edição), pula esse item
            if ignorar_id and item.get("id") == ignorar_id:
                continue
            # Só considera itens do mesmo tipo
            if self._resolver_tipo(item) != tipo:
                continue
            # Pega o título (aceita campo legado "servico")
            titulo_atual = str(item.get("titulo", item.get("servico", ""))).strip().lower()
            # Se bate, é duplicata
            if titulo_atual == alvo:
                return True
        # Não encontrou duplicata
        return False

    # Descobre o tipo de um item, cuidando de itens legados que não têm campo "tipo"
    def _resolver_tipo(self, item: dict[str, Any]) -> str:
        """Descobre o tipo do item; itens antigos sem campo 'tipo' viram 'senha'."""
        # Pega o tipo explícito, se existir
        tipo_bruto = str(item.get("tipo", "")).strip().lower()
        # Se não for um tipo válido, assume "senha" (compatibilidade com cofres antigos)
        if tipo_bruto in TIPOS_SUPORTADOS:
            return tipo_bruto
        return "senha"

    # Aplica IN-PLACE as migrações de campos legados num único item
    # (campo "tipo", "titulo" a partir de "servico", default "favorito"=False).
    # Helper compartilhado entre _normalizar_item (cópia) e _normalizar_estrutura_cofre
    # (in-place no carregamento), pra ter UMA fonte da verdade da migração.
    def _aplicar_migracao_legada(self, item: dict[str, Any]) -> None:
        """Aplica regras de migração de cofres antigos diretamente no item."""
        # Se o tipo não está presente ou é inválido, força "senha"
        if "tipo" not in item or self._resolver_tipo(item) != item.get("tipo"):
            item["tipo"] = self._resolver_tipo(item)
        # Migra campo legado "servico" → "titulo" (sem apagar o "servico")
        if "titulo" not in item and "servico" in item:
            item["titulo"] = item["servico"]
        # Garante campo de favorito presente
        item.setdefault("favorito", False)

    # Normaliza um item bruto retornando uma CÓPIA com campos padronizados
    # Não muda o original — usado por listar_itens / obter_item
    def _normalizar_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """Retorna cópia normalizada do item, com tipo/titulo/favorito garantidos."""
        # Cria cópia rasa para não mexer no original
        normalizado = dict(item)
        # Aplica migrações na cópia
        self._aplicar_migracao_legada(normalizado)
        # Garante que todos os campos editáveis daquele tipo existem (vazios se nada)
        for campo in CAMPOS_EDITAVEIS_POR_TIPO[normalizado["tipo"]]:
            normalizado.setdefault(campo, "")
        return normalizado

    # Remove os campos sensíveis de um item para exibição na lista
    def _item_sem_sensiveis(self, item: dict[str, Any]) -> dict[str, Any]:
        """Cria cópia do item sem os campos marcados como sensíveis."""
        # Copia o item
        copia = dict(item)
        # Pega o tipo para saber quais campos remover
        tipo_item = self._resolver_tipo(item)
        # Remove cada campo sensível da cópia
        for campo_sensivel in CAMPOS_SENSIVEIS_POR_TIPO.get(tipo_item, ()):
            copia.pop(campo_sensivel, None)
        # Retorna a versão "pública" do item
        return copia

    # Valida e normaliza os dados enviados para criar ou editar um item
    def _validar_dados_item(self, tipo: str, dados: dict[str, Any]) -> dict[str, Any]:
        """Valida campos obrigatórios conforme o tipo do item."""
        # Rejeita se o tipo não é um dos suportados
        if tipo not in TIPOS_SUPORTADOS:
            raise ValueError(f"Tipo de item '{tipo}' não é suportado.")

        # Cria um dicionário limpo só com os campos permitidos para o tipo
        limpos: dict[str, Any] = {}
        for campo in CAMPOS_EDITAVEIS_POR_TIPO[tipo]:
            valor = dados.get(campo, "")
            # Converte None para string vazia
            if valor is None:
                valor = ""
            # Strings ficam com strip para tirar espaços extras nas bordas
            # Conteúdo de notas é exceção: preserva espaços e quebras de linha
            if isinstance(valor, str) and campo != "conteudo":
                valor = valor.strip()
            limpos[campo] = valor

        # Confere se todos os campos obrigatórios estão preenchidos
        for campo_obrigatorio in CAMPOS_OBRIGATORIOS_POR_TIPO[tipo]:
            if not limpos.get(campo_obrigatorio):
                # Gera mensagem amigável usando o rótulo do campo
                raise ValueError(
                    f"O campo '{self._rotulo_amigavel_campo(campo_obrigatorio)}' é obrigatório."
                )

        # Validações específicas por tipo
        if tipo == "cartao":
            # Remove espaços e traços do número do cartão
            limpos["numero"] = limpos["numero"].replace(" ", "").replace("-", "")
            # Verifica se o número do cartão tem só dígitos e tamanho plausível
            if not limpos["numero"].isdigit():
                raise ValueError("O número do cartão deve conter apenas dígitos.")
            if not (12 <= len(limpos["numero"]) <= 19):
                raise ValueError("O número do cartão deve ter entre 12 e 19 dígitos.")
            # Verifica o CVV (se preenchido)
            if limpos.get("cvv") and not (
                limpos["cvv"].isdigit() and 3 <= len(limpos["cvv"]) <= 4
            ):
                raise ValueError("O CVV deve ter 3 ou 4 dígitos.")

        # Retorna os dados validados e normalizados
        return limpos

    # Converte um nome técnico de campo num rótulo amigável para mensagens
    @staticmethod
    def _rotulo_amigavel_campo(campo: str) -> str:
        """Converte nome técnico do campo em texto amigável para o usuário."""
        mapa = {
            "titulo": "Título",
            "login": "Usuário/E-mail",
            "senha": "Senha",
            "numero": "Número",
            "validade": "Validade",
            "cvv": "CVV",
            "titular": "Titular",
            "bandeira": "Bandeira",
            "cor": "Cor",
            "tipo_documento": "Tipo do documento",
            "nome_titular": "Nome do titular",
            "orgao_emissor": "Órgão emissor",
            "data_emissao": "Data de emissão",
            "conteudo": "Conteúdo",
            "tipo_seguranca": "Tipo de segurança",
            "chave": "Chave de licença",
            "email_licenca": "E-mail da licença",
            "data_compra": "Data de compra",
            "observacao": "Observação",
        }
        # Retorna o rótulo se existir; senão, devolve o próprio nome técnico
        return mapa.get(campo, campo)

    # Verifica se o usuário está logado; se não estiver, impede a operação
    def _garantir_sessao(self) -> None:
        """Garante que exista sessão autenticada antes de operar no cofre."""
        if not self.esta_autenticado():
            raise PermissionError("É necessário fazer login para acessar o cofre.")

    # Garante que a estrutura interna do cofre tenha os campos mínimos
    # E que cada item esteja com a migração legada aplicada (in-place).
    def _normalizar_estrutura_cofre(self) -> None:
        """Normaliza estrutura interna mínima do cofre descriptografado."""
        # Se não existe a lista de itens, cria uma vazia
        self._dados_cofre.setdefault("credenciais", [])
        # Se não existem metadados, cria com as datas atuais
        self._dados_cofre.setdefault(
            "metadados",
            {
                "criado_em": self._agora_iso(),
                "atualizado_em": self._agora_iso(),
            },
        )
        # Aplica migração legada in-place em cada item (UMA fonte da verdade)
        for item in self._dados_cofre["credenciais"]:
            self._aplicar_migracao_legada(item)

    # Carrega o conteúdo de um keyfile do disco e retorna o segredo normalizado
    def _carregar_segredo_keyfile(self, caminho_keyfile: str) -> bytes:
        """Carrega keyfile do disco e devolve seu segredo normalizado."""
        caminho = Path(caminho_keyfile).expanduser().resolve()
        if not caminho.exists():
            raise ValueError("O keyfile informado não foi encontrado.")
        if not caminho.is_file():
            raise ValueError("O caminho informado para keyfile não é um arquivo válido.")
        return normalizar_segredo_keyfile(caminho.read_bytes())

    # Verifica se o arquivo do cofre usa o formato antigo (menos seguro)
    def _arquivo_usa_formato_legado(self, dados_arquivo: dict[str, Any]) -> bool:
        """Detecta se o arquivo ainda usa o formato antigo baseado em Fernet."""
        if int(dados_arquivo.get("versao", 1)) < VERSAO_COFRE_ATUAL:
            return True
        if str(dados_arquivo.get("kdf", {}).get("algoritmo", "")).lower() != "argon2id":
            return True
        return not isinstance(dados_arquivo.get("dados_cofre_criptografados"), dict)

    # Carrega o arquivo do cofre e valida se todos os campos obrigatórios estão presentes
    # Usa cache em memória para evitar reler o JSON do disco a cada chamada
    # (a UI consulta isso várias vezes por segundo em telas de bloqueio/login)
    def _carregar_arquivo_obrigatorio(self) -> dict[str, Any]:
        """Carrega arquivo persistido com cache; valida campos críticos."""
        # Se já temos em cache, devolve direto (sem I/O)
        if self._cache_arquivo is not None:
            return self._cache_arquivo

        dados_arquivo = self._armazenamento.carregar()
        if dados_arquivo is None:
            raise FileNotFoundError("Cofre ainda não foi inicializado.")

        campos_obrigatorios = [
            "kdf",
            "verificador_senha",
            "dados_cofre_criptografados",
            "controle_acesso",
            "politica_acesso",
        ]
        faltantes = [campo for campo in campos_obrigatorios if campo not in dados_arquivo]
        if faltantes:
            raise ValueError(f"Arquivo do cofre incompleto: faltando {', '.join(faltantes)}.")

        # Guarda no cache para próximas leituras desta sessão
        self._cache_arquivo = dados_arquivo
        return dados_arquivo

    # Wrapper de escrita que SEMPRE invalida o cache antes/depois
    # Use este método em vez de chamar self._armazenamento.salvar diretamente
    def _salvar_arquivo(self, dados_arquivo: dict[str, Any]) -> None:
        """Salva no disco e atualiza o cache para refletir o novo conteúdo."""
        self._armazenamento.salvar(dados_arquivo)
        # O dict salvo é o novo conteúdo do disco; vira o cache atual
        self._cache_arquivo = dados_arquivo

    # Carrega e valida um arquivo de exportação de credenciais
    @staticmethod
    def _carregar_pacote_exportacao(caminho_origem: str | Path) -> dict[str, Any]:
        """Carrega e valida minimamente um pacote de exportação de credenciais."""
        caminho = Path(caminho_origem).expanduser().resolve()
        if not caminho.exists():
            raise ValueError("O arquivo de importação não foi encontrado.")
        if not caminho.is_file():
            raise ValueError("O caminho informado para importação não é um arquivo válido.")

        try:
            with caminho.open("r", encoding="utf-8") as arquivo:
                pacote = json.load(arquivo)
        except json.JSONDecodeError as exc:
            raise ValueError("O arquivo de importação não é um JSON válido.") from exc

        if not isinstance(pacote, dict):
            raise ValueError("O pacote de importação possui estrutura inválida.")

        if pacote.get("tipo") != "exportacao_credenciais_cofre_seguro":
            raise ValueError("O arquivo selecionado não é uma exportação válida do cofre.")

        campos_obrigatorios = [
            "kdf",
            "verificador_senha",
            "dados_exportados_criptografados",
        ]
        faltantes = [campo for campo in campos_obrigatorios if campo not in pacote]
        if faltantes:
            raise ValueError(
                f"Pacote de importação incompleto: faltando {', '.join(faltantes)}."
            )

        return pacote

    # Obtém as regras de política de acesso, preenchendo padrões quando ausentes
    def _politica_acesso(self, dados_arquivo: dict[str, Any]) -> dict[str, int]:
        """Resolve política de acesso com valores padrão em caso de ausência."""
        politica_salva = dados_arquivo.get("politica_acesso", {})
        politica: dict[str, int] = {}
        for chave, valor_padrao in self.POLITICA_PADRAO.items():
            valor = politica_salva.get(chave, valor_padrao)
            politica[chave] = int(valor)
        dados_arquivo["politica_acesso"] = politica
        return politica

    # Converte o nome do algoritmo KDF para um texto amigável para mostrar na tela
    @staticmethod
    def _rotulo_kdf(kdf: dict[str, Any]) -> str:
        """Traduz configuração do KDF para rótulo da interface."""
        algoritmo = str(kdf.get("algoritmo", "scrypt")).lower()
        if algoritmo == "argon2id":
            memoria_mb = int(kdf.get("memory_cost", 0)) // 1024
            return f"Argon2id ({memoria_mb} MB)"
        return "scrypt (legado)"

    # Converte o nome do algoritmo de criptografia para um texto amigável para a tela
    @staticmethod
    def _rotulo_cifra(carga_criptografada: Any) -> str:
        """Traduz a cifra em uso para rótulo da interface."""
        if isinstance(carga_criptografada, dict):
            algoritmo = str(carga_criptografada.get("algoritmo", "")).lower()
            if algoritmo == "aes-256-gcm":
                return "AES-256-GCM"
        return "Fernet (legado)"

    # Retorna a data e hora atuais no formato ISO padrão
    @staticmethod
    def _agora_iso() -> str:
        """Retorna timestamp ISO local com precisão de segundos."""
        return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
