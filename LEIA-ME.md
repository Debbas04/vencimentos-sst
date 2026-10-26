---
projeto: empresa
tipo: output
data: 2026-10-26
status: ativo
fontes: ["[[001 Prazos e Periodicidades]]"]
---

# Controle de vencimentos de SST

Lê uma planilha com funcionários, o que cada função exige e os registros de ASO, treinamentos e OS. Gera um relatório HTML do que está **vencido**, **faltando**, vencendo em **até 30 dias** e em **31 a 60 dias**, por obra e por empresa (próprios e terceirizados), mais os **CA de EPI**.

## Arquivos

| Arquivo | O que é |
|---|---|
| `controle-sst.xlsx` | A planilha. A que está aqui tem **dados fictícios** para teste |
| `RODAR.bat` | Dois cliques: gera o relatório e abre no navegador |
| `vencimentos.py` | Lê a planilha e calcula a situação de cada item |
| `relatorio.py` | Monta o HTML do relatório (visual, filtros, impressão) |
| `criar_planilha.py` | Cria um modelo novo (vazio ou com exemplo) |
| `esquema.py` | Abas, colunas, itens e funções padrão (mude aqui para mudar nos dois scripts) |
| `relatorios/` | Relatórios gerados, um por data |

## Uso

```bash
py -3.13 criar_planilha.py --saida "D:/Empresa/SST/controle-sst.xlsx"
py -3.13 vencimentos.py --planilha "D:/Empresa/SST/controle-sst.xlsx"
py -3.13 vencimentos.py --hoje 2026-12-01 --nao-abrir
```

Precisa só de Python com `openpyxl` (o `py -3.13` desta máquina já tem).

## A planilha

| Aba | Conteúdo |
|---|---|
| **Itens** | Código, descrição, validade em meses (vazio = não vence), base legal. Prazos padrão conferidos em 26/10/2026 |
| **Funções** | Uma linha por função, uma coluna por item: `X` = exigido com a validade padrão; número = validade própria (ex.: `24` no ASO do administrativo) |
| **Funcionários** | Matrícula, nome, função, obra, empresa (`Própria` ou a terceirizada), admissão, situação (Ativo/Afastado/Desligado) |
| **Registros** | Uma linha por ASO, treinamento ou OS feito. Vale o mais recente. `Vence em` só quando for diferente do calculado |
| **EPI e CA** | CAs dos EPIs em uso e a validade (consultar no CAEPI) |

O relatório também lista **problemas na planilha**: matrícula que não existe, código desconhecido, data inválida, função sem linha na aba Funções.

## O relatório

Visual com as cores de segurança da NBR 7195 (as das placas de obra): vermelho = vencido, laranja = vence em até 30 dias, amarelo = 31 a 60 dias, azul = sem registro (ação obrigatória), verde = em dia. Seções, nessa ordem:

1. **Faixa de sinalização** com as contagens; clicar numa cor filtra a tabela.
2. **Esta semana:** o que está vencido, sem registro ou vence em até 30 dias, agrupado por item com a ação (agendar exame, montar turma, colher assinatura da OS, fazer integração) e a lista de pessoas. Inclui EPI com CA vencendo.
3. **Por obra:** barra e contagem de cada canteiro; clicar no nome filtra a tabela.
4. **Pendências:** tabela com filtros de situação, obra, empresa e busca. Os filtros ficam no endereço da página, então dá para salvar nos favoritos a visão de uma obra.
5. **CA dos EPIs** e **Corrigir na planilha**.

Funciona no celular, no modo escuro e na impressão (Ctrl+P sai sem os filtros e com as cores). As fontes (Barlow) vêm do Google Fonts; sem internet, o navegador usa uma fonte do sistema e o resto funciona igual.

## Cuidados

- **A planilha real fica fora do cofre** (ex.: `D:\Empresa\SST\`) e é passada com `--planilha`. O relatório tem nomes: documento interno.
- Não registrar resultado de exame nem CID, só data e aptidão (ver [[006 LGPD e Dados de Saude]]).
- A matriz da aba Funções é um ponto de partida genérico. O técnico ajusta ao PGR e ao PCMSO da empresa.

## Próximos passos

1. Trocar o exemplo pela planilha que o técnico usa hoje: adaptar as colunas dela ao esquema, ou o esquema a ela.
2. Versão em HTML puro (abre a planilha no navegador, sem Python) para rodar no PC do técnico.
3. Aviso automático semanal (tarefa agendada no Windows ou e-mail para o técnico).
