import cv2
import numpy as np
import os

# Número de imagens para processar
quantidade_imagens = 1 # Ajuste conforme o número de imagens na sua pasta
pasta = "imagens"

for i in range(1, quantidade_imagens + 1):
    caminho = f"{pasta}/{i}.jpg"
    image = cv2.imread(caminho)

    if image is None:
        print(f"[ERRO] Imagem {caminho} não encontrada.")
        continue

    # Redimensionar a imagem para facilitar o processamento
    image = cv2.resize(image, (800, 600))
    original_image = image.copy()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)
    blurred = cv2.GaussianBlur(enhanced_gray, (7, 7), 0)

    gradX = cv2.Sobel(blurred, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradX = cv2.convertScaleAbs(gradX)

    thresh = cv2.adaptiveThreshold(gradX, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 1)

    # --- PRINCIPAL AJUSTE AQUI: Reduzir o kernel do fechamento morfológico ---
    # Experimente com estes valores. (25, 3) é um bom ponto de partida, ou (30, 5).
    # Se ainda ficar tudo branco, reduza ainda mais.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3)) # AJUSTADO
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # --- AJUSTE AQUI: Reduzir as iterações de erosão/dilatação, ou remover se necessário ---
    # Tente 1 iteração. Se ainda ficar tudo branco, remova essas linhas temporariamente.
    closed = cv2.erode(closed, None, iterations=1) # AJUSTADO
    closed = cv2.dilate(closed, None, iterations=1) # AJUSTADO

    # Encontrar contornos
    contours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    found_barcode = False
    if contours:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for c in contours:
            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int8(box)

            width = rect[1][0]
            height = rect[1][1]

            if width < height:
                width, height = height, width

            area = cv2.contourArea(c)
            if area < 100:
                continue

            aspect_ratio = width / float(height)
            if aspect_ratio > 2 and aspect_ratio < 30:
                cv2.drawContours(original_image, [box], -1, (0, 255, 0), 3)
                found_barcode = True
                break
    
    if not found_barcode:
        print(f"Nenhum código de barras provável encontrado na imagem {i}.")

    # --- Visualizações das etapas intermediárias para depuração ---
    cv2.imshow("Original", original_image)
    cv2.imshow("Gray", gray)
    cv2.imshow("Enhanced Gray", enhanced_gray)
    cv2.imshow("Blurred", blurred)
    cv2.imshow("GradX", gradX)
    cv2.imshow("Thresh", thresh)
    cv2.imshow("Closed", closed) # Preste muita atenção a esta imagem

    cv2.imshow(f"Resultado Imagem {i}", original_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()