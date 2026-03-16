# app/interface.py
import tkinter as tk
from tkinter import ttk, messagebox

from whatsapp_sender import WhatsAppSender
from message_templates import gerar_mensagem_fallback

#  Paleta

COLORS = {
    "bg":            "#0F1923",
    "surface":       "#162330",
    "surface_alt":   "#1C2E3D",
    "border":        "#253545",
    "accent":        "#25D366",
    "accent_hover":  "#1DB954",
    "text_primary":  "#E8F0F7",
    "text_secondary":"#7A9BB5",
    "text_muted":    "#4A6275",
    "danger":        "#E05555",
    "sent_bg":       "#0D2418",
    "sent_fg":       "#25D366",
    "row_odd":       "#162330",
    "row_even":      "#1A2B3A",
    "select_bg":     "#1E3D52",
    "select_fg":     "#E8F0F7",
    "btn_cell_bg":   "#1C3A28",
    "btn_cell_fg":   "#25D366",
    "btn_cell_hov":  "#234D32",
}

FONT_LABEL  = ("Segoe UI", 9)
FONT_HEADER = ("Segoe UI", 8, "bold")
FONT_BTN    = ("Segoe UI", 8, "bold")
FONT_STATUS = ("Segoe UI", 8)

#  Classe principal

class InterfaceAgendamentos:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.whatsapp = WhatsAppSender()
        self.dados: list = []

        self._configure_root()
        self._apply_styles()
        self._build_ui()

    #  Configuração inicial

    def _configure_root(self) -> None:
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(720, 420)

    def _apply_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Custom.Treeview",
            background=COLORS["row_odd"],
            foreground=COLORS["text_primary"],
            fieldbackground=COLORS["row_odd"],
            rowheight=32,
            font=FONT_LABEL,
            borderwidth=0,
            relief="flat",
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=COLORS["surface"],
            foreground=COLORS["text_secondary"],
            font=FONT_HEADER,
            relief="flat",
            borderwidth=0,
            padding=(6, 9),
        )
        style.map(
            "Custom.Treeview",
            background=[("selected", COLORS["select_bg"])],
            foreground=[("selected", COLORS["select_fg"])],
        )
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", COLORS["surface_alt"])],
        )
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["surface"],
            troughcolor=COLORS["bg"],
            arrowcolor=COLORS["text_muted"],
            borderwidth=0,
        )

    #  Construção da UI

    def _build_ui(self) -> None:
        # Cabeçalho
        header = tk.Frame(self.root, bg=COLORS["bg"])
        header.pack(fill="x", padx=20, pady=(18, 6))

        tk.Label(
            header,
            text="Agendamentos",
            font=("Segoe UI", 13, "bold"),
            fg=COLORS["text_primary"],
            bg=COLORS["bg"],
        ).pack(side="left")

        self.counter_label = tk.Label(
            header, text="",
            font=("Segoe UI", 8, "bold"),
            fg=COLORS["accent"],
            bg=COLORS["surface_alt"],
            padx=10, pady=3,
        )
        # exibido apenas quando há dados

        # Separador
        tk.Frame(self.root, height=1, bg=COLORS["border"]).pack(
            fill="x", padx=20, pady=(4, 10)
        )

        # Tabela
        self._build_table()

        # Separador
        tk.Frame(self.root, height=1, bg=COLORS["border"]).pack(
            fill="x", padx=20, pady=(10, 8)
        )

        #  Barra de status
        status_bar = tk.Frame(self.root, bg=COLORS["bg"])
        status_bar.pack(fill="x", padx=20, pady=(0, 14))

        self.status_dot = tk.Label(
            status_bar, text="●",
            font=("Segoe UI", 8),
            fg=COLORS["text_muted"],
            bg=COLORS["bg"],
        )
        self.status_dot.pack(side="left")

        self.status_label = tk.Label(
            status_bar,
            text="Aguardando dados…",
            font=FONT_STATUS,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg"],
        )
        self.status_label.pack(side="left", padx=(4, 0))

    def _build_table(self) -> None:
        wrapper = tk.Frame(self.root, bg=COLORS["bg"])
        wrapper.pack(fill="both", expand=True, padx=20)

        columns = [
            ("protocolo",   "Protocolo",    100, "center"),
            ("cliente",     "Cliente",      200, "w"),
            ("telefone",    "Telefone",     120, "center"),
            ("agendamento", "Agendamento",  170, "center"),
            ("acao",        "WhatsApp",     120, "center"),
        ]

        self.tree = ttk.Treeview(
            wrapper,
            columns=[c[0] for c in columns],
            show="headings",
            height=18,
            style="Custom.Treeview",
        )

        for col_id, heading, width, anchor in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor=anchor, minwidth=60)

        self.tree.tag_configure("odd",   background=COLORS["row_odd"])
        self.tree.tag_configure("even",  background=COLORS["row_even"])
        self.tree.tag_configure("sent",  background=COLORS["sent_bg"],
                                          foreground=COLORS["sent_fg"])

        vsb = ttk.Scrollbar(wrapper, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        wrapper.rowconfigure(0, weight=1)
        wrapper.columnconfigure(0, weight=1)

        self.tree.bind("<Button-1>", self.on_click)
        self.tree.bind("<Motion>",   self._on_motion)

    #  Utilitários de UI

    def _set_status(self, text: str, color: str = None) -> None:
        self.status_label.config(text=text)
        self.status_dot.config(fg=color or COLORS["text_muted"])

    def _stripe_rows(self) -> None:
        for i, item in enumerate(self.tree.get_children()):
            tags = [t for t in self.tree.item(item, "tags") if t not in ("odd", "even")]
            tags.append("odd" if i % 2 == 0 else "even")
            self.tree.item(item, tags=tags)

    def _update_counter(self, n: int) -> None:
        if n:
            self.counter_label.config(text=f"{n} registro{'s' if n != 1 else ''}")
            self.counter_label.pack(side="left", padx=(10, 0))
        else:
            self.counter_label.pack_forget()

    def _on_motion(self, event: tk.Event) -> None:
        """Muda o cursor ao passar sobre a coluna de ação."""
        col  = self.tree.identify_column(event.x)
        row  = self.tree.identify_row(event.y)
        if col == "#5" and row:
            self.tree.configure(cursor="hand2")
        else:
            self.tree.configure(cursor="")

    #  MÉTODOS PRINCIPAIS  (nomenclatura preservada)

    def carregar_dados(self, lista: list) -> None:
        self.dados = lista
        self.tree.delete(*self.tree.get_children())

        for item in lista:
            self.tree.insert(
                "", "end",
                values=(
                    item["protocolo"],
                    item["cliente"],
                    item["telefone"],
                    item["agendamento"],
                    "Enviar 📩",
                ),
            )

        self._stripe_rows()
        self._update_counter(len(lista))
        self._set_status(
            f"{len(lista)} agendamento(s) carregado(s).",
            COLORS["accent"],
        )

    def on_click(self, event: tk.Event) -> None:
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        coluna = self.tree.identify_column(event.x)
        linha  = self.tree.identify_row(event.y)

        # Enviar WhatsApp está na coluna 5
        if coluna != "#5":
            return

        item = self.tree.item(linha, "values")
        protocolo, cliente, telefone, agendamento, _ = item

        if not messagebox.askyesno(
            "Enviar WhatsApp",
            f"Enviar mensagem de confirmação para {cliente}?",
        ):
            return

        mensagem = gerar_mensagem_fallback(
            cliente, agendamento, protocolo, "Endereço não informado"
        )

        try:
            self.whatsapp.abrir_whatsapp(telefone, mensagem)
            # Marca linha como enviada
            self.tree.item(linha, tags=("sent",))
            self._set_status(
                f"✓  Mensagem enviada para {cliente}.",
                COLORS["accent"],
            )
            messagebox.showinfo("Sucesso", f"Mensagem enviada para {cliente}.")
        except Exception as exc:
            self._set_status(f"Erro ao enviar para {cliente}.", COLORS["danger"])
            messagebox.showerror("Erro", f"Falha ao enviar mensagem:\n{exc}")
