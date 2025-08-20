import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import qrcode

# ---------- Estado global ----------
qr_preview = None
cor_qr = "black"
cor_fundo = "white"

# ---------- Utilitários ----------
def get_font(size: int):
    """Tenta carregar uma fonte TrueType para suportar acentos; cai no default se não achar."""
    caminhos = [
        r"C:\Windows\Fonts\arial.ttf",                         # Windows
        r"C:\Windows\Fonts\ARIAL.TTF",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",     # Linux
        "/System/Library/Fonts/Supplemental/Arial.ttf",        # macOS
    ]
    for p in caminhos:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def escolher_cor(tipo):
    global cor_qr, cor_fundo
    cor = colorchooser.askcolor()[1]
    if cor:
        if tipo == "qr":
            cor_qr = cor
            btn_cor_qr.config(bg=cor)
        else:
            cor_fundo = cor
            btn_cor_fundo.config(bg=cor)

def add_legenda(img: Image.Image, texto: str, fonte: ImageFont.ImageFont, cor_texto: str, cor_fundo_img: str):
    """Adiciona uma legenda centralizada abaixo da imagem, ajustando a altura conforme o texto."""
    if not texto:
        return img

    draw_tmp = ImageDraw.Draw(img)
    # Usa textbbox (substitui textsize nas versões novas do Pillow)
    bbox = draw_tmp.textbbox((0, 0), texto, font=fonte)
    w_texto = bbox[2] - bbox[0]
    h_texto = bbox[3] - bbox[1]

    margem_vertical = 12
    largura, altura = img.size
    altura_extra = h_texto + margem_vertical * 2

    nova = Image.new("RGB", (largura, altura + altura_extra), color=cor_fundo_img)
    nova.paste(img, (0, 0))

    draw = ImageDraw.Draw(nova)
    x = (largura - w_texto) // 2
    y = altura + margem_vertical
    draw.text((x, y), texto, fill=cor_texto, font=fonte)

    return nova

def redimensionar_preview(img: Image.Image, max_dim=250):
    """Redimensiona proporcionalmente para caber no preview."""
    w, h = img.size
    escala = min(max_dim / w, max_dim / h)
    new_size = (max(1, int(w * escala)), max(1, int(h * escala)))
    return img.resize(new_size, Image.LANCZOS)

# ---------- Core ----------
def gerar_qrcode_preview(texto):
    """Gera o QR, aplica legenda (se houver) e mostra preview."""
    global qr_preview, cor_qr, cor_fundo

    if not texto.strip():
        messagebox.showwarning("Aviso", "Digite algum valor para gerar o QR Code!")
        return None

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=2,
    )
    qr.add_data(texto)
    qr.make(fit=True)

    img = qr.make_image(fill_color=cor_qr, back_color=cor_fundo).convert("RGB")

    legenda = entrada_legenda.get().strip()
    fonte = get_font(16)  # tamanho confortável para legenda
    if legenda:
        img = add_legenda(img, legenda, fonte, cor_qr, cor_fundo)

    # Preview proporcional
    preview_img = redimensionar_preview(img, max_dim=250)
    qr_preview = ImageTk.PhotoImage(preview_img)
    preview_label.config(image=qr_preview)
    preview_label.image = qr_preview

    return img  # retorna a imagem original para salvar

def salvar_qrcode(img):
    if img is None:
        return
    caminho = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("Imagem PNG", "*.png")],
        title="Salvar QR Code"
    )
    if caminho:
        img.save(caminho)
        messagebox.showinfo("Sucesso", f"QR Code salvo em:\n{caminho}")

def gerar():
    """Monta o conteúdo conforme tipo selecionado e gera/salva."""
    tipo = combo_tipo.get()

    if tipo in ["Link", "Telefone", "WhatsApp", "E-mail", "Texto livre"]:
        valor = entrada_valor.get().strip()
        if not valor:
            messagebox.showwarning("Aviso", "Digite um valor!")
            return

        if tipo == "Link":
            conteudo = valor
        elif tipo == "Telefone":
            conteudo = f"tel:{valor}"
        elif tipo == "WhatsApp":
            conteudo = f"https://wa.me/{valor}"
        elif tipo == "E-mail":
            conteudo = f"mailto:{valor}"
        else:  # Texto livre
            conteudo = valor

    elif tipo == "Wi-Fi":
        ssid = entrada_ssid.get().strip()
        senha = entrada_senha.get().strip()
        cript = combo_crypto.get()
        if not ssid:
            messagebox.showwarning("Aviso", "Digite o SSID da rede Wi-Fi!")
            return
        # Formato padrão WiFi QR: WIFI:T:<WPA|WEP|nopass>;S:<SSID>;P:<password>;;
        conteudo = f"WIFI:T:{cript};S:{ssid};P:{senha};;"

    elif tipo == "Localização":
        lat = entrada_lat.get().strip()
        lon = entrada_lon.get().strip()
        if not lat or not lon:
            messagebox.showwarning("Aviso", "Digite latitude e longitude!")
            return
        conteudo = f"geo:{lat},{lon}"

    else:
        messagebox.showerror("Erro", "Tipo não reconhecido!")
        return

    img = gerar_qrcode_preview(conteudo)
    if img:
        salvar_qrcode(img)

