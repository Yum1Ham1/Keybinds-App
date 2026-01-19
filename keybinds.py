import customtkinter as ctk
import keyboard
import threading
import winsound
import time
import json
import os
import webbrowser

# ================== CONFIG ==================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ================== VARIÁVEIS ==================
keybinds = {}
registered_hotkeys = {}
listening = False
placeholder_active = False
current_mode = "dark"
current_lang = "pt" # Idioma padrão

listener_key = "pause"
SAVE_DIR = "keybinds_data"
SAVE_FILE = os.path.join(SAVE_DIR, "keybinds.json")

# ================== DICIONÁRIO DE TRADUÇÃO ==================
translations = {
    "pt": {
        "title": "⌨ Sistema de Keybinds",
        "btn_theme": "🌗 Alternar Modo",
        "btn_capture": "🎯 Capturar tecla",
        "placeholder_capture": "🎯 Pressione uma tecla...",
        "placeholder_text": "Digite o texto para a tecla '{}' aqui...",
        "btn_add": "➕ Adicionar keybind",
        "lbl_list": "📌 Keybinds cadastradas",
        "btn_listen_on": "⏯ Ligar Listener ({})",
        "btn_listen_off": "⏯ Desligar Listener ({})",
        "btn_change_listener": "🎛 Alterar tecla Listener",
        "status_ready": "🟢 Pronto",
        "status_already_exists": "⚠ Tecla '{}' já cadastrada!",
        "status_captured": "Tecla capturada: {}",
        "status_editing": "✏ Editando '{}'",
        "status_deleted": "❌ '{}' deletada",
        "status_fill": "⚠ Preencha a tecla e o texto!",
        "status_listening_on": "▶ Listener LIGADO ({})",
        "status_listening_off": "⏸ Listener DESLIGADO ({})",
        "status_listener_set": "Listener agora em '{}'",
    },
    "en": {
        "title": "⌨ Keybinds System",
        "btn_theme": "🌗 Toggle Mode",
        "btn_capture": "🎯 Capture Key",
        "placeholder_capture": "🎯 Press a key...",
        "placeholder_text": "Type the text for key '{}' here...",
        "btn_add": "➕ Add keybind",
        "lbl_list": "📌 Registered Keybinds",
        "btn_listen_on": "⏯ Start Listener ({})",
        "btn_listen_off": "⏯ Stop Listener ({})",
        "btn_change_listener": "🎛 Change Listener Key",
        "status_ready": "🟢 Ready",
        "status_already_exists": "⚠ Key '{}' already exists!",
        "status_captured": "Key captured: {}",
        "status_editing": "✏ Editing '{}'",
        "status_deleted": "❌ '{}' deleted",
        "status_fill": "⚠ Fill both key and text!",
        "status_listening_on": "▶ Listener ON ({})",
        "status_listening_off": "⏸ Listener OFF ({})",
        "status_listener_set": "Listener set to '{}'",
    }
}

# ================== FUNÇÕES ==================
def toggle_language():
    global current_lang
    current_lang = "en" if current_lang == "pt" else "pt"
    update_ui_text()

def update_ui_text():
    lang = translations[current_lang]
    lbl_main_title.configure(text=lang["title"])
    btn_theme_toggle.configure(text=lang["btn_theme"])
    btn_cap.configure(text=lang["btn_capture"])
    btn_add_key.configure(text=lang["btn_add"])
    lbl_lista.configure(text=lang["lbl_list"])
    btn_change_listener.configure(text=lang["btn_change_listener"])
    
    # Atualiza botão do listener dependendo do estado
    l_key = listener_key.upper()
    if listening:
        btn_listener.configure(text=lang["btn_listen_off"].format(l_key))
        label_status.configure(text=lang["status_listening_on"].format(l_key))
    else:
        btn_listener.configure(text=lang["btn_listen_on"].format(l_key))
        label_status.configure(text=lang["status_ready"])

def beep_on(): winsound.Beep(1200,150)
def beep_off(): winsound.Beep(600,150)

def salvar_keybinds():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
    with open(SAVE_FILE,"w",encoding="utf-8") as f:
        json.dump(keybinds,f,ensure_ascii=False,indent=4)

def carregar_keybinds():
    global keybinds
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE,"r",encoding="utf-8") as f:
            keybinds = json.load(f)
        atualizar_lista()

# ================== CAPTURA ==================
def capturar_tecla():
    global placeholder_active
    lang = translations[current_lang]
    label_status.configure(text=lang["placeholder_capture"])
    time.sleep(0.2)
    evento = keyboard.read_event()
    while evento.event_type != keyboard.KEY_DOWN:
        evento = keyboard.read_event()

    tecla = evento.name
    if tecla in keybinds:
        label_status.configure(text=lang["status_already_exists"].format(tecla))
        return

    entry_tecla.configure(state="normal")
    entry_tecla.delete(0,"end")
    entry_tecla.insert(0,tecla)
    entry_tecla.configure(state="disabled")

    entry_texto.delete("1.0","end")
    entry_texto.insert("1.0", lang["placeholder_text"].format(tecla))
    placeholder_active = True
    label_status.configure(text=lang["status_captured"].format(tecla))

