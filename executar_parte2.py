import rclpy
import csv
from pathlib import Path
from cg_interfaces.msg import RobotSensors
from cg_interfaces.srv import MoveCmd
from rclpy.qos import qos_profile_sensor_data
from rclpy.wait_for_message import wait_for_message

from executar_parte1 import chamar_servico
from parte2 import DESLOCAMENTOS, registrar_leitura


def ler_sensor(no):
    recebeu, mensagem = wait_for_message(
        RobotSensors,
        no,
        "/culling_games/robot_sensors",
        qos_profile=qos_profile_sensor_data,
        time_to_wait=5,
    )
    if not recebeu:
        raise RuntimeError("O simulador não enviou uma leitura em 5 segundos.")

    return {direcao: getattr(mensagem, direcao) for direcao in DESLOCAMENTOS}

def salvar_mapa(mapa):
    linhas = [linha for linha, coluna in mapa]
    colunas = [coluna for linha, coluna in mapa]
    arquivo = Path(__file__).with_name("mapa_descoberto.csv")

    with arquivo.open("w", newline="") as f:
        escritor = csv.writer(f)
        for linha in range(min(linhas), max(linhas) + 1):
            valores = []
            for coluna in range(min(colunas), max(colunas) + 1):
                posicao = (linha, coluna)
                if posicao == (0, 0):
                    valores.append("r")
                else:
                    valores.append(mapa.get(posicao, "?"))
            escritor.writerow(valores)

    print("Mapa descoberto salvo em:", arquivo.name)


def executar(no):
    mover = no.create_client(MoveCmd, "/move_command")
    if not mover.wait_for_service(timeout_sec=5):
        raise RuntimeError("O serviço /move_command está indisponível.")

    direcoes = ("up", "down", "left", "right")
    oposta = {"up": "down", "down": "up", "left": "right", "right": "left"}

    mapa = {}
    visitadas = set()
    pilha = []
    posicao = (0, 0)
    passos = 0

    while True:
        # Uma leitura por casa já basta: as paredes do labirinto são fixas.
        if posicao not in visitadas:
            registrar_leitura(mapa, visitadas, posicao, ler_sensor(no))

        # Procurar uma vizinha livre em que o robô ainda não pisou.
        avancar = None
        for direcao in direcoes:
            dl, dc = DESLOCAMENTOS[direcao]
            vizinha = (posicao[0] + dl, posicao[1] + dc)
            if mapa.get(vizinha) == "f" and vizinha not in visitadas:
                avancar = direcao
                break

        if avancar is not None:
            movimento = avancar
        elif pilha:
            movimento = oposta[pilha[-1]]
        else:
            break  # Voltamos à largada e esgotamos os caminhos disponíveis.

        pedido = MoveCmd.Request()
        pedido.direction = movimento
        resposta = chamar_servico(no, mover, pedido)
        if not resposta.success:
            raise RuntimeError(f"Movimento {movimento} recusado em {posicao}.")

        if avancar is not None:
            pilha.append(movimento)
        else:
            pilha.pop()

        dl, dc = DESLOCAMENTOS[movimento]
        posicao = (posicao[0] + dl, posicao[1] + dc)
        passos += 1

        if passos % 100 == 0:
            print(f"{passos} movimentos | {len(visitadas)} casas visitadas")

    alvo = next((casa for casa, valor in mapa.items() if valor == "t"), None)
    print("Exploração concluída.")
    print("Posição final, relativa à largada:", posicao)
    print("Alvo observado, relativo à largada:", alvo)
    print("Células conhecidas:", len(mapa))
    print("Casas visitadas:", len(visitadas))
    print("Movimentos de exploração:", passos)
    salvar_mapa(mapa)
    return mapa


if __name__ == "__main__":
    rclpy.init()
    no = rclpy.create_node("explorador_parte2")
    try:
        executar(no)
    finally:
        no.destroy_node()
        rclpy.shutdown()