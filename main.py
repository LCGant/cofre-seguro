from __future__ import annotations

import argparse

from cofre_seguro.gui import iniciar_interface
from cofre_seguro.storage import GerenciadorArquivoCofre
from cofre_seguro.vault import ServicoCofre


def construir_parser() -> argparse.ArgumentParser:
    """Cria parser de argumentos para escolher caminho do arquivo do cofre."""
    parser = argparse.ArgumentParser(description="Cofre de Senhas Seguro")
    parser.add_argument(
        "--arquivo",
        dest="caminho_arquivo",
        default="cofre_seguro_dados.json",
        help="Caminho do arquivo local do cofre (padrão: cofre_seguro_dados.json)",
    )
    return parser


def main() -> None:
    """Inicializa serviços da aplicação e sobe a interface gráfica."""
    argumentos = construir_parser().parse_args()
    armazenamento = GerenciadorArquivoCofre(argumentos.caminho_arquivo)
    servico = ServicoCofre(armazenamento)
    iniciar_interface(servico)


if __name__ == "__main__":
    main()