# ---------- UI ----------
janela = tk.Tk()
janela.title("Gerador de QR Codes")
janela.geometry("520x840")
janela.resizable(False, False)

titulo = tk.Label(janela, text="Gerador de QR Codes", font=("Arial", 16, "bold"))
titulo.pack(pady=10)

# Seleção do tipo
frame_tipo = tk.Frame(janela)
frame_tipo.pack(pady=10)

tk.Label(frame_tipo, text="Tipo de QR Code:").grid(row=0, column=0, padx=5)
combo_tipo = ttk.Combobox(
    frame_tipo,
    values=["Link", "Telefone", "WhatsApp", "E-mail", "Texto livre", "Wi-Fi", "Localização"],
    state="readonly",
    width=22
)
combo_tipo.current(0)
combo_tipo.grid(row=0, column=1, padx=5)

# Frame dinâmico
frame_dinamico = tk.Frame(janela)
frame_dinamico.pack(pady=10)

def atualizar_campos(event=None):
    for w in frame_dinamico.winfo_children():
        w.destroy()
    tipo = combo_tipo.get()

    if tipo in ["Link", "Telefone", "WhatsApp", "E-mail", "Texto livre"]:
        tk.Label(frame_dinamico, text="Digite o valor:").pack(anchor="w")
        global entrada_valor
        entrada_valor = tk.Entry(frame_dinamico, width=52)
        entrada_valor.pack()

    elif tipo == "Wi-Fi":
        tk.Label(frame_dinamico, text="SSID:").pack(anchor="w")
        global entrada_ssid
        entrada_ssid = tk.Entry(frame_dinamico, width=40)
        entrada_ssid.pack()

        tk.Label(frame_dinamico, text="Senha:").pack(anchor="w")
        global entrada_senha
        entrada_senha = tk.Entry(frame_dinamico, width=40, show="*")
        entrada_senha.pack()

        tk.Label(frame_dinamico, text="Criptografia:").pack(anchor="w")
        global combo_crypto
        combo_crypto = ttk.Combobox(frame_dinamico, values=["WPA", "WEP", "nopass"], state="readonly", width=10)
        combo_crypto.current(0)
        combo_crypto.pack()

    elif tipo == "Localização":
        tk.Label(frame_dinamico, text="Latitude:").pack(anchor="w")
        global entrada_lat
        entrada_lat = tk.Entry(frame_dinamico, width=20)
        entrada_lat.pack()

        tk.Label(frame_dinamico, text="Longitude:").pack(anchor="w")
        global entrada_lon
        entrada_lon = tk.Entry(frame_dinamico, width=20)
        entrada_lon.pack()

combo_tipo.bind("<<ComboboxSelected>>", atualizar_campos)
atualizar_campos()

# Personalização
frame_custom = tk.LabelFrame(janela, text="Personalização", padx=10, pady=10)
frame_custom.pack(pady=10, fill="x")

btn_cor_qr = tk.Button(frame_custom, text="Cor do QR", command=lambda: escolher_cor("qr"), bg=cor_qr, fg="white")
btn_cor_qr.pack(side="left", padx=10)

btn_cor_fundo = tk.Button(frame_custom, text="Cor de Fundo", command=lambda: escolher_cor("fundo"), bg=cor_fundo, fg="black")
btn_cor_fundo.pack(side="left", padx=10)

tk.Label(frame_custom, text="Frase abaixo:").pack(side="left", padx=6)
entrada_legenda = tk.Entry(frame_custom, width=24)
entrada_legenda.pack(side="left", padx=6)

# Botão gerar
btn_gerar = tk.Button(janela, text="Gerar QR Code", command=gerar, bg="#4CAF50", fg="white", width=22)
btn_gerar.pack(pady=10)

# Preview
label_preview = tk.Label(janela, text="Pré-visualização:")
label_preview.pack(pady=5)
preview_label = tk.Label(janela, bg="white", width=260, height=260)
preview_label.pack(pady=10)

janela.mainloop()