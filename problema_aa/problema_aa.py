import pygame 
import numpy as np 
import math
import sys

MALLA_MENOR = (36, 40, 56)
MALLA_MAYOR = (62, 70, 96)

ANCHO = 1100
ALTO = 550
FPS = 60

class Particula:
    def __init__(self, pos, v, dir, dt):
        self.pos = np.array(pos, dtype=float)
        self.v = np.array(v, dtype=float)
        dir = np.array(dir, dtype=float)
        self.dir = dir / np.linalg.norm(dir)
        self.dt = dt
    def cambiar_posicion(self):
        self.pos += self.v * self.dir * self.dt

class Camara2D:
    def __init__(self, limites_mundo, ancho_pantalla, alto_pantalla, margen):
        self.xmin, self.xmax, self.ymin, self.ymax = limites_mundo 
        self.ancho_pantalla = ancho_pantalla
        self.alto_pantalla = alto_pantalla
        self.margen = margen 

        ancho_mundo = self.xmax - self.xmin 
        alto_mundo = self.ymax - self.ymin 

        ancho_usable = ancho_pantalla - 2 * margen 
        alto_usable = alto_pantalla - 2 * margen 

        self.escala = min(ancho_usable / ancho_mundo, alto_usable / alto_mundo)

        self.des_x = (ancho_pantalla - ancho_mundo * self.escala) / 2 - self.xmin * self.escala 
        self.des_y = (alto_pantalla - alto_mundo * self.escala) / 2 + self.ymax * self.escala 

    def convertir_a_pixeles(self, p):
        x, y = p
        x = x * self.escala + self.des_x 
        y = -y * self.escala + self.des_y 
        return int(round(x)), int(round(y))
    
    def rect_mundo_a_pantalla(self, x0, x1, y0, y1):
        p1 = self.convertir_a_pixeles((x0, y1))
        p2 = self.convertir_a_pixeles((x1, y0))

        x = min(p1[0], p2[0])
        y = min(p1[1], p2[1])

        ancho = abs(p1[0] - p2[0])
        alto = abs(p1[1] - p2[1])

        return pygame.Rect(x, y, ancho, alto)
    
def dibujar_gradiente_vertical(superficie, color_inicial, color_final):
    ancho, alto = superficie.get_size() 
    for y in range(alto):
        t = y / max(1, alto - 1)
        r = int(color_final[0] * (1 - t) + color_inicial[0] * t)
        g = int(color_final[1] * (1 - t) + color_inicial[1] * t)
        b = int(color_final[2] * (1 - t) + color_inicial[2] * t)
        pygame.draw.line(superficie, (r, g, b), (0, y), (ancho, y))

def dibujar_texto(superficie, fuente, texto, pos, color = (235, 240, 250)):
    img = fuente.render(texto, True, color)
    superficie.blit(img, pos)

def dibujar_malla(superficie, camara, espaciado_menor, espaciado_mayor):
    xmin, xmax, ymin, ymax = camara.xmin, camara.xmax, camara.ymin, camara.ymax
    x_inicial = math.floor(xmin/espaciado_menor) * espaciado_menor
    x_final = math.ceil(xmax/espaciado_menor) * espaciado_menor
    y_inicial = math.floor(ymin/espaciado_menor) * espaciado_menor
    y_final = math.ceil(ymax/espaciado_menor) * espaciado_menor

    x = x_inicial
    while x <= x_final + 1e-9:
        p0 = camara.convertir_a_pixeles((x, ymin))
        p1 = camara.convertir_a_pixeles((x, ymax))

        if abs((x / espaciado_menor) % espaciado_mayor) < 1e-9:
            dibujar_texto(
                superficie,
                pygame.font.SysFont("consolas", 11),
                str(x),
                (p0[0]-20, p0[1]+10)
            )
            color = MALLA_MAYOR
            ancho = 2
        else: 
            color = MALLA_MENOR
            ancho = 1 
        pygame.draw.line(superficie, color, p0, p1, ancho)
        x += espaciado_menor

    y = y_inicial
    while y <= y_final + 1e-9:
        p0 = camara.convertir_a_pixeles((xmin, y))
        p1 = camara.convertir_a_pixeles((xmax, y))

        if abs((y / espaciado_menor) % espaciado_mayor) < 1e-9:
            dibujar_texto(
                superficie,
                pygame.font.SysFont("consolas", 11),
                str(y),
                (p0[0]-50, p0[1]-5)
            )
            color = MALLA_MAYOR
            ancho = 2
        else: 
            color = MALLA_MENOR
            ancho = 1 
        pygame.draw.line(superficie, color, p0, p1, ancho)
        y += espaciado_menor

