from flask import Flask, request, render_template
import pandas as pd
from datetime import datetime

app = Flask(__name__)


def formatar_brl(valor: float) -> str:
    """Formata número float no padrão brasileiro: R$ 0.000,00"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


@app.route("/", methods=["GET", "POST"])
def index():
    erro = None
    total_formatado = None
    data_hoje = datetime.now().strftime("%d/%m/%Y")

    if request.method == "POST":
        if "arquivo" not in request.files:
            erro = "Nenhum arquivo enviado."
        else:
            file = request.files["arquivo"]

            if file.filename == "":
                erro = "Nenhum arquivo selecionado."
            else:
                try:
                    # Lê o CSV enviado (em memória)
                    df = pd.read_csv(file)

                    # Normaliza nomes das colunas para minúsculo
                    colunas_lower = {c.lower(): c for c in df.columns}

                    if "saldo" not in colunas_lower:
                        erro = "A coluna 'Saldo' não foi encontrada no CSV. Verifique o cabeçalho."
                    else:
                        col_saldo = colunas_lower["saldo"]

                        # Converte para número (se já estiver como 0.26, 10.50 etc)
                        df[col_saldo] = df[col_saldo].astype(float)

                        # Soma
                        total = df[col_saldo].sum()

                        # Formata em R$
                        total_formatado = formatar_brl(total)

                except Exception as e:
                    erro = f"Erro ao processar o arquivo: {e}"

    return render_template(
        "index.html",
        erro=erro,
        total_formatado=total_formatado,
        data_hoje=data_hoje,
    )


if __name__ == "__main__":
    # Para rodar localmente
    app.run(debug=True)
