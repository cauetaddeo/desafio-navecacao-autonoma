# Desafio de navegação autônoma

O projeto resolve um desafio de navegação no simulador Culling Games, usando Python e ROS 2 Jazzy. Na primeira parte, o robô recebe o mapa completo e calcula o menor caminho até o alvo. Na segunda, ele explora o ambiente com sensores locais, constrói seu próprio mapa e usa esse mapa para reproduzir a rota da primeira parte.

## 1. Navegação com o mapa completo

### 1.1 Leitura do mapa

O programa `executar_parte1.py` consulta o serviço `/get_map`. O simulador devolve as dimensões do labirinto e uma lista com suas células. O programa organiza essa lista em linhas e colunas e identifica o robô (`r`), o alvo (`t`), as paredes (`b`) e os espaços livres (`f`).

### 1.2 Cálculo da menor rota

A função `buscar_rota`, em `parte1.py`, usa busca em largura (BFS). Cada célula transitável é um vértice, e cada movimento para cima, para baixo, para a esquerda ou para a direita custa um passo.

A BFS examina primeiro as células a um passo da largada, depois as que estão a dois passos, e assim por diante. Por isso, a primeira vez que alcança o alvo, já encontrou uma rota mínima. A função registra de qual célula veio e qual movimento fez para reconstruir a sequência de comandos.

### 1.3 Execução no simulador

O programa envia cada comando pelo serviço `/move_command` e aguarda a confirmação antes de enviar o próximo. No `test.csv`, o robô saiu de `(1, 1)` e chegou ao alvo em `(13, 14)` com **25 movimentos: 12 para baixo e 13 para a direita**. As coordenadas seguem o formato `(linha, coluna)`, com contagem a partir de zero.

## 2. Exploração e construção do mapa

### 2.1 Leitura dos sensores

O explorador começa com um mapa vazio e adota a largada como origem `(0, 0)`. A cada nova posição, lê o tópico `/culling_games/robot_sensors`, que informa o conteúdo das oito células vizinhas, incluindo as diagonais. A função `registrar_leitura`, em `parte2.py`, converte essas direções em coordenadas e atualiza o mapa.

O programa também guarda as posições visitadas pelo robô. Uma casa livre na diagonal, por exemplo, já pode estar registrada no mapa mesmo que o robô ainda não tenha pisado nela.

### 2.2 Exploração com DFS e retorno à largada

O programa `executar_parte2.py` usa busca em profundidade (DFS). O robô avança para uma vizinha livre ainda não visitada e guarda o movimento em uma pilha. Quando esgota as opções, executa o movimento inverso para voltar à célula anterior. Esse retorno é o *backtracking*.

O robô registra o alvo ao identificá-lo pelos sensores e deixa a entrada nessa célula para a reprodução da rota, pois pisar nela encerra a partida. Ao terminar a exploração, volta à largada e salva o mapa em `mapa_descoberto.csv`.

### 2.3 Reprodução da rota e comparação

O programa `reproduzir_rota.py` lê o CSV descoberto, aplica a mesma função `buscar_rota` da parte 1 e executa os movimentos no simulador. A comparação foi feita no mesmo `test.csv`, partindo da mesma posição.

| Etapa | Resultado observado |
|---|---|
| Parte 1 — BFS sobre o mapa fornecido | 12 movimentos para baixo e 13 para a direita. Chegada em `(13, 14)` no passo 25. |
| Parte 2 — exploração por sensores | 841 células conhecidas, 728 casas visitadas e 1.454 movimentos de exploração. Retorno à largada. |
| Parte 2 — BFS sobre o mapa descoberto | A mesma sequência de 12 movimentos para baixo e 13 para a direita. Chegada em `(13, 14)` no passo 25. |

Os 1.454 movimentos incluem as idas e voltas necessárias para explorar o ambiente. Depois que o mapa foi salvo, o robô conseguiu reproduzir a rota original de **25 movimentos** usando apenas o conhecimento adquirido na exploração.

## 3. Como reproduzir o teste

### 3.1 Preparar o ambiente e abrir o simulador

Com ROS 2 Jazzy e `colcon` instalados no Ubuntu, execute na raiz do repositório:

```bash
sudo apt install python3-pygame
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
ros2 run cg maze --map test.csv
```

Mantenha esse terminal aberto durante o teste.

### 3.2 Executar a parte 1

Abra um segundo terminal na raiz do repositório e execute:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
python3 parte1.py
python3 executar_parte1.py
```

O primeiro comando Python imprime a rota de referência do `test.csv`. O segundo consulta o mapa do simulador e movimenta o robô até o alvo.

### 3.3 Executar a parte 2

No segundo terminal, reinicie o mesmo mapa:

```bash
ros2 service call /reset cg_interfaces/srv/Reset "{is_random: false}"
```

Quando o robô voltar à largada, inicie a exploração:

```bash
python3 executar_parte2.py
```

Aguarde a mensagem `Mapa descoberto salvo em: mapa_descoberto.csv`. A DFS termina com o robô na largada. A partir dessa posição, execute:

```bash
python3 reproduzir_rota.py
```

Compare a linha `Rota:` com a impressa por `parte1.py` na etapa 3.2. Neste teste, as sequências coincidem e o último movimento exibido é `25 | right | (13, 14)`.

### 3.4 Teste da parte 1 em um labirinto com obstáculos

O mapa `1.csv` contém paredes internas que obrigam o robô a fazer desvios. O objetivo deste teste foi verificar se a mesma BFS usada no `test.csv` conseguia calcular e executar a menor rota em outro labirinto, sem alterar o algoritmo.

**Como executar**

Com o projeto já compilado, encerre o simulador anterior caso ele esteja aberto. Na raiz do repositório, abra o `1.csv` no primeiro terminal:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run cg maze --map 1.csv
```

Mantenha o simulador aberto. Em um segundo terminal, também na raiz do repositório, execute:

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
python3 executar_parte1.py
```

O script consulta o mapa ativo pelo serviço `/get_map`, calcula a rota com BFS e envia os movimentos ao robô pelo serviço `/move_command`.

**Resultado observado**

O robô partiu de `(1, 1)`, contornou as paredes e alcançou o alvo em `(14, 14)` após 102 movimentos. O terminal registrou o último passo como `102 | left | (14, 14)`, e o simulador exibiu a tela de vitória. A mesma implementação encontrou uma rota mínima de 25 movimentos no `test.csv` e de 102 movimentos no `1.csv`.

Simulador utilizado: [Culling Games](https://github.com/rmnicola/culling_games).