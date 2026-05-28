# Diagrama de Atividade — Fluxo do Chamado (OS)

```mermaid
flowchart TD
  A[Início] --> B[Abrir chamado]
  B --> C{Departamento informado?}
  C -- não --> C1[Rejeitar: departamento obrigatório] --> B
  C -- sim --> D[Salvar OS (status=aberta)]
  D --> E[Registrar histórico: OS criada]
  E --> F[Kanban]

  F --> G{Avançar status?}
  G -- não --> F
  G -- sim --> H[Validar sequência (RN004)]
  H --> I{Usuário tem permissão por departamento?}
  I -- não --> I1[Rejeitar: acesso negado] --> F
  I -- sim --> J[Calcular próximo status]

  J --> K{Próximo status = em_andamento?}
  K -- sim --> K1{OS tem técnico?}
  K1 -- não --> K2[Atribuir técnico automaticamente ao usuário (não-admin)]
  K1 -- sim --> L
  K2 --> L
  K -- não --> L

  L{Status atual é em_andamento?}
  L -- sim --> M[Solicitar descrição do serviço (modal)]
  M --> N{Descrição preenchida?}
  N -- não --> M
  N -- sim --> O[Avançar status e registrar histórico com observação]
  L -- não --> P[Avançar status e registrar histórico]

  P --> Q{Novo status = encerrada?}
  O --> Q

  Q -- sim --> R[Fim: OS encerrada]
  Q -- não --> F
```

