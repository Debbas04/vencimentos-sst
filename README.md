# Vencimentos de SST

Relatório de vencimentos de ASO, treinamentos NR, ordens de serviço e CA de EPI para construtora: o que está vencido, sem registro ou vence em 30 e 60 dias, por obra e por empresa (próprios e terceirizados).

**Usar online:** abra a página do GitHub Pages deste repositório e escolha a planilha. A planilha é lida no próprio navegador (Python via [Pyodide](https://pyodide.org)) e não é enviada para lugar nenhum. Sem planilha, use “Ver exemplo com dados fictícios” ou “Baixar modelo vazio”.

**Usar no computador:** `py -3.13 vencimentos.py --planilha caminho/controle-sst.xlsx` (precisa de `openpyxl`). Modelo: `py -3.13 criar_planilha.py`.

| Arquivo | O que faz |
|---|---|
| `index.html` | A ferramenta online |
| `web.py` | Ponte entre a página e os scripts |
| `vencimentos.py` | Lê a planilha e calcula a situação de cada item |
| `relatorio.py` | Monta o HTML do relatório |
| `criar_planilha.py` | Gera o modelo (vazio ou com exemplo fictício) |
| `esquema.py` | Abas, colunas, prazos padrão e matriz de funções |

Os prazos padrão (aba Itens) foram conferidos em 26/10/2026 e são ponto de partida: o que vale é o PGR e o PCMSO da empresa. Não registre resultado de exame nem CID na planilha, só datas e aptidão (LGPD).
