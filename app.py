from flask import Flask, request, render_template
from datetime import datetime
import csv
import io

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
                    # Lê o arquivo enviado como texto
                    stream = io.TextIOWrapper(file.stream, encoding="utf-8", errors="ignore")

                    # Usa DictReader para ler por nome de coluna
                    reader = csv.DictReader(stream)

                    # Normaliza nomes de coluna para minúsculo
                    fieldnames_lower = {name.lower(): name for name in reader.fieldnames}

                    if "saldo" not in fieldnames_lower:
                        erro = "A coluna 'Saldo' não foi encontrada no CSV. Verifique o cabeçalho."
                    else:
                        col_saldo = fieldnames_lower["saldo"]

                        total = 0.0
                        for row in reader:
                            valor_str = row.get(col_saldo, "").strip()

                            if not valor_str:
                                continue

                            # Aceita "1234.56" ou "1234,56"
                            valor_str = valor_str.replace(".", "").replace(",", ".") if "," in valor_str else valor_str
                            try:
                                valor = float(valor_str)
                                total += valor
                            except ValueError:
                                # ignora linhas com valores inválidos
                                continue

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
    app.run(host="0.0.0.0", port=5000)
