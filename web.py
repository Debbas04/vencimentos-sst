"""Ponte entre a página web (index.html) e os scripts. Roda no navegador, via Pyodide.

A planilha chega como bytes, é lida em memória e nunca sai do computador de quem abriu a página.
"""
import datetime as dt
import io
import json
from pathlib import PurePath

from openpyxl import load_workbook

import criar_planilha
import relatorio
import vencimentos


def relatorio_de_bytes(dados, nome, hoje_iso, gerado_em):
    """Devolve JSON: {"html": ...} ou {"erro": mensagem para mostrar na página}."""
    hoje = dt.date.fromisoformat(hoje_iso)
    if hasattr(dados, "to_py"):  # Uint8Array vindo do JavaScript
        dados = dados.to_py()
    try:
        wb = load_workbook(io.BytesIO(bytes(dados)), data_only=True, read_only=True)
    except Exception:
        return json.dumps({"erro": "Não consegui ler esse arquivo como planilha do Excel (.xlsx). "
                                   "Abra no Excel, salve como .xlsx e tente de novo."})
    try:
        res = vencimentos.analisar(wb, hoje)
    except SystemExit as erro:  # os scripts encerram com uma mensagem quando falta aba ou coluna
        return json.dumps({"erro": f"{erro} Baixe o modelo vazio para ver as abas e colunas esperadas."})
    finally:
        wb.close()
    return json.dumps({"html": relatorio.gerar_html(res, hoje, PurePath(nome), gerado_em=gerado_em)})


def planilha_bytes(exemplo, hoje_iso):
    """Modelo vazio (exemplo=False) ou com dados fictícios datados a partir de hoje."""
    buf = io.BytesIO()
    criar_planilha.montar(buf, exemplo, dt.date.fromisoformat(hoje_iso))
    return buf.getvalue()
