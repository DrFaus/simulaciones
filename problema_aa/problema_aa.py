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

def dibujar_grafico_carrera(
    screen,
    tiempos,
    pos_tortuga,
    pos_liebre,
    rect,
    font=None,
    titulo="Posición vs tiempo"
):
    """
    Dibuja un gráfico dentro del juego usando pygame.

    Parámetros
    ----------
    screen : pygame.Surface
        Superficie principal donde se hará blit del gráfico.
    tiempos : array-like
        Arreglo de tiempos.
    pos_tortuga : array-like
        Arreglo de posiciones de la tortuga.
    pos_liebre : array-like
        Arreglo de posiciones de la liebre.
    rect : tuple[int, int, int, int]
        Región donde se dibujará el gráfico: (x, y, ancho, alto).
    font : pygame.font.Font o None
        Fuente para texto. Si es None, se crea una por defecto.
    titulo : str
        Título del gráfico.
    """

    # -----------------------------
    # Validación mínima
    # -----------------------------
    tiempos = np.asarray(tiempos, dtype=float)
    pos_tortuga = np.asarray(pos_tortuga, dtype=float)
    pos_liebre = np.asarray(pos_liebre, dtype=float)

    if not (len(tiempos) == len(pos_tortuga) == len(pos_liebre)):
        raise ValueError("Los tres arreglos deben tener la misma longitud.")

    if len(tiempos) < 2:
        return

    if font is None:
        font = pygame.font.SysFont("consolas", 16)
    font_titulo = pygame.font.SysFont("consolas", 18, bold=True)

    # -----------------------------
    # Región del gráfico
    # -----------------------------
    x0, y0, w, h = rect

    # Surface independiente para el gráfico
    grafico = pygame.Surface((w, h), pygame.SRCALPHA)

    # -----------------------------
    # Estética
    # -----------------------------
    COLOR_FONDO = (20, 24, 38, 185)      # azul grisáceo con buen contraste
    COLOR_BORDE = (85, 95, 125)
    COLOR_TEXTO = (255, 255, 255)
    COLOR_EJES = (255, 255, 255)
    COLOR_GRID = (190, 210, 220, 60)
    COLOR_TORTUGA = (120, 230, 160)
    COLOR_LIEBRE = (245, 220, 90)

    grafico.fill(COLOR_FONDO)
    pygame.draw.rect(grafico, COLOR_BORDE, (0, 0, w, h), width=2, border_radius=8)

    # -----------------------------
    # Márgenes internos del gráfico
    # -----------------------------
    margen_izq = 60
    margen_der = 20
    margen_sup = 40
    margen_inf = 45

    plot_x = margen_izq
    plot_y = margen_sup
    plot_w = w - margen_izq - margen_der
    plot_h = h - margen_sup - margen_inf

    # -----------------------------
    # Rango de datos
    # -----------------------------
    t_min = np.min(tiempos)
    t_max = np.max(tiempos)

    y_min_datos = min(np.min(pos_tortuga), np.min(pos_liebre))
    y_max_datos = max(np.max(pos_tortuga), np.max(pos_liebre))

    # Para que no quede pegado
    if np.isclose(t_min, t_max):
        t_max = t_min + 1.0
    if np.isclose(y_min_datos, y_max_datos):
        y_max_datos = y_min_datos + 1.0

    # Si quieres que empiece en cero cuando tenga sentido:
    y_min = min(0.0, y_min_datos)
    y_max = y_max_datos

    # -----------------------------
    # Funciones de mapeo
    # -----------------------------
    def map_x(t):
        return plot_x + (t - t_min) / (t_max - t_min) * plot_w

    def map_y(y):
        return plot_y + plot_h - (y - y_min) / (y_max - y_min) * plot_h

    # -----------------------------
    # Grid y ticks
    # -----------------------------
    n_ticks_x = 5
    n_ticks_y = 5
    tick_len = 6

    # Eje x
    for i in range(n_ticks_x + 1):
        frac = i / n_ticks_x
        tx = plot_x + frac * plot_w
        valor_t = t_min + frac * (t_max - t_min)

        # línea de grid
        pygame.draw.line(grafico, COLOR_GRID, (tx, plot_y), (tx, plot_y + plot_h), 1)

        # tick
        pygame.draw.line(
            grafico,
            COLOR_EJES,
            (tx, plot_y + plot_h),
            (tx, plot_y + plot_h + tick_len),
            2
        )

        # etiqueta
        texto = font.render(f"{valor_t:.1f}", True, COLOR_TEXTO)
        rect_txt = texto.get_rect(center=(tx, plot_y + plot_h + 18))
        grafico.blit(texto, rect_txt)

    # Eje y
    for i in range(n_ticks_y + 1):
        frac = i / n_ticks_y
        ty = plot_y + plot_h - frac * plot_h
        valor_y = y_min + frac * (y_max - y_min)

        # línea de grid
        pygame.draw.line(grafico, COLOR_GRID, (plot_x, ty), (plot_x + plot_w, ty), 1)

        # tick
        pygame.draw.line(
            grafico,
            COLOR_EJES,
            (plot_x - tick_len, ty),
            (plot_x, ty),
            2
        )

        # etiqueta
        texto = font.render(f"{valor_y:.1f}", True, COLOR_TEXTO)
        rect_txt = texto.get_rect(right=plot_x - 10, centery=ty)
        grafico.blit(texto, rect_txt)

    # -----------------------------
    # Ejes
    # -----------------------------
    pygame.draw.line(
        grafico,
        COLOR_EJES,
        (plot_x, plot_y + plot_h),
        (plot_x + plot_w, plot_y + plot_h),
        2
    )
    pygame.draw.line(
        grafico,
        COLOR_EJES,
        (plot_x, plot_y),
        (plot_x, plot_y + plot_h),
        2
    )

    # -----------------------------
    # Convertir datos a puntos
    # -----------------------------
    puntos_tortuga = [(map_x(t), map_y(y)) for t, y in zip(tiempos, pos_tortuga)]
    puntos_liebre = [(map_x(t), map_y(y)) for t, y in zip(tiempos, pos_liebre)]

    # -----------------------------
    # Dibujar curvas
    # -----------------------------
    if len(puntos_tortuga) >= 2:
        pygame.draw.lines(grafico, COLOR_TORTUGA, False, puntos_tortuga, 3)

    if len(puntos_liebre) >= 2:
        pygame.draw.lines(grafico, COLOR_LIEBRE, False, puntos_liebre, 3)

    # Marcar último punto
    pygame.draw.circle(grafico, COLOR_TORTUGA, (int(puntos_tortuga[-1][0]), int(puntos_tortuga[-1][1])), 4)
    pygame.draw.circle(grafico, COLOR_LIEBRE, (int(puntos_liebre[-1][0]), int(puntos_liebre[-1][1])), 4)

    # -----------------------------
    # Título
    # -----------------------------
    txt_titulo = font_titulo.render(titulo, True, COLOR_TEXTO)
    grafico.blit(txt_titulo, (12, 8))

    # -----------------------------
    # Etiquetas de ejes
    # -----------------------------
    txt_x = font.render("Tiempo", True, COLOR_TEXTO)
    rect_x = txt_x.get_rect(center=(plot_x + plot_w / 2, h - 14))
    grafico.blit(txt_x, rect_x)

    txt_y = font.render("Posición", True, COLOR_TEXTO)
    txt_y_rot = pygame.transform.rotate(txt_y, 90)
    rect_y = txt_y_rot.get_rect(center=(18, plot_y + plot_h / 2))
    grafico.blit(txt_y_rot, rect_y)

    # -----------------------------
    # Leyenda
    # -----------------------------
    ley_x = w - 150
    ley_y = 10

    pygame.draw.line(grafico, COLOR_TORTUGA, (ley_x, ley_y + 10), (ley_x + 24, ley_y + 10), 3)
    txt_tort = font.render("Tortuga", True, COLOR_TEXTO)
    grafico.blit(txt_tort, (ley_x + 32, ley_y + 2))

    pygame.draw.line(grafico, COLOR_LIEBRE, (ley_x, ley_y + 32), (ley_x + 24, ley_y + 32), 3)
    txt_lieb = font.render("Liebre", True, COLOR_TEXTO)
    grafico.blit(txt_lieb, (ley_x + 32, ley_y + 24))

    # -----------------------------
    # Colocar gráfico en pantalla
    # -----------------------------
    screen.blit(grafico, (x0, y0))

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

    tiempo_array = [tiempo]
    posicion_tortuga_array = [posicion_inicial_tortuga[1]]
    posicion_liebre_array = [posicion_inicial_liebre[1]]

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

                    tiempo_array = [tiempo]
                    posicion_tortuga_array = [posicion_inicial_tortuga[1]]
                    posicion_liebre_array = [posicion_inicial_liebre[1]]

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

            tiempo_array.append(tiempo)
            posicion_tortuga_array.append(tortuga.pos[1])
            posicion_liebre_array.append(liebre.pos[1])
        
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
            dibujar_grafico_carrera(
                pantalla,
                tiempo_array,
                posicion_tortuga_array,
                posicion_liebre_array,
                font = fuente_menor,
                rect=(700, 160, 400, 250)
            )
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    correr_simulacion()





 

