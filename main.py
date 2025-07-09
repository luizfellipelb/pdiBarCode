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

    print(f"\nProcessando Imagem {i}...")

    # Redimensiona para facilitar o processamento
    image_resized = cv2.resize(image.copy(), (600, 400))
    cv2.imshow(f"Imagem {i} - 1. Original Redimensionada", image_resized)
    cv2.waitKey(0)

    # Converte para escala de cinza
    gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
    cv2.imshow(f"Imagem {i} - 2. Escala de Cinza", gray)
    cv2.waitKey(0)

    # Aplica desfoque Gaussiano
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)
    cv2.imshow(f"Imagem {i} - 3. Desfoque Gaussiano", blurred)
    cv2.waitKey(0)

    # Calcula o gradiente horizontal (destaca linhas verticais)
    gradX = cv2.Sobel(blurred, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=3)
    gradX = cv2.convertScaleAbs(gradX)
    cv2.imshow(f"Imagem {i} - 4. Gradiente X (Sobel)", gradX)
    cv2.waitKey(0)

    # Binarização com Otsu
    _, thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imshow(f"Imagem {i} - 5. Binarização (Otsu)", thresh)
    cv2.waitKey(0)

    # Fechamento morfológico (preenche pequenos buracos e une segmentos)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    cv2.imshow(f"Imagem {i} - 6. Fechamento Morfológico", closed)
    cv2.waitKey(0)

    # Erosão e Dilatação para refinar a forma (ANTES DO HOUGH)
    closed = cv2.erode(closed, None, iterations=2)
    closed = cv2.dilate(closed, None, iterations=2)
    cv2.imshow(f"Imagem {i} - 7. Erosão e Dilatação (Pré-Hough)", closed)
    cv2.waitKey(0)

    # Detectar linhas com Hough
    lines = cv2.HoughLinesP(closed, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)

    # Criar uma máscara preta e desenhar as linhas detectadas
    mask = np.zeros_like(gray)
    if lines is not None:
        for line in lines:
            # CORREÇÃO AQUI: Acessar o primeiro elemento do array 'line'
            x1, y1, x2, y2 = line[0]
            cv2.line(mask, (x1, y1), (x2, y2), 255, 3)
    cv2.imshow(f"Imagem {i} - 8. Máscara de Linhas (Hough)", mask)
    cv2.waitKey(0)

    # APLICANDO EROSÃO E DILATAÇÃO NA MÁSCARA DE LINHAS
    kernel_erode_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    mask_eroded = cv2.erode(mask, kernel_erode_dilate, iterations=1)
    cv2.imshow(f"Imagem {i} - 9. Máscara de Linhas (Erosão)", mask_eroded)
    cv2.waitKey(0)
    mask_dilated = cv2.dilate(mask_eroded, kernel_erode_dilate, iterations=1)
    cv2.imshow(f"Imagem {i} - 10. Máscara de Linhas (Erosão + Dilatação)", mask_dilated)
    cv2.waitKey(0)

    # Encontrar contornos na máscara de linhas modificada
    contours, _ = cv2.findContours(mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    image_with_detection = image_resized.copy() # Usar uma cópia para desenhar a detecção final

    if contours:
        # Escolher o maior contorno que provavelmente é o código de barras
        c = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        cv2.drawContours(image_with_detection, [box], -1, (0, 255, 0), 3)
        print(f"Código de barras detectado na imagem {i}!")
    else:
        print(f"Nenhum código de barras detectado na imagem {i}.")

    cv2.imshow(f"Imagem {i} - 11. Detecção Final", image_with_detection)
    cv2.waitKey(0)
    cv2.destroyAllWindows()