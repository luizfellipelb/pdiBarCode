import cv2
import numpy as np
import os

# Número de imagens para processar
quantidade_imagens = 90

pasta = "imagens"

for i in range(1, quantidade_imagens + 1):
    caminho = f"{pasta}/{i}.jpg"
    image = cv2.imread(caminho)

    if image is None:
        print(f"[ERRO] Imagem {caminho} não encontrada.")
        continue

    # Redimensionar a imagem para facilitar o processamento
    image = cv2.resize(image, (600, 400))

    # Converter para escala de cinza
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Reduzir ruído com blur
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)

    # Gradiente horizontal para realçar bordas verticais
    gradX = cv2.Sobel(blurred, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradX = cv2.convertScaleAbs(gradX)

    # Threshold
    _, thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Fechamento morfológico com kernel horizontal
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Limpeza: erosão seguida de dilatação
    closed = cv2.erode(closed, None, iterations=4)
    closed = cv2.dilate(closed, None, iterations=4)

    # Encontrar contornos
    contours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        c = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = box.astype(int)
        cv2.drawContours(image, [box], -1, (0, 255, 0), 3)

    # Mostrar a imagem com o resultado
    cv2.imshow(f"Imagem {i}", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
