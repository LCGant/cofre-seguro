from __future__ import annotations

import json
import math
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .security import (
    VERSAO_COFRE_ATUAL,
    criar_registro_senha_mestra,
    criptografar_objeto,
    descriptografar_objeto,
    descriptografar_objeto_legado,
    gerar_chave_criptografia,
    gerar_chave_fernet_legado,
    gerar_conteudo_keyfile,
    gerar_senha_forte,
    normalizar_segredo_keyfile,
    validar_forca_senha_mestra,
    verificar_senha_mestra,
)
from .storage import GerenciadorArquivoCofre


@dataclass(slots=True)
class ResultadoLogin:
    """Representa o resultado da tentativa de autenticação no cofre."""

    sucesso: bool
    mensagem: str
    atraso_segundos: int = 0
    bloqueio_restante: int = 0


class ServicoCofre:
    """Implementa regras do cofre, autenticação e operações de credenciais."""

    POLITICA_PADRAO = {
        "max_tentativas": 5,
        "atraso_max_segundos": 8,
        "bloqueio_base_segundos": 30,
        "bloqueio_max_segundos": 300,
    }

    def __init__(self, armazenamento: GerenciadorArquivoCofre) -> None:
        """Inicializa o serviço com o gerenciador de persistência local."""
        self._armazenamento = armazenamento
        self._chave_sessao: bytes | None = None
        self._dados_cofre: dict[str, Any] | None = None
        self._segredo_keyfile_sessao: bytes | None = None

    def existe_cofre(self) -> bool:
        """Indica se já existe um cofre inicializado no disco."""
        return self._armazenamento.existe_cofre()

    def cofre_requer_keyfile(self) -> bool:
        """Informa se o cofre configurado exige keyfile para autenticação."""
        if not self.existe_cofre():
            return False
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        return bool(dados_arquivo.get("kdf", {}).get("usa_keyfile", False))

    def obter_resumo_seguranca(self) -> dict[str, Any]:
        """Retorna metadados resumidos de proteção para exibição na interface."""
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

        dados_arquivo = self._carregar_arquivo_obrigatorio()
        kdf = dados_arquivo.get("kdf", {})
        formato_legado = self._arquivo_usa_formato_legado(dados_arquivo)
        algoritmo_kdf = self._rotulo_kdf(kdf)
        algoritmo_cifra = self._rotulo_cifra(dados_arquivo.get("dados_cofre_criptografados"))

        return {
            "configurado": True,
            "versao": int(dados_arquivo.get("versao", 1)),
            "algoritmo_kdf": algoritmo_kdf,
            "algoritmo_cifra": algoritmo_cifra,
            "usa_keyfile": bool(kdf.get("usa_keyfile", False)),
            "status_formato": "Legado" if formato_legado else "Atual",
            "memoria_argon2_mb": int(kdf.get("memory_cost", 0)) // 1024,
        }

    def criar_keyfile(self, caminho_destino: str | Path) -> Path:
        """Cria um keyfile aleatório em disco com permissão restrita quando possível."""
        caminho = Path(caminho_destino).expanduser().resolve()
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if caminho.exists():
            raise ValueError("Já existe um arquivo nesse caminho para o keyfile.")

        caminho.write_bytes(gerar_conteudo_keyfile())
        try:
            caminho.chmod(0o600)
        except OSError:
            pass
        return caminho

    def criar_cofre(self, senha_mestra: str, caminho_keyfile: str | None = None) -> None:
        """Cria um novo cofre local com senha mestra e keyfile opcional."""
        if self.existe_cofre():
            raise ValueError("Já existe um cofre inicializado neste caminho.")

        senha_valida, mensagem = validar_forca_senha_mestra(senha_mestra)
        if not senha_valida:
            raise ValueError(mensagem)

        segredo_keyfile = self._carregar_segredo_keyfile(caminho_keyfile) if caminho_keyfile else None
        registro = criar_registro_senha_mestra(senha_mestra, segredo_keyfile=segredo_keyfile)
        chave_aes = gerar_chave_criptografia(
            senha_mestra,
            registro["kdf"],
            segredo_keyfile=segredo_keyfile,
        )
        agora = self._agora_iso()
        dados_cofre = {
            "credenciais": [],
            "metadados": {
                "criado_em": agora,
                "atualizado_em": agora,
            },
        }

        estrutura_arquivo = self._montar_estrutura_arquivo(
            registro=registro,
            dados_cofre=dados_cofre,
            chave_criptografia=chave_aes,
            controle_acesso={
                "falhas_consecutivas": 0,
                "bloqueado_ate": 0.0,
                "bloqueios_aplicados": 0,
            },
            politica_acesso=dict(self.POLITICA_PADRAO),
            metadados_arquivo={
                "criado_em": agora,
                "atualizado_em": agora,
            },
        )
        self._armazenamento.salvar(estrutura_arquivo)

    def tentar_login(
        self,
        senha_mestra: str,
        caminho_keyfile: str | None = None,
    ) -> ResultadoLogin:
        """Valida login com atraso progressivo, keyfile opcional e migração legada."""
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        controle = dados_arquivo.setdefault("controle_acesso", {})
        politica = self._politica_acesso(dados_arquivo)
        agora_ts = time.time()

        bloqueado_ate = float(controle.get("bloqueado_ate", 0.0))
        if bloqueado_ate > agora_ts:
            restante = math.ceil(bloqueado_ate - agora_ts)
            mensagem = (
                "Cofre temporariamente bloqueado por múltiplas falhas. "
                f"Tente novamente em {restante} segundo(s)."
            )
            return ResultadoLogin(
                sucesso=False,
                mensagem=mensagem,
                atraso_segundos=0,
                bloqueio_restante=restante,
            )

        segredo_keyfile = None
        if bool(dados_arquivo.get("kdf", {}).get("usa_keyfile", False)):
            if not caminho_keyfile:
                raise ValueError("Este cofre exige um keyfile para concluir o login.")
            segredo_keyfile = self._carregar_segredo_keyfile(caminho_keyfile)

        senha_ok = verificar_senha_mestra(
            senha_mestra,
            dados_arquivo["kdf"],
            dados_arquivo["verificador_senha"],
            segredo_keyfile=segredo_keyfile,
        )

        if senha_ok:
            formato_legado = self._arquivo_usa_formato_legado(dados_arquivo)
            dados_cofre, chave_sessao = self._abrir_carga_criptografada(
                dados_arquivo,
                senha_mestra,
                segredo_keyfile,
            )
            if not isinstance(dados_cofre, dict):
                raise ValueError("Estrutura interna do cofre inválida.")

            self._dados_cofre = dados_cofre
            self._chave_sessao = chave_sessao
            self._segredo_keyfile_sessao = segredo_keyfile
            self._normalizar_estrutura_cofre()

            controle["falhas_consecutivas"] = 0
            controle["bloqueado_ate"] = 0.0

            migrado = False
            if formato_legado:
                migrado = self._migrar_arquivo_se_necessario(
                    dados_arquivo=dados_arquivo,
                    senha_mestra=senha_mestra,
                    dados_cofre=self._dados_cofre,
                    segredo_keyfile=segredo_keyfile,
                )

            if not migrado:
                dados_arquivo.setdefault("metadados", {})["atualizado_em"] = self._agora_iso()
                self._armazenamento.salvar(dados_arquivo)

            mensagem = "Login realizado com sucesso."
            if migrado:
                mensagem = (
                    "Login realizado com sucesso. "
                    "O cofre foi atualizado automaticamente para proteção mais forte."
                )

            return ResultadoLogin(True, mensagem)

        falhas = int(controle.get("falhas_consecutivas", 0)) + 1
        controle["falhas_consecutivas"] = falhas

        atraso = min(
            int(politica["atraso_max_segundos"]),
            2 ** max(0, falhas - 1),
        )

        bloqueio_restante = 0
        mensagem = (
            "Credenciais de desbloqueio incorretas. "
            f"Aguarde {atraso} segundo(s) para tentar novamente."
        )

        if falhas >= int(politica["max_tentativas"]):
            bloqueios_aplicados = int(controle.get("bloqueios_aplicados", 0)) + 1
            controle["bloqueios_aplicados"] = bloqueios_aplicados
            duracao_bloqueio = min(
                int(politica["bloqueio_max_segundos"]),
                int(politica["bloqueio_base_segundos"]) * bloqueios_aplicados,
            )
            controle["bloqueado_ate"] = agora_ts + duracao_bloqueio
            controle["falhas_consecutivas"] = 0
            atraso = 0
            bloqueio_restante = duracao_bloqueio
            mensagem = (
                "Limite de tentativas atingido. "
                f"Cofre bloqueado por {duracao_bloqueio} segundo(s)."
            )

        dados_arquivo.setdefault("metadados", {})["atualizado_em"] = self._agora_iso()
        self._armazenamento.salvar(dados_arquivo)

        return ResultadoLogin(
            sucesso=False,
            mensagem=mensagem,
            atraso_segundos=atraso,
            bloqueio_restante=bloqueio_restante,
        )

    def tempo_restante_bloqueio(self) -> int:
        """Retorna quantos segundos faltam para o fim de um bloqueio ativo."""
        if not self.existe_cofre():
            return 0
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        bloqueado_ate = float(dados_arquivo.get("controle_acesso", {}).get("bloqueado_ate", 0.0))
        restante = bloqueado_ate - time.time()
        if restante <= 0:
            return 0
        return math.ceil(restante)

    def esta_autenticado(self) -> bool:
        """Indica se existe sessão autenticada com dados descriptografados."""
        return self._chave_sessao is not None and self._dados_cofre is not None

    def listar_credenciais(self, filtro: str = "") -> list[dict[str, str]]:
        """Lista credenciais do cofre sem expor a senha no resultado padrão."""
        self._garantir_sessao()
        termo = filtro.strip().lower()
        saida: list[dict[str, str]] = []

        for credencial in self._dados_cofre.get("credenciais", []):
            servico = str(credencial.get("servico", ""))
            login = str(credencial.get("login", ""))
            observacao = str(credencial.get("observacao", ""))
            if termo and termo not in f"{servico} {login} {observacao}".lower():
                continue
            saida.append(
                {
                    "id": str(credencial.get("id", "")),
                    "servico": servico,
                    "login": login,
                    "observacao": observacao,
                    "atualizado_em": str(credencial.get("atualizado_em", "")),
                }
            )

        saida.sort(key=lambda item: item["servico"].lower())
        return saida

    def obter_credencial(
        self,
        credencial_id: str,
        incluir_senha: bool = False,
    ) -> dict[str, str] | None:
        """Obtém uma credencial específica pelo identificador interno."""
        self._garantir_sessao()
        credencial = self._buscar_credencial_por_id(credencial_id)
        if credencial is None:
            return None

        resultado = {
            "id": str(credencial.get("id", "")),
            "servico": str(credencial.get("servico", "")),
            "login": str(credencial.get("login", "")),
            "observacao": str(credencial.get("observacao", "")),
            "atualizado_em": str(credencial.get("atualizado_em", "")),
        }
        if incluir_senha:
            resultado["senha"] = str(credencial.get("senha", ""))
        return resultado

    def adicionar_credencial(
        self,
        servico: str,
        login: str,
        senha: str,
        observacao: str = "",
    ) -> str:
        """Adiciona nova credencial validada e persiste o cofre criptografado."""
        self._garantir_sessao()
        servico_limpo = servico.strip()
        login_limpo = login.strip()
        observacao_limpa = observacao.strip()

        if not servico_limpo:
            raise ValueError("O campo Serviço é obrigatório.")
        if not login_limpo:
            raise ValueError("O campo Usuário/E-mail é obrigatório.")
        if not senha:
            raise ValueError("O campo Senha é obrigatório.")

        if self._credencial_duplicada(servico_limpo, login_limpo):
            raise ValueError("Já existe uma credencial para este serviço e usuário.")

        agora = self._agora_iso()
        credencial = {
            "id": secrets.token_hex(16),
            "servico": servico_limpo,
            "login": login_limpo,
            "senha": senha,
            "observacao": observacao_limpa,
            "criado_em": agora,
            "atualizado_em": agora,
        }

        self._dados_cofre["credenciais"].append(credencial)
        self._persistir_cofre()
        return credencial["id"]

    def editar_credencial(
        self,
        credencial_id: str,
        servico: str,
        login: str,
        senha: str,
        observacao: str = "",
    ) -> None:
        """Atualiza uma credencial existente com validação de duplicidade."""
        self._garantir_sessao()
        servico_limpo = servico.strip()
        login_limpo = login.strip()
        observacao_limpa = observacao.strip()

        if not servico_limpo:
            raise ValueError("O campo Serviço é obrigatório.")
        if not login_limpo:
            raise ValueError("O campo Usuário/E-mail é obrigatório.")
        if not senha:
            raise ValueError("O campo Senha é obrigatório.")

        credencial = self._buscar_credencial_por_id(credencial_id)
        if credencial is None:
            raise ValueError("Credencial não encontrada.")

        if self._credencial_duplicada(servico_limpo, login_limpo, ignorar_id=credencial_id):
            raise ValueError("Já existe outra credencial para este serviço e usuário.")

        credencial["servico"] = servico_limpo
        credencial["login"] = login_limpo
        credencial["senha"] = senha
        credencial["observacao"] = observacao_limpa
        credencial["atualizado_em"] = self._agora_iso()
        self._persistir_cofre()

    def excluir_credencial(self, credencial_id: str) -> None:
        """Remove uma credencial do cofre e grava as alterações."""
        self._garantir_sessao()
        credenciais = self._dados_cofre.get("credenciais", [])
        tamanho_antes = len(credenciais)
        credenciais_filtradas = [item for item in credenciais if item.get("id") != credencial_id]

        if len(credenciais_filtradas) == tamanho_antes:
            raise ValueError("Credencial não encontrada.")

        self._dados_cofre["credenciais"] = credenciais_filtradas
        self._persistir_cofre()

    def autenticar_acao_sensivel(self, senha_mestra: str) -> bool:
        """Revalida a senha mestra para ações sensíveis usando a sessão atual."""
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        return verificar_senha_mestra(
            senha_mestra,
            dados_arquivo["kdf"],
            dados_arquivo["verificador_senha"],
            segredo_keyfile=self._segredo_keyfile_sessao,
        )

    def revelar_senha(self, credencial_id: str, senha_mestra: str) -> str:
        """Revela a senha de uma credencial após autenticação correta."""
        self._garantir_sessao()
        if not self.autenticar_acao_sensivel(senha_mestra):
            raise PermissionError("Falha de autenticação para revelar a senha.")

        credencial = self._buscar_credencial_por_id(credencial_id)
        if credencial is None:
            raise ValueError("Credencial não encontrada.")

        return str(credencial.get("senha", ""))

    def exportar_credenciais(
        self,
        caminho_destino: str | Path,
        senha_exportacao: str,
        credencial_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Exporta credenciais para um pacote criptografado independente do cofre atual."""
        self._garantir_sessao()
        senha_valida, mensagem = validar_forca_senha_mestra(senha_exportacao)
        if not senha_valida:
            raise ValueError(
                f"A senha de exportação precisa ser forte. {mensagem}"
            )

        caminho_resolvido = Path(caminho_destino).expanduser().resolve()
        if caminho_resolvido == self._armazenamento.caminho:
            raise ValueError("Escolha outro arquivo; a exportação não pode sobrescrever o cofre atual.")

        credenciais_fonte = self._dados_cofre.get("credenciais", [])
        ids_filtrados = set(credencial_ids or [])
        credenciais_exportadas: list[dict[str, Any]] = []

        for credencial in credenciais_fonte:
            if ids_filtrados and str(credencial.get("id")) not in ids_filtrados:
                continue
            credenciais_exportadas.append(dict(credencial))

        if not credenciais_exportadas:
            raise ValueError("Não há credenciais para exportar.")

        registro = criar_registro_senha_mestra(senha_exportacao)
        chave_exportacao = gerar_chave_criptografia(senha_exportacao, registro["kdf"])
        agora = self._agora_iso()
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

        GerenciadorArquivoCofre(caminho_resolvido).salvar(pacote)
        return {
            "arquivo": str(caminho_resolvido),
            "quantidade": len(credenciais_exportadas),
        }

    def importar_credenciais(
        self,
        caminho_origem: str | Path,
        senha_importacao: str,
        sobrescrever_duplicadas: bool = False,
    ) -> dict[str, int]:
        """Importa um pacote criptografado de credenciais para o cofre autenticado."""
        self._garantir_sessao()
        pacote = self._carregar_pacote_exportacao(caminho_origem)

        if not verificar_senha_mestra(
            senha_importacao,
            pacote["kdf"],
            pacote["verificador_senha"],
        ):
            raise PermissionError("Senha de importação incorreta.")

        chave_importacao = gerar_chave_criptografia(senha_importacao, pacote["kdf"])
        carga = descriptografar_objeto(
            pacote["dados_exportados_criptografados"],
            chave_importacao,
        )
        if not isinstance(carga, dict):
            raise ValueError("Pacote de importação inválido.")

        credenciais = carga.get("credenciais", [])
        if not isinstance(credenciais, list):
            raise ValueError("Pacote de importação com lista de credenciais inválida.")

        inseridas = 0
        atualizadas = 0
        ignoradas = 0
        agora = self._agora_iso()

        for item in credenciais:
            if not isinstance(item, dict):
                ignoradas += 1
                continue

            servico = str(item.get("servico", "")).strip()
            login = str(item.get("login", "")).strip()
            senha = str(item.get("senha", ""))
            observacao = str(item.get("observacao", "")).strip()

            if not servico or not login or not senha:
                ignoradas += 1
                continue

            existente = self._buscar_credencial_por_servico_login(servico, login)
            if existente is not None:
                if not sobrescrever_duplicadas:
                    ignoradas += 1
                    continue
                existente["senha"] = senha
                existente["observacao"] = observacao
                existente["atualizado_em"] = agora
                atualizadas += 1
                continue

            nova_credencial = {
                "id": secrets.token_hex(16),
                "servico": servico,
                "login": login,
                "senha": senha,
                "observacao": observacao,
                "criado_em": str(item.get("criado_em", agora)),
                "atualizado_em": str(item.get("atualizado_em", agora)),
            }
            self._dados_cofre["credenciais"].append(nova_credencial)
            inseridas += 1

        if inseridas or atualizadas:
            self._persistir_cofre()

        return {
            "inseridas": inseridas,
            "atualizadas": atualizadas,
            "ignoradas": ignoradas,
        }

    def reconfigurar_seguranca(
        self,
        senha_mestra_atual: str,
        nova_senha_mestra: str | None = None,
        usar_keyfile: bool = False,
        caminho_keyfile: str | None = None,
    ) -> str:
        """Reconfigura senha mestra, keyfile e formato forte do cofre atual."""
        self._garantir_sessao()

        if not self.autenticar_acao_sensivel(senha_mestra_atual):
            raise PermissionError("Senha mestra atual incorreta.")

        senha_destino = (nova_senha_mestra or "").strip() or senha_mestra_atual
        if nova_senha_mestra:
            senha_valida, mensagem = validar_forca_senha_mestra(senha_destino)
            if not senha_valida:
                raise ValueError(mensagem)

        segredo_keyfile_destino = None
        if usar_keyfile:
            if caminho_keyfile:
                segredo_keyfile_destino = self._carregar_segredo_keyfile(caminho_keyfile)
            elif self._segredo_keyfile_sessao is not None:
                segredo_keyfile_destino = self._segredo_keyfile_sessao
            else:
                raise ValueError("Selecione ou gere um keyfile para ativar essa proteção.")

        registro = criar_registro_senha_mestra(
            senha_destino,
            segredo_keyfile=segredo_keyfile_destino,
        )
        chave_criptografia = gerar_chave_criptografia(
            senha_destino,
            registro["kdf"],
            segredo_keyfile=segredo_keyfile_destino,
        )

        dados_arquivo = self._carregar_arquivo_obrigatorio()
        metadados_arquivo = dict(dados_arquivo.get("metadados", {}))
        metadados_arquivo["seguranca_atualizada_em"] = self._agora_iso()

        estrutura_arquivo = self._montar_estrutura_arquivo(
            registro=registro,
            dados_cofre=self._dados_cofre,
            chave_criptografia=chave_criptografia,
            controle_acesso=dados_arquivo.get("controle_acesso"),
            politica_acesso=dados_arquivo.get("politica_acesso"),
            metadados_arquivo=metadados_arquivo,
        )
        self._armazenamento.salvar(estrutura_arquivo)

        self._chave_sessao = chave_criptografia
        self._segredo_keyfile_sessao = segredo_keyfile_destino

        if nova_senha_mestra and usar_keyfile:
            return "Senha mestra e keyfile atualizados com sucesso."
        if nova_senha_mestra:
            return "Senha mestra atualizada com sucesso."
        if usar_keyfile:
            return "Proteção com keyfile aplicada ao cofre."
        return "Proteção com keyfile removida; o cofre segue protegido pela senha mestra."

    def gerar_senha(self, comprimento: int = 16) -> str:
        """Gera senha forte para preenchimento rápido no formulário."""
        return gerar_senha_forte(comprimento=comprimento)

    def encerrar_sessao(self) -> None:
        """Limpa referências de sessão para reduzir exposição em memória."""
        if isinstance(self._dados_cofre, dict):
            for credencial in self._dados_cofre.get("credenciais", []):
                if "senha" in credencial:
                    credencial["senha"] = ""

        self._dados_cofre = None
        self._chave_sessao = None
        self._segredo_keyfile_sessao = None

    def _persistir_cofre(self) -> None:
        """Criptografa e salva o estado atual do cofre em disco."""
        self._garantir_sessao()
        dados_arquivo = self._carregar_arquivo_obrigatorio()
        agora = self._agora_iso()
        self._dados_cofre.setdefault("metadados", {})["atualizado_em"] = agora

        carga_criptografada = criptografar_objeto(self._dados_cofre, self._chave_sessao)
        dados_arquivo["versao"] = VERSAO_COFRE_ATUAL
        dados_arquivo["dados_cofre_criptografados"] = carga_criptografada
        dados_arquivo.setdefault("metadados", {})["atualizado_em"] = agora
        self._armazenamento.salvar(dados_arquivo)

    def _abrir_carga_criptografada(
        self,
        dados_arquivo: dict[str, Any],
        senha_mestra: str,
        segredo_keyfile: bytes | None,
    ) -> tuple[dict[str, Any], bytes | None]:
        """Abre os dados do cofre conforme o formato atual ou legado."""
        if self._arquivo_usa_formato_legado(dados_arquivo):
            chave_fernet = gerar_chave_fernet_legado(senha_mestra, dados_arquivo["kdf"])
            dados_cofre = descriptografar_objeto_legado(
                dados_arquivo["dados_cofre_criptografados"],
                chave_fernet,
            )
            return dados_cofre, None

        chave_aes = gerar_chave_criptografia(
            senha_mestra,
            dados_arquivo["kdf"],
            segredo_keyfile=segredo_keyfile,
        )
        dados_cofre = descriptografar_objeto(
            dados_arquivo["dados_cofre_criptografados"],
            chave_aes,
        )
        return dados_cofre, chave_aes

    def _migrar_arquivo_se_necessario(
        self,
        dados_arquivo: dict[str, Any],
        senha_mestra: str,
        dados_cofre: dict[str, Any],
        segredo_keyfile: bytes | None,
    ) -> bool:
        """Migra cofres legados para Argon2id + AES-256-GCM ao abrir com sucesso."""
        if not self._arquivo_usa_formato_legado(dados_arquivo):
            return False

        registro = criar_registro_senha_mestra(
            senha_mestra,
            segredo_keyfile=segredo_keyfile,
        )
        chave_criptografia = gerar_chave_criptografia(
            senha_mestra,
            registro["kdf"],
            segredo_keyfile=segredo_keyfile,
        )

        metadados_arquivo = dict(dados_arquivo.get("metadados", {}))
        metadados_arquivo["migrado_em"] = self._agora_iso()
        metadados_arquivo["origem_migracao"] = f"versao_{dados_arquivo.get('versao', 1)}"

        estrutura_arquivo = self._montar_estrutura_arquivo(
            registro=registro,
            dados_cofre=dados_cofre,
            chave_criptografia=chave_criptografia,
            controle_acesso=dados_arquivo.get("controle_acesso"),
            politica_acesso=dados_arquivo.get("politica_acesso"),
            metadados_arquivo=metadados_arquivo,
        )
        self._armazenamento.salvar(estrutura_arquivo)
        self._chave_sessao = chave_criptografia
        return True

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
        agora = self._agora_iso()
        metadados = dict(metadados_arquivo or {})
        metadados.setdefault("criado_em", agora)
        metadados["atualizado_em"] = agora

        return {
            "versao": VERSAO_COFRE_ATUAL,
            "kdf": registro["kdf"],
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

    def _buscar_credencial_por_id(self, credencial_id: str) -> dict[str, Any] | None:
        """Procura uma credencial pelo identificador único."""
        for credencial in self._dados_cofre.get("credenciais", []):
            if credencial.get("id") == credencial_id:
                return credencial
        return None

    def _buscar_credencial_por_servico_login(
        self,
        servico: str,
        login: str,
    ) -> dict[str, Any] | None:
        """Procura uma credencial pelo par serviço e usuário."""
        alvo_servico = servico.lower()
        alvo_login = login.lower()
        for credencial in self._dados_cofre.get("credenciais", []):
            servico_atual = str(credencial.get("servico", "")).lower()
            login_atual = str(credencial.get("login", "")).lower()
            if servico_atual == alvo_servico and login_atual == alvo_login:
                return credencial
        return None

    def _credencial_duplicada(
        self,
        servico: str,
        login: str,
        ignorar_id: str | None = None,
    ) -> bool:
        """Valida duplicidade por serviço e usuário de forma case-insensitive."""
        alvo_servico = servico.lower()
        alvo_login = login.lower()

        for credencial in self._dados_cofre.get("credenciais", []):
            if ignorar_id and credencial.get("id") == ignorar_id:
                continue
            servico_atual = str(credencial.get("servico", "")).lower()
            login_atual = str(credencial.get("login", "")).lower()
            if servico_atual == alvo_servico and login_atual == alvo_login:
                return True

        return False

    def _garantir_sessao(self) -> None:
        """Garante que exista sessão autenticada antes de operar no cofre."""
        if not self.esta_autenticado():
            raise PermissionError("É necessário fazer login para acessar o cofre.")

    def _normalizar_estrutura_cofre(self) -> None:
        """Normaliza estrutura interna mínima do cofre descriptografado."""
        self._dados_cofre.setdefault("credenciais", [])
        self._dados_cofre.setdefault(
            "metadados",
            {
                "criado_em": self._agora_iso(),
                "atualizado_em": self._agora_iso(),
            },
        )

    def _carregar_segredo_keyfile(self, caminho_keyfile: str) -> bytes:
        """Carrega keyfile do disco e devolve seu segredo normalizado."""
        caminho = Path(caminho_keyfile).expanduser().resolve()
        if not caminho.exists():
            raise ValueError("O keyfile informado não foi encontrado.")
        if not caminho.is_file():
            raise ValueError("O caminho informado para keyfile não é um arquivo válido.")
        return normalizar_segredo_keyfile(caminho.read_bytes())

    def _arquivo_usa_formato_legado(self, dados_arquivo: dict[str, Any]) -> bool:
        """Detecta se o arquivo ainda usa o formato antigo baseado em Fernet."""
        if int(dados_arquivo.get("versao", 1)) < VERSAO_COFRE_ATUAL:
            return True
        if str(dados_arquivo.get("kdf", {}).get("algoritmo", "")).lower() != "argon2id":
            return True
        return not isinstance(dados_arquivo.get("dados_cofre_criptografados"), dict)

    def _carregar_arquivo_obrigatorio(self) -> dict[str, Any]:
        """Carrega arquivo persistido e valida campos críticos obrigatórios."""
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

        return dados_arquivo

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

    def _politica_acesso(self, dados_arquivo: dict[str, Any]) -> dict[str, int]:
        """Resolve política de acesso com valores padrão em caso de ausência."""
        politica_salva = dados_arquivo.get("politica_acesso", {})
        politica: dict[str, int] = {}
        for chave, valor_padrao in self.POLITICA_PADRAO.items():
            valor = politica_salva.get(chave, valor_padrao)
            politica[chave] = int(valor)
        dados_arquivo["politica_acesso"] = politica
        return politica

    @staticmethod
    def _rotulo_kdf(kdf: dict[str, Any]) -> str:
        """Traduz configuração do KDF para rótulo da interface."""
        algoritmo = str(kdf.get("algoritmo", "scrypt")).lower()
        if algoritmo == "argon2id":
            memoria_mb = int(kdf.get("memory_cost", 0)) // 1024
            return f"Argon2id ({memoria_mb} MB)"
        return "scrypt (legado)"

    @staticmethod
    def _rotulo_cifra(carga_criptografada: Any) -> str:
        """Traduz a cifra em uso para rótulo da interface."""
        if isinstance(carga_criptografada, dict):
            algoritmo = str(carga_criptografada.get("algoritmo", "")).lower()
            if algoritmo == "aes-256-gcm":
                return "AES-256-GCM"
        return "Fernet (legado)"

    @staticmethod
    def _agora_iso() -> str:
        """Retorna timestamp ISO local com precisão de segundos."""
        return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
