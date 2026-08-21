import os
import time
import threading
from flask import Flask, jsonify
from flask_cors import CORS
from playwright.sync_api import sync_playwright

app = Flask(__name__)
CORS(app)

janela_macro = []
dados_sinal_atual = {
    "status": "ANALISANDO",
    "vela_anterior": "---",
    "alvo": "2.00x",
    "rsi": "0%",
    "estado_mercado": "ESTÁVEL",
    "emoji": "🔎"
}

def processar_dados_banca(nova_vela):
    global janela_macro, dados_sinal_atual
    janela_macro.append(nova_vela)
    if len(janela_macro) > 50:
        janela_macro.pop(0)

    boas_50 = sum(1 for v in janela_macro if v >= 2.00)
    total_rsi = min(len(janela_macro), 10)
    rsi = (sum(1 for v in janela_macro[-total_rsi:] if v >= 2.00) / total_rsi) * 100 if total_rsi > 0 else 0

    if rsi >= 50 and len(janela_macro) >= 5:
        dados_sinal_atual = {
            "status": "📥 ENTRAR APÓS VELA",
            "vela_anterior": f"{nova_vela:.2f}x",
            "alvo": "2.00x",
            "rsi": f"{rsi:.0f}%",
            "emoji": "📥"
        }
    else:
        dados_sinal_atual = {
            "status": "⚠️ AGUARDAR GRÁFICO",
            "vela_anterior": f"{nova_vela:.2f}x",
            "alvo": "---",
            "rsi": f"{rsi:.0f}%",
            "emoji": "⚠️"
        }

def monitorizar_aviator():
    while True:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
                pagina = browser.new_page()
                pagina.goto("https://elephantbet.co.mz", timeout=60000)
                time.sleep(5)
                ultima_vela = None
                while True:
                    seletores = [".bubble-multiplier", "app-stats-item", ".stats-item", ".history-item"]
                    elemento_vela = None
                    for seletor in seletores:
                        if pagina.locator(seletor).first.is_visible():
                            elemento_vela = pagina.locator(seletor).first
                            break
                    if elemento_vela:
                        texto_cru = elemento_vela.text_content().strip()
                        vela_real = float(texto_cru.replace("x", "").replace(",", ".").strip())
                        if vela_real != ultima_vela:
                            ultima_vela = vela_real
                            processar_dados_banca(vela_real)
                    time.sleep(2)
        except Exception:
            time.sleep(5)

@app.route('/api/sinal', methods=['GET'])
def obter_sinal():
    return jsonify(dados_sinal_atual)

# ESTA PARTE É O SEU NOVO PAINEL SEM IFRAME PARA O TELEMÓVEL
@app.route('/', methods=['GET'])
def pagina_principal():
    return """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>PAINEL ROBÔ MULTIBANCAS</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: sans-serif; }
            body { background-color: #0b0e11; color: white; padding: 15px; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }
            .painel-container { width: 100%; max-width: 400px; background: #161a1e; border: 2px solid #f3ba2f; border-radius: 12px; padding: 15px; text-align: center; }
            .titulo { font-size: 14px; color: #f3ba2f; font-weight: bold; margin-bottom: 12px; }
            .box-sinal { background: rgba(0, 0, 0, 0.5); border: 1px solid rgba(243, 186, 47, 0.2); padding: 15px; border-radius: 8px; margin-bottom: 15px; }
            .status { font-size: 18px; font-weight: 800; color: #f3ba2f; margin-bottom: 10px; }
            .grid-dados { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px; }
            .dado-item { display: flex; flex-direction: column; font-size: 11px; color: #a0a5ad; }
            .dado-item span { font-size: 14px; font-weight: bold; color: #ffffff; margin-top: 2px; }
            .aviso-mobile { font-size: 11px; color: #8a919e; margin-top: 5px; }
        </style>
    </head>
    <body>
        <div class="painel-container">
            <div class="titulo">🐍 ROBÔ MULTIBANCAS V2 🐍</div>
            <div class="box-sinal">
                <div class="status" id="bot-status">🔎 CONECTANDO AO SERVIDOR...</div>
                <div class="grid-dados">
                    <div class="dado-item">Última Vela<span id="bot-vela">---</span></div>
                    <div class="dado-item">Filtro RSI<span id="bot-rsi">--%</span></div>
                    <div class="dado-item">Alvo Mínimo<span id="bot-alvo">2.00x</span></div>
                </div>
            </div>
            <p class="aviso-mobile">Use o modo <b>Janela Pop-up</b> do seu Samsung para deixar este painel flutuando por cima do jogo original!</p>
        </div>
    <script>
        async function procurarSinalReal() {
            try {
                const resposta = await fetch('/api/sinal');
                const dados = await resposta.json();
                document.getElementById("bot-status").innerText = dados.emoji + " " + dados.status;
                document.getElementById("bot-vela").innerText = dados.vela_anterior;
                document.getElementById("bot-alvo").innerText = dados.alvo;
                document.getElementById("bot-rsi").innerText = dados.rsi;
                if (dados.status.includes("ENTRAR")) {
                    document.getElementById("bot-status").style.color = "#00ff88";
                } else {
                    document.getElementById("bot-status").style.color = "#ff4a4a";
                }
            } catch (erro) {
                document.getElementById("bot-status").innerText = "⏳ AGUARDANDO SINAL...";
                document.getElementById("bot-status").style.color = "#f3ba2f";
            }
        }
        setInterval(procurarSinalReal, 3000);
    </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    threading.Thread(target=monitorizar_aviator, daemon=True).start()
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta, debug=False)
