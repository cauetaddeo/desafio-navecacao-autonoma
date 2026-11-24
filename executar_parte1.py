import rclpy
from cg_interfaces.srv import GetMap, MoveCmd

from parte1 import buscar_rota


def chamar_servico(no, cliente, pedido):
    futuro = cliente.call_async(pedido)
    rclpy.spin_until_future_complete(no, futuro, timeout_sec=5.0)
    if not futuro.done():
        raise RuntimeError(f"Sem resposta de {cliente.srv_name}")
    return futuro.result()


def executar(no):
    obter_mapa = no.create_client(GetMap, "/get_map")
    mover = no.create_client(MoveCmd, "/move_command")

    for cliente in (obter_mapa, mover):
        if not cliente.wait_for_service(timeout_sec=5.0):
            raise RuntimeError(f"Serviço indisponível: {cliente.srv_name}")

    # 1. Reconstruir as linhas do mapa que o ROS enviou em uma lista única.
    resposta = chamar_servico(no, obter_mapa, GetMap.Request())
    linhas, colunas = resposta.occupancy_grid_shape
    celulas = list(resposta.occupancy_grid_flattened)
    mapa = [
        celulas[linha * colunas : (linha + 1) * colunas]
        for linha in range(linhas)
    ]

    # 2. Encontrar o robô e o alvo no mapa atual e calcular a rota.
    inicio = divmod(celulas.index("r"), colunas)
    alvo = divmod(celulas.index("t"), colunas)
    rota = buscar_rota(mapa, inicio, alvo)

    if rota is None:
        print(f"Não há caminho de {inicio} até {alvo}.")
        return

    print(f"Início: {inicio} | Alvo: {alvo} | Rota: {len(rota)} passos")

    # 3. Enviar um movimento e aguardar a confirmação antes do próximo.
    posicao = inicio
    for passo, direcao in enumerate(rota, start=1):
        pedido = MoveCmd.Request()
        pedido.direction = direcao
        resultado = chamar_servico(no, mover, pedido)
        posicao = tuple(resultado.robot_pos)

        if not resultado.success:
            print(f"Movimento {direcao} recusado no passo {passo}. Posição: {posicao}")
            return

        print(f"{passo:02d} | {direcao} | {posicao}")

    if posicao == alvo:
        print(f"Alvo alcançado em {len(rota)} movimentos.")
    else:
        print(f"A rota terminou em {posicao}. O alvo era {alvo}.")


if __name__ == "__main__":
    rclpy.init()
    no = rclpy.create_node("navegacao_parte1")
    try:
        executar(no)
    finally:
        no.destroy_node()
        rclpy.shutdown()