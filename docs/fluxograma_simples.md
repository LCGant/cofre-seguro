# Fluxograma Simples

Fluxograma de visão geral do projeto **Cofre Seguro**.

```mermaid
flowchart TD
    A[Início da aplicação] --> B{Já existe cofre?}

    B -- Não --> C[Tela de criação]
    C --> D[Usuário define senha mestra<br/>e keyfile opcional]
    D --> E{Senha forte?}
    E -- Não --> C
    E -- Sim --> F[Cofre criado e criptografado]
    F --> G[Tela de login]

    B -- Sim --> G

    G --> H[Usuário informa senha mestra]
    H --> I{Login válido?}
    I -- Não --> J[Atraso progressivo<br/>ou bloqueio temporário]
    J --> G
    I -- Sim --> K[Tela principal<br/>sidebar + dashboard + cards]

    K --> L[Buscar e filtrar itens<br/>por tipo ou favoritos]
    K --> M[Cadastrar novo item<br/>senha, cartão, documento,<br/>nota, wifi ou licença]
    K --> N[Visualizar, editar<br/>ou excluir item]
    K --> O[Revelar ou copiar<br/>campo sensível<br/>sessão já autenticada]
    K --> P[Configurações:<br/>trocar senha, exportar,<br/>importar, alternar tema]
    K --> Q[Sair ou inatividade<br/>5 min]

    L --> K
    M --> K
    N --> K
    O --> K
    P --> K

    Q --> R[Encerrar sessão<br/>limpar dados sensíveis]
    R --> S[Fim]
```
