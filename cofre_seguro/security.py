from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import string
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

VERSAO_COFRE_ATUAL = 2
AAD_AES_GCM = b"Cofre de Senhas Seguro v2"
PARAMETROS_ARGON2ID_PADRAO = {
    "iterations": 3,
    "lanes": 4,
    "memory_cost": 65536,
    "dklen_verificador": 32,
    "dklen_chave": 32,
}
PARAMETROS_SCRYPT_LEGADO = {
    "n": 2**14,
    "r": 8,
    "p": 1,
    "dklen_verificador": 32,
    "dklen_chave": 32,
}


def _b64_encode(valor: bytes) -> str:
    """Codifica bytes em Base64 textual para armazenamento em JSON."""
    return base64.b64encode(valor).decode("utf-8")


def _b64_decode(valor: str) -> bytes:
    """Decodifica Base64 textual para bytes."""
    return base64.b64decode(valor.encode("utf-8"))


def _serializar_dados(dados: Any) -> bytes:
    """Serializa dados em JSON estável para criptografia autenticada."""
    return json.dumps(
        dados,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def gerar_bytes_seguro(tamanho: int = 16) -> bytes:
    """Gera bytes criptograficamente seguros com o módulo secrets."""
    return secrets.token_bytes(tamanho)


def gerar_conteudo_keyfile(tamanho: int = 64) -> bytes:
    """Gera conteúdo aleatório para um keyfile local dedicado."""
    return gerar_bytes_seguro(tamanho)


def normalizar_segredo_keyfile(conteudo: bytes | None) -> bytes | None:
    """Normaliza o conteúdo do keyfile para um segredo fixo de entrada do KDF."""
    if conteudo is None:
        return None
    if not conteudo:
        raise ValueError("O keyfile selecionado está vazio.")
    return hashlib.blake2b(
        conteudo,
        digest_size=32,
        person=b"CofreKeyfile",
    ).digest()


def validar_forca_senha_mestra(senha: str) -> tuple[bool, str]:
    """Valida requisitos mínimos de força para a senha mestra."""
    if len(senha) < 12:
        return False, "A senha mestra deve ter pelo menos 12 caracteres."

    if not any(caractere.islower() for caractere in senha):
        return False, "Inclua ao menos uma letra minúscula na senha mestra."

    if not any(caractere.isupper() for caractere in senha):
        return False, "Inclua ao menos uma letra maiúscula na senha mestra."

    if not any(caractere.isdigit() for caractere in senha):
        return False, "Inclua ao menos um número na senha mestra."

    if not any(caractere in string.punctuation for caractere in senha):
        return False, "Inclua ao menos um caractere especial na senha mestra."

    return True, "Senha mestra válida."


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
    kdf = Argon2id(
        salt=salt,
        length=dklen,
        iterations=iterations,
        lanes=lanes,
        memory_cost=memory_cost,
        secret=segredo_keyfile,
    )
    return kdf.derive(senha.encode("utf-8"))


def derivar_chave_scrypt_legado(
    senha: str,
    salt: bytes,
    n: int,
    r: int,
    p: int,
    dklen: int,
) -> bytes:
    """Deriva uma chave com scrypt para compatibilidade com cofres legados."""
    return hashlib.scrypt(
        password=senha.encode("utf-8"),
        salt=salt,
        n=n,
        r=r,
        p=p,
        dklen=dklen,
    )


def criar_registro_senha_mestra(
    senha_mestra: str,
    segredo_keyfile: bytes | None = None,
    parametros_argon2id: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Cria salts e verificador da senha mestra para o formato atual do cofre."""
    parametros = dict(PARAMETROS_ARGON2ID_PADRAO)
    if parametros_argon2id:
        parametros.update(parametros_argon2id)

    salt_verificador = gerar_bytes_seguro(16)
    salt_criptografia = gerar_bytes_seguro(16)
    verificador = derivar_chave_argon2id(
        senha=senha_mestra,
        salt=salt_verificador,
        iterations=int(parametros["iterations"]),
        lanes=int(parametros["lanes"]),
        memory_cost=int(parametros["memory_cost"]),
        dklen=int(parametros["dklen_verificador"]),
        segredo_keyfile=segredo_keyfile,
    )

    return {
        "kdf": {
            "algoritmo": "argon2id",
            "iterations": int(parametros["iterations"]),
            "lanes": int(parametros["lanes"]),
            "memory_cost": int(parametros["memory_cost"]),
            "dklen_verificador": int(parametros["dklen_verificador"]),
            "dklen_chave": int(parametros["dklen_chave"]),
            "salt_verificador": _b64_encode(salt_verificador),
            "salt_criptografia": _b64_encode(salt_criptografia),
            "usa_keyfile": segredo_keyfile is not None,
        },
        "verificador_senha": _b64_encode(verificador),
    }


def verificar_senha_mestra(
    senha_mestra: str,
    kdf: dict[str, Any],
    verificador_senha: str,
    segredo_keyfile: bytes | None = None,
) -> bool:
    """Verifica a senha mestra com comparação segura em tempo constante."""
    algoritmo = str(kdf.get("algoritmo", "scrypt")).lower()
    esperado = _b64_decode(verificador_senha)

    if algoritmo == "argon2id":
        salt_verificador = _b64_decode(kdf["salt_verificador"])
        calculado = derivar_chave_argon2id(
            senha=senha_mestra,
            salt=salt_verificador,
            iterations=int(kdf["iterations"]),
            lanes=int(kdf["lanes"]),
            memory_cost=int(kdf["memory_cost"]),
            dklen=int(kdf["dklen_verificador"]),
            segredo_keyfile=segredo_keyfile,
        )
        return hmac.compare_digest(calculado, esperado)

    salt_verificador = _b64_decode(kdf["salt_verificador"])
    calculado = derivar_chave_scrypt_legado(
        senha=senha_mestra,
        salt=salt_verificador,
        n=int(kdf["n"]),
        r=int(kdf["r"]),
        p=int(kdf["p"]),
        dklen=int(kdf["dklen_verificador"]),
    )
    return hmac.compare_digest(calculado, esperado)


def gerar_chave_criptografia(
    senha_mestra: str,
    kdf: dict[str, Any],
    segredo_keyfile: bytes | None = None,
) -> bytes:
    """Deriva a chave de criptografia apropriada para a versão atual do cofre."""
    algoritmo = str(kdf.get("algoritmo", "scrypt")).lower()
    salt_criptografia = _b64_decode(kdf["salt_criptografia"])

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

    return derivar_chave_scrypt_legado(
        senha=senha_mestra,
        salt=salt_criptografia,
        n=int(kdf["n"]),
        r=int(kdf["r"]),
        p=int(kdf["p"]),
        dklen=int(kdf["dklen_chave"]),
    )


def gerar_chave_fernet_legado(senha_mestra: str, kdf: dict[str, Any]) -> bytes:
    """Deriva chave em formato Fernet para leitura de cofres legados."""
    chave_bruta = gerar_chave_criptografia(senha_mestra, kdf)
    return base64.urlsafe_b64encode(chave_bruta)


def criptografar_objeto(dados: Any, chave_aes: bytes) -> dict[str, str]:
    """Criptografa dados com AES-256-GCM no formato atual do projeto."""
    nonce = gerar_bytes_seguro(12)
    ciphertext = AESGCM(chave_aes).encrypt(nonce, _serializar_dados(dados), AAD_AES_GCM)
    return {
        "algoritmo": "aes-256-gcm",
        "nonce": _b64_encode(nonce),
        "ciphertext": _b64_encode(ciphertext),
    }


def descriptografar_objeto(carga_criptografada: dict[str, str], chave_aes: bytes) -> Any:
    """Descriptografa o payload atual protegido com AES-256-GCM."""
    if not isinstance(carga_criptografada, dict):
        raise ValueError("Payload criptografado inválido para o formato atual.")
    if carga_criptografada.get("algoritmo") != "aes-256-gcm":
        raise ValueError("Algoritmo de criptografia não suportado.")

    nonce = _b64_decode(carga_criptografada["nonce"])
    ciphertext = _b64_decode(carga_criptografada["ciphertext"])

    try:
        conteudo = AESGCM(chave_aes).decrypt(nonce, ciphertext, AAD_AES_GCM)
    except InvalidTag as exc:
        raise ValueError("Falha ao descriptografar os dados do cofre.") from exc

    try:
        return json.loads(conteudo.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("Os dados descriptografados estão inválidos.") from exc


def criptografar_objeto_legado(dados: Any, chave_fernet: bytes) -> str:
    """Criptografa dados no formato legado para testes e compatibilidade."""
    token = Fernet(chave_fernet).encrypt(_serializar_dados(dados))
    return token.decode("utf-8")


def descriptografar_objeto_legado(token: str, chave_fernet: bytes) -> Any:
    """Descriptografa token Fernet de cofres legados."""
    try:
        conteudo = Fernet(chave_fernet).decrypt(token.encode("utf-8"))
    except InvalidToken as exc:
        raise ValueError("Falha ao descriptografar os dados do cofre legado.") from exc

    try:
        return json.loads(conteudo.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("Os dados descriptografados estão inválidos.") from exc


def gerar_senha_forte(
    comprimento: int = 16,
    incluir_maiusculas: bool = True,
    incluir_minusculas: bool = True,
    incluir_numeros: bool = True,
    incluir_especiais: bool = True,
) -> str:
    """Gera senha aleatória forte garantindo classes de caracteres selecionadas."""
    grupos: list[str] = []

    if incluir_maiusculas:
        grupos.append(string.ascii_uppercase)
    if incluir_minusculas:
        grupos.append(string.ascii_lowercase)
    if incluir_numeros:
        grupos.append(string.digits)
    if incluir_especiais:
        grupos.append(string.punctuation)

    if not grupos:
        raise ValueError("Selecione ao menos um conjunto de caracteres.")

    if comprimento < len(grupos):
        raise ValueError(
            "Comprimento insuficiente para cobrir os conjuntos de caracteres selecionados."
        )

    caracteres = [secrets.choice(grupo) for grupo in grupos]
    universo = "".join(grupos)

    while len(caracteres) < comprimento:
        caracteres.append(secrets.choice(universo))

    indice = len(caracteres) - 1
    while indice > 0:
        novo_indice = secrets.randbelow(indice + 1)
        caracteres[indice], caracteres[novo_indice] = (
            caracteres[novo_indice],
            caracteres[indice],
        )
        indice -= 1

    return "".join(caracteres)
