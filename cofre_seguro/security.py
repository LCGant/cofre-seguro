# Permite usar recursos de versões mais novas do Python mesmo em versões antigas
from __future__ import annotations

# 'base64' serve para transformar dados binários em texto legível (e vice-versa)
import base64
# 'hashlib' oferece funções para criar "impressões digitais" (hashes) de dados
import hashlib
# 'hmac' permite comparar dados de forma segura, sem vazar informações pelo tempo de resposta
import hmac
# 'json' permite converter dados do Python para o formato JSON (texto estruturado) e vice-versa
import json
# 'secrets' gera números e bytes aleatórios de forma segura (próprio para criptografia)
import secrets
# 'string' contém conjuntos prontos de letras, números e caracteres especiais
import string
# 'Any' é uma anotação de tipo que significa "qualquer tipo de dado"
from typing import Any

# Importa exceção que indica falha na autenticação da criptografia AES-GCM
from cryptography.exceptions import InvalidTag
# Importa o Fernet (método de criptografia simétrica) e sua exceção de token inválido
from cryptography.fernet import Fernet, InvalidToken
# Importa o AES-GCM, um algoritmo de criptografia forte e moderno
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
# Importa o Argon2id, um algoritmo moderno para derivar chaves a partir de senhas
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

# Número da versão atual do formato do cofre (versão 2 é a mais recente)
VERSAO_COFRE_ATUAL = 2
# Dados adicionais de autenticação usados na criptografia AES-GCM (como uma "etiqueta" que identifica o cofre)
AAD_AES_GCM = b"Cofre de Senhas Seguro v2"
# Configurações padrão do algoritmo Argon2id (controla o quão difícil é "adivinhar" a senha)
PARAMETROS_ARGON2ID_PADRAO = {
    "iterations": 3,          # Quantas vezes o algoritmo repete o processo (mais = mais seguro, mas mais lento)
    "lanes": 4,               # Quantas "pistas" paralelas de processamento usar
    "memory_cost": 65536,     # Quanta memória RAM usar (em kilobytes) — dificulta ataques
    "dklen_verificador": 32,  # Tamanho em bytes da chave usada para verificar a senha
    "dklen_chave": 32,        # Tamanho em bytes da chave usada para criptografar dados
}
# Configurações do algoritmo antigo (scrypt) para manter compatibilidade com cofres mais velhos
PARAMETROS_SCRYPT_LEGADO = {
    "n": 2**14,              # Fator de custo de CPU/memória do scrypt
    "r": 8,                  # Tamanho do bloco interno do scrypt
    "p": 1,                  # Fator de paralelismo do scrypt
    "dklen_verificador": 32, # Tamanho em bytes da chave de verificação
    "dklen_chave": 32,       # Tamanho em bytes da chave de criptografia
}


# Função que transforma bytes (dados binários) em texto Base64, para poder guardar em JSON
def _b64_encode(valor: bytes) -> str:
    """Codifica bytes em Base64 textual para armazenamento em JSON."""
    # Converte os bytes para Base64 e depois transforma o resultado em texto (string)
    return base64.b64encode(valor).decode("utf-8")


# Função que faz o contrário: transforma texto Base64 de volta em bytes (dados binários)
def _b64_decode(valor: str) -> bytes:
    """Decodifica Base64 textual para bytes."""
    # Transforma o texto em bytes e depois decodifica o Base64
    return base64.b64decode(valor.encode("utf-8"))


# Função que transforma qualquer dado do Python em bytes JSON padronizados (sempre na mesma ordem)
def _serializar_dados(dados: Any) -> bytes:
    """Serializa dados em JSON estável para criptografia autenticada."""
    # Converte os dados para texto JSON de forma padronizada e compacta
    return json.dumps(
        dados,
        ensure_ascii=False,     # Permite caracteres especiais como acentos
        separators=(",", ":"),  # Remove espaços extras para economizar espaço
        sort_keys=True,         # Ordena as chaves em ordem alfabética (garante resultado sempre igual)
    ).encode("utf-8")  # Transforma o texto JSON em bytes usando codificação UTF-8


# Função que gera uma sequência de bytes aleatórios e seguros (usada para criar salts, nonces, etc.)
def gerar_bytes_seguro(tamanho: int = 16) -> bytes:
    """Gera bytes criptograficamente seguros com o módulo secrets."""
    # Usa o módulo 'secrets' para gerar bytes verdadeiramente aleatórios
    return secrets.token_bytes(tamanho)


