DESLOCAMENTOS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
    "up_left": (-1, -1),
    "up_right": (-1, 1),
    "down_left": (1, -1),
    "down_right": (1, 1),
}


def registrar_leitura(mapa, visitadas, posicao, leitura):
    linha, coluna = posicao
    visitadas.add(posicao)
    mapa[posicao] = "f"

    for direcao, (dl, dc) in DESLOCAMENTOS.items():
        vizinha = (linha + dl, coluna + dc)
        mapa[vizinha] = leitura[direcao]




if __name__ == "__main__":
    mapa = {}
    visitadas = set()

    na_largada = {
        "up": "b", "down": "f", "left": "b", "right": "f",
        "up_left": "b", "up_right": "b", "down_left": "b", "down_right": "f",
    }
    depois_de_descer = {
        "up": "f", "down": "f", "left": "b", "right": "f",
        "up_left": "b", "up_right": "f", "down_left": "b", "down_right": "f",
    }

    registrar_leitura(mapa, visitadas, (0, 0), na_largada)
    registrar_leitura(mapa, visitadas, (1, 0), depois_de_descer)

    print("Células conhecidas:", len(mapa))
    print("Posições visitadas:", sorted(visitadas))