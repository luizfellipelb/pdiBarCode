import cv2
import numpy as np
import os

quantidade_imagens = 90
pasta = "imagens"

for i in range(1, quantidade_imagens + 1):
    caminho = f"{pasta}/{i}.jpg"
    image = cv2.imread(caminho)

    if image is None:
        print(f"[ERRO] Imagem {caminho} não encontrada.")
        continue

    # Redimensiona para facilitar o processamento
    image = cv2.resize(image, (600, 400))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)

    # Gradiente horizontal (destaca linhas verticais)
    gradX = cv2.Sobel(blurred, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=3)
    gradX = cv2.convertScaleAbs(gradX)

    # Binarização com Otsu
    _, thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Fechamento morfológico
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    closed = cv2.erode(closed, None, iterations=2)
    closed = cv2.dilate(closed, None, iterations=2)

    # Detectar linhas com Hough
    lines = cv2.HoughLinesP(closed, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)

    # Criar uma máscara preta e desenhar as linhas
    mask = np.zeros_like(gray)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(mask, (x1, y1), (x2, y2), 255, 3)

    # Encontrar contornos na máscara de linhas
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Escolher o maior contorno que provavelmente é o código de barras
        c = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        cv2.drawContours(image, [box], -1, (0, 255, 0), 3)

    cv2.imshow(f"Imagem {i}", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
