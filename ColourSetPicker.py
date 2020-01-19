# Script First Worked on: 2020-01-19
# By: Charles S Turvey

from cv2 import cvtColor, COLOR_HSV2RGB
import numpy as np
import pygame
from pygame.locals import *


# ms = 9.1, mv = 8.4 seems to work
def colgen():
    # Deterministically generates a number of (hopefully) distinct colours
    # Note that the colour space is 0-1 on each axis, not 0-255
    h = np.linspace(0, 0.75, n + 1, dtype="float32")[:-1]
    s = 0.75 + (0.25 * np.sin(np.arange(0, n, dtype="float32") * ms))
    v = 0.8 + (0.1 * np.sin(np.arange(0, n, dtype="float32") * mv))
    # v = np.repeat(1, n)
    return cvtColor(np.uint8(np.transpose([h, s, v]).reshape(1, -1, 3) * 255), COLOR_HSV2RGB)[0]


pygame.init()
w, h = 500, 500
screen = pygame.display.set_mode((w, h))
screensize = np.int32((w, h))
textfont = pygame.font.Font(None, 30)

n = 10

while True:
    screen.fill(0)
    ms, mv = 10 * np.float32(pygame.mouse.get_pos()) / (w, h)
    for x, c in zip(np.linspace(0, w, n + 1)[:-1], colgen()):
        pygame.draw.rect(screen, c, [[x, 0], [w/n, h]])
    screen.blit(textfont.render("N: {}  S: {:.1f}  V: {:.1f}".format(n, ms, mv),
                                True, (0, 0, 0), (255, 255, 255)), (0, 0))
    pygame.display.flip()
    for e in pygame.event.get():
        if e.type == QUIT:
            quit()
        elif e.type == KEYDOWN:
            if e.key == K_ESCAPE:
                quit()
            if e.key == K_UP:
                n += 1
            if e.key == K_DOWN:
                n -= 1
