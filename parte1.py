import csv
from collections import deque
from pathlib import Path


def buscar_rota(mapa, inicio, alvo):
    movimentos = [
        ("up", -1, 0),
        ("down", 1, 0),
        ("left", 0, -1),
        ("right", 0, 1),
    ]

    fila = deque([inicio])
    anterior = {inicio: None}

    while fila:
        atual = fila.popleft()
        if atual == alvo:
            break

        linha, coluna = atual
        for direcao, dl, dc in movimentos:
            l, c = linha + dl, coluna + dc
            if not (0 <= l < len(mapa) and 0 <= c < len(mapa[0])):
                continue

            vizinha = (l, c)
            if mapa[l][c] == "b" or vizinha in anterior:
                continue

            anterior[vizinha] = (atual, direcao)
            fila.append(vizinha)

    if alvo not in anterior:
        return None

    rota = []
    atual = alvo
    while atual != inicio:
        atual, direcao = anterior[atual]
        rota.append(direcao)

    rota.reverse()
    return rota


if __name__ == "__main__":
    arquivo = Path(__file__).parent / "src" / "cg" / "maps" / "test.csv"
    with arquivo.open(newline="") as f:
        mapa = list(csv.reader(f))

    posicoes = {}
    for linha, valores in enumerate(mapa):
        for coluna, celula in enumerate(valores):
            if celula in ("r", "t"):
                posicoes[celula] = (linha, coluna)

    rota = buscar_rota(mapa, posicoes["r"], posicoes["t"])
    if rota is None:
        print("O alvo está fora de alcance.")
    else:
        print("Início:", posicoes["r"], "| Alvo:", posicoes["t"])
        print("Quantidade de movimentos:", len(rota))
        print("Rota:", rota)