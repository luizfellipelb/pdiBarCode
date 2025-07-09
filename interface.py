import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# --- Configurações ---
PASTA_IMAGENS = "imagens"
QUANTIDADE_MAX_IMAGENS = 90  # Limite máximo de imagens a serem carregadas
TAMANHO_MINIATURA = (100, 100)
IMAGENS_POR_PAGINA = 20  # Número de miniaturas por página
ATRASO_EXIBICAO_PASSO_A_PASSO_MS = 500  # Atraso em milissegundos entre cada etapa

# --- Função de Processamento de Imagem (Seu Código Adaptado) ---
def processar_e_exibir_passos(caminho_imagem, nome_arquivo):
    image = cv2.imread(caminho_imagem)

    if image is None:
        print(f"[ERRO] Imagem {caminho_imagem} não encontrada.")
        return

    print(f"\nProcessando Imagem: {nome_arquivo}...")

    # Cria uma nova janela para exibir os passos
    passos_window = tk.Toplevel()
    passos_window.title(f"Passo a Passo: {nome_arquivo}")
    passos_window.geometry("800x700")  # Tamanho maior para melhor visualização
    
    # Frame principal
    main_frame = tk.Frame(passos_window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Canvas para a imagem
    canvas = tk.Canvas(main_frame, bg='white')
    canvas.pack(fill=tk.BOTH, expand=True)

    # Frame para controles
    controls_frame = tk.Frame(main_frame)
    controls_frame.pack(fill=tk.X, pady=(10, 0))

    # Texto descritivo
    text_label = tk.Label(main_frame, text="", font=("Arial", 12), wraplength=700)
    text_label.pack(pady=(10, 0))

    # Variáveis para controle dos passos
    current_step = 0
    photo_image_tk = None
    list_of_steps = []

    def update_image_on_canvas(cv_image, title_text):
        nonlocal photo_image_tk
        img_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB) if len(cv_image.shape) == 3 else cv2.cvtColor(cv_image, cv2.COLOR_GRAY2RGB)
        img_pil = Image.fromarray(img_rgb)
        
        # Redimensiona mantendo a proporção
        canvas_width = canvas.winfo_width() - 20
        canvas_height = canvas.winfo_height() - 20
        
        img_ratio = img_pil.width / img_pil.height
        canvas_ratio = canvas_width / canvas_height
        
        if canvas_ratio > img_ratio:
            new_height = canvas_height
            new_width = int(new_height * img_ratio)
        else:
            new_width = canvas_width
            new_height = int(new_width / img_ratio)
            
        img_pil = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        photo_image_tk = ImageTk.PhotoImage(image=img_pil)
        canvas.delete("all")
        canvas.create_image(canvas.winfo_width()/2, canvas.winfo_height()/2, image=photo_image_tk, anchor=tk.CENTER)
        text_label.config(text=title_text)
        passos_window.update_idletasks()

    def show_step(step_index):
        nonlocal current_step
        if 0 <= step_index < len(list_of_steps):
            current_step = step_index
            step = list_of_steps[current_step]
            
            # Converte para BGR se a imagem estiver em escala de cinza para exibição
            if len(step["image"].shape) == 2:
                display_image = cv2.cvtColor(step["image"], cv2.COLOR_GRAY2BGR)
            else:
                display_image = step["image"]
                
            update_image_on_canvas(display_image, step["title"])
            
            # Atualiza estado dos botões
            btn_prev.config(state=tk.NORMAL if current_step > 0 else tk.DISABLED)
            btn_next.config(state=tk.NORMAL if current_step < len(list_of_steps) - 1 else tk.DISABLED)
            step_label.config(text=f"Passo {current_step + 1} de {len(list_of_steps)}")

    def next_step():
        show_step(current_step + 1)

    def prev_step():
        show_step(current_step - 1)

    def auto_play():
        if auto_play_running.get():
            if current_step < len(list_of_steps) - 1:
                next_step()
                passos_window.after(ATRASO_EXIBICAO_PASSO_A_PASSO_MS, auto_play)
            else:
                auto_play_running.set(False)
                btn_auto.config(text="Auto Play")

    def toggle_auto_play():
        if auto_play_running.get():
            auto_play_running.set(False)
            btn_auto.config(text="Auto Play")
        else:
            auto_play_running.set(True)
            btn_auto.config(text="Parar")
            auto_play()

    # Botões de navegação
    nav_frame = tk.Frame(controls_frame)
    nav_frame.pack(side=tk.LEFT, padx=5)

    btn_prev = tk.Button(nav_frame, text="← Anterior", command=prev_step, state=tk.DISABLED)
    btn_prev.pack(side=tk.LEFT, padx=2)

    step_label = tk.Label(nav_frame, text="Passo 0 de 0", width=15)
    step_label.pack(side=tk.LEFT, padx=2)

    btn_next = tk.Button(nav_frame, text="Próximo →", command=next_step, state=tk.DISABLED)
    btn_next.pack(side=tk.LEFT, padx=2)

    # Botão Auto Play
    auto_play_frame = tk.Frame(controls_frame)
    auto_play_frame.pack(side=tk.LEFT, padx=20)

    auto_play_running = tk.BooleanVar(value=False)
    btn_auto = tk.Button(auto_play_frame, text="Auto Play", command=toggle_auto_play)
    btn_auto.pack(side=tk.LEFT)

    # Botão Fechar
    btn_close = tk.Button(controls_frame, text="Fechar", command=passos_window.destroy)
    btn_close.pack(side=tk.RIGHT, padx=5)

    # Processamento da imagem (mesmo que antes)
    list_of_steps = []

    # 1. Redimensiona para facilitar o processamento
    image_resized = cv2.resize(image.copy(), (600, 400))
    list_of_steps.append({"image": image_resized, "title": "1. Original Redimensionada"})

    # 2. Converte para escala de cinza
    gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
    list_of_steps.append({"image": gray, "title": "2. Escala de Cinza"})

    # 3. Aplica desfoque Gaussiano
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)
    list_of_steps.append({"image": blurred, "title": "3. Desfoque Gaussiano"})

    # 4. Calcula o gradiente horizontal (destaca linhas verticais)
    gradX = cv2.Sobel(blurred, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=3)
    gradX = cv2.convertScaleAbs(gradX)
    list_of_steps.append({"image": gradX, "title": "4. Gradiente X (Sobel)"})

    # 5. Binarização com Otsu
    _, thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    list_of_steps.append({"image": thresh, "title": "5. Binarização (Otsu)"})

    # 6. Fechamento morfológico (preenche pequenos buracos e une segmentos)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 3))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    list_of_steps.append({"image": closed, "title": "6. Fechamento Morfológico"})

    # 7. Erosão e Dilatação para refinar a forma (ANTES DO HOUGH)
    closed = cv2.erode(closed, None, iterations=2)
    closed = cv2.dilate(closed, None, iterations=2)
    list_of_steps.append({"image": closed, "title": "7. Erosão e Dilatação (Pré-Hough)"})

    # 8. Detectar linhas com Hough
    lines = cv2.HoughLinesP(closed, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=10)
    mask = np.zeros_like(gray)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(mask, (x1, y1), (x2, y2), 255, 3)
    list_of_steps.append({"image": mask, "title": "8. Máscara de Linhas (Hough)"})

    # 9. Aplicando Erosão na máscara de linhas
    kernel_erode_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
    mask_eroded = cv2.erode(mask, kernel_erode_dilate, iterations=1)
    list_of_steps.append({"image": mask_eroded, "title": "9. Máscara de Linhas (Erosão)"})

    # 10. Aplicando Dilatação na máscara de linhas
    mask_dilated = cv2.dilate(mask_eroded, kernel_erode_dilate, iterations=1)
    list_of_steps.append({"image": mask_dilated, "title": "10. Máscara de Linhas (Erosão + Dilatação)"})

    # 11. Encontrar contornos e detecção final
    contours, _ = cv2.findContours(mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image_with_detection = image_resized.copy()

    if contours:
        c = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.intp(box)
        cv2.drawContours(image_with_detection, [box], -1, (0, 255, 0), 3)
        print(f"Código de barras detectado na imagem {nome_arquivo}!")
    else:
        print(f"Nenhum código de barras detectado na imagem {nome_arquivo}.")
    list_of_steps.append({"image": image_with_detection, "title": "11. Detecção Final"})

    # Mostra o primeiro passo
    show_step(0)

    # Configura o redimensionamento responsivo
    def on_canvas_resize(event):
        if list_of_steps and current_step < len(list_of_steps):
            show_step(current_step)

    canvas.bind("<Configure>", on_canvas_resize)

    passos_window.protocol("WM_DELETE_WINDOW", passos_window.destroy)
    passos_window.mainloop()

# --- Configuração da Interface Gráfica Principal Aprimorada ---
def iniciar_interface():
    root = tk.Tk()
    root.title("Selecione uma Imagem para Detecção de Código de Barras")
    root.geometry("800x600")

    # Frame principal
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Título
    title_label = tk.Label(main_frame, text="Selecione uma Imagem", font=("Arial", 14, "bold"))
    title_label.pack(pady=(0, 10))

    # Frame para miniaturas com barra de rolagem
    canvas_frame = tk.Frame(main_frame)
    canvas_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(canvas_frame)
    scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Controles de página
    controls_frame = tk.Frame(main_frame)
    controls_frame.pack(fill=tk.X, pady=(10, 0))

    current_page = tk.IntVar(value=0)
    total_pages = tk.IntVar(value=0)

    def update_page_display():
        page_info = f"Página {current_page.get() + 1} de {total_pages.get()}"
        page_label.config(text=page_info)

    def show_page(page_num):
        # Limpa o frame de miniaturas
        for widget in scrollable_frame.winfo_children():
            widget.destroy()

        # Calcula o intervalo de imagens a mostrar
        start_idx = page_num * IMAGENS_POR_PAGINA
        end_idx = min(start_idx + IMAGENS_POR_PAGINA, len(imagens_carregadas))

        # Organiza as miniaturas em um grid
        num_colunas = 5
        for idx in range(start_idx, end_idx):
            caminho, img_tk, nome_arquivo = imagens_carregadas[idx]
            row = (idx - start_idx) // num_colunas
            col = (idx - start_idx) % num_colunas

            # Frame para cada miniatura
            thumb_frame = tk.Frame(scrollable_frame, padx=5, pady=5)
            thumb_frame.grid(row=row, column=col, padx=5, pady=5)

            # Botão com a miniatura
            btn = tk.Button(thumb_frame, image=img_tk,
                           command=lambda p=caminho, n=nome_arquivo: processar_e_exibir_passos(p, n))
            btn.image = img_tk  # Mantém uma referência para a imagem
            btn.pack()

            # Label com o nome do arquivo
            lbl = tk.Label(thumb_frame, text=nome_arquivo)
            lbl.pack()

        # Atualiza controles de navegação
        current_page.set(page_num)
        update_page_display()
        btn_prev_page.config(state=tk.NORMAL if page_num > 0 else tk.DISABLED)
        btn_next_page.config(state=tk.NORMAL if page_num < total_pages.get() - 1 else tk.DISABLED)

    def next_page():
        if current_page.get() < total_pages.get() - 1:
            show_page(current_page.get() + 1)

    def prev_page():
        if current_page.get() > 0:
            show_page(current_page.get() - 1)

    # Botões de navegação de página
    btn_prev_page = tk.Button(controls_frame, text="← Página Anterior", command=prev_page, state=tk.DISABLED)
    btn_prev_page.pack(side=tk.LEFT, padx=5)

    page_label = tk.Label(controls_frame, text="Página 0 de 0")
    page_label.pack(side=tk.LEFT, padx=10)

    btn_next_page = tk.Button(controls_frame, text="Próxima Página →", command=next_page, state=tk.DISABLED)
    btn_next_page.pack(side=tk.LEFT, padx=5)

    # Carrega as miniaturas das imagens
    imagens_carregadas = []
    for i in range(1, QUANTIDADE_MAX_IMAGENS + 1):
        caminho = os.path.join(PASTA_IMAGENS, f"{i}.jpg")
        if os.path.exists(caminho):
            try:
                img_pil = Image.open(caminho)
                img_pil.thumbnail(TAMANHO_MINIATURA, Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img_pil)
                imagens_carregadas.append((caminho, img_tk, f"{i}.jpg"))
            except Exception as e:
                print(f"[AVISO] Não foi possível carregar a imagem {caminho}: {e}")
        else:
            print(f"[AVISO] Imagem {caminho} não encontrada. Ignorando.")

    if not imagens_carregadas:
        tk.Label(scrollable_frame, text="Nenhuma imagem encontrada na pasta 'imagens'.").pack()
        root.mainloop()
        return

    # Calcula o número total de páginas
    total_pages.set((len(imagens_carregadas) + IMAGENS_POR_PAGINA - 1) // IMAGENS_POR_PAGINA)
    update_page_display()

    # Mostra a primeira página
    show_page(0)

    # Configura o redimensionamento responsivo
    def on_window_resize(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    root.bind("<Configure>", on_window_resize)

    root.mainloop()

# --- Inicia a aplicação ---
if __name__ == "__main__":
    iniciar_interface()