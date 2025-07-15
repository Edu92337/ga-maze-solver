import pygame, random, copy

HEIGHT, WIDTH = 400, 400
CELL_SIZE = 10
GRID_HEIGHT, GRID_WIDTH = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE
POPULATION = 300

def count_neigh(mapa, i, j, altura, largura):
    total = 0
    for di in [-1, 0, 1]:
        for dj in [-1, 0, 1]:
            if di == 0 and dj == 0:
                continue
            ni, nj = i + di, j + dj
            if 0 <= ni < altura and 0 <= nj < largura:
                total += mapa[ni][nj]
            else:
                total += 1
    return total

def dentro_dos_limites(i, j):
    return 0 <= i < GRID_HEIGHT and 0 <= j < GRID_WIDTH

class Maze():
    def __init__(self, prob_obstaculo=0.8):
        while True:
            mapa = []
            self.vazios = []
            for i in range(GRID_HEIGHT):
                linha = []
                for j in range(GRID_WIDTH):
                    if random.random() < prob_obstaculo:
                        linha.append(1)
                    else:
                        linha.append(0)
                mapa.append(linha)

            novo_mapa = copy.deepcopy(mapa)
            for i in range(GRID_HEIGHT):
                for j in range(GRID_WIDTH):
                    if count_neigh(mapa, i, j, GRID_HEIGHT, GRID_WIDTH) > 0:
                        novo_mapa[i][j] = 1
                    else:
                        novo_mapa[i][j] = 0
                        self.vazios.append([i, j])

            if len(self.vazios) >= 2:
                self.vazios.sort()
                self.inicio = self.vazios[0]
                self.vazios.remove(self.inicio)
                self.fim = self.vazios[-1]
                self.matrix = novo_mapa
                break  

    def draw_maze(self, screen):
        screen.fill('black')
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if self.matrix[i][j] == 1:
                    pygame.draw.rect(screen, 'green', (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                elif self.matrix[i][j] == 0:
                    pygame.draw.rect(screen, 'black', (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.draw.rect(screen, 'yellow', (self.inicio[1] * CELL_SIZE, self.inicio[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, 'red', (self.fim[1] * CELL_SIZE, self.fim[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

class Cromossomo():
    def __init__(self, inicio, maze):
        self.maze = maze
        self.inicio = inicio
        self.moves = [[0,1],[0,-1],[1,0],[-1,0]]
        self.path = []
        pos = list(inicio)
        for _ in range(100):
            random.shuffle(self.moves)
            for move in self.moves:
                nova_linha = pos[0] + move[0]
                nova_coluna = pos[1] + move[1]
                if dentro_dos_limites(nova_linha, nova_coluna) and maze.matrix[nova_linha][nova_coluna] == 0:
                    self.path.append(move)
                    pos = [nova_linha, nova_coluna]
                    break
        self.comprimento = len(self.path)
        self.dist_goal = 0
        self.bom = True
        self.pos_atual = list(inicio)
        self.corrigir()

    def corrigir(self):
        pos = list(self.inicio)
        self.bom = True
        for i, move in enumerate(self.path):
            nova_linha = pos[0] + move[0]
            nova_coluna = pos[1] + move[1]
            if not dentro_dos_limites(nova_linha, nova_coluna) or self.maze.matrix[nova_linha][nova_coluna] == 1:
                self.path = self.path[:i]
                self.bom = False
                break
            pos = [nova_linha, nova_coluna]
        self.pos_atual = pos
        self.comprimento = len(self.path)
        self.dist_goal = abs(pos[0] - self.maze.fim[0]) + abs(pos[1] - self.maze.fim[1])

    def show_cromossomo(self, screen):
        pos = list(self.inicio)
        for move in self.path:
            nova_linha = pos[0] + move[0]
            nova_coluna = pos[1] + move[1]

            if dentro_dos_limites(nova_linha, nova_coluna) and self.maze.matrix[nova_linha][nova_coluna] == 0:
                pygame.draw.rect(screen, 'yellow', (pos[1] * CELL_SIZE, pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pos[0] = nova_linha
                pos[1] = nova_coluna
            else:
                break

class GeneticAlgo():
    def __init__(self, inicio, maze):
        self.inicio = inicio
        self.maze = maze
        self.population = [Cromossomo(inicio, maze) for _ in range(POPULATION)]
        self.vitoria = False
        self.geracao = 0

    def fitness(self, cromossomo):
        if len(cromossomo.path) == 0:
            return 0.01
        if cromossomo.dist_goal == 0:
            return 1000

        max_dist_possivel = GRID_HEIGHT + GRID_WIDTH
        progresso = 1 - (cromossomo.dist_goal / max_dist_possivel)
        eficiencia = 1 / (1 + len(cromossomo.path))
        return (progresso * 0.9) + (eficiencia * 0.1)

    def selection(self):
        pais = []
        for _ in range(len(self.population) // 2):
            candidatos = random.sample(self.population, 5)
            candidatos.sort(key=self.fitness, reverse=True)
            r = random.random()
            if r < 0.7:
                pais.append(candidatos[0])
            elif r < 0.9:
                pais.append(candidatos[1])
            else:
                pais.append(candidatos[2])
        return pais

    def mutation(self):
        for cromossomo in self.population:
            if len(cromossomo.path) == 0:
                continue
            if random.random() < 0.2:
                for _ in range(2):
                    if len(cromossomo.path) == 0:
                        break
                    idx = random.randint(0, len(cromossomo.path) - 1)
                    if random.random() < 0.5 and cromossomo.bom:
                        # Mutação orientada
                        dx = 1 if self.maze.fim[0] > cromossomo.pos_atual[0] else -1
                        dy = 1 if self.maze.fim[1] > cromossomo.pos_atual[1] else -1
                        cromossomo.path[idx] = [dx, 0] if random.random() < 0.5 else [0, dy]
                    else:
                        cromossomo.path[idx] = random.choice(cromossomo.moves)
                cromossomo.corrigir()

    def crossover(self):
        pais = self.selection()
        filhos = []
        for i in range(0, len(pais) - 1, 2):
            pai1, pai2 = pais[i], pais[i+1]
            min_len = min(len(pai1.path), len(pai2.path))
            if min_len < 2:
                continue
            ponto_corte = random.randint(1, min_len - 1)
            filho1 = Cromossomo(self.inicio, self.maze)
            filho2 = Cromossomo(self.inicio, self.maze)
            filho1.path = pai1.path[:ponto_corte] + pai2.path[ponto_corte:]
            filho2.path = pai2.path[:ponto_corte] + pai1.path[ponto_corte:]
            filho1.corrigir()
            filho2.corrigir()
            filhos.extend([filho1, filho2])
        return pais + filhos+ [Cromossomo(self.inicio, self.maze) for _ in range(POPULATION//2)]

    def run(self, screen):
        self.geracao += 1
        self.population.sort(key=self.fitness, reverse=True)
        elite = self.population[:10]
        nova_populacao = self.crossover()
        nova_populacao += elite
        while len(nova_populacao) < POPULATION:
            # Aumentar a diversidade
            novo = Cromossomo(self.inicio, self.maze)
            nova_populacao.append(novo)
        self.population = nova_populacao

        self.mutation()

        for cromossomo in self.population:
            if cromossomo.dist_goal == 0:
                self.vitoria = True
                print("Objetivo alcançado!")
                break

        melhor = max(self.population, key=self.fitness)
        print(f"Geração {self.geracao} | Melhor fitness: {self.fitness(melhor):.4f} | Distância: {melhor.dist_goal}")

        for i in range(min(5, len(self.population))):
            self.population[i].show_cromossomo(screen)

def main():
    pygame.init()
    screen = pygame.display.set_mode((HEIGHT, WIDTH))
    running = True
    clock = pygame.time.Clock()
    pygame.display.set_caption("Genetic Algo for Maze Solving")
    maze = Maze(prob_obstaculo=0.02)
    ga = GeneticAlgo(maze.inicio, maze)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        maze.draw_maze(screen)
        ga.run(screen)
        if ga.vitoria :
            break

        pygame.display.flip()
        clock.tick(10)

if __name__ == '__main__':
    main()
