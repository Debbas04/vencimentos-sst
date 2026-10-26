"""Monta o HTML do relatório de vencimentos de SST: um arquivo só, que abre em qualquer navegador.

Direção visual: cores de segurança da NBR 7195 (as das placas de obra) sobre cinza concreto,
Barlow Condensed nos títulos e números. A faixa de sinalização do topo é o único elemento forte.
"""
import datetime as dt
import html
from collections import Counter, defaultdict

import esquema as E

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
ORDEM = ("vencido", "faltando", "30", "60", "ok")
esc = html.escape


def data_longa(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def data_curta(d):
    return d.strftime("%d/%m/%Y") if d else "—"


def plural(n, um, varios):
    return f"{n} {um if n == 1 else varios}"


def prazo(dias, status):
    if status == "faltando":
        return "sem registro"
    if dias is None:
        return "não vence"
    if dias < 0:
        return f"há {plural(-dias, 'dia', 'dias')}"
    if dias == 0:
        return "hoje"
    return f"em {plural(dias, 'dia', 'dias')}"


def quando(l):
    if l["status"] == "faltando":
        return "sem registro"
    verbo = "venceu" if l["status"] == "vencido" else "vence"
    return f"{verbo} {l['vence']:%d/%m} ({prazo(l['dias'], l['status'])})"


def chip(status, curto=True):
    rotulo = {"30": f"Até {E.ALERTA_CURTO} dias", "60": f"{E.ALERTA_CURTO + 1} a {E.ALERTA_LONGO} dias"}.get(status) \
        if curto else None
    return f'<span class="chip c-{status}">{esc(rotulo or E.STATUS[status][0])}</span>'


def barra(cont, total, rotulo):
    if not total:
        return ""
    partes = "".join(
        f'<span class="b-{s}" style="width:{cont[s] / total * 100:.2f}%"></span>' for s in ORDEM if cont[s]
    )
    # o mesmo dado sempre aparece em texto ao lado, então a barra fica fora do leitor de tela
    return f'<div class="barra" aria-hidden="true" title="{esc(rotulo)}">{partes}</div>'


def resumo_contagem(cont, ate):
    pedacos = []
    if cont["vencido"]:
        pedacos.append(plural(cont["vencido"], "vencido", "vencidos"))
    if cont["faltando"]:
        pedacos.append(f"{cont['faltando']} sem registro")
    if cont["30"]:
        pedacos.append(f"{cont['30']} {'vence' if cont['30'] == 1 else 'vencem'} até {ate:%d/%m}")
    if cont["60"]:
        pedacos.append(f"{cont['60']} entre {E.ALERTA_CURTO + 1} e {E.ALERTA_LONGO} dias")
    return ", ".join(pedacos) or "tudo em dia"


# ---------------------------------------------------------------- blocos

def bloco_placa(linhas):
    cont = Counter(l["status"] for l in linhas)
    segs = []
    for s in ORDEM:
        n = cont[s]
        rotulo = E.STATUS[s][0 if n == 1 else 1]
        segs.append(
            f'<button type="button" class="seg s-{s}" data-status="{s}" aria-pressed="false" '
            f'aria-label="{n} {esc(rotulo.lower())}: mostrar na tabela">'
            f'<b>{n}</b><span>{esc(rotulo)}</span></button>'
        )
    total = len(linhas)
    pct = round(cont["ok"] / total * 100) if total else 100
    texto = f"{pct}% dos itens controlados estão em dia" if total else "Nenhum item controlado ainda"
    return (f'<section class="placa" aria-label="Resumo por situação">{"".join(segs)}</section>'
            f'<div class="conf">{barra(cont, total, texto)}<p>{texto}.</p></div>')


def bloco_semana(linhas, cas, hoje):
    ate = hoje + dt.timedelta(days=E.ALERTA_CURTO)
    urgentes = [l for l in linhas if l["status"] in ("vencido", "faltando", "30")]
    grupos = defaultdict(list)
    for l in urgentes:
        grupos[(l["codigo"], l["item"])].append(l)

    def peso(item):
        pessoas = item[1]
        return (-sum(p["status"] in ("vencido", "faltando") for p in pessoas), -len(pessoas))

    blocos = []
    for (cod, item), pessoas in sorted(grupos.items(), key=peso):
        cont = Counter(p["status"] for p in pessoas)
        acao = E.ACOES.get(cod, E.ACAO_PADRAO)
        lis = "".join(
            f'<li>{chip(p["status"])}<span class="quem"><span class="nome">{esc(p["nome"])}</span>'
            f'<span class="det">{esc(p["funcao"])}, {esc(p["obra"])}{" (afastado)" if "afastado" in p["nota"] else ""}</span></span>'
            f'<span class="qd">{esc(quando(p))}</span></li>'
            for p in pessoas
        )
        blocos.append(
            f'<div class="acao"><div class="acao-tit"><h3>{esc(item)}</h3>'
            f'<p class="verbo">{esc(acao)}: {plural(len(pessoas), "pessoa", "pessoas")}</p>'
            f'<p class="nota">{esc(resumo_contagem(cont, ate))}</p></div><ul class="pessoas">{lis}</ul></div>'
        )

    epis = [c for c in cas if c["status"] in ("vencido", "30")]
    if epis:
        lis = "".join(
            f'<li>{chip(c["status"])}<span class="quem"><span class="nome">{esc(c["epi"])}</span>'
            f'<span class="det">CA {esc(c["ca"])}, {esc(c["fabricante"])}</span></span>'
            f'<span class="qd">{"venceu" if c["status"] == "vencido" else "vence"} {c["vence"]:%d/%m} '
            f'({prazo(c["dias"], c["status"])})</span></li>'
            for c in epis
        )
        blocos.append(
            '<div class="acao"><div class="acao-tit"><h3>EPI com CA vencendo</h3>'
            f'<p class="verbo">Trocar o lote ou confirmar nova validade no CAEPI: {plural(len(epis), "EPI", "EPIs")}</p>'
            f'</div><ul class="pessoas">{lis}</ul></div>'
        )

    if blocos:
        corpo = "".join(blocos)
    else:
        proximos = sorted((l for l in linhas if l["dias"] is not None and l["dias"] >= 0), key=lambda l: l["dias"])
        dica = (f" O próximo vencimento é {esc(proximos[0]['item'])} de {esc(proximos[0]['nome'])}, "
                f"em {proximos[0]['vence']:%d/%m/%Y}.") if proximos else ""
        corpo = f'<p class="vazio">Nada para resolver ou agendar agora.{dica}</p>'

    return (f'<section id="semana" aria-labelledby="t-semana"><h2 id="t-semana">Esta semana</h2>'
            f'<p class="intro">Vencidos, sem registro e o que vence até {data_longa(ate)}. '
            f'Exame e turma levam tempo para marcar, por isso entram já.</p>{corpo}</section>')


def bloco_obras(linhas, hoje):
    ate = hoje + dt.timedelta(days=E.ALERTA_CURTO)
    por_obra = defaultdict(Counter)
    pessoas = defaultdict(set)
    for l in linhas:
        por_obra[l["obra"]][l["status"]] += 1
        pessoas[l["obra"]].add(l["matricula"])
    linhas_html = "".join(
        f'<li><button type="button" class="obra-btn" data-obra="{esc(o)}">{esc(o)}</button>'
        f'<span class="det">{plural(len(pessoas[o]), "pessoa", "pessoas")}</span>'
        f'{barra(c, sum(c.values()), resumo_contagem(c, ate))}'
        f'<span class="qd">{esc(resumo_contagem(c, ate))}</span></li>'
        for o, c in sorted(por_obra.items())
    )
    return (f'<section aria-labelledby="t-obras"><h2 id="t-obras">Por obra</h2>'
            f'<ul class="obras">{linhas_html or "<li>Nenhuma obra na planilha.</li>"}</ul></section>')


def bloco_tabela(linhas):
    obras = sorted({l["obra"] for l in linhas})
    empresas = sorted({l["empresa"] for l in linhas})
    opcoes = lambda xs: "".join(f'<option value="{esc(x)}">{esc(x)}</option>' for x in xs)
    st_opcoes = "".join(f'<option value="{s}">{esc(E.STATUS[s][0])}</option>' for s in ORDEM)
    corpo = []
    for l in linhas:
        busca = " ".join([l["nome"], l["matricula"], l["funcao"], l["codigo"], l["item"]]).lower()
        nota = f'<span class="nota">{esc(l["nota"])}</span>' if l["nota"] else ""
        corpo.append(
            f'<tr data-obra="{esc(l["obra"])}" data-emp="{esc(l["empresa"])}" data-status="{l["status"]}" data-txt="{esc(busca)}">'
            f'<td data-label="Situação">{chip(l["status"])}</td>'
            f'<td data-label="Pessoa"><span class="nome">{esc(l["nome"])}</span>'
            f'<span class="nota">Matrícula {esc(l["matricula"])}, {esc(l["funcao"])}</span></td>'
            f'<td data-label="Item"><span class="nome" translate="no">{esc(l["codigo"])}</span><span class="nota">{esc(l["item"])}</span></td>'
            f'<td data-label="Obra">{esc(l["obra"])}<span class="nota">{esc(l["empresa"])}</span></td>'
            f'<td data-label="Último" class="num">{data_curta(l["data"])}</td>'
            f'<td data-label="Vence" class="num">{data_curta(l["vence"])}</td>'
            f'<td data-label="Prazo">{prazo(l["dias"], l["status"])}{nota}</td></tr>'
        )
    return f"""<section id="pendencias" aria-labelledby="t-pend"><h2 id="t-pend">Pendências</h2>
<div class="filtros">
<label>Situação<select id="f-st" name="situacao"><option value="">Todas, menos em dia</option>{st_opcoes}</select></label>
<label>Obra<select id="f-obra" name="obra"><option value="">Todas</option>{opcoes(obras)}</select></label>
<label>Empresa<select id="f-emp" name="empresa"><option value="">Todas</option>{opcoes(empresas)}</select></label>
<label class="busca">Buscar<input type="search" id="f-busca" name="busca" placeholder="Ex.: Otávio, 1015, pedreiro, NR35…" autocomplete="off" spellcheck="false"></label>
<label class="check"><input type="checkbox" id="f-ok" name="em-dia"> Mostrar itens em dia</label>
<button type="button" id="limpar">Limpar filtros</button>
<p class="cont" id="cont" aria-live="polite"></p></div>
<table class="tab" id="pend"><thead><tr><th scope="col">Situação</th><th scope="col">Pessoa</th><th scope="col">Item</th>
<th scope="col">Obra</th><th scope="col">Último</th><th scope="col">Vence</th><th scope="col">Prazo</th></tr></thead>
<tbody>{"".join(corpo)}</tbody></table>
<p class="vazio" id="vazio" hidden>Nenhum item com esses filtros. Use “Limpar filtros” para ver tudo.</p></section>"""


def bloco_ca(cas):
    if not cas:
        return ('<section aria-labelledby="t-ca"><h2 id="t-ca">CA dos EPIs em uso</h2>'
                '<p class="vazio">Nenhum CA cadastrado. Preencha a aba “EPI e CA” para ter alerta de validade.</p></section>')
    linhas = "".join(
        f'<tr><td data-label="Situação">{chip(c["status"])}</td><td data-label="EPI"><span class="nome">{esc(c["epi"])}</span>'
        f'<span class="nota">{esc(c["fabricante"])}</span></td><td data-label="CA" class="num" translate="no">{esc(c["ca"])}</td>'
        f'<td data-label="Validade" class="num">{data_curta(c["vence"])}</td><td data-label="Prazo">{prazo(c["dias"], c["status"])}</td></tr>'
        for c in cas
    )
    return (f'<section aria-labelledby="t-ca"><h2 id="t-ca">CA dos EPIs em uso</h2><table class="tab">'
            f'<thead><tr><th scope="col">Situação</th><th scope="col">EPI</th><th scope="col">CA</th>'
            f'<th scope="col">Validade</th><th scope="col">Prazo</th></tr></thead><tbody>{linhas}</tbody></table></section>')


def bloco_problemas(problemas):
    if not problemas:
        return ""
    itens = "".join(f"<li>{esc(p)}</li>" for p in problemas)
    return (f'<section aria-labelledby="t-prob"><h2 id="t-prob">Corrigir na planilha</h2>'
            f'<p class="intro">Essas linhas ficaram fora do relatório. Corrija e gere de novo.</p>'
            f'<ul class="problemas">{itens}</ul></section>')


# ---------------------------------------------------------------- página

CSS = """
:root{
--concreto:#E6E8E9;--papel:#FFFFFF;--grafite:#1D2328;--cimento:#56616A;--linha:#CBD1D5;
--vermelho:#C8102E;--laranja:#E35205;--amarelo:#F6BE00;--azul:#005EB8;--verde:#19803A;
--t-vencido:#A50D26;--t-30:#A63C00;--t-60:#6E5300;--t-faltando:#004A93;--t-ok:#14672F;
--f-vencido:#FBE6E9;--f-30:#FDEBE1;--f-60:#FFF4CC;--f-faltando:#E2EDF9;--f-ok:#E3F2E7;
--cond:"Barlow Condensed","Arial Narrow","Roboto Condensed",sans-serif;
--corpo:"Barlow","Segoe UI",system-ui,sans-serif;color-scheme:light}
@media (prefers-color-scheme:dark){:root{
--concreto:#15191C;--papel:#1F2529;--grafite:#E7EAEC;--cimento:#9EA9B1;--linha:#353D43;
--t-vencido:#FF8C99;--t-30:#FFA36B;--t-60:#F2CF55;--t-faltando:#7DB8F5;--t-ok:#77D196;
--f-vencido:#3B1A20;--f-30:#3B2416;--f-60:#352C0F;--f-faltando:#14283D;--f-ok:#163020;color-scheme:dark}}
*{box-sizing:border-box}
body{margin:0;background:var(--concreto);color:var(--grafite);font:400 15px/1.5 var(--corpo);
-webkit-font-smoothing:antialiased;font-variant-numeric:tabular-nums}
main{max-width:1180px;margin:0 auto;padding:32px 16px 56px}
h1,h2,h3{font-family:var(--cond);font-weight:700;line-height:1.1;margin:0;text-wrap:balance}
h1{font-size:clamp(32px,5vw,46px);letter-spacing:-.01em}
h2{font-size:26px;margin:44px 0 6px}
h3{font-size:20px;font-weight:600}
p{margin:0}
.topo{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:12px 32px;margin-bottom:20px}
.topo .sub{color:var(--cimento);margin-top:6px}
.topo .data{font-family:var(--cond);font-size:22px;font-weight:600;text-align:right}
.topo .data span{display:block;font-family:var(--corpo);font-size:13px;font-weight:400;color:var(--cimento)}
/* faixa de sinalização */
.placa{display:grid;grid-template-columns:repeat(5,1fr);border-radius:6px;overflow:hidden}
.seg{all:unset;box-sizing:border-box;cursor:pointer;padding:16px 18px 14px;display:flex;flex-direction:column;gap:4px;min-height:118px;position:relative}
.seg b{font-family:var(--cond);font-weight:700;font-size:clamp(40px,6vw,64px);line-height:.9}
.seg span{font-weight:500;font-size:14px;line-height:1.25}
.s-vencido{background:var(--vermelho);color:#fff}.s-30{background:var(--laranja);color:#1D2328}
.s-60{background:var(--amarelo);color:#1D2328}.s-faltando{background:var(--azul);color:#fff}.s-ok{background:var(--verde);color:#fff}
.seg[aria-pressed=true]{box-shadow:inset 0 -6px 0 rgba(0,0,0,.45)}
.seg:hover b{text-decoration:underline;text-decoration-thickness:3px;text-underline-offset:6px}
.seg:focus-visible,.obra-btn:focus-visible,button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid var(--grafite);outline-offset:2px}
.conf{display:flex;align-items:center;gap:14px;margin-top:10px;color:var(--cimento);font-size:14px}
.conf .barra{flex:1;max-width:520px}
.barra{display:flex;height:10px;border-radius:5px;overflow:hidden;background:var(--linha)}
.barra span{display:block;height:100%}
.b-vencido{background:var(--vermelho)}.b-30{background:var(--laranja)}.b-60{background:var(--amarelo)}.b-faltando{background:var(--azul)}.b-ok{background:var(--verde)}
.intro{color:var(--cimento);max-width:72ch;margin-bottom:14px}
.nota{display:block;color:var(--cimento);font-size:13px}
.nome{display:block;font-weight:600}
.det{color:var(--cimento);font-size:14px}
.qd{font-size:14px;white-space:nowrap}
.chip{display:inline-block;padding:1px 8px;border-radius:3px;font-size:12.5px;font-weight:600;white-space:nowrap;line-height:1.6}
.c-vencido{color:var(--t-vencido);background:var(--f-vencido)}.c-30{color:var(--t-30);background:var(--f-30)}
.c-60{color:var(--t-60);background:var(--f-60)}.c-faltando{color:var(--t-faltando);background:var(--f-faltando)}.c-ok{color:var(--t-ok);background:var(--f-ok)}
/* esta semana: quadro em linhas */
#semana{background:var(--papel);border-radius:6px;padding:4px 24px 8px;margin-top:36px}
#semana h2{margin-top:22px}
.acao{display:grid;grid-template-columns:minmax(200px,300px) 1fr;gap:8px 32px;padding:18px 0;border-top:1px solid var(--linha)}
.acao-tit .verbo{font-weight:600;margin-top:4px}
.pessoas{list-style:none;margin:0;padding:0}
.pessoas li{display:grid;grid-template-columns:112px 1fr auto;gap:2px 16px;align-items:baseline;padding:7px 0}
.pessoas li+li{border-top:1px dashed var(--linha)}
.quem .nome{display:inline;margin-right:10px}
/* obras */
.obras{list-style:none;margin:0;padding:0;background:var(--papel);border-radius:6px}
.obras li{display:grid;grid-template-columns:260px 90px 220px 1fr;gap:6px 18px;align-items:center;padding:14px 20px}
.obras li+li{border-top:1px solid var(--linha)}
.obra-btn{all:unset;cursor:pointer;font-weight:600;border-radius:2px}
.obra-btn:hover{text-decoration:underline}
/* filtros e tabela */
.filtros{display:flex;flex-wrap:wrap;align-items:flex-end;gap:10px 14px;margin:10px 0 12px}
.filtros label{display:flex;flex-direction:column;gap:3px;font-size:13px;color:var(--cimento)}
.filtros .busca{flex:1;min-width:220px}
.filtros .check{flex-direction:row;align-items:center;gap:6px;padding-bottom:8px;color:var(--grafite);font-size:14px}
select,input[type=search]{font:inherit;font-size:14px;color:var(--grafite);background:var(--papel);border:1px solid var(--linha);border-radius:4px;padding:7px 9px;min-height:38px}
input[type=checkbox]{width:18px;height:18px;accent-color:var(--azul)}
#limpar{font:inherit;font-size:14px;font-weight:600;color:var(--grafite);background:transparent;border:1px solid var(--linha);border-radius:4px;padding:7px 12px;min-height:38px;cursor:pointer}
#limpar:hover{background:var(--papel)}
.cont{margin-left:auto;padding-bottom:8px;color:var(--cimento);font-size:14px}
.tab{width:100%;border-collapse:collapse;background:var(--papel);border-radius:6px;overflow:hidden}
.tab th{font-family:var(--cond);font-weight:600;font-size:16px;text-align:left;padding:10px 12px;border-bottom:2px solid var(--grafite);position:sticky;top:0;background:var(--papel)}
.tab td{padding:9px 12px;border-top:1px solid var(--linha);vertical-align:top;overflow-wrap:anywhere}
.tab tbody tr{content-visibility:auto;contain-intrinsic-size:auto 56px}
section{scroll-margin-top:16px}
button,select,input,label{touch-action:manipulation;-webkit-tap-highlight-color:transparent}
.pular{position:absolute;left:16px;top:-60px;background:var(--grafite);color:var(--papel);padding:8px 14px;border-radius:4px;font-weight:600;z-index:2}
.pular:focus{top:12px}
.tab td.num{white-space:nowrap}
.tab tr[hidden]{display:none!important}
.vazio{background:var(--papel);border-radius:6px;padding:18px 20px;color:var(--cimento)}
#semana .vazio{padding:16px 0 20px}
.problemas{background:var(--papel);border-radius:6px;margin:0;padding:14px 20px 14px 40px}
.problemas li+li{margin-top:4px}
footer{margin-top:44px;color:var(--cimento);font-size:13px;max-width:80ch}
footer p+p{margin-top:4px}
@media (max-width:860px){
.placa{grid-template-columns:repeat(2,1fr)}.seg.s-ok{grid-column:span 2}
.acao{grid-template-columns:1fr}
.pessoas li{grid-template-columns:auto 1fr}.pessoas .qd{grid-column:2;white-space:normal}
.quem .nome{display:block}
.placa .seg{min-height:96px}
.obras li{grid-template-columns:1fr auto}.obras .barra{grid-column:1/-1}.obras .qd{grid-column:1/-1;white-space:normal}
.tab thead{display:none}.tab,.tab tbody,.tab tr,.tab td{display:block;width:100%}
.tab tr{border-top:1px solid var(--linha);padding:8px 0}.tab td{border:0;padding:3px 14px;display:grid;grid-template-columns:84px 1fr;gap:10px}
.tab td::before{content:attr(data-label);color:var(--cimento);font-size:13px}
.tab td>*{grid-column:2;justify-self:start}.tab td[data-label="Último"]{display:none}
.cont{margin-left:0;width:100%}
#semana{padding:4px 16px 8px}
.topo .data{text-align:left}}
@media print{
body{background:#fff;font-size:12px}main{padding:0;max-width:none}
.filtros,#limpar{display:none}.seg{min-height:0;padding:8px 10px}.seg b{font-size:30px}
#semana,.obras,.tab{border:1px solid #bbb}.tab th{position:static}
.placa,.barra span,.chip{-webkit-print-color-adjust:exact;print-color-adjust:exact}
section{break-inside:avoid-page}.tab tr{break-inside:avoid}}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
"""

JS = """(()=>{
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const linhas=$$('#pend tbody tr');
const f={st:$('#f-st'),obra:$('#f-obra'),emp:$('#f-emp'),busca:$('#f-busca'),ok:$('#f-ok')};
function aplicar(){
  const b=f.busca.value.trim().toLowerCase();let n=0;
  for(const tr of linhas){const d=tr.dataset;
    const vis=(!f.obra.value||d.obra===f.obra.value)&&(!f.emp.value||d.emp===f.emp.value)&&
      (f.st.value?d.status===f.st.value:(f.ok.checked||d.status!=='ok'))&&(!b||d.txt.includes(b));
    tr.hidden=!vis;if(vis)n++;}
  $('#cont').textContent=n+(n===1?' item':' itens');
  $('#vazio').hidden=n>0;
  $$('.seg').forEach(s=>s.setAttribute('aria-pressed',String(s.dataset.status===f.st.value)));
  salvarNoEndereco();
}
function irParaTabela(){$('#pendencias').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});}
$$('.seg').forEach(s=>s.addEventListener('click',()=>{
  f.st.value=f.st.value===s.dataset.status?'':s.dataset.status;aplicar();if(f.st.value)irParaTabela();}));
$$('.obra-btn').forEach(b=>b.addEventListener('click',()=>{f.obra.value=b.dataset.obra;aplicar();irParaTabela();}));
Object.values(f).forEach(e=>e.addEventListener(e.tagName==='SELECT'||e.type==='checkbox'?'change':'input',aplicar));
$('#limpar').addEventListener('click',()=>{f.st.value='';f.obra.value='';f.emp.value='';f.busca.value='';f.ok.checked=false;aplicar();});
// filtros ficam no endereço (#obra=...&situacao=...), para salvar nos favoritos uma visão por obra
function salvarNoEndereco(){
  const p=new URLSearchParams();
  if(f.st.value)p.set('situacao',f.st.value);if(f.obra.value)p.set('obra',f.obra.value);
  if(f.emp.value)p.set('empresa',f.emp.value);if(f.busca.value)p.set('busca',f.busca.value);if(f.ok.checked)p.set('em-dia','1');
  try{history.replaceState(null,'',p.toString()?'#'+p:location.pathname+location.search);}catch(e){}
}
(function lerDoEndereco(){
  const p=new URLSearchParams(location.hash.slice(1));
  f.st.value=p.get('situacao')||'';f.obra.value=p.get('obra')||'';f.emp.value=p.get('empresa')||'';
  f.busca.value=p.get('busca')||'';f.ok.checked=p.has('em-dia');
})();
aplicar();
})();
"""


def gerar_html(res, hoje, planilha, gerado_em=None):
    """planilha: Path (só o nome aparece). gerado_em: texto pronto; a versão web passa a hora local do navegador."""
    linhas, cas = res["linhas"], res["cas"]
    gerado_em = gerado_em or f"{dt.datetime.now():%d/%m/%Y às %H:%M}"
    n_obras = len({l["obra"] for l in linhas})
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vencimentos de SST, {hoje:%d/%m/%Y}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">
<meta name="theme-color" content="#E6E8E9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#15191C" media="(prefers-color-scheme: dark)">
<style>{CSS}</style></head><body><a class="pular" href="#semana">Pular para “Esta semana”</a><main>
<header class="topo"><div><h1>Vencimentos de SST</h1>
<p class="sub">{plural(res["pessoas"], "pessoa ativa ou afastada", "pessoas ativas ou afastadas")} em {plural(n_obras, "obra", "obras")}. Planilha {esc(planilha.name)}.</p></div>
<p class="data"><span>Situação em</span>{data_longa(hoje)}</p></header>
{bloco_placa(linhas)}
{bloco_semana(linhas, cas, hoje)}
{bloco_obras(linhas, hoje)}
{bloco_tabela(linhas)}
{bloco_ca(cas)}
{bloco_problemas(res["problemas"])}
<footer><p>Gerado em {gerado_em}. Documento interno com nomes de funcionários: não publique nem envie em grupo aberto.</p>
<p>Os prazos padrão foram conferidos em 26/10/2026. Na dúvida, vale o que está no PGR e no PCMSO da empresa.</p></footer>
</main><script>{JS}</script></body></html>"""