# Função que gera o conteúdo aleatório de um "keyfile" (arquivo-chave extra de segurança)
def gerar_conteudo_keyfile(tamanho: int = 64) -> bytes:
    """Gera conteúdo aleatório para um keyfile local dedicado."""
    # Reutiliza a função de gerar bytes seguros, mas com tamanho maior (64 bytes)
    return gerar_bytes_seguro(tamanho)


# Função que padroniza o conteúdo de um keyfile para um tamanho fixo usando hash
def normalizar_segredo_keyfile(conteudo: bytes | None) -> bytes | None:
    """Normaliza o conteúdo do keyfile para um segredo fixo de entrada do KDF."""
    # Se não foi fornecido nenhum keyfile, retorna None (nada)
    if conteudo is None:
        return None
    # Se o keyfile existe mas está vazio, isso é um erro
    if not conteudo:
        raise ValueError("O keyfile selecionado está vazio.")
    # Usa o algoritmo BLAKE2b para criar um "resumo" de tamanho fixo (32 bytes) do keyfile
    # O parâmetro 'person' é uma etiqueta que diferencia este uso de outros usos do BLAKE2b
    return hashlib.blake2b(
        conteudo,
        digest_size=32,
        person=b"CofreKeyfile",
    ).digest()


# Função que verifica se a senha mestra atende aos requisitos mínimos de segurança
def validar_forca_senha_mestra(senha: str) -> tuple[bool, str]:
    """Valida requisitos mínimos de força para a senha mestra."""
    # Verifica se a senha tem pelo menos 12 caracteres
    if len(senha) < 12:
        return False, "A senha mestra deve ter pelo menos 12 caracteres."

    # Verifica se tem pelo menos uma letra minúscula (a-z)
    if not any(caractere.islower() for caractere in senha):
        return False, "Inclua ao menos uma letra minúscula na senha mestra."

    # Verifica se tem pelo menos uma letra maiúscula (A-Z)
    if not any(caractere.isupper() for caractere in senha):
        return False, "Inclua ao menos uma letra maiúscula na senha mestra."

    # Verifica se tem pelo menos um número (0-9)
    if not any(caractere.isdigit() for caractere in senha):
        return False, "Inclua ao menos um número na senha mestra."

    # Verifica se tem pelo menos um caractere especial (!, @, #, etc.)
    if not any(caractere in string.punctuation for caractere in senha):
        return False, "Inclua ao menos um caractere especial na senha mestra."

    # Se passou por todas as verificações acima, a senha é válida
    return True, "Senha mestra válida."


# Função que cria uma chave a partir da senha usando o algoritmo moderno Argon2id
def derivar_chave_argon2id(
    senha: str,
    salt: bytes,
    iterations: int,
    lanes: int,
    memory_cost: int,
    dklen: int,
    segredo_keyfile: bytes | None = None,
) -> bytes:
    """Deriva uma chave com Argon2id usando senha mestra e keyfile opcional."""
    # Configura o Argon2id com todos os parâmetros de segurança
    kdf = Argon2id(
        salt=salt,                  # "Sal" aleatório que torna cada derivação única
        length=dklen,               # Tamanho da chave que será gerada
        iterations=iterations,      # Número de repetições do algoritmo
        lanes=lanes,                # Número de processamentos paralelos
        memory_cost=memory_cost,    # Quantidade de memória que o algoritmo vai usar
        secret=segredo_keyfile,     # Segredo extra vindo do keyfile (opcional)
    )
    # Executa a derivação: transforma a senha (texto) em uma chave criptográfica (bytes)
    return kdf.derive(senha.encode("utf-8"))


# Função que cria uma chave usando o algoritmo antigo scrypt (para cofres da versão anterior)
def derivar_chave_scrypt_legado(
    senha: str,
    salt: bytes,
    n: int,
    r: int,
    p: int,
    dklen: int,
) -> bytes:
    """Deriva uma chave com scrypt para compatibilidade com cofres legados."""
    # Usa o hashlib.scrypt para transformar a senha em uma chave criptográfica
    return hashlib.scrypt(
        password=senha.encode("utf-8"),  # A senha do usuário convertida para bytes
        salt=salt,                        # "Sal" aleatório para tornar a chave única
        n=n,                              # Fator de custo de CPU/memória
        r=r,                              # Tamanho do bloco
        p=p,                              # Fator de paralelismo
        dklen=dklen,                      # Tamanho da chave resultante
    )


