import time, os, threading, requests
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
janela_macro = []
dados_sinal_atual = {"status": "ANALISANDO", "vela_anterior": "0.00x", "previsao_topo": "---", "protecao": "---", "alvo_principal": "---", "rsi": "0%", "estado_mercado": "ESTÁVEL", "emoji": "🔎"}

# O SEU INDEX.HTML FICOU EMBUTIDO AQUI DENTRO (RESOLVE O PROBLEMA DO SAMSUNG NOTES)
PAGINA_HTML = """
<!DOCTYPE html><html lang="pt"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no"><title>ROBÔ MULTIBANCAS MOBILE</title><style>*{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}body,html{width:100%;height:100%;background-color:#0b0e11;overflow:hidden;display:flex;flex-direction:column}.seletor-plataformas{width:100%;background-color:#161a1e;display:flex;justify-content:space-around;padding:12px 6px;border-bottom:1px solid #2b3139}.btn-plataforma{background-color:#2b3139;color:#fff;border:1px solid #474f5a;padding:10px;font-size:11px;font-weight:700;border-radius:6px;cursor:pointer;flex:1;margin:0 4px;text-align:center}.btn-plataforma.active{background-color:#f3ba2f;color:#000;border-color:#f3ba2f}.painel-bot{width:100%;height:42%;background:linear-gradient(145deg,#161a1e,#0e1114);border-bottom:3px solid #f3ba2f;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:10px;color:#fff}.titulo{font-size:12px;color:#f3ba2f;font-weight:700;margin-bottom:8px;text-transform:uppercase;letter-spacing:1px}.box-sinal{background:rgba(0,0,0,.5);border:1px solid rgba(243,186,47,.3);padding:12px;border-radius:8px;width:95%;max-width:360px}.status{font-size:16px;font-weight:800;color:#00ff88;text-align:center;margin-bottom:8px}.grelha-dados{display:grid;grid-template-columns:repeat(2,1fr);gap:6px;font-size:11px;color:#a0a5ad;background:rgba(255,255,255,.05);padding:8px;border-radius:4px}.grelha-dados p{padding:2px 0}.grelha-dados span{font-weight:700;color:#fff}.area-jogo{width:100%;height:58%;border:none;background-color:#000}</style></head><body><div class="seletor-plataformas"><button class="btn-plataforma active" onclick="mudarPlataforma('betway','https://betway.co.mz')">BETWAY</button><button class="btn-plataforma" onclick="mudarPlataforma('elephant','https://elephantbet.co.mz')">ELEPHANT BET</button><button class="btn-plataforma" onclick="mudarPlataforma('888bet','https://888bet.co.mz')">888BET</button></div><div class="painel-bot"><div class="titulo">🐍 ROBÔ NUVEM - ADAPTATIVO 🐍</div><div class="box-sinal"><div class="status" id="bot-status">🔎 CONECTANDO À API DO SERVIDOR...</div><div class="grelha-dados"><p>Última: <span id="bot-vela">---</span></p><p>RSI: <span id="bot-rsi">--%</span></p><p>🔮 Padrão: <span id="bot-topo" style="color:#9b5de5">---</span></p><p>🛡️ 1ª Prot: <span id="bot-protecao" style="color:#f3ba2f Meso">---</span></p><p>🎯 2ª Alvo: <span id="bot-alvo" style="color:#00ff88">---</span></p></div></div></div><iframe id="iframe-jogo" class="area-jogo" src="https://betway.co.mz"></iframe><script>const URL_SERVIDOR=window.location.origin+"/api/sinal";let plataformaAtual="betway";function mudarPlataforma(e,a){plataformaAtual=e,document.getElementById("iframe-jogo").src=a;const t=document.querySelectorAll(".btn-plataforma");t.forEach(e=>e.classList.remove("active")),event.target.classList.add("active")}async function procurarSinal(){try{const e=await fetch(URL_SERVIDOR);if(!e.ok)throw new Error;const a=await e.json();document.getElementById("bot-status").innerText=a.emoji+" "+a.status,document.getElementById("bot-vela").innerText=a.vela_anterior,document.getElementById("bot-rsi").innerText=a.rsi,document.getElementById("bot-topo").innerText=a.estado_mercado,document.getElementById("bot-protecao").innerText=a.protecao,document.getElementById("bot-alvo").innerText=a.alvo_principal,a.status.includes("ENTRAR")?document.getElementById("bot-status").style.color="#00ff88":document.getElementById("bot-status").style.color="#ff4a4a"}catch(e){document.getElementById("bot-status").innerText="⏳ CONECTANDO À NUVEM...",document.getElementById("bot-status").style.color="#f3ba2f"}}setInterval(procurarSinal,2000);</script></body></html>
"""

