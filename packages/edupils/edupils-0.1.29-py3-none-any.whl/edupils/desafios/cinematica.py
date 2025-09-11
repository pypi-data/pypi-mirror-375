from edupils import constantes, desenho
import asyncio


class Objeto:
    def __init__(
        self,
        nome,
        posicao_inicial,
        altura,
        funcao_movimento=None,
        forma="quadrado",
        cor="azul",
        origem_em_metros=(10, 1),
        pixels_por_metro=25,
    ):
        self.nome = nome
        self.posicao = posicao_inicial
        self.altura = altura
        self.funcao_movimento = funcao_movimento or (lambda t: self.posicao)
        self.forma = forma
        self.cor = cor
        self.origem_metros = origem_em_metros
        self.pixels_por_metro = pixels_por_metro
        self.desenhar()

    def desenhar(self, camada=constantes.NOME_PAINEL_FRENTE):
        x = (self.posicao + self.origem_metros[0]) * self.pixels_por_metro
        y = (self.altura + self.origem_metros[1] - 1) * self.pixels_por_metro
        if self.forma == "quadrado":
            desenho.desenhar_retangulo(
                x, y, 20, 20, camada, cor_preenchimento=self.cor
            )
        elif self.forma == "triangulo":
            desenho.desenhar_triangulo(
                x+10, y+12, 14, self.cor, camada, angulo=270, proporcao_base=1.61
            )
        elif self.forma == "circulo":
            desenho.desenhar_arco(
                x+10, y+10, 10, 0, 360, camada, cor_preenchimento=self.cor, cor_contorno=self.cor, largura_contorno=1
            )



class Animacao:
    def __init__(
        self,
        tempo=10,
        frames_por_segundo=10,
        distancia_em_metros=20,
        origem_em_metros=(10, 1),
        pixels_por_metro=25,
        deixar_rastro=False,
    ):
        self.tempo = tempo
        self.frames_por_segundo = frames_por_segundo
        self.distancia_em_metros = distancia_em_metros
        self.origem_em_metros = origem_em_metros
        self.pixels_por_metro = pixels_por_metro
        self.deixar_rastro = deixar_rastro
        self.objetos = {}
        self.desenhar_eixo_x()

    def adicionar_objeto(
        self,
        nome,
        posicao_inicial,
        funcao_movimento,
        forma="quadrado",
        cor="azul"
    ):
        self.objetos[nome] = Objeto(
            nome,
            posicao_inicial,
            0,
            funcao_movimento,
            forma=forma,
            cor=cor,
            origem_em_metros=self.origem_em_metros,
            pixels_por_metro=self.pixels_por_metro,
        )

    def desenhar_eixo_x(self, camada=constantes.NOME_PAINEL_AUXILIAR):
        desenho.apagar_painel(camada)
        inicio_y = self.origem_em_metros[1] * self.pixels_por_metro
        fim_y = inicio_y
        inicio_x = (
            (self.origem_em_metros[0] - self.distancia_em_metros)
            * self.pixels_por_metro
            * 2
        )
        fim_x = (
            (self.origem_em_metros[0] + self.distancia_em_metros)
            * self.pixels_por_metro
            * 2
        )
        desenho.desenhar_linha(inicio_x, inicio_y, fim_x, fim_y, id_canvas=camada)

        for i in range(-2 * self.distancia_em_metros, 2 * self.distancia_em_metros + 1):
            x = (i + self.origem_em_metros[0]) * self.pixels_por_metro
            desenho.escrever_texto(
                str(i), x + 2, inicio_y + 12, id_canvas=camada, tamanho=10
            )
            desenho.desenhar_linha(x, inicio_y, x, inicio_y + 5, id_canvas=camada)

    def desenhar_tempo(self, t, camada=constantes.NOME_PAINEL_FRENTE):
        desenho.escrever_texto(
            f"t = {t:.1f} s",
            400,
            100,
            id_canvas=camada,
            tamanho=12,
            cor="black",
        )

    def desenhar_quadro(self, t, camada=constantes.NOME_PAINEL_FRENTE):
        desenho.apagar_painel(camada)
        self.desenhar_tempo(t, camada=camada)
        for obj in self.objetos.values():
            obj.posicao = obj.funcao_movimento(t)
            obj.desenhar(camada=camada)

    def desenhar_rastro(self, t, camada=constantes.NOME_PAINEL_FUNDO):
        for obj in self.objetos.values():
            obj.posicao = obj.funcao_movimento(t)
            obj.desenhar(camada=camada)
        desenho.clarear_com_marca_dagua(camada, .6)

    def apagar_tudo(self):
        for camada in [constantes.NOME_PAINEL_FUNDO, constantes.NOME_PAINEL_FRENTE]:
            desenho.apagar_painel(camada)

    async def animar(self):
        self.apagar_tudo()
        max_steps = int(self.tempo * self.frames_por_segundo)
        dt = 1 / self.frames_por_segundo

        for step in range(max_steps):
            t = step * dt
            
            self.desenhar_quadro(t)
            if self.deixar_rastro and (t % 1 < .001):
                self.desenhar_rastro(t, camada=constantes.NOME_PAINEL_FUNDO)
            
            await asyncio.sleep(dt)

class Animacao2D(Animacao):
    pass
