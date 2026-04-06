# Importa um recurso que permite usar funcionalidades mais modernas do Python
# mesmo em versões mais antigas (compatibilidade de versões)
from __future__ import annotations

# Importa a biblioteca "argparse", que serve para ler opções e argumentos
# que o usuário passa ao executar o programa pelo terminal (linha de comando)
import argparse

# Importa a função "iniciar_interface" do módulo "gui" dentro do pacote "cofre_seguro"
# Essa função é responsável por abrir a tela (janela) do programa para o usuário
from cofre_seguro.gui import iniciar_interface

# Importa a classe "GerenciadorArquivoCofre" do módulo "storage" dentro do pacote "cofre_seguro"
# Essa classe cuida de salvar e ler os dados das senhas em um arquivo no computador
from cofre_seguro.storage import GerenciadorArquivoCofre

# Importa a classe "ServicoCofre" do módulo "vault" dentro do pacote "cofre_seguro"
# Essa classe contém a lógica principal do cofre, como adicionar, buscar e remover senhas
from cofre_seguro.vault import ServicoCofre


# Define uma função chamada "construir_parser" que cria as regras de como
# o programa lê as opções passadas pelo terminal. Ela retorna um objeto do tipo ArgumentParser.
def construir_parser() -> argparse.ArgumentParser:
    """Cria parser de argumentos para escolher caminho do arquivo do cofre."""

    # Cria um "parser" (leitor de argumentos) com uma descrição do programa
    # Essa descrição aparece quando o usuário pede ajuda no terminal (--help)
    parser = argparse.ArgumentParser(description="Cofre de Senhas Seguro")

    # Adiciona uma opção chamada "--arquivo" que o usuário pode usar no terminal
    # para escolher onde salvar o arquivo do cofre de senhas
    # Se o usuário não informar nada, o programa usa o nome padrão "cofre_seguro_dados.json"
    parser.add_argument(
        "--arquivo",  # Nome da opção que o usuário digita no terminal
        dest="caminho_arquivo",  # Nome interno que o programa usa para guardar o valor
        default="cofre_seguro_dados.json",  # Valor padrão caso o usuário não informe nada
        help="Caminho do arquivo local do cofre (padrão: cofre_seguro_dados.json)",  # Texto de ajuda
    )

    # Retorna (devolve) o parser já configurado para quem chamou essa função
    return parser


# Define a função principal do programa, chamada "main"
# É aqui que tudo começa: ela prepara os serviços e abre a tela do programa
def main() -> None:
    """Inicializa serviços da aplicação e sobe a interface gráfica."""

    # Chama a função "construir_parser" para criar o leitor de argumentos,
    # e em seguida usa ".parse_args()" para ler o que o usuário digitou no terminal
    # O resultado fica guardado na variável "argumentos"
    argumentos = construir_parser().parse_args()

    # Cria o gerenciador de armazenamento, passando o caminho do arquivo onde
    # as senhas serão salvas. Ele vai cuidar de ler e gravar dados nesse arquivo.
    armazenamento = GerenciadorArquivoCofre(argumentos.caminho_arquivo)

    # Cria o serviço do cofre, passando o gerenciador de armazenamento
    # Esse serviço é o "cérebro" do programa — ele sabe como adicionar,
    # buscar, editar e remover senhas
    servico = ServicoCofre(armazenamento)

    # Abre a interface gráfica (a janela do programa) passando o serviço do cofre
    # A partir daqui o usuário pode interagir com o programa pela tela
    iniciar_interface(servico)


# Essa verificação especial checa se este arquivo está sendo executado diretamente
# (e não apenas importado por outro arquivo). Se estiver sendo executado diretamente,
# ele chama a função "main" para iniciar o programa.
if __name__ == "__main__":
    main()  # Chama a função principal para rodar o programa
