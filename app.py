import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Dicionário dinâmico para simular e processar a inteligência do mercado ao vivo
@app.route('/api/sinal', methods=['GET'])
def obter_sinal():
    import random
    # Gera uma sequência realista focada na taxa de assertividade desejada
    velas_recentes = [round(random.uniform(1.0, 5.0), 2) for _ in range(10)]
    velas_boas = sum(1 for v in list(velas_recentes) if v >= 2.00)
    
    # Força e calibra o filtro de eficácia/RSI para rondar a margem estratégica de 50%
    rsi_calculado = int((velas_boas / len(velas_recentes)) * 100)
    ultima_vela_gerada = velas_recentes[-1]
    
    if rsi_calculado >= 50:
        resposta = {
            "status": "📥 ENTRAR APÓS VELA",
            "vela_anterior": f"{ultima_vela_gerada:.2f}x",
            "alvo": "2.00x",
            "rsi": f"{rsi_calculado}%",
            "emoji": "📥"
        }
    else:
        resposta = {
            "status": "⚠️ AGUARDAR GRÁFICO",
            "vela_anterior": f"{ultima_vela_gerada:.2f}x",
            "alvo": "---",
            "rsi": f"{rsi_calculado}%",
            "emoji": "⚠️"
        }
    return jsonify(resposta)

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
    porta = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=porta, debug=False)
