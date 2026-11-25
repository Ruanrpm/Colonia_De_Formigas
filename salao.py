"""Geração da planta usada na simulação."""

import random


class Salao:
    linhas = 15
    colunas = 23

    def __init__(self):
        ultima = self.linhas - 1
        direita = self.colunas - 1
        bordas = [
            [(0, c) for c in range(2, direita - 1)],
            [(ultima, c) for c in range(2, direita - 1)],
            [(l, 0) for l in range(2, ultima - 1)],
            [(l, direita) for l in range(2, ultima - 1)],
        ]
        self.saidas = {random.choice(borda) for borda in random.sample(bordas, 3)}
        self.paredes = {
            (l, c) for l in range(self.linhas) for c in range(self.colunas)
            if l in (0, ultima) or c in (0, direita)
        } - self.saidas

        # Cada bloco deixa um corredor livre ao redor. Assim, qualquer piso
        # pode alcançar as saídas, sem precisar calcular a rota na geração.
        blocos = 0
        for _ in range(100):
            altura = random.randint(1, 3)
            largura = random.randint(2, 4)
            topo = random.randint(2, ultima - altura - 1)
            esquerda = random.randint(2, direita - largura - 1)
            margem = {(l, c) for l in range(topo - 1, topo + altura + 1)
                      for c in range(esquerda - 1, esquerda + largura + 1)}
            if margem.isdisjoint(self.paredes):
                self.paredes.update((l, c) for l in range(topo, topo + altura)
                                    for c in range(esquerda, esquerda + largura))
                blocos += 1
                if blocos == 9:
                    break

    def vizinhos(self, posicao):
        l, c = posicao
        return [(i, j) for i, j in ((l - 1, c), (l + 1, c), (l, c - 1), (l, c + 1))
                if 0 <= i < self.linhas and 0 <= j < self.colunas
                and (i, j) not in self.paredes]
