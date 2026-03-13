from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


class GerenciadorArquivoCofre:
    """Gerencia persistência local do arquivo do cofre com escrita atômica."""

    def __init__(self, caminho_arquivo: str | Path | None = None) -> None:
        """Inicializa o caminho do arquivo onde o cofre será armazenado."""
        caminho_base = Path(caminho_arquivo) if caminho_arquivo else Path("cofre_seguro_dados.json")
        self._caminho = caminho_base.expanduser().resolve()
        self._caminho.parent.mkdir(parents=True, exist_ok=True)

    @property
    def caminho(self) -> Path:
        """Retorna o caminho absoluto do arquivo do cofre."""
        return self._caminho

    def existe_cofre(self) -> bool:
        """Informa se o arquivo do cofre já existe no disco."""
        return self._caminho.exists()

    def carregar(self) -> dict[str, Any] | None:
        """Lê e devolve os dados do cofre salvos em JSON."""
        if not self.existe_cofre():
            return None

        try:
            with self._caminho.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except json.JSONDecodeError as exc:
            raise ValueError("Arquivo do cofre inválido ou corrompido.") from exc

        if not isinstance(dados, dict):
            raise ValueError("Formato do arquivo do cofre inválido.")

        return dados

    def salvar(self, dados: dict[str, Any]) -> None:
        """Salva o cofre com substituição atômica para reduzir risco de corrupção."""
        if not isinstance(dados, dict):
            raise ValueError("Os dados do cofre devem ser um objeto JSON.")

        nome_temporario = ""
        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                delete=False,
                dir=str(self._caminho.parent),
                prefix=f"{self._caminho.name}.",
                suffix=".tmp",
            ) as arquivo_temporario:
                json.dump(dados, arquivo_temporario, ensure_ascii=False, indent=2)
                arquivo_temporario.flush()
                os.fsync(arquivo_temporario.fileno())
                nome_temporario = arquivo_temporario.name

            os.replace(nome_temporario, self._caminho)
        finally:
            if nome_temporario and os.path.exists(nome_temporario):
                os.remove(nome_temporario)

        try:
            os.chmod(self._caminho, 0o600)
        except OSError:
            return