# Função que prepara tudo que é necessário para proteger a senha mestra no cofre
def criar_registro_senha_mestra(
    senha_mestra: str,
    segredo_keyfile: bytes | None = None,
    parametros_argon2id: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Cria salts e verificador da senha mestra para o formato atual do cofre."""
    # Começa com os parâmetros padrão do Argon2id
    parametros = dict(PARAMETROS_ARGON2ID_PADRAO)
    # Se o usuário forneceu parâmetros personalizados, sobrescreve os padrões
    if parametros_argon2id:
        parametros.update(parametros_argon2id)

    # Gera um "sal" aleatório exclusivo para a verificação da senha (16 bytes)
    salt_verificador = gerar_bytes_seguro(16)
    # Gera outro "sal" aleatório exclusivo para a criptografia dos dados (16 bytes)
    salt_criptografia = gerar_bytes_seguro(16)
    # Deriva o "verificador": uma chave que será usada depois para conferir se a senha está correta
    verificador = derivar_chave_argon2id(
        senha=senha_mestra,
        salt=salt_verificador,
        iterations=int(parametros["iterations"]),
        lanes=int(parametros["lanes"]),
        memory_cost=int(parametros["memory_cost"]),
        dklen=int(parametros["dklen_verificador"]),
        segredo_keyfile=segredo_keyfile,
    )

    # Retorna um dicionário com todas as informações necessárias para verificar e usar a senha depois
    return {
        "kdf": {
            "algoritmo": "argon2id",                                    # Nome do algoritmo usado
            "iterations": int(parametros["iterations"]),                # Repetições do algoritmo
            "lanes": int(parametros["lanes"]),                          # Pistas paralelas
            "memory_cost": int(parametros["memory_cost"]),              # Memória utilizada
            "dklen_verificador": int(parametros["dklen_verificador"]),  # Tamanho da chave de verificação
            "dklen_chave": int(parametros["dklen_chave"]),              # Tamanho da chave de criptografia
            "salt_verificador": _b64_encode(salt_verificador),          # Sal do verificador em Base64
            "salt_criptografia": _b64_encode(salt_criptografia),        # Sal da criptografia em Base64
            "usa_keyfile": segredo_keyfile is not None,                 # Indica se um keyfile foi usado
        },
        "verificador_senha": _b64_encode(verificador),  # O verificador da senha em Base64
    }


# Função que confere se a senha mestra digitada pelo usuário está correta
def verificar_senha_mestra(
    senha_mestra: str,
    kdf: dict[str, Any],
    verificador_senha: str,
    segredo_keyfile: bytes | None = None,
) -> bool:
    """Verifica a senha mestra com comparação segura em tempo constante."""
    # Descobre qual algoritmo foi usado para criar o cofre (argon2id ou scrypt antigo)
    algoritmo = str(kdf.get("algoritmo", "scrypt")).lower()
    # Decodifica o verificador salvo no cofre de Base64 para bytes
    esperado = _b64_decode(verificador_senha)

    # Se o cofre usa o algoritmo moderno Argon2id
    if algoritmo == "argon2id":
        # Recupera o sal que foi usado na criação do verificador
        salt_verificador = _b64_decode(kdf["salt_verificador"])
        # Deriva a chave novamente usando a senha que o usuário digitou agora
        calculado = derivar_chave_argon2id(
            senha=senha_mestra,
            salt=salt_verificador,
            iterations=int(kdf["iterations"]),
            lanes=int(kdf["lanes"]),
            memory_cost=int(kdf["memory_cost"]),
            dklen=int(kdf["dklen_verificador"]),
            segredo_keyfile=segredo_keyfile,
        )
        # Compara a chave calculada com a esperada de forma segura (tempo constante)
        # "Tempo constante" significa que a comparação demora o mesmo tempo, certa ou errada
        # Isso impede que um atacante descubra a senha aos poucos medindo o tempo de resposta
        return hmac.compare_digest(calculado, esperado)

    # Se o cofre usa o algoritmo antigo scrypt (cofre legado / versão anterior)
    # Recupera o sal do verificador
    salt_verificador = _b64_decode(kdf["salt_verificador"])
    # Deriva a chave com scrypt usando a senha digitada
    calculado = derivar_chave_scrypt_legado(
        senha=senha_mestra,
        salt=salt_verificador,
        n=int(kdf["n"]),
        r=int(kdf["r"]),
        p=int(kdf["p"]),
        dklen=int(kdf["dklen_verificador"]),
    )
    # Compara de forma segura em tempo constante
    return hmac.compare_digest(calculado, esperado)


# Função que gera a chave usada para criptografar/descriptografar os dados do cofre
def gerar_chave_criptografia(
    senha_mestra: str,
    kdf: dict[str, Any],
    segredo_keyfile: bytes | None = None,
) -> bytes:
    """Deriva a chave de criptografia apropriada para a versão atual do cofre."""
    # Descobre qual algoritmo o cofre utiliza
    algoritmo = str(kdf.get("algoritmo", "scrypt")).lower()
    # Decodifica o sal de criptografia salvo no cofre
    salt_criptografia = _b64_decode(kdf["salt_criptografia"])

    # Se usa o algoritmo moderno Argon2id, deriva a chave com ele
    if algoritmo == "argon2id":
        return derivar_chave_argon2id(
            senha=senha_mestra,
            salt=salt_criptografia,
            iterations=int(kdf["iterations"]),
            lanes=int(kdf["lanes"]),
            memory_cost=int(kdf["memory_cost"]),
            dklen=int(kdf["dklen_chave"]),
            segredo_keyfile=segredo_keyfile,
        )

    # Caso contrário, usa o algoritmo antigo scrypt para manter compatibilidade
    return derivar_chave_scrypt_legado(
        senha=senha_mestra,
        salt=salt_criptografia,
        n=int(kdf["n"]),
        r=int(kdf["r"]),
        p=int(kdf["p"]),
        dklen=int(kdf["dklen_chave"]),
    )


# Função que gera a chave no formato Fernet (usado em cofres antigos, versão 1)
def gerar_chave_fernet_legado(senha_mestra: str, kdf: dict[str, Any]) -> bytes:
    """Deriva chave em formato Fernet para leitura de cofres legados."""
    # Primeiro, deriva a chave bruta (32 bytes) a partir da senha
    chave_bruta = gerar_chave_criptografia(senha_mestra, kdf)
    # Converte para Base64 no formato que o Fernet espera receber
    return base64.urlsafe_b64encode(chave_bruta)


# Função que criptografa (embaralha/protege) os dados usando AES-256-GCM
def criptografar_objeto(dados: Any, chave_aes: bytes) -> dict[str, str]:
    """Criptografa dados com AES-256-GCM no formato atual do projeto."""
    # Gera um "nonce" (número usado uma única vez) de 12 bytes — garante que cada criptografia seja diferente
    nonce = gerar_bytes_seguro(12)
    # Criptografa os dados serializados com AES-GCM, usando o nonce e os dados de autenticação adicionais
    ciphertext = AESGCM(chave_aes).encrypt(nonce, _serializar_dados(dados), AAD_AES_GCM)
    # Retorna um dicionário com o algoritmo usado, o nonce e os dados criptografados, tudo em Base64
    return {
        "algoritmo": "aes-256-gcm",           # Identifica qual algoritmo foi usado
        "nonce": _b64_encode(nonce),           # O nonce convertido para texto Base64
        "ciphertext": _b64_encode(ciphertext), # Os dados criptografados convertidos para texto Base64
    }


# Função que descriptografa (desembaralha/recupera) os dados protegidos com AES-256-GCM
def descriptografar_objeto(carga_criptografada: dict[str, str], chave_aes: bytes) -> Any:
    """Descriptografa o payload atual protegido com AES-256-GCM."""
    # Verifica se os dados recebidos são um dicionário válido
    if not isinstance(carga_criptografada, dict):
        raise ValueError("Payload criptografado inválido para o formato atual.")
    # Verifica se o algoritmo indicado é o esperado (aes-256-gcm)
    if carga_criptografada.get("algoritmo") != "aes-256-gcm":
        raise ValueError("Algoritmo de criptografia não suportado.")

    # Decodifica o nonce de Base64 para bytes
    nonce = _b64_decode(carga_criptografada["nonce"])
    # Decodifica os dados criptografados de Base64 para bytes
    ciphertext = _b64_decode(carga_criptografada["ciphertext"])

    # Tenta descriptografar os dados
    try:
        # Usa AES-GCM para descriptografar, verificando a autenticidade dos dados
        conteudo = AESGCM(chave_aes).decrypt(nonce, ciphertext, AAD_AES_GCM)
    except InvalidTag as exc:
        # Se a chave estiver errada ou os dados foram alterados, a descriptografia falha
        raise ValueError("Falha ao descriptografar os dados do cofre.") from exc

    # Tenta converter os bytes descriptografados de volta para dados Python (via JSON)
    try:
        return json.loads(conteudo.decode("utf-8"))
    except json.JSONDecodeError as exc:
        # Se o JSON estiver corrompido, informa o erro
        raise ValueError("Os dados descriptografados estão inválidos.") from exc


# Função que criptografa dados no formato antigo (Fernet) — usada para manter compatibilidade
def criptografar_objeto_legado(dados: Any, chave_fernet: bytes) -> str:
    """Criptografa dados no formato legado para testes e compatibilidade."""
    # Usa o Fernet para criptografar os dados serializados e gera um token (texto criptografado)
    token = Fernet(chave_fernet).encrypt(_serializar_dados(dados))
    # Converte o token de bytes para texto
    return token.decode("utf-8")


# Função que descriptografa dados no formato antigo (Fernet) — para abrir cofres da versão 1
def descriptografar_objeto_legado(token: str, chave_fernet: bytes) -> Any:
    """Descriptografa token Fernet de cofres legados."""
    # Tenta descriptografar o token Fernet
    try:
        # Converte o token de texto para bytes e descriptografa com a chave Fernet
        conteudo = Fernet(chave_fernet).decrypt(token.encode("utf-8"))
    except InvalidToken as exc:
        # Se a chave estiver errada ou o token for inválido, informa o erro
        raise ValueError("Falha ao descriptografar os dados do cofre legado.") from exc

    # Tenta converter os bytes descriptografados em dados Python (via JSON)
    try:
        return json.loads(conteudo.decode("utf-8"))
    except json.JSONDecodeError as exc:
        # Se o JSON estiver corrompido, informa o erro
        raise ValueError("Os dados descriptografados estão inválidos.") from exc


# Função que gera uma senha aleatória forte com os tipos de caracteres escolhidos
def gerar_senha_forte(
    comprimento: int = 16,                # Tamanho total da senha (padrão: 16 caracteres)
    incluir_maiusculas: bool = True,      # Se deve incluir letras maiúsculas (A-Z)
    incluir_minusculas: bool = True,      # Se deve incluir letras minúsculas (a-z)
    incluir_numeros: bool = True,         # Se deve incluir números (0-9)
    incluir_especiais: bool = True,       # Se deve incluir caracteres especiais (!@#$, etc.)
) -> str:
    """Gera senha aleatória forte garantindo classes de caracteres selecionadas."""
    # Cria uma lista vazia para guardar os grupos de caracteres selecionados
    grupos: list[str] = []

    # Adiciona cada grupo de caracteres à lista, conforme as opções escolhidas
    if incluir_maiusculas:
        grupos.append(string.ascii_uppercase)   # Adiciona "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if incluir_minusculas:
        grupos.append(string.ascii_lowercase)   # Adiciona "abcdefghijklmnopqrstuvwxyz"
    if incluir_numeros:
        grupos.append(string.digits)            # Adiciona "0123456789"
    if incluir_especiais:
        grupos.append(string.punctuation)       # Adiciona caracteres como "!@#$%^&*()" etc.

    # Se nenhum grupo foi selecionado, não é possível gerar uma senha
    if not grupos:
        raise ValueError("Selecione ao menos um conjunto de caracteres.")

    # Se o comprimento pedido é menor que a quantidade de grupos, não dá para garantir um de cada
    if comprimento < len(grupos):
        raise ValueError(
            "Comprimento insuficiente para cobrir os conjuntos de caracteres selecionados."
        )

    # Garante pelo menos um caractere de cada grupo selecionado (escolhe aleatoriamente)
    caracteres = [secrets.choice(grupo) for grupo in grupos]
    # Junta todos os grupos em uma única string com todos os caracteres possíveis
    universo = "".join(grupos)

    # Preenche o restante da senha com caracteres aleatórios de qualquer grupo
    while len(caracteres) < comprimento:
        caracteres.append(secrets.choice(universo))

    # Embaralha os caracteres de forma aleatória (algoritmo Fisher-Yates)
    # Isso evita que os primeiros caracteres sejam sempre um de cada grupo na mesma ordem
    indice = len(caracteres) - 1  # Começa do último caractere
    while indice > 0:
        # Escolhe uma posição aleatória entre 0 e o índice atual
        novo_indice = secrets.randbelow(indice + 1)
        # Troca os caracteres de posição (o atual com o sorteado)
        caracteres[indice], caracteres[novo_indice] = (
            caracteres[novo_indice],
            caracteres[indice],
        )
        # Vai para o caractere anterior
        indice -= 1

    # Junta todos os caracteres da lista em uma única string e retorna a senha pronta
    return "".join(caracteres)