@app.route('/')
def home():
    return render_template_string(PAGINA_HTML)

@app.route('/api/sinal')
def obter_sinal():
    r = jsonify(dados_sinal_atual); r.headers.add("Access-Control-Allow-Origin", "*"); return r

def calcular_alvos_adaptativos(historico):
    verdes = [v for v in historico if v >= 2.00]
    media_base = sum(verdes[-4:]) / min(len(verdes), 4) if verdes else 2.50
    topo_previsto = max(2.00, min(media_base, 12.00))
    sequencia = ['V' if x >= 2.00 else 'A' for x in historico[-4:]] if len(historico) >= 4 else []
    ultimas_3 = historico[-3:] if len(historico) >= 3 else []
    if sequencia == ['V', 'A', 'V', 'A'] or sequencia == ['A', 'V', 'A', 'V']:
        return f"{topo_previsto:.2f}x", "1.50x", "2.00x", "PADRÃO XADREZ ATIVO", "🔀"
    elif any(v >= 10.00 for v in ultimas_3):
        return f"{topo_previsto:.2f}x", "1.30x", "1.65x", "PÓS VELA ROSA", "🌸"
    elif all(v < 1.50 for v in ultimas_3) and len(ultimas_3) == 3:
        return f"{topo_previsto:.2f}x", "1.40x", "1.90x", "QUEBRA DE CICLO AZUL", "⚡"
    else:
        return f"{topo_previsto:.2f}x", f"{topo_previsto*0.60:.2f}x", f"{topo_previsto*0.90:.2f}x", "ONDA DE ALTA", "🐍"

def API_auto_recuperacao():
    global janela_macro, dados_sinal_atual
    endpoints = ["https://elephantbet.co.mz", "https://betway.co.mz"]
    while True:
        dados = None
        for url in endpoints:
            try:
                res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla"})
                if res.status_code == 200:
                    dados = [float(i['multiplier']) for i in res.json()['results']]; break
            except: continue
        if dados:
            janela_macro = dados[-50:]
            total = len(janela_macro)
            boas = sum(1 for v in janela_macro if v >= 2.00)
            rsi = (sum(1 for v in janela_macro[-min(total,10):] if v >= 2.00) / min(total,10)) * 100 if total > 0 else 0
            assertividade = (boas / total) * 100 if total > 0 else 0
            topo, prot, alvo, tendencia, emoji = calcular_alvos_adaptativos(janela_macro)
            if assertividade >= 50.0 or rsi >= 50.0:
                status_texto = "📥 ENTRAR APÓS VELA"
            else:
                status_texto = "📥 ENTRAR (MERCADO CONSERVADOR)"
                prot, alvo, tendencia, emoji = "1.30x", "1.60x", "MERCADO RETRAÍDO", "⚠️"
            dados_sinal_atual = {"status": status_texto, "vela_anterior": f"{janela_macro[-1]:.2f}x", "previsao_topo": topo, "protecao": prot, "alvo_principal": alvo, "rsi": f"{rsi:.0f}%", "estado_mercado": tendencia, "emoji": emoji}
        time.sleep(3)

if __name__ == "__main__":
    threading.Thread(target=API_auto_recuperacao, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
