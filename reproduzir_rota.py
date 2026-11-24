import csv
from pathlib import Path

import rclpy
from cg_interfaces.srv import MoveCmd

from executar_parte1 import chamar_servico
from parte1 import buscar_rota


def reproduzir(no):
    arquivo = Path(__file__).with_name("mapa_descoberto.csv")
    with arquivo.open(newline="") as f:
        mapa = list(csv.reader(f))

    posicoes = {}
    for linha, valores in enumerate(mapa):
        for coluna, valor in enumerate(valores):
            if valor in ("r", "t"):
                posicoes[valor] = (linha, coluna)
            elif valor == "?":
                mapa[linha][coluna] = "b"  # Planejar só por casas conhecidas.

    if "r" not in posicoes or "t" not in posicoes:
        raise RuntimeError("O mapa descoberto precisa conter a largada e o alvo.")

    rota = buscar_rota(mapa, posicoes["r"], posicoes["t"])
    if rota is None:
        raise RuntimeError("O mapa descoberto não contém um caminho até o alvo.")

    print("Rota:", rota)
    print("Movimentos planejados:", len(rota))

    mover = no.create_client(MoveCmd, "/move_command")
    if not mover.wait_for_service(timeout_sec=5):
        raise RuntimeError("O serviço /move_command está indisponível.")

    for passo, direcao in enumerate(rota, start=1):
        pedido = MoveCmd.Request()
        pedido.direction = direcao
        resposta = chamar_servico(no, mover, pedido)
        if not resposta.success:
            raise RuntimeError(f"Movimento recusado no passo {passo}: {direcao}")

        print(f"{passo:02d} | {direcao} | {tuple(resposta.robot_pos)}")

    if rota and tuple(resposta.robot_pos) == tuple(resposta.target_pos):
        print(f"Alvo confirmado pelo simulador em {len(rota)} movimentos.")
    else:
        raise RuntimeError("A execução terminou sem confirmar a chegada ao alvo.")


if __name__ == "__main__":
    rclpy.init()
    no = rclpy.create_node("reproduzir_rota")
    try:
        reproduzir(no)
    finally:
        no.destroy_node()
        rclpy.shutdown()