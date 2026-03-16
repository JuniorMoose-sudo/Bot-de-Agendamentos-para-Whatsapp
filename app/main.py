import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

from planilha_manager import PlanilhaManager
from service import BotService


#  Paleta e constantes visuais

COLORS = {
    "bg":           "#0F1923",
    "surface":      "#162330",
    "surface_alt":  "#1C2E3D",
    "border":       "#253545",
    "accent":       "#25D366",
    "accent_hover": "#1DB954",
    "accent_dark":  "#128C4A",
    "text_primary": "#E8F0F7",
    "text_secondary":"#7A9BB5",
    "text_muted":   "#4A6275",
    "danger":       "#E05555",
    "sent_bg":      "#0D2418",
    "sent_fg":      "#25D366",
    "row_odd":      "#162330",
    "row_even":     "#1A2B3A",
    "select_bg":    "#1E3D52",
    "select_fg":    "#E8F0F7",
}

FONT_TITLE   = ("Segoe UI", 15, "bold")
FONT_SUB     = ("Segoe UI", 10)
FONT_LABEL   = ("Segoe UI", 9)
FONT_MONO    = ("Consolas", 9)
FONT_BTN     = ("Segoe UI", 9, "bold")
FONT_STATUS  = ("Segoe UI", 8)

#  Helpers de estilo

def _style_button(btn: tk.Button, variant: str = "primary") -> None:
    """Aplica estilo e hover a um tk.Button."""
    if variant == "primary":
        bg, fg, hov = COLORS["accent"], "#0F1923", COLORS["accent_hover"]
    elif variant == "secondary":
        bg, fg, hov = COLORS["surface_alt"], COLORS["text_primary"], COLORS["border"]
    else:
        bg, fg, hov = COLORS["danger"], "#ffffff", "#c04040"

    btn.configure(
        bg=bg, fg=fg, activebackground=hov, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2",
        font=FONT_BTN, padx=14, pady=7,
    )
    btn.bind("<Enter>", lambda _: btn.configure(bg=hov))
    btn.bind("<Leave>", lambda _: btn.configure(bg=bg))


def _separator(parent, **kw) -> tk.Frame:
    return tk.Frame(parent, height=1, bg=COLORS["border"], **kw)

#  Classe principal