def clear_placeholder(event):
    global placeholder_active
    if placeholder_active:
        entry_texto.delete("1.0","end")
        placeholder_active = False

# ================== LISTA ==================
def atualizar_lista():
    for widget in lista_frame.winfo_children():
        widget.destroy()

    for tecla, texto in keybinds.items():
        item_frame = ctk.CTkFrame(
            lista_frame,
            fg_color="#111111" if current_mode=="dark" else "#dcdcdc",
            corner_radius=6
        )
        item_frame.pack(fill="x", pady=3, padx=5)

        ctk.CTkLabel(
            item_frame,
            text=f"{tecla} ➜ {texto}",
            anchor="w",
            text_color="#00bfff" if current_mode=="dark" else "#0077cc"
        ).pack(side="left", fill="x", expand=True, padx=8)

        ctk.CTkButton(
            item_frame,
            text="✏",
            width=30,
            command=lambda t=tecla: editar_keybind(t)
        ).pack(side="right", padx=3)

        ctk.CTkButton(
            item_frame,
            text="❌",
            width=30,
            fg_color="#ff5555",
            hover_color="#ff7777",
            command=lambda t=tecla: deletar_keybind(t)
        ).pack(side="right", padx=3)

def editar_keybind(tecla):
    lang = translations[current_lang]
    entry_tecla.configure(state="normal")
    entry_tecla.delete(0,"end")
    entry_tecla.insert(0,tecla)
    entry_tecla.configure(state="disabled")

    entry_texto.delete("1.0","end")
    entry_texto.insert("1.0", keybinds[tecla])

    del keybinds[tecla]
    atualizar_lista()
    label_status.configure(text=lang["status_editing"].format(tecla))

def deletar_keybind(tecla):
    lang = translations[current_lang]
    del keybinds[tecla]
    atualizar_lista()
    salvar_keybinds()
    label_status.configure(text=lang["status_deleted"].format(tecla))

def adicionar_keybind():
    lang = translations[current_lang]
    tecla = entry_tecla.get().strip()
    texto = entry_texto.get("1.0","end").strip()

    if not tecla or not texto:
        label_status.configure(text=lang["status_fill"])
        return

    keybinds[tecla] = texto
    entry_tecla.configure(state="normal")
    entry_tecla.delete(0,"end")
    entry_tecla.configure(state="disabled")
    entry_texto.delete("1.0","end")

    atualizar_lista()
    salvar_keybinds()
    label_status.configure(text=lang["status_ready"])

# ================== LISTENER ==================
def toggle_listener():
    global listening
    lang = translations[current_lang]
    l_key = listener_key.upper()
    if listening:
        for tecla, hotkey_id in registered_hotkeys.items():
            keyboard.remove_hotkey(hotkey_id)
        registered_hotkeys.clear()
        listening = False
        beep_off()
        btn_listener.configure(text=lang["btn_listen_on"].format(l_key))
        label_status.configure(text=lang["status_listening_off"].format(l_key))
    else:
        for tecla, texto in keybinds.items():
            hotkey_id = keyboard.add_hotkey(tecla, lambda t=texto: keyboard.write(t))
            registered_hotkeys[tecla] = hotkey_id
        listening = True
        beep_on()
        btn_listener.configure(text=lang["btn_listen_off"].format(l_key))
        label_status.configure(text=lang["status_listening_on"].format(l_key))

def definir_listener_key():
    global listener_key
    lang = translations[current_lang]
    label_status.configure(text=lang["placeholder_capture"])
    evento = keyboard.read_event()
    while evento.event_type != keyboard.KEY_DOWN:
        evento = keyboard.read_event()
    listener_key = evento.name
    label_status.configure(text=lang["status_listener_set"].format(listener_key.upper()))
    keyboard.clear_all_hotkeys()
    keyboard.add_hotkey(listener_key, toggle_listener)
    btn_listener.configure(text=lang["btn_listen_on"].format(listener_key.upper()) if not listening else lang["btn_listen_off"].format(listener_key.upper()))

# ================== TEMA ==================
def set_colors_by_mode(mode):
    global current_mode
    current_mode = mode

    bg = "#0a0a0a" if mode=="dark" else "#f0f0f0"
    entry_bg = "#2a2a2a" if mode=="dark" else "#d6d6d6"
    entry_text = "#ffffff" if mode=="dark" else "#000000"
    border = "#00bfff" if mode=="dark" else "#0077cc"

    frame.configure(fg_color=bg)
    lista_frame.configure(fg_color="#111111" if mode=="dark" else "#dcdcdc")

    entry_tecla.configure(
        fg_color=entry_bg,
        text_color=entry_text,
        border_color=border,
        border_width=2
    )
    entry_texto.configure(
        fg_color=entry_bg,
        text_color=entry_text,
        border_color=border,
        border_width=2
    )

    label_status.configure(text_color="#00ff99" if mode=="dark" else "#000000")
    lbl_lista.configure(text_color="#00bfff" if mode=="dark" else "#000000")

    footer_frame.configure(fg_color="#111111" if mode=="dark" else "#e0e0e0")
    lbl_credit.configure(text_color="#00bfff" if mode=="dark" else "#0055aa")
    lbl_version.configure(text_color="#aaaaaa" if mode=="dark" else "#444444")
    btn_github.configure(border_color=border, text_color=border)
    btn_linkedin.configure(border_color=border, text_color=border)
    btn_listener.configure(fg_color="#0066cc")
    btn_change_listener.configure(fg_color="#00bfff")

