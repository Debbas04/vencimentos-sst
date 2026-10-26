"""Esquema da planilha controle-sst.xlsx: abas, colunas e valores padrão.

Usado por criar_planilha.py (que monta o modelo) e por vencimentos.py (que lê).
Mudou uma coluna aqui, muda nos dois.
"""

ABA_LEIAME = "LEIA-ME"
ABA_ITENS = "Itens"
ABA_FUNCOES = "Funções"
ABA_FUNCIONARIOS = "Funcionários"
ABA_REGISTROS = "Registros"
ABA_CA = "EPI e CA"

COLS_ITENS = ["Código", "Descrição", "Validade (meses)", "Base legal", "Observação"]
COLS_FUNCIONARIOS = ["Matrícula", "Nome", "Função", "Obra", "Empresa", "Admissão", "Situação"]
COLS_REGISTROS = ["Matrícula", "Código", "Data de realização", "Vence em", "Observação"]
COLS_CA = ["EPI", "Fabricante", "CA", "Validade do CA", "Em uso"]

SITUACOES = ["Ativo", "Afastado", "Desligado"]

# Faixas de alerta, em dias até o vencimento
ALERTA_CURTO = 30
ALERTA_LONGO = 60

# Situações do relatório: código -> (singular, plural, ordem de urgência)
STATUS = {
    "vencido": ("Vencido", "Vencidos", 0),
    "faltando": ("Sem registro", "Sem registro", 1),
    "30": (f"Vence em até {ALERTA_CURTO} dias", f"Vencem em até {ALERTA_CURTO} dias", 2),
    "60": (f"Vence em {ALERTA_CURTO + 1} a {ALERTA_LONGO} dias", f"Vencem em {ALERTA_CURTO + 1} a {ALERTA_LONGO} dias", 3),
    "ok": ("Em dia", "Em dia", 4),
}

# O que fazer com cada item no bloco "Esta semana" (o padrão vale para treinamentos NR)
ACOES = {
    "ASO": "Agendar exame periódico",
    "OS": "Colher assinatura da ordem de serviço",
    "INTEG": "Fazer a integração antes de entrar no canteiro",
}
ACAO_PADRAO = "Incluir em turma ou reciclagem"

# (código, descrição, validade em meses ou None = não vence, base legal, observação)
# Prazos conferidos em 26/10/2026: ver "001 Prazos e Periodicidades" na biblioteca de SST.
ITENS_PADRAO = [
    ("ASO", "ASO periódico (exame clínico)", 12, "NR-7, item 7.5.8",
     "12 meses para expostos a riscos do PGR; 24 meses para os demais. O PCMSO manda. "
     "Ajuste por função na aba Funções."),
    ("NR18", "Treinamento NR-18 (inicial ou periódico)", 24, "NR-18, item 18.14 e Anexo I",
     "Inicial de 4 h antes de começar na obra; periódico a cada 2 anos (4 h). Registre a data do último."),
    ("NR35", "Trabalho em altura (NR-35)", 24, "NR-35",
     "Inicial e periódico de 8 h, a cada 2 anos. Refazer também após mudança de procedimento, "
     "acidente ou afastamento acima de 90 dias."),
    ("NR10", "Eletricidade (NR-10 básico ou reciclagem)", 24, "NR-10",
     "Reciclagem a cada 2 anos. Carga horária da reciclagem: conferir no texto vigente."),
    ("NR33", "Espaço confinado (NR-33)", 12, "NR-33",
     "Reciclagem anual de 8 h. Conferir após a revisão recente da NR-33."),
    ("NR12", "Operação de máquinas (NR-12)", None, "NR-12",
     "A NR-12 não fixa periodicidade. Se o PGR fixar, preencha a validade para ter alerta."),
    ("NR11", "Operador de equipamento de movimentação (NR-11)", None, "NR-11",
     "Conferir no texto vigente a validade do cartão de identificação do operador."),
    ("OS", "Ordem de serviço de SST assinada", None, "NR-1",
     "Não vence. Refazer quando mudar a função ou os riscos."),
    ("INTEG", "Integração de segurança na obra", None, "NR-18 / PGR da obra",
     "Não vence. Exigida antes de entrar no canteiro."),
]

# Matriz função × item. "X" = exigido com a validade padrão; número = exigido com essa validade (meses).
# Ponto de partida genérico: o técnico deve ajustar ao PGR e ao PCMSO da empresa.
FUNCOES_PADRAO = {
    "Servente":              {"ASO": "X", "NR18": "X", "OS": "X", "INTEG": "X"},
    "Pedreiro":              {"ASO": "X", "NR18": "X", "NR35": "X", "OS": "X", "INTEG": "X"},
    "Carpinteiro":           {"ASO": "X", "NR18": "X", "NR35": "X", "NR12": "X", "OS": "X", "INTEG": "X"},
    "Armador":               {"ASO": "X", "NR18": "X", "NR35": "X", "NR12": "X", "OS": "X", "INTEG": "X"},
    "Eletricista":           {"ASO": "X", "NR18": "X", "NR35": "X", "NR10": "X", "OS": "X", "INTEG": "X"},
    "Encanador":             {"ASO": "X", "NR18": "X", "NR33": "X", "OS": "X", "INTEG": "X"},
    "Montador de andaime":   {"ASO": "X", "NR18": "X", "NR35": "X", "OS": "X", "INTEG": "X"},
    "Operador de grua":      {"ASO": "X", "NR18": "X", "NR35": "X", "NR11": "X", "OS": "X", "INTEG": "X"},
    "Encarregado":           {"ASO": "X", "NR18": "X", "NR35": "X", "OS": "X", "INTEG": "X"},
    "Almoxarife":            {"ASO": "X", "NR18": "X", "OS": "X", "INTEG": "X"},
    "Técnico de segurança":  {"ASO": "X", "NR18": "X", "NR35": "X", "NR33": "X", "OS": "X", "INTEG": "X"},
    "Engenheiro":            {"ASO": 24, "NR18": "X", "NR35": "X", "OS": "X", "INTEG": "X"},
    "Administrativo":        {"ASO": 24, "OS": "X"},
}
