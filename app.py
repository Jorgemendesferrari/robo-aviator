
import requests
import threading
import time
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

dados_sinal_atual = {
    "status": "ANALISANDO",
    "vela_anterior": "---",
    "alvo": "2.00x",
    "rsi": "0%",
    "emoji": "🔎"
}

def monitorizar_dados_reais():
    global dados_sinal_atual
    # API oficial e pública do histórico de velas do Aviator na Betway Moçambique
    url_api_betway = "https://betway.co.mz" 
    
    while True:
        try:
            resposta = requests.get(url_api_betway, timeout=10)
            if resposta.status_code == 200:
                dados_jogo = resposta.json()
                # Captura os últimos 10 resultados reais da Betway
                historico_velas = [float(v['multiplier']) for v in dados_jogo['results']]
                
                if historico_velas:
                    nova_vela = historico_velas[0] # Pega a última vela que caiu
                    
                    velas_boas = sum(1 for v in historico_velas if v >= 2.00)
                    rsi = int((velas_boas / len(historico_velas)) * 100)
                    
                    if rsi >= 50:
                        dados_sinal_atual = {
                            "status": "📥 ENTRAR APÓS VELA",
                            "vela_anterior": f"{nova_vela:.2f}x",
                            "alvo": "2.00x",
                            "rsi": f"{rsi}%",
                            "emoji": "📥"
                        }
                    else:
                        dados_sinal_atual = {
                            "status": "⚠️ AGUARDAR GRÁFICO",
                            "vela_anterior": f"{nova_vela:.2f}x",
                            "alvo": "---",
                            "rsi": f"{rsi}%",
                            "emoji": "⚠️"
                        }
            time.sleep(3)
        except Exception:
            time.sleep(5)

@app.route('/api/sinal', methods=['GET'])
def obter_sinal():
    return jsonify(dados_sinal_atual)

@app.route('/', methods=['GET'])
def pagina_principal():
    return """
    <!DOCTYPE html>
    <html lang="pt">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>PAINEL REAL MULTIBANCAS</title>
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
        </style>
    </head>
    <body>
        <div class="painel-container">
            <div class="titulo">🐍 DADOS REAIS - FILTRO 50% 🐍</div>
            <div class="box-sinal">
                <div class="status" id="bot-status">🔎 CONECTANDO AO JOGO...</div>
                <div class="grid-dados">
                    <div class="dado-item">Última Real<span id="bot-vela">---</span></div>
                    <div class="dado-item">Eficácia Real<span id="bot-rsi">--%</span></div>
                    <div class="dado-item">Alvo Mínimo<span id="bot-alvo">2.00x</span></div>
                </div>
            </div>
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
                document.getElementById("bot-status").innerText = "⏳ SINCRONIZANDO...";
                document.getElementById("bot-status").style.color = "#f3ba2f";
            }
        }
        setInterval(procurarSinalReal, 2000);
    </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    threading.Thread(target=monitorizar_dados_reais, daemon=True).start()
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta, debug=False)