def toggle_theme():
    set_colors_by_mode("light" if current_mode=="dark" else "dark")

# ================== INTERFACE ==================
app = ctk.CTk()
app.title("Keybinds de Texto")
app.geometry("650x820")
app.resizable(False, False)

frame = ctk.CTkFrame(app, corner_radius=12)
frame.pack(padx=20, pady=20, fill="both", expand=True)

top_frame = ctk.CTkFrame(frame)
top_frame.pack(fill="x", pady=(0,15))

lbl_main_title = ctk.CTkLabel(
    top_frame,
    text="⌨ Sistema de Keybinds",
    font=("Segoe UI",24,"bold"),
    text_color="#00bfff"
)
lbl_main_title.pack(side="left", padx=15)

# Botões de Controle (Tema e Idioma)
control_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
control_frame.pack(side="right", padx=15)

btn_theme_toggle = ctk.CTkButton(
    control_frame,
    text="🌗 Alternar Modo",
    command=toggle_theme,
    width=120
)
btn_theme_toggle.pack(side="top", pady=2)

btn_lang_toggle = ctk.CTkButton(
    control_frame,
    text="🌐 PT / EN",
    command=toggle_language,
    width=120,
    fg_color="#555555"
)
btn_lang_toggle.pack(side="top", pady=2)

entry_tecla = ctk.CTkEntry(frame, state="disabled", height=35)
entry_tecla.pack(fill="x", pady=6)

btn_cap = ctk.CTkButton(frame, text="🎯 Capturar tecla", command=capturar_tecla)
btn_cap.pack(pady=6)

entry_texto = ctk.CTkTextbox(frame, height=100)
entry_texto.pack(fill="x", pady=6)
entry_texto.bind("<FocusIn>", clear_placeholder)

btn_add_key = ctk.CTkButton(frame, text="➕ Adicionar keybind", command=adicionar_keybind)
btn_add_key.pack(pady=8)

lbl_lista = ctk.CTkLabel(frame, text="📌 Keybinds cadastradas")
lbl_lista.pack(pady=(15,5))

lista_frame = ctk.CTkScrollableFrame(frame, height=200)
lista_frame.pack(fill="x")

# ================== LISTENER ==================
listener_frame = ctk.CTkFrame(frame, fg_color="transparent")
listener_frame.pack(pady=5, fill="x")

btn_listener = ctk.CTkButton(
    listener_frame,
    text=f"⏯ Ligar Listener ({listener_key.upper()})",
    command=toggle_listener,
    fg_color="#0066cc",
    corner_radius=8,
    height=40,
    width=300
)
btn_listener.pack(side="left", padx=(0,10))

btn_change_listener = ctk.CTkButton(
    listener_frame,
    text="🎛 Alterar tecla Listener",
    command=definir_listener_key,
    fg_color="#00bfff",
    corner_radius=8,
    height=40,
    width=300
)
btn_change_listener.pack(side="left")

# ================== STATUS ==================
label_status = ctk.CTkLabel(frame, text="🟢 Pronto")
label_status.pack(pady=5)

# ================== FOOTER ==================
footer_frame = ctk.CTkFrame(app, corner_radius=12, height=70)
footer_frame.pack(side="bottom", fill="x", padx=15, pady=10)

lbl_credit = ctk.CTkLabel(
    footer_frame,
    text="© 2026 • Thiago Pucinelli Aires da Silva",
    font=("Segoe UI", 12, "bold")
)
lbl_credit.pack(side="left", padx=15, pady=15)

lbl_version = ctk.CTkLabel(
    footer_frame,
    text="Keybinds App • v1.0",
    font=("Segoe UI", 11)
)
lbl_version.pack(side="left", padx=15, pady=15)

def abrir_github():
    webbrowser.open("https://github.com/TheThiagoPucinelli")

def abrir_linkedin():
    webbrowser.open("https://www.linkedin.com/in/thiagopucinelli/")

btn_github = ctk.CTkButton(
    footer_frame,
    text="GitHub",
    width=110,
    border_width=1,
    fg_color="transparent",
    command=abrir_github
)
btn_github.pack(side="right", padx=5, pady=15)

btn_linkedin = ctk.CTkButton(
    footer_frame,
    text="LinkedIn",
    width=110,
    border_width=1,
    fg_color="transparent",
    command=abrir_linkedin
)
btn_linkedin.pack(side="right", padx=5, pady=15)

# ================== START ==================
set_colors_by_mode(current_mode)
carregar_keybinds()
keyboard.add_hotkey(listener_key, toggle_listener)
app.mainloop()