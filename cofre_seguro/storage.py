# Essa linha permite usar recursos modernos de tipagem mesmo em versões mais antigas do Python
from __future__ import annotations

# 'json' serve para ler e escrever dados no formato JSON (um formato de texto muito usado para guardar informações)
import json
# 'os' dá acesso a funções do sistema operacional, como apagar arquivos, mudar permissões, etc.
import os
# 'Path' facilita trabalhar com caminhos de arquivos e pastas no computador
from pathlib import Path
# 'NamedTemporaryFile' cria um arquivo temporário com nome, útil para salvar dados de forma segura
from tempfile import NamedTemporaryFile
# 'Any' é usado na tipagem para dizer que um valor pode ser de qualquer tipo
from typing import Any


# Aqui criamos uma classe, que é como uma "ficha técnica" que agrupa funções e dados relacionados
# Essa classe cuida de tudo que envolve salvar e ler o arquivo do cofre no computador
class GerenciadorArquivoCofre:
    """Gerencia persistência local do arquivo do cofre com escrita atômica."""

    # '__init__' é a função que roda automaticamente quando criamos um novo GerenciadorArquivoCofre
    # Ela prepara tudo que o gerenciador precisa para funcionar
    def __init__(self, caminho_arquivo: str | Path | None = None) -> None:
        """Inicializa o caminho do arquivo onde o cofre será armazenado."""
        # Se o usuário passou um caminho de arquivo, usa ele; senão, usa um nome padrão
        caminho_base = Path(caminho_arquivo) if caminho_arquivo else Path("cofre_seguro_dados.json")
        # 'expanduser' resolve o '~' para a pasta do usuário, e 'resolve' transforma em caminho completo (absoluto)
        self._caminho = caminho_base.expanduser().resolve()
        # Cria a pasta onde o arquivo vai ficar, caso ela ainda não exista
        # 'parents=True' cria todas as pastas necessárias no caminho
        # 'exist_ok=True' não dá erro se a pasta já existir
        self._caminho.parent.mkdir(parents=True, exist_ok=True)

    # '@property' transforma essa função em um atributo que pode ser acessado sem parênteses
    # Exemplo: em vez de chamar gerenciador.caminho(), basta usar gerenciador.caminho
    @property
    def caminho(self) -> Path:
        """Retorna o caminho absoluto do arquivo do cofre."""
        # Devolve o caminho completo do arquivo do cofre
        return self._caminho

    # Função que verifica se o arquivo do cofre já existe no computador
    def existe_cofre(self) -> bool:
        """Informa se o arquivo do cofre já existe no disco."""
        # Retorna True (verdadeiro) se o arquivo existe, ou False (falso) se não existe
        return self._caminho.exists()

    # Função que lê os dados salvos no arquivo do cofre e devolve eles
    def carregar(self) -> dict[str, Any] | None:
        """Lê e devolve os dados do cofre salvos em JSON."""
        # Se o arquivo do cofre não existe, retorna None (nada), pois não há o que carregar
        if not self.existe_cofre():
            return None

        # 'try' tenta executar o código abaixo; se der erro, vai para o 'except'
        try:
            # Abre o arquivo do cofre para leitura ("r" = read = ler), usando codificação UTF-8
            # 'with' garante que o arquivo será fechado corretamente depois de usar
            with self._caminho.open("r", encoding="utf-8") as arquivo:
                # 'json.load' lê o conteúdo do arquivo e transforma de texto JSON em dados do Python
                dados = json.load(arquivo)
        # Se o arquivo não estiver em formato JSON válido, cai aqui neste tratamento de erro
        except json.JSONDecodeError as exc:
            # Lança um erro avisando que o arquivo está corrompido ou inválido
            raise ValueError("Arquivo do cofre inválido ou corrompido.") from exc

        # Verifica se os dados lidos são um dicionário (estrutura chave-valor, como uma lista de contatos)
        if not isinstance(dados, dict):
            # Se não for um dicionário, lança erro pois o formato está errado
            raise ValueError("Formato do arquivo do cofre inválido.")

        # Devolve os dados carregados do arquivo
        return dados

    # Função que salva os dados do cofre no arquivo de forma segura
    # Usa "escrita atômica": primeiro escreve num arquivo temporário, depois substitui o original
    # Isso evita que o arquivo fique corrompido se o programa travar no meio da escrita
    def salvar(self, dados: dict[str, Any]) -> None:
        """Salva o cofre com substituição atômica para reduzir risco de corrupção."""
        # Verifica se o que foi passado para salvar é realmente um dicionário
        if not isinstance(dados, dict):
            # Se não for dicionário, lança erro pois só aceitamos esse formato
            raise ValueError("Os dados do cofre devem ser um objeto JSON.")

        # Variável que vai guardar o nome do arquivo temporário (começa vazia)
        nome_temporario = ""
        # 'try' tenta executar o código; o 'finally' no final vai rodar sempre, com ou sem erro
        try:
            # Cria um arquivo temporário na mesma pasta do cofre
            # 'mode="w"' = modo escrita, 'delete=False' = não apagar automaticamente ao fechar
            # 'dir' = pasta onde criar, 'prefix' e 'suffix' = início e fim do nome do arquivo
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                delete=False,
                dir=str(self._caminho.parent),
                prefix=f"{self._caminho.name}.",
                suffix=".tmp",
            ) as arquivo_temporario:
                # 'json.dump' converte os dados do Python para texto JSON e escreve no arquivo
                # 'ensure_ascii=False' permite acentos, 'indent=2' deixa o JSON organizado e legível
                json.dump(dados, arquivo_temporario, ensure_ascii=False, indent=2)
                # 'flush' força o Python a enviar tudo que está em memória para o arquivo
                arquivo_temporario.flush()
                # 'fsync' força o sistema operacional a gravar os dados no disco de verdade
                os.fsync(arquivo_temporario.fileno())
                # Guarda o nome do arquivo temporário para usar depois
                nome_temporario = arquivo_temporario.name

            # Substitui o arquivo original pelo temporário de uma vez só (operação atômica)
            # Isso garante que o arquivo nunca fica pela metade
            os.replace(nome_temporario, self._caminho)
        # 'finally' roda sempre, mesmo se acontecer um erro acima
        finally:
            # Se o arquivo temporário ainda existe (por exemplo, se deu erro antes do replace),
            # apaga ele para não deixar lixo no computador
            if nome_temporario and os.path.exists(nome_temporario):
                os.remove(nome_temporario)

        # 'try' tenta mudar as permissões do arquivo
        try:
            # Define que só o dono do arquivo pode ler e escrever nele (permissão 600)
            # Isso é uma medida de segurança para proteger os dados do cofre
            os.chmod(self._caminho, 0o600)
        # Se der erro ao mudar permissões (por exemplo, no Windows que não suporta isso direito),
        # simplesmente ignora e segue em frente
        except OSError:
            return
