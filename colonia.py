"""Colônia de Formigas para buscar uma saída. Cada aresta custa um passo."""

import random


FORMIGAS = 20
RODADAS = 20
EVAPORACAO = 0.25


class Colonia:
    def __init__(self, salao, inicio):
        self.salao = salao
        self.inicio = inicio
        self.melhor_rota = []
        # Chave: (origem, destino). Um trecho ainda inexplorado tem peso base 1.
        self.feromonio = {}

    def distancia_estimada(self, posicao):
        # Distância de Manhattan até a saída mais próxima, ignorando paredes.
        l, c = posicao
        return min(abs(l - i) + abs(c - j) for i, j in self.salao.saidas)

    def caminhar(self):
        caminho = [self.inicio]
        visitados = {self.inicio}

        while caminho[-1] not in self.salao.saidas:
            atual = caminho[-1]
            opcoes = [v for v in self.salao.vizinhos(atual) if v not in visitados]
            if not opcoes:
                break  # Beco sem saída: esta formiga encerra sua tentativa.

            # Sorteio ponderado: aproximar-se de uma saída favorece o passo.
            # Mais feromônio também aumenta a chance de escolher o trecho.
            pesos = []
            distancia_atual = self.distancia_estimada(atual)
            for vizinho in opcoes:
                atracao = 4 if self.distancia_estimada(vizinho) < distancia_atual else 1
                trilha = self.feromonio.get((atual, vizinho), 0)
                pesos.append((1 + trilha) * atracao)

            proximo = random.choices(opcoes, weights=pesos)[0]
            caminho.append(proximo)
            visitados.add(proximo)
        return caminho

    def executar_rodada(self):
        # Todas exploram usando o feromônio deixado pelas rodadas anteriores.
        caminhos = [self.caminhar() for _ in range(FORMIGAS)]

        for trecho in self.feromonio:
            self.feromonio[trecho] *= 1 - EVAPORACAO

        for caminho in caminhos:
            if caminho[-1] not in self.salao.saidas:
                continue
            if not self.melhor_rota or len(caminho) < len(self.melhor_rota):
                self.melhor_rota = caminho

            # Uma rota de L passos recebe 1/L em cada trecho percorrido.
            # Quanto menor a rota, maior o reforço por formiga.
            passos = len(caminho) - 1
            for origem, destino in zip(caminho, caminho[1:]):
                trecho = (origem, destino)
                self.feromonio[trecho] = self.feromonio.get(trecho, 0) + 1 / passos

        return caminhos
