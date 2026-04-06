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
    """Implementa regras do cofre, autenticação e operações de credenciais."""

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
        dados_cofre = {
            "credenciais": [],       # Lista vazia de credenciais (ainda não tem nenhuma)
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
        self._armazenamento.salvar(estrutura_arquivo)

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
                self._armazenamento.salvar(dados_arquivo)

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
        self._armazenamento.salvar(dados_arquivo)

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

    # Lista as credenciais salvas no cofre, podendo filtrar por um termo de busca
    def listar_credenciais(self, filtro: str = "") -> list[dict[str, str]]:
        """Lista credenciais do cofre sem expor a senha no resultado padrão."""
        # Garante que o usuário está logado antes de continuar
        self._garantir_sessao()
        # Remove espaços e converte o filtro para minúsculas para busca sem distinção de maiúsculas
        termo = filtro.strip().lower()
        # Lista que vai guardar os resultados
        saida: list[dict[str, str]] = []

        # Percorre cada credencial salva no cofre
        for credencial in self._dados_cofre.get("credenciais", []):
            # Pega os campos de cada credencial
            servico = str(credencial.get("servico", ""))
            login = str(credencial.get("login", ""))
            observacao = str(credencial.get("observacao", ""))
            # Se tem filtro e o termo não aparece nos campos, pula essa credencial
            if termo and termo not in f"{servico} {login} {observacao}".lower():
                continue
            # Adiciona a credencial na lista de saída (sem a senha, por segurança)
            saida.append(
                {
                    "id": str(credencial.get("id", "")),
                    "servico": servico,
                    "login": login,
                    "observacao": observacao,
                    "atualizado_em": str(credencial.get("atualizado_em", "")),
                }
            )

        # Ordena a lista pelo nome do serviço em ordem alfabética
        saida.sort(key=lambda item: item["servico"].lower())
        # Retorna a lista de credenciais encontradas
        return saida

    # Busca e retorna uma credencial específica pelo seu identificador (ID)
    def obter_credencial(
        self,
        credencial_id: str,
        incluir_senha: bool = False,
    ) -> dict[str, str] | None:
        """Obtém uma credencial específica pelo identificador interno."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Procura a credencial pelo ID
        credencial = self._buscar_credencial_por_id(credencial_id)
        # Se não encontrou, retorna None (nada)
        if credencial is None:
            return None

        # Monta o dicionário com os dados da credencial (sem a senha por padrão)
        resultado = {
            "id": str(credencial.get("id", "")),
            "servico": str(credencial.get("servico", "")),
            "login": str(credencial.get("login", "")),
            "observacao": str(credencial.get("observacao", "")),
            "atualizado_em": str(credencial.get("atualizado_em", "")),
        }
        # Se foi pedido para incluir a senha, adiciona ela no resultado
        if incluir_senha:
            resultado["senha"] = str(credencial.get("senha", ""))
        # Retorna os dados da credencial
        return resultado

    # Adiciona uma nova credencial (serviço, login, senha) ao cofre
    def adicionar_credencial(
        self,
        servico: str,
        login: str,
        senha: str,
        observacao: str = "",
    ) -> str:
        """Adiciona nova credencial validada e persiste o cofre criptografado."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Remove espaços extras do início e fim dos campos
        servico_limpo = servico.strip()
        login_limpo = login.strip()
        observacao_limpa = observacao.strip()

        # Verifica se o campo serviço foi preenchido
        if not servico_limpo:
            raise ValueError("O campo Serviço é obrigatório.")
        # Verifica se o campo login foi preenchido
        if not login_limpo:
            raise ValueError("O campo Usuário/E-mail é obrigatório.")
        # Verifica se o campo senha foi preenchido
        if not senha:
            raise ValueError("O campo Senha é obrigatório.")

        # Verifica se já existe uma credencial com o mesmo serviço e login
        if self._credencial_duplicada(servico_limpo, login_limpo):
            raise ValueError("Já existe uma credencial para este serviço e usuário.")

        # Pega a data e hora atuais
        agora = self._agora_iso()
        # Monta o dicionário da nova credencial com todos os dados
        credencial = {
            "id": secrets.token_hex(16),    # Gera um identificador único aleatório
            "servico": servico_limpo,
            "login": login_limpo,
            "senha": senha,
            "observacao": observacao_limpa,
            "criado_em": agora,             # Data de criação
            "atualizado_em": agora,         # Data da última atualização
        }

        # Adiciona a nova credencial na lista de credenciais do cofre
        self._dados_cofre["credenciais"].append(credencial)
        # Criptografa e salva o cofre atualizado no disco
        self._persistir_cofre()
        # Retorna o ID da credencial criada
        return credencial["id"]

    # Edita (atualiza) uma credencial que já existe no cofre
    def editar_credencial(
        self,
        credencial_id: str,
        servico: str,
        login: str,
        senha: str,
        observacao: str = "",
    ) -> None:
        """Atualiza uma credencial existente com validação de duplicidade."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Remove espaços extras dos campos
        servico_limpo = servico.strip()
        login_limpo = login.strip()
        observacao_limpa = observacao.strip()

        # Verifica se o campo serviço foi preenchido
        if not servico_limpo:
            raise ValueError("O campo Serviço é obrigatório.")
        # Verifica se o campo login foi preenchido
        if not login_limpo:
            raise ValueError("O campo Usuário/E-mail é obrigatório.")
        # Verifica se o campo senha foi preenchido
        if not senha:
            raise ValueError("O campo Senha é obrigatório.")

        # Busca a credencial pelo ID
        credencial = self._buscar_credencial_por_id(credencial_id)
        # Se não encontrou, mostra erro
        if credencial is None:
            raise ValueError("Credencial não encontrada.")

        # Verifica se já existe OUTRA credencial com o mesmo serviço e login
        # (ignora a própria credencial que está sendo editada)
        if self._credencial_duplicada(servico_limpo, login_limpo, ignorar_id=credencial_id):
            raise ValueError("Já existe outra credencial para este serviço e usuário.")

        # Atualiza os campos da credencial com os novos valores
        credencial["servico"] = servico_limpo
        credencial["login"] = login_limpo
        credencial["senha"] = senha
        credencial["observacao"] = observacao_limpa
        # Atualiza a data de modificação
        credencial["atualizado_em"] = self._agora_iso()
        # Criptografa e salva o cofre atualizado no disco
        self._persistir_cofre()

    # Remove (exclui) uma credencial do cofre
    def excluir_credencial(self, credencial_id: str) -> None:
        """Remove uma credencial do cofre e grava as alterações."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Pega a lista de credenciais atual
        credenciais = self._dados_cofre.get("credenciais", [])
        # Guarda o tamanho da lista antes de filtrar
        tamanho_antes = len(credenciais)
        # Cria uma nova lista SEM a credencial que queremos excluir
        credenciais_filtradas = [item for item in credenciais if item.get("id") != credencial_id]

        # Se o tamanho não mudou, significa que não encontrou a credencial para excluir
        if len(credenciais_filtradas) == tamanho_antes:
            raise ValueError("Credencial não encontrada.")

        # Substitui a lista de credenciais pela lista filtrada (sem a excluída)
        self._dados_cofre["credenciais"] = credenciais_filtradas
        # Criptografa e salva o cofre atualizado no disco
        self._persistir_cofre()

    # Verifica a senha mestra novamente para confirmar ações importantes (como revelar senha)
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

    # Mostra a senha de uma credencial, mas só se o usuário confirmar a senha mestra
    def revelar_senha(self, credencial_id: str, senha_mestra: str) -> str:
        """Revela a senha de uma credencial após autenticação correta."""
        # Garante que o usuário está logado
        self._garantir_sessao()
        # Verifica a senha mestra para garantir que é realmente o dono do cofre
        if not self.autenticar_acao_sensivel(senha_mestra):
            raise PermissionError("Falha de autenticação para revelar a senha.")

        # Busca a credencial pelo ID
        credencial = self._buscar_credencial_por_id(credencial_id)
        # Se não encontrou, mostra erro
        if credencial is None:
            raise ValueError("Credencial não encontrada.")

        # Retorna a senha da credencial
        return str(credencial.get("senha", ""))

    # Exporta (copia) credenciais para um arquivo separado, protegido por outra senha
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

        # Pega todas as credenciais do cofre
        credenciais_fonte = self._dados_cofre.get("credenciais", [])
        # Se foram informados IDs específicos, cria um conjunto para filtrar
        ids_filtrados = set(credencial_ids or [])
        # Lista que vai guardar as credenciais selecionadas para exportação
        credenciais_exportadas: list[dict[str, Any]] = []

        # Percorre cada credencial do cofre
        for credencial in credenciais_fonte:
            # Se há filtro de IDs e esta credencial não está na lista, pula
            if ids_filtrados and str(credencial.get("id")) not in ids_filtrados:
                continue
            # Adiciona uma cópia da credencial na lista de exportação
            credenciais_exportadas.append(dict(credencial))

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
            "tipo": "exportacao_credenciais_cofre_seguro",  # Identificador do tipo de arquivo
            "versao_exportacao": 1,                          # Versão do formato de exportação
            "kdf": registro["kdf"],                          # Configurações de derivação de chave
            "verificador_senha": registro["verificador_senha"],  # Verificador da senha
            "dados_exportados_criptografados": criptografar_objeto(  # Dados criptografados
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

            # Pega os campos do item, removendo espaços extras
            servico = str(item.get("servico", "")).strip()
            login = str(item.get("login", "")).strip()
            senha = str(item.get("senha", ""))
            observacao = str(item.get("observacao", "")).strip()

            # Se falta algum campo obrigatório, ignora esse item
            if not servico or not login or not senha:
                ignoradas += 1
                continue

            # Procura se já existe uma credencial com o mesmo serviço e login
            existente = self._buscar_credencial_por_servico_login(servico, login)
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

            # Se não existe, cria uma nova credencial
            nova_credencial = {
                "id": secrets.token_hex(16),  # Gera um novo ID aleatório
                "servico": servico,
                "login": login,
                "senha": senha,
                "observacao": observacao,
                "criado_em": str(item.get("criado_em", agora)),         # Mantém a data original se tiver
                "atualizado_em": str(item.get("atualizado_em", agora)), # Mantém a data original se tiver
            }
            # Adiciona a nova credencial no cofre
            self._dados_cofre["credenciais"].append(nova_credencial)
            inseridas += 1

        # Se houve alguma inserção ou atualização, salva o cofre
        if inseridas or atualizadas:
            self._persistir_cofre()

        # Retorna o resumo da importação (quantas foram inseridas, atualizadas e ignoradas)
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
        self._armazenamento.salvar(estrutura_arquivo)

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
    def gerar_senha(self, comprimento: int = 16) -> str:
        """Gera senha forte para preenchimento rápido no formulário."""
        return gerar_senha_forte(comprimento=comprimento)

    # Encerra a sessão atual, limpando todos os dados sensíveis da memória
    def encerrar_sessao(self) -> None:
        """Limpa referências de sessão para reduzir exposição em memória."""
        # Se existem dados do cofre na memória, apaga as senhas armazenadas
        if isinstance(self._dados_cofre, dict):
            # Percorre cada credencial e apaga a senha da memória
            for credencial in self._dados_cofre.get("credenciais", []):
                if "senha" in credencial:
                    credencial["senha"] = ""

        # Limpa todas as referências de sessão (dados, chave e keyfile)
        self._dados_cofre = None
        self._chave_sessao = None
        self._segredo_keyfile_sessao = None

    # --- Métodos internos (privados) - usados apenas dentro desta classe ---

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
        self._armazenamento.salvar(dados_arquivo)

    # Descriptografa os dados do cofre, tratando formato atual e legado (antigo)
    def _abrir_carga_criptografada(
        self,
        dados_arquivo: dict[str, Any],
        senha_mestra: str,
        segredo_keyfile: bytes | None,
    ) -> tuple[dict[str, Any], bytes | None]:
        """Abre os dados do cofre conforme o formato atual ou legado."""
        # Se o arquivo usa o formato antigo (legado), usa o método antigo de descriptografia
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

    # Migra (atualiza) cofres no formato antigo para o formato moderno mais seguro
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
        self._armazenamento.salvar(estrutura_arquivo)
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
            "verificador_senha": registro["verificador_senha"],  # Hash da senha para verificação
            "dados_cofre_criptografados": criptografar_objeto(dados_cofre, chave_criptografia),  # Dados embaralhados
            "controle_acesso": {
                # Número de tentativas de login erradas seguidas
                "falhas_consecutivas": int((controle_acesso or {}).get("falhas_consecutivas", 0)),
                # Momento até quando o cofre está bloqueado
                "bloqueado_ate": float((controle_acesso or {}).get("bloqueado_ate", 0.0)),
                # Quantas vezes o cofre já foi bloqueado
                "bloqueios_aplicados": int((controle_acesso or {}).get("bloqueios_aplicados", 0)),
            },
            # Regras de política de acesso (ou usa as padrão se não tiver)
            "politica_acesso": dict(politica_acesso or self.POLITICA_PADRAO),
            "metadados": metadados,  # Informações sobre datas de criação e atualização
        }

    # Procura uma credencial na lista pelo seu identificador único (ID)
    def _buscar_credencial_por_id(self, credencial_id: str) -> dict[str, Any] | None:
        """Procura uma credencial pelo identificador único."""
        # Percorre cada credencial do cofre
        for credencial in self._dados_cofre.get("credenciais", []):
            # Se o ID bate, retorna a credencial encontrada
            if credencial.get("id") == credencial_id:
                return credencial
        # Se não encontrou nenhuma, retorna None (nada)
        return None

    # Procura uma credencial pelo par serviço + login (ex: "Gmail" + "joao@gmail.com")
    def _buscar_credencial_por_servico_login(
        self,
        servico: str,
        login: str,
    ) -> dict[str, Any] | None:
        """Procura uma credencial pelo par serviço e usuário."""
        # Converte para minúsculas para comparar sem diferenciar maiúsculas
        alvo_servico = servico.lower()
        alvo_login = login.lower()
        # Percorre cada credencial do cofre
        for credencial in self._dados_cofre.get("credenciais", []):
            # Pega o serviço e login da credencial atual em minúsculas
            servico_atual = str(credencial.get("servico", "")).lower()
            login_atual = str(credencial.get("login", "")).lower()
            # Se ambos batem, retorna a credencial encontrada
            if servico_atual == alvo_servico and login_atual == alvo_login:
                return credencial
        # Se não encontrou, retorna None
        return None

    # Verifica se já existe outra credencial com o mesmo serviço e login
    def _credencial_duplicada(
        self,
        servico: str,
        login: str,
        ignorar_id: str | None = None,
    ) -> bool:
        """Valida duplicidade por serviço e usuário de forma case-insensitive."""
        # Converte para minúsculas para comparação sem diferenciar maiúsculas
        alvo_servico = servico.lower()
        alvo_login = login.lower()

        # Percorre cada credencial do cofre
        for credencial in self._dados_cofre.get("credenciais", []):
            # Se há um ID para ignorar (ex: ao editar), pula essa credencial
            if ignorar_id and credencial.get("id") == ignorar_id:
                continue
            # Pega serviço e login em minúsculas
            servico_atual = str(credencial.get("servico", "")).lower()
            login_atual = str(credencial.get("login", "")).lower()
            # Se encontrou uma duplicata, retorna True (sim, é duplicada)
            if servico_atual == alvo_servico and login_atual == alvo_login:
                return True

        # Se não encontrou duplicata, retorna False
        return False

    # Verifica se o usuário está logado; se não estiver, impede a operação
    def _garantir_sessao(self) -> None:
        """Garante que exista sessão autenticada antes de operar no cofre."""
        # Se não está autenticado, lança um erro de permissão
        if not self.esta_autenticado():
            raise PermissionError("É necessário fazer login para acessar o cofre.")

    # Garante que a estrutura interna do cofre tenha os campos mínimos necessários
    def _normalizar_estrutura_cofre(self) -> None:
        """Normaliza estrutura interna mínima do cofre descriptografado."""
        # Se não existe a lista de credenciais, cria uma vazia
        self._dados_cofre.setdefault("credenciais", [])
        # Se não existem metadados, cria com as datas atuais
        self._dados_cofre.setdefault(
            "metadados",
            {
                "criado_em": self._agora_iso(),
                "atualizado_em": self._agora_iso(),
            },
        )

    # Carrega o conteúdo de um keyfile do disco e retorna o segredo normalizado
    def _carregar_segredo_keyfile(self, caminho_keyfile: str) -> bytes:
        """Carrega keyfile do disco e devolve seu segredo normalizado."""
        # Converte e resolve o caminho do arquivo
        caminho = Path(caminho_keyfile).expanduser().resolve()
        # Verifica se o arquivo existe
        if not caminho.exists():
            raise ValueError("O keyfile informado não foi encontrado.")
        # Verifica se é realmente um arquivo (e não uma pasta)
        if not caminho.is_file():
            raise ValueError("O caminho informado para keyfile não é um arquivo válido.")
        # Lê o conteúdo do arquivo e normaliza para uso como segredo
        return normalizar_segredo_keyfile(caminho.read_bytes())

    # Verifica se o arquivo do cofre usa o formato antigo (menos seguro)
    def _arquivo_usa_formato_legado(self, dados_arquivo: dict[str, Any]) -> bool:
        """Detecta se o arquivo ainda usa o formato antigo baseado em Fernet."""
        # Se a versão do arquivo é menor que a atual, é formato legado
        if int(dados_arquivo.get("versao", 1)) < VERSAO_COFRE_ATUAL:
            return True
        # Se o algoritmo de KDF não é Argon2id, é formato legado
        if str(dados_arquivo.get("kdf", {}).get("algoritmo", "")).lower() != "argon2id":
            return True
        # Se os dados criptografados não são um dicionário, é formato legado
        return not isinstance(dados_arquivo.get("dados_cofre_criptografados"), dict)

    # Carrega o arquivo do cofre e verifica se todos os campos obrigatórios estão presentes
    def _carregar_arquivo_obrigatorio(self) -> dict[str, Any]:
        """Carrega arquivo persistido e valida campos críticos obrigatórios."""
        # Carrega o arquivo do disco
        dados_arquivo = self._armazenamento.carregar()
        # Se não conseguiu carregar, o cofre não existe
        if dados_arquivo is None:
            raise FileNotFoundError("Cofre ainda não foi inicializado.")

        # Lista de campos que o arquivo PRECISA ter para ser válido
        campos_obrigatorios = [
            "kdf",
            "verificador_senha",
            "dados_cofre_criptografados",
            "controle_acesso",
            "politica_acesso",
        ]
        # Verifica quais campos estão faltando
        faltantes = [campo for campo in campos_obrigatorios if campo not in dados_arquivo]
        # Se falta algum campo, mostra erro informando quais estão faltando
        if faltantes:
            raise ValueError(f"Arquivo do cofre incompleto: faltando {', '.join(faltantes)}.")

        # Retorna os dados do arquivo validados
        return dados_arquivo

    # @staticmethod indica que este método não precisa de uma instância da classe para funcionar
    # Carrega e valida um arquivo de exportação de credenciais
    @staticmethod
    def _carregar_pacote_exportacao(caminho_origem: str | Path) -> dict[str, Any]:
        """Carrega e valida minimamente um pacote de exportação de credenciais."""
        # Converte e resolve o caminho do arquivo
        caminho = Path(caminho_origem).expanduser().resolve()
        # Verifica se o arquivo existe
        if not caminho.exists():
            raise ValueError("O arquivo de importação não foi encontrado.")
        # Verifica se é realmente um arquivo
        if not caminho.is_file():
            raise ValueError("O caminho informado para importação não é um arquivo válido.")

        # Tenta abrir e ler o arquivo como JSON
        try:
            # Abre o arquivo para leitura com codificação UTF-8
            with caminho.open("r", encoding="utf-8") as arquivo:
                # Converte o conteúdo JSON em um dicionário Python
                pacote = json.load(arquivo)
        # Se o arquivo não é um JSON válido, mostra erro
        except json.JSONDecodeError as exc:
            raise ValueError("O arquivo de importação não é um JSON válido.") from exc

        # Verifica se o conteúdo carregado é um dicionário
        if not isinstance(pacote, dict):
            raise ValueError("O pacote de importação possui estrutura inválida.")

        # Verifica se o tipo do pacote é uma exportação válida do cofre
        if pacote.get("tipo") != "exportacao_credenciais_cofre_seguro":
            raise ValueError("O arquivo selecionado não é uma exportação válida do cofre.")

        # Lista de campos obrigatórios no pacote de exportação
        campos_obrigatorios = [
            "kdf",
            "verificador_senha",
            "dados_exportados_criptografados",
        ]
        # Verifica quais campos estão faltando
        faltantes = [campo for campo in campos_obrigatorios if campo not in pacote]
        # Se falta algum campo, mostra erro
        if faltantes:
            raise ValueError(
                f"Pacote de importação incompleto: faltando {', '.join(faltantes)}."
            )

        # Retorna o pacote validado
        return pacote

    # Obtém as regras de política de acesso, preenchendo com valores padrão se necessário
    def _politica_acesso(self, dados_arquivo: dict[str, Any]) -> dict[str, int]:
        """Resolve política de acesso com valores padrão em caso de ausência."""
        # Pega a política salva no arquivo (ou dicionário vazio se não existir)
        politica_salva = dados_arquivo.get("politica_acesso", {})
        # Cria um novo dicionário para a política resolvida
        politica: dict[str, int] = {}
        # Para cada regra padrão, pega o valor salvo ou usa o padrão
        for chave, valor_padrao in self.POLITICA_PADRAO.items():
            valor = politica_salva.get(chave, valor_padrao)
            politica[chave] = int(valor)
        # Atualiza a política no arquivo
        dados_arquivo["politica_acesso"] = politica
        # Retorna a política completa
        return politica

    # @staticmethod indica que este método não precisa de uma instância da classe
    # Converte o nome do algoritmo KDF para um texto amigável para mostrar na tela
    @staticmethod
    def _rotulo_kdf(kdf: dict[str, Any]) -> str:
        """Traduz configuração do KDF para rótulo da interface."""
        # Pega o nome do algoritmo em minúsculas
        algoritmo = str(kdf.get("algoritmo", "scrypt")).lower()
        # Se é Argon2id (formato moderno), mostra o nome e a quantidade de memória usada
        if algoritmo == "argon2id":
            memoria_mb = int(kdf.get("memory_cost", 0)) // 1024
            return f"Argon2id ({memoria_mb} MB)"
        # Se é qualquer outro, mostra como "scrypt (legado)" (formato antigo)
        return "scrypt (legado)"

    # @staticmethod indica que este método não precisa de uma instância da classe
    # Converte o nome do algoritmo de criptografia para um texto amigável para a tela
    @staticmethod
    def _rotulo_cifra(carga_criptografada: Any) -> str:
        """Traduz a cifra em uso para rótulo da interface."""
        # Se os dados criptografados são um dicionário, verifica o algoritmo
        if isinstance(carga_criptografada, dict):
            algoritmo = str(carga_criptografada.get("algoritmo", "")).lower()
            # Se é AES-256-GCM (formato moderno), mostra o nome
            if algoritmo == "aes-256-gcm":
                return "AES-256-GCM"
        # Se não é formato moderno, mostra como "Fernet (legado)" (formato antigo)
        return "Fernet (legado)"

    # @staticmethod indica que este método não precisa de uma instância da classe
    # Retorna a data e hora atuais no formato ISO padrão internacional
    @staticmethod
    def _agora_iso() -> str:
        """Retorna timestamp ISO local com precisão de segundos."""
        # Pega a hora atual em UTC, converte para o fuso local, e formata como texto ISO
        return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