class App:
    """ Aplicação principal do bot de agendamento via WhatsApp"""
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._configure_root()

        self.planilha_manager = PlanilhaManager()
        self.service           = BotService()
        self.arquivo_atual     = None

        self._build_ui()
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

    #  Configuração da janela raiz

    def _configure_root(self) -> None:
        self.root.title("WhatsApp Bot — Confirmação de Agendamentos")
        self.root.geometry("1060x680")
        self.root.resizable(True, True)
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(800, 520)

        # Ícone embutido (fallback silencioso)
        try:
            self.root.iconbitmap(default="icon.ico")
        except Exception:
            pass


    #  Construção da interface

    def _build_ui(self) -> None:
        self._build_sidebar()
        self._build_main_panel()

    # Painel lateral esquerdo

    def _build_sidebar(self) -> None:
        """ Constrói a barra lateral com opções de arquivo e data, além de informações de status. """
        sidebar = tk.Frame(self.root, bg=COLORS["surface"], width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo / marca
        logo_frame = tk.Frame(sidebar, bg=COLORS["surface"])
        logo_frame.pack(fill="x", padx=20, pady=(28, 10))

        tk.Label(
            logo_frame, text="●", font=("Segoe UI", 22),
            fg=COLORS["accent"], bg=COLORS["surface"]
        ).pack(side="left")

        tk.Label(
            logo_frame, text=" WA Bot",
            font=("Segoe UI", 14, "bold"),
            fg=COLORS["text_primary"], bg=COLORS["surface"]
        ).pack(side="left")

        _separator(sidebar).pack(fill="x", padx=16, pady=(8, 20))

        # Seção: arquivo
        self._sidebar_section(sidebar, "PLANILHA")

        self.btn_selecionar = tk.Button(
            sidebar, text="  📁  Selecionar Arquivo",
            anchor="w", command=self.selecionar_e_carregar_datas
        )
        _style_button(self.btn_selecionar, "secondary")
        self.btn_selecionar.configure(font=("Segoe UI", 9), padx=12, pady=8)
        self.btn_selecionar.pack(fill="x", padx=16, pady=(0, 8))

        self.file_label = tk.Label(
            sidebar, text="Nenhum arquivo",
            font=("Segoe UI", 8), fg=COLORS["text_muted"],
            bg=COLORS["surface"], wraplength=180, justify="left"
        )
        self.file_label.pack(fill="x", padx=16, pady=(0, 16))

        _separator(sidebar).pack(fill="x", padx=16, pady=(0, 16))

        # Seção: data
        self._sidebar_section(sidebar, "DATA DO AGENDAMENTO")

        self.date_combo = ttk.Combobox(sidebar, state="disabled", font=FONT_LABEL)
        self.date_combo.pack(fill="x", padx=16, pady=(0, 10))

        self.btn_carregar = tk.Button(
            sidebar, text="  📂  Carregar Agendamentos",
            anchor="w", command=self.carregar_agendamentos_por_data
        )
        _style_button(self.btn_carregar, "primary")
        self.btn_carregar.configure(font=("Segoe UI", 9), padx=12, pady=8)
        self.btn_carregar.pack(fill="x", padx=16, pady=(0, 8))

        # Espaço flexível
        tk.Frame(sidebar, bg=COLORS["surface"]).pack(fill="both", expand=True)

        # Rodapé
        _separator(sidebar).pack(fill="x", padx=16, pady=8)
        tk.Label(
            sidebar, text="v1.0  •  WhatsApp Bot Local",
            font=("Segoe UI", 7), fg=COLORS["text_muted"],
            bg=COLORS["surface"]
        ).pack(pady=(0, 12))

    def _sidebar_section(self, parent, title: str) -> None:
        tk.Label(
            parent, text=title,
            font=("Segoe UI", 7, "bold"),
            fg=COLORS["text_muted"], bg=COLORS["surface"]
        ).pack(anchor="w", padx=16, pady=(0, 6))

    # Painel principal direito

    def _build_main_panel(self) -> None:
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(side="left", fill="both", expand=True)

        # Cabeçalho
        header = tk.Frame(main, bg=COLORS["bg"])
        header.pack(fill="x", padx=28, pady=(24, 0))

        self.subtitle_label = tk.Label(
            header,
            text="Selecione uma planilha para começar",
            font=("Segoe UI", 13, "bold"),
            fg=COLORS["text_primary"], bg=COLORS["bg"]
        )
        self.subtitle_label.pack(side="left")

        self.counter_badge = tk.Label(
            header, text="",
            font=("Segoe UI", 8, "bold"),
            fg=COLORS["accent"], bg=COLORS["surface_alt"],
            padx=10, pady=3
        )
        # exibido apenas quando há dados

        _separator(main).pack(fill="x", padx=28, pady=14)

        # Tabela
        self._build_table(main)

        _separator(main).pack(fill="x", padx=28, pady=12)

        # Barra de ação + status
        self._build_action_bar(main)

    def _build_table(self, parent) -> None:
        table_outer = tk.Frame(parent, bg=COLORS["bg"])
        table_outer.pack(fill="both", expand=True, padx=28)

        # Cabeçalho de colunas customizado
        columns = [
            ("protocolo",  "Protocolo",    95,  "center"),
            ("nome",       "Cliente",      200, "w"),
            ("telefone",   "Telefone",     130, "center"),
            ("endereco",   "Endereço",     310, "w"),
            ("data",       "Agendamento",  150, "center"),
        ]

        self._apply_treeview_style()

        self.tree = ttk.Treeview(
            table_outer,
            columns=[c[0] for c in columns],
            show="headings",
            height=16,
            style="Custom.Treeview",
        )

        for col_id, heading, width, anchor in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor=anchor, minwidth=60)

        self.tree.tag_configure(
            "enviado",
            background=COLORS["sent_bg"],
            foreground=COLORS["sent_fg"],
        )
        self.tree.tag_configure("odd",  background=COLORS["row_odd"])
        self.tree.tag_configure("even", background=COLORS["row_even"])

        vsb = ttk.Scrollbar(table_outer, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(table_outer, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_outer.rowconfigure(0, weight=1)
        table_outer.columnconfigure(0, weight=1)

    def _apply_treeview_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Custom.Treeview",
            background=COLORS["row_odd"],
            foreground=COLORS["text_primary"],
            fieldbackground=COLORS["row_odd"],
            rowheight=30,
            font=FONT_LABEL,
            borderwidth=0,
            relief="flat",
        )
        style.configure(
            "Custom.Treeview.Heading",
            background=COLORS["surface"],
            foreground=COLORS["text_secondary"],
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            borderwidth=0,
            padding=(6, 8),
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
        # Scrollbars
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["surface"],
            troughcolor=COLORS["bg"],
            arrowcolor=COLORS["text_muted"],
            borderwidth=0,
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=COLORS["surface"],
            troughcolor=COLORS["bg"],
            arrowcolor=COLORS["text_muted"],
            borderwidth=0,
        )
        # Combobox
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["surface_alt"],
            background=COLORS["surface_alt"],
            foreground=COLORS["text_primary"],
            arrowcolor=COLORS["text_secondary"],
            bordercolor=COLORS["border"],
            insertcolor=COLORS["text_primary"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", COLORS["surface_alt"])],
            foreground=[("readonly", COLORS["text_primary"])],
        )

    def _build_action_bar(self, parent) -> None:
        bar = tk.Frame(parent, bg=COLORS["bg"])
        bar.pack(fill="x", padx=28, pady=(0, 18))

        self.btn_enviar = tk.Button(
            bar,
            text="  📤  Enviar Mensagem",
            command=self.enviar,
        )
        _style_button(self.btn_enviar, "primary")
        self.btn_enviar.pack(side="left")

        # Indicador de status com ponto colorido
        status_frame = tk.Frame(bar, bg=COLORS["bg"])
        status_frame.pack(side="right")

        self.status_dot = tk.Label(
            status_frame, text="●",
            font=("Segoe UI", 8),
            fg=COLORS["text_muted"], bg=COLORS["bg"]
        )
        self.status_dot.pack(side="left")

        self.status_label = tk.Label(
            status_frame,
            text="Pronto.",
            font=FONT_STATUS,
            fg=COLORS["text_secondary"],
            bg=COLORS["bg"],
        )
        self.status_label.pack(side="left", padx=(4, 0))


    #  Utilitários de UI

    def _set_status(self, text: str, color: str = None) -> None:
        self.status_label.config(text=text)
        dot_color = color or COLORS["text_muted"]
        self.status_dot.config(fg=dot_color)

    def _update_counter(self, n: int) -> None:
        if n:
            self.counter_badge.config(text=f"{n} agendamento{'s' if n != 1 else ''}")
            self.counter_badge.pack(side="left", padx=(12, 0))
        else:
            self.counter_badge.pack_forget()

    def _stripe_rows(self) -> None:
        """Aplica listras alternadas nas linhas da tabela."""
        for i, item in enumerate(self.tree.get_children()):
            current_tags = list(self.tree.item(item, "tags"))
            current_tags = [t for t in current_tags if t not in ("odd", "even")]
            current_tags.append("odd" if i % 2 == 0 else "even")
            self.tree.item(item, tags=current_tags)

    #  MÉTODOS PRINCIPAIS  (nomenclatura preservada)

    def on_closing(self) -> None:
        self.service.close()
        self.root.destroy()

    def selecionar_e_carregar_datas(self) -> None:
        arquivo = filedialog.askopenfilename(
            title="Selecione a planilha de agendamentos",
            filetypes=[("Planilhas Excel", "*.xlsx *.xls")],
        )
        if not arquivo:
            return

        self.arquivo_atual = arquivo
        nome_arquivo = os.path.basename(arquivo)

        self.file_label.config(
            text=nome_arquivo,
            fg=COLORS["text_secondary"],
        )
        self._set_status("Analisando datas da planilha…", COLORS["accent"])

        self.planilha_manager.set_caminho(arquivo)
        try:
            datas = self.planilha_manager.obter_datas_disponiveis()
        except Exception as exc:
            messagebox.showerror("Erro ao carregar a planilha", str(exc))
            self._set_status("Erro ao carregar dados.", COLORS["danger"])
            self.date_combo.config(state="disabled")
            self.subtitle_label.config(text="Erro ao carregar os dados.")
            return

        if datas:
            self.date_combo["values"] = datas
            self.date_combo.set(datas[0])
            self.date_combo.config(state="readonly")
            self.subtitle_label.config(text=f"Agendamentos — {nome_arquivo}")
            self._set_status(f"{len(datas)} data(s) disponível(is).", COLORS["accent"])
        else:
            self.date_combo.config(state="disabled")
            self.subtitle_label.config(text="Nenhuma data encontrada na planilha.")
            self._set_status("Nenhuma data encontrada.", COLORS["danger"])
            return

        self.tree.delete(*self.tree.get_children())
        self._update_counter(0)

    def carregar_agendamentos_por_data(self) -> None:
        if not self.arquivo_atual:
            messagebox.showwarning("Aviso", "Selecione uma planilha primeiro.")
            return

        data_selecionada = self.date_combo.get()
        if not data_selecionada:
            messagebox.showwarning("Aviso", "Selecione uma data.")
            return

        self._set_status(f"Carregando agendamentos para {data_selecionada}…", COLORS["accent"])

        try:
            dados = self.planilha_manager.carregar_clientes_por_data(data_selecionada)
        except Exception as exc:
            messagebox.showerror("Erro ao Carregar Planilha", str(exc))
            self._set_status("Erro ao carregar dados.", COLORS["danger"])
            return

        self.tree.delete(*self.tree.get_children())

        if not dados:
            self._set_status(f"Nenhum cliente encontrado para {data_selecionada}.", COLORS["text_muted"])
            self._update_counter(0)
            return

        inserir = self.tree.insert
        for c in dados:
            inserir("", "end", values=(
                c["protocolo"],
                c["nome"],
                c["telefone"],
                c["endereco"],
                c["data_agendamento"],
            ))

        self._stripe_rows()
        self.subtitle_label.config(text=f"Agendamentos — {data_selecionada}")
        self._set_status(f"{len(dados)} clientes carregados.", COLORS["accent"])
        self._update_counter(len(dados))

    def enviar(self) -> None:
        selecionado = self.tree.focus()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um cliente na lista.")
            return

        protocolo, nome, telefone, endereco, data = self.tree.item(selecionado)["values"]
        cliente = {
            "protocolo": protocolo,
            "nome":      nome,
            "telefone":  telefone,
            "endereco":  endereco,
            "data":      data,
        }

        self.btn_enviar.config(state="disabled")
        self._set_status(f"Enviando mensagem para {nome}…", COLORS["accent"])

        def resultado_envio(*, success, cliente, error):
            self.root.after(0, lambda: self._finalizar_envio(selecionado, cliente, success, error))

        try:
            self.service.enviar_mensagem_async(cliente, callback=resultado_envio)
        except Exception as exc:
            self.btn_enviar.config(state="normal")
            messagebox.showerror("Erro", f"Falha ao iniciar o envio:\n{exc}")
            self._set_status("Erro crítico durante o envio.", COLORS["danger"])

    def _finalizar_envio(self, item_id: str, cliente: dict, success: bool, error) -> None:
        self.btn_enviar.config(state="normal")

        if error:
            messagebox.showerror("Erro", f"Falha ao enviar mensagem:\n{error}")
            self._set_status("Erro crítico durante o envio.", COLORS["danger"])
            return

        if success:
            if self.tree.exists(item_id):
                # Preserva tag de listra mas adiciona 'enviado' com prioridade visual
                self.tree.item(item_id, tags=("enviado",))
            self._set_status(
                f"✓  Mensagem enviada com sucesso para {cliente['nome']}.",
                COLORS["accent"],
            )
        else:
            self._set_status(
                f"Falha ao enviar para {cliente['nome']}. Verifique o console.",
                COLORS["danger"],
            )

#  Entry-point

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