def dibujar_panel(superficie, rect, relleno_rgba, borde_rgb):
    radius = 18
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, relleno_rgba, panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, borde_rgb, panel.get_rect(), width=2, border_radius=radius)
    superficie.blit(panel, rect.topleft)

def dibujar_badge(superficie, fuente, texto, pos, relleno_rgba, borde_rgb, color_texto):
    img = fuente. render(texto, True, color_texto)
    pad_x, pad_y = 14, 8
    rect = pygame.Rect(
        pos[0],
        pos[1],
        img.get_width() + 2 * pad_x,
        img.get_height() + 2 * pad_y
    )

    badge = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(badge, relleno_rgba, badge.get_rect(), border_radius=16)
    pygame.draw.rect(badge, borde_rgb, badge.get_rect(), width=2, border_radius=16)
    badge.blit(img, (pad_x, pad_y))
    superficie.blit(badge, rect.topleft)

def correr_simulacion():
    pygame.init()
    pygame.display.set_caption("Conejo vs Tortuga")
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("consolas", 20)
    fuente_menor = pygame.font.SysFont("consolas", 16)
    fuente_mayor = pygame.font.SysFont("consolas", 24)

    xmin, xmax, ymin, ymax = -1, 11, -1, 11

    camara = Camara2D((xmin, xmax, ymin, ymax), ANCHO, ALTO, margen = 70)
    
    dt = 1 / FPS

    tiempo = 0.0
    tiempo_texto_reinicio = 0.0

    paused = False
    liebre_corriendo = True 
    mostrar_reinicio = False 
    mostrar_ganador = False 
    ganador = None 

    posicion_inicial_tortuga = (3.5, 0)
    posicion_inicial_liebre = (6.5, 0)

    velocidad_tortuga = 0.3 # m/s
    velocidad_liebre = 0.9 # m/s

    direccion = (0, 1)

    tortuga = Particula(posicion_inicial_tortuga, velocidad_tortuga, direccion, dt)
    liebre = Particula(posicion_inicial_liebre, velocidad_liebre, direccion, dt)

    fondo = pygame.image.load("pasto.png").convert()
    fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

    img_tortuga = pygame.image.load("tortuga.png").convert_alpha()
    img_tortuga = pygame.transform.scale(img_tortuga, (80, 80))
    img_liebre = pygame.image.load("liebre.png").convert_alpha()
    img_liebre = pygame.transform.scale(img_liebre, (80, 80))

    corriendo = True 
    while corriendo:
        tiempo_real = reloj.tick(FPS) / 1000.0
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False 
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    corriendo = False 
                elif evento.key == pygame.K_SPACE:
                    paused = not paused 
                elif evento.key == pygame.K_a:
                    liebre_corriendo = not liebre_corriendo
                elif evento.key == pygame.K_r:
                    tiempo = 0.0 
                    tortuga = Particula(posicion_inicial_tortuga, velocidad_tortuga, direccion, dt)
                    liebre = Particula(posicion_inicial_liebre, velocidad_liebre, direccion, dt)
                    paused = False 
                    mostrar_reinicio = True 
                    tiempo_texto_reinicio = 0.8
                    mostrar_ganador = False

        pantalla.blit(fondo, (0, 0))
        posicion_tortuga = camara.convertir_a_pixeles(tortuga.pos)
        posicion_liebre = camara.convertir_a_pixeles(liebre.pos)
        punto_final = camara.convertir_a_pixeles((0.0, 10.0))

        if posicion_tortuga[1] < punto_final[1]:
            paused = True 
            mostrar_ganador = True 
            ganador = "Ganó la tortuga!!!"
        if posicion_liebre[1] < punto_final[1]:
            paused = True 
            mostrar_ganador = True 
            ganador = "Ganó la liebre!!!"
        if (posicion_tortuga[1] < punto_final[1]) and (posicion_liebre[1] < punto_final[1]):
            ganador = "Empate!!!"
        
        if not paused:
            tiempo += dt 
            tortuga.cambiar_posicion()
            if liebre_corriendo:
                liebre.cambiar_posicion()
            else: 
                dibujar_texto(
                    pantalla, 
                    fuente_mayor, 
                    "Z",
                    (20*tiempo % 70 + posicion_liebre[0], 5*math.sin(5*tiempo) + posicion_liebre[1] - 20),
                    (255, 0, 0)
                )
        
        if mostrar_reinicio:
            tiempo_texto_reinicio -= dt 
            if tiempo_texto_reinicio <= 0:
                mostrar_reinicio = False 

        # dibujar_gradiente_vertical(pantalla, (17, 94, 14), (60, 209, 54))

        panel_rect = pygame.Rect(18, 16, 225, 180)
        dibujar_panel(pantalla, panel_rect, (20, 24, 38, 185), (85, 95, 125))

        p0 = camara.convertir_a_pixeles((3,0))
        p1 = camara.convertir_a_pixeles((7, 0))
        pygame.draw.line(pantalla, (255, 255, 255), p0, p1, width=10)
        p0 = camara.convertir_a_pixeles((3,10))
        p1 = camara.convertir_a_pixeles((7, 10))
        pygame.draw.line(pantalla, (255, 255, 255), p0, p1, width=10)


        rect_tortuga = img_tortuga.get_rect(center=posicion_tortuga)
        pantalla.blit(img_tortuga, rect_tortuga)

        rect_liebre = img_liebre.get_rect(center=posicion_liebre)
        pantalla.blit(img_liebre, rect_liebre)

        pygame.draw.circle(pantalla, (255, 0, 0), posicion_tortuga, 6)
        pygame.draw.circle(pantalla, (255, 0, 0), posicion_liebre, 6)

        dibujar_texto(pantalla, fuente_mayor, "Simulación", (34, 28))
        dibujar_texto(pantalla, fuente, f"t = {tiempo: 0.3f} s", (34, 62))

        dibujar_texto(
            pantalla,
            fuente_menor,
            f"Tortuga: {tortuga.pos[1]: .2f} m",
            (34, 120),
            (170, 180, 200)
        )

        dibujar_texto(
            pantalla,
            fuente_menor,
            f"Liebre: {liebre.pos[1]: .2f} m",
            (34, 145),
            (170, 180, 200)
        )

        dibujar_badge(
            pantalla,
            fuente_menor,
            "Espacio = pausar",
            (20, ALTO - 48),
            (28, 34, 52, 185),
            (90, 105, 140),
            (170, 180, 200)
        )

        dibujar_badge(
            pantalla,
            fuente_menor,
            "r = reiniciar",
            (185, ALTO - 48),
            (28, 34, 52, 185),
            (90, 105, 140),
            (170, 180, 200)
        )

        dibujar_badge(
            pantalla,
            fuente_menor,
            "a = dormir/despertar a la liebre",
            (750, ALTO - 48),
            (28, 34, 52, 185),
            (90, 105, 140),
            (170, 180, 200)
        )

        if paused: 
            dibujar_badge(
                pantalla,
                fuente,
                "PAUSA",
                (ANCHO-160, 20),
                (55, 42, 18, 210),
                (210, 170, 90),
                (255, 210, 120)
            )

        if mostrar_reinicio:
            dibujar_badge(
                pantalla,
                fuente,
                "REINICIANDO",
                (ANCHO-240, 64),
                (24, 52, 68, 210),
                (100, 190, 220),
                (120, 220, 255)
            )

        if mostrar_ganador:
            dibujar_badge(
                pantalla,
                fuente,
                ganador,
                (ANCHO/3, 20),
                (24, 52, 68, 210),
                (100, 190, 220),
                (120, 220, 255)
            )
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    correr_simulacion()





 

