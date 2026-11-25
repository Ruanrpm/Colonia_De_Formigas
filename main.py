"""Execute com python main.py para abrir o simulador."""

import tkinter as tk

from colonia import Colonia, FORMIGAS, RODADAS
from salao import Salao


FUNDO = "#f1f3ef"
TINTA = "#182d29"
SECUNDARIA = "#475f56"
PISO = "#142e2b"
PAREDE = "#536964"
TRILHA = "#38bfa9"
SAIDA = "#9ce3b1"
ROTA = "#ffc268"
FORMIGA = "#f3f9ed"
INICIO = "#bcaafa"


class Simulador:
    def __init__(self, janela):
        self.janela = janela
        janela.title("Rotas de fuga | Colônia de Formigas")
        janela.geometry("1060x690")
        janela.minsize(820, 560)
        janela.configure(bg=FUNDO)
        self.evento = None
        self.velocidade = tk.StringVar(value="Normal")
        self.status = tk.StringVar()
        self.rodada_texto = tk.StringVar()
        self.melhor_texto = tk.StringVar()

        topo = tk.Frame(janela, bg=FUNDO)
        topo.pack(fill="x", padx=24, pady=(16, 10))
        self.texto(topo, "Rotas de fuga", 25, negrito=True).pack(side="left")
        self.texto(topo, "Simulação por Colônia de Formigas", 11).pack(side="right")

        corpo = tk.Frame(janela, bg=FUNDO)
        corpo.pack(fill="both", expand=True, padx=24)
        lateral = tk.Frame(corpo, bg=FUNDO, width=210)
        lateral.pack(side="right", fill="y", padx=(18, 0))
        lateral.pack_propagate(False)
        self.tela = tk.Canvas(corpo, bg=PISO, highlightthickness=0)
        self.tela.pack(fill="both", expand=True)
        self.tela.bind("<Configure>", lambda _: self.desenhar_planta())
        self.tela.bind("<Button-1>", self.selecionar)

        self.texto(lateral, "Simulação", 15, negrito=True).pack(anchor="w")
        self.texto(lateral, f"{FORMIGAS} formigas por rodada", 10).pack(anchor="w")
        for legenda, variavel in [("Rodada", self.rodada_texto),
                                  ("Melhor rota", self.melhor_texto)]:
            self.texto(lateral, legenda, 10).pack(anchor="w", pady=(15, 0))
            self.texto(lateral, "", 18, negrito=True, variavel=variavel).pack(anchor="w")
        self.acao = self.botao(lateral, "Iniciar colônia", self.acionar, True)
        self.botao(lateral, "Gerar novo salão", self.novo_salao)
        self.texto(lateral, "Velocidade", 10).pack(anchor="w", pady=(13, 3))
        botoes = tk.Frame(lateral, bg=FUNDO)
        botoes.pack(anchor="w")
        for valor in ("Normal", "Rápida"):
            tk.Radiobutton(botoes, text=valor, value=valor, variable=self.velocidade,
                           bg=FUNDO, fg=TINTA, font=("Segoe UI", 10)).pack(side="left")
        self.texto(lateral, "", 10, variavel=self.status, largura=200).pack(
            fill="x", pady=14)

        legenda = tk.Frame(janela, bg=FUNDO)
        legenda.pack(fill="x", padx=24, pady=12)
        for nome, cor in [("Início", INICIO), ("Saída", SAIDA), ("Parede", PAREDE),
                          ("Formiga", FORMIGA), ("Feromônio", TRILHA), ("Melhor rota", ROTA)]:
            marca = tk.Canvas(legenda, width=16, height=16, bg=PISO, highlightthickness=0)
            marca.pack(side="left")
            marca.create_rectangle(4, 4, 12, 12, fill=cor, outline="")
            self.texto(legenda, nome, 9).pack(side="left", padx=(4, 12))
        self.novo_salao()

    def texto(self, pai, texto, tamanho, negrito=False, variavel=None, largura=0):
        return tk.Label(pai, text=texto, textvariable=variavel, bg=FUNDO,
                        fg=TINTA if negrito else SECUNDARIA, anchor="w", justify="left",
                        wraplength=largura, font=("Segoe UI", tamanho, "bold" if negrito else "normal"))

    def botao(self, pai, titulo, funcao, destaque=False):
        b = tk.Button(pai, text=titulo, command=funcao, relief="flat", borderwidth=0,
                      bg="#17675a" if destaque else "#dee6df", fg="white" if destaque else TINTA,
                      font=("Segoe UI", 10, "bold"), pady=7, cursor="hand2")
        b.pack(fill="x", pady=(10, 0))
        return b

    def cancelar_evento(self):
        if self.evento is not None:
            self.janela.after_cancel(self.evento)
            self.evento = None

    def novo_salao(self):
        self.salao = Salao()
        self.preparar(None)

    def preparar(self, inicio):
        self.cancelar_evento()
        self.inicio = inicio
        self.colonia = None
        self.rodada = 0
        self.caminhos = []
        self.feromonio_visivel = {}
        self.passo = 0
        self.estado = "pronto"
        self.rodada_texto.set(f"0 / {RODADAS}")
        self.melhor_texto.set("—")
        self.acao.config(text="Iniciar colônia", state="disabled" if inicio is None else "normal")
        self.status.set("Clique em uma célula livre para posicionar a pessoa."
                        if inicio is None else "Ponto inicial escolhido. Inicie a colônia.")
        self.desenhar_planta()

    def selecionar(self, evento):
        if self.estado in ("rodando", "pausado"):
            return
        c = int((evento.x - self.x0) // self.celula)
        l = int((evento.y - self.y0) // self.celula)
        if not (0 <= l < self.salao.linhas and 0 <= c < self.salao.colunas):
            return
        if (l, c) in self.salao.paredes or (l, c) in self.salao.saidas:
            self.status.set("Escolha uma célula do piso para marcar o início.")
            return
        self.preparar((l, c))

    def acionar(self):
        if self.estado == "rodando":
            self.cancelar_evento()
            self.estado = "pausado"
            self.acao.config(text="Continuar")
            self.status.set("Simulação pausada.")
            return
        if self.estado == "pausado":
            self.estado = "rodando"
            self.acao.config(text="Pausar")
            self.status.set("As formigas estão explorando o salão.")
            if self.caminhos:
                self.animar()
            else:
                self.proxima_rodada()
            return
        if self.inicio is None:
            return
        self.preparar(self.inicio)
        self.colonia = Colonia(self.salao, self.inicio)
        self.estado = "rodando"
        self.acao.config(text="Pausar")
        self.status.set("As formigas estão explorando o salão.")
        self.proxima_rodada()

    def proxima_rodada(self):
        self.rodada += 1
        self.rodada_texto.set(f"{self.rodada} / {RODADAS}")
        # A animação reproduz os caminhos reais sorteados pelo algoritmo.
        self.caminhos = self.colonia.executar_rodada()
        self.passo = 0
        self.animar()

    def animar(self):
        self.evento = None
        self.tela.delete("formiga")
        duracao = max(len(caminho) for caminho in self.caminhos)
        if self.passo < duracao:
            self.desenhar_formigas(self.passo)
            self.passo += 1
            atraso = 8 if self.velocidade.get() == "Rápida" else 48
            self.evento = self.janela.after(atraso, self.animar)
            return

        self.caminhos = []
        self.feromonio_visivel = self.colonia.feromonio.copy()
        self.desenhar_trilhas()
        if self.colonia.melhor_rota:
            self.melhor_texto.set(f"{len(self.colonia.melhor_rota) - 1} passos")
        if self.rodada < RODADAS:
            self.evento = self.janela.after(80, self.proxima_rodada)
        else:
            self.estado = "finalizado"
            self.acao.config(text="Executar novamente")
            self.status.set("A linha dourada mostra a melhor rota encontrada."
                            if self.colonia.melhor_rota else
                            "Nenhuma formiga alcançou uma saída. Tente novamente.")
            self.desenhar_resultado()

    def centro(self, posicao):
        l, c = posicao
        return self.x0 + (c + 0.5) * self.celula, self.y0 + (l + 0.5) * self.celula

    def desenhar_formigas(self, passo):
        raio = max(2, self.celula * 0.14)
        for caminho in self.caminhos:
            if passo < len(caminho):
                x, y = self.centro(caminho[passo])
                self.tela.create_oval(x-raio, y-raio, x+raio, y+raio,
                                      fill=FORMIGA, outline=PISO, tags="formiga")

    def desenhar_planta(self):
        t = self.tela
        t.delete("all")
        w, h = t.winfo_width(), t.winfo_height()
        self.celula = max(1, min((w-20)//self.salao.colunas, (h-20)//self.salao.linhas))
        s = self.celula
        self.x0 = (w - self.salao.colunas * s) // 2
        self.y0 = (h - self.salao.linhas * s) // 2
        for l in range(self.salao.linhas):
            for c in range(self.salao.colunas):
                x, y = self.x0 + c*s, self.y0 + l*s
                cor = PAREDE if (l, c) in self.salao.paredes else PISO
                t.create_rectangle(x, y, x+s, y+s, fill=cor, outline="#324a46")
        for pos in self.salao.saidas:
            x, y = self.centro(pos)
            t.create_rectangle(x-s*.46, y-s*.46, x+s*.46, y+s*.46,
                               fill=SAIDA, outline="", tags="marcas")
            t.create_text(x, y, text="S", fill=PISO, font=("Segoe UI", max(8, s//3), "bold"),
                          tags="marcas")
        if self.inicio is not None:
            x, y = self.centro(self.inicio)
            t.create_oval(x-s*.35, y-s*.35, x+s*.35, y+s*.35, fill=INICIO,
                          outline="", tags="marcas")
        self.desenhar_trilhas()
        if self.caminhos and self.passo > 0:
            self.desenhar_formigas(self.passo - 1)
        if self.estado == "finalizado":
            self.desenhar_resultado()

    def desenhar_trilhas(self):
        self.tela.delete("trilha")
        if self.colonia:
            for (a, b), valor in self.feromonio_visivel.items():
                if valor >= 0.05:
                    cor = TRILHA if valor >= 0.5 else "#37746b"
                    self.tela.create_line(*self.centro(a), *self.centro(b), fill=cor,
                                          width=min(6, 1 + valor), tags="trilha")
        self.tela.tag_raise("marcas")

    def desenhar_resultado(self):
        rota = self.colonia.melhor_rota
        if rota:
            pontos = [n for pos in rota for n in self.centro(pos)]
            self.tela.create_line(*pontos, fill=ROTA, width=max(3, self.celula//5),
                                  joinstyle="round")
            self.tela.tag_raise("marcas")


if __name__ == "__main__":
    janela = tk.Tk()
    Simulador(janela)
    janela.mainloop()
