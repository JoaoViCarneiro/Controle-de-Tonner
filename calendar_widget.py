"""
calendar_widget.py
Widget de calendário com meses em português.
"""

import customtkinter as ctk
from datetime import datetime
import calendar

MESES_PT = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


class DatePicker(ctk.CTkToplevel):
    def __init__(self, parent, callback, data_inicial=None):
        super().__init__(parent)
        self.callback = callback
        self.title("Selecionar Data")
        self.geometry("320x430")
        self.resizable(False, False)
        self.update_idletasks()
        larg_tela = self.winfo_screenwidth()
        alt_tela = self.winfo_screenheight()
        x = (larg_tela - 320) // 2
        y = (alt_tela - 430) // 2
        self.geometry(f"+{x}+{y}")
        self.hoje = datetime.now()

        # Se vier data preenchida no campo, abre nela; senão abre no mês atual
        # Guarda a data selecionada (para destacar no calendário)
        self.dia_selecionado = None
        self.mes_selecionado = None
        self.ano_selecionado = None

        if data_inicial:
            try:
                partes = data_inicial.strip().split('/')
                if len(partes) == 3:
                    self.dia_selecionado = int(partes[0])
                    self.mes_selecionado = int(partes[1])
                    self.ano_selecionado = int(partes[2])
                    self.ano_atual = self.ano_selecionado
                    self.mes_atual = self.mes_selecionado
                else:
                    self.ano_atual = self.hoje.year
                    self.mes_atual = self.hoje.month
            except Exception:
                self.ano_atual = self.hoje.year
                self.mes_atual = self.hoje.month
        else:
            self.ano_atual = self.hoje.year
            self.mes_atual = self.hoje.month

        self.dias_botoes = []
        self.setup_ui()
        self.carregar_calendario()
        self.grab_set()
        self.focus_set()

    def setup_ui(self):
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkButton(header_frame, text="◀◀", width=40, command=self.ano_anterior,
                      fg_color="gray30", hover_color="gray20").pack(side="left", padx=2)
        ctk.CTkButton(header_frame, text="◀", width=30,
                      command=self.mes_anterior).pack(side="left", padx=2)

        self.label_mes_ano = ctk.CTkLabel(header_frame, text="",
                                          font=ctk.CTkFont(size=16, weight="bold"), cursor="hand2")
        self.label_mes_ano.pack(side="left", expand=True, fill="x")
        self.label_mes_ano.bind("<Button-1>", self.abrir_seletor_ano)

        ctk.CTkButton(header_frame, text="▶", width=30,
                      command=self.proximo_mes).pack(side="right", padx=2)
        ctk.CTkButton(header_frame, text="▶▶", width=40, command=self.proximo_ano,
                      fg_color="gray30", hover_color="gray20").pack(side="right", padx=2)

        dias_frame = ctk.CTkFrame(self)
        dias_frame.pack(pady=5, padx=10, fill="x")
        for i, dia in enumerate(["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]):
            ctk.CTkLabel(dias_frame, text=dia, font=ctk.CTkFont(size=12, weight="bold"),
                         width=42, height=20).grid(row=0, column=i, padx=1, pady=2)

        self.calendario_frame = ctk.CTkFrame(self)
        self.calendario_frame.pack(pady=10, padx=10, fill="both", expand=True)

        for linha in range(6):
            for coluna in range(7):
                frame_dia = ctk.CTkFrame(self.calendario_frame, width=42, height=38, corner_radius=5)
                frame_dia.grid(row=linha, column=coluna, padx=2, pady=2)
                frame_dia.grid_propagate(False)
                btn_dia = ctk.CTkButton(frame_dia, text="", width=38, height=34,
                                        fg_color="transparent", hover_color="#2C3E50",
                                        command=lambda: None)
                btn_dia.pack(expand=True, fill="both")
                self.dias_botoes.append((frame_dia, btn_dia))

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(btn_frame, text="Hoje", command=self.selecionar_hoje,
                      width=100, fg_color="#3498DB", hover_color="#2980B9").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Limpar", command=self.limpar_data,
                      width=100, fg_color="gray40", hover_color="gray30").pack(side="right", padx=5)

    def carregar_calendario(self):
        self.label_mes_ano.configure(text=f"{MESES_PT[self.mes_atual]} {self.ano_atual}")
        primeiro_dia = datetime(self.ano_atual, self.mes_atual, 1)
        dia_semana = (primeiro_dia.weekday() + 1) % 7
        _, ultimo_dia = calendar.monthrange(self.ano_atual, self.mes_atual)
        dia_atual = 1
        for idx, (frame_dia, btn_dia) in enumerate(self.dias_botoes):
            coluna = idx % 7
            linha = idx // 7
            if linha == 0 and coluna < dia_semana:
                btn_dia.configure(text="", fg_color="transparent", state="disabled", command=lambda: None)
            elif dia_atual <= ultimo_dia:
                is_hoje = (self.ano_atual == self.hoje.year and
                           self.mes_atual == self.hoje.month and
                           dia_atual == self.hoje.day)
                is_selecionado = (self.dia_selecionado is not None and
                                  dia_atual == self.dia_selecionado and
                                  self.mes_atual == self.mes_selecionado and
                                  self.ano_atual == self.ano_selecionado)

                if is_selecionado:
                    # Verde escuro com borda — data atualmente selecionada
                    cor_fundo = "#1A6B3A"
                elif is_hoje and not is_selecionado:
                    # Azul sutil — dia de hoje (quando não é o selecionado)
                    cor_fundo = "#2E4F7A"
                else:
                    cor_fundo = "transparent"

                btn_dia.configure(
                    text=str(dia_atual),
                    fg_color=cor_fundo,
                    hover_color="#2C3E50",
                    state="normal",
                    command=lambda d=dia_atual: self.selecionar_data(d)
                )
                dia_atual += 1
            else:
                btn_dia.configure(text="", fg_color="transparent", state="disabled", command=lambda: None)

    def abrir_seletor_ano(self, event=None):
        dialog = ctk.CTkInputDialog(text="Digite o ano (1900-2100):", title="Selecionar Ano")
        ano = dialog.get_input()
        if ano and ano.isdigit():
            ano = int(ano)
            if 1900 <= ano <= 2100:
                self.ano_atual = ano
                self.carregar_calendario()

    def ano_anterior(self): self.ano_atual -= 1; self.carregar_calendario()
    def proximo_ano(self): self.ano_atual += 1; self.carregar_calendario()

    def mes_anterior(self):
        if self.mes_atual == 1: self.mes_atual = 12; self.ano_atual -= 1
        else: self.mes_atual -= 1
        self.carregar_calendario()

    def proximo_mes(self):
        if self.mes_atual == 12: self.mes_atual = 1; self.ano_atual += 1
        else: self.mes_atual += 1
        self.carregar_calendario()

    def selecionar_data(self, dia):
        self.dia_selecionado = dia
        self.mes_selecionado = self.mes_atual
        self.ano_selecionado = self.ano_atual
        self.carregar_calendario()
        self.callback(f"{dia:02d}/{self.mes_atual:02d}/{self.ano_atual}")
        self.destroy()

    def selecionar_hoje(self):
        self.callback(self.hoje.strftime("%d/%m/%Y"))
        self.destroy()

    def limpar_data(self):
        self.callback("")
        self.destroy()


class DateEntry(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent")
        self.entry = ctk.CTkEntry(self, **kwargs)
        self.entry.pack(side="left", padx=(0, 5))
        ctk.CTkButton(self, text="📅", width=35, height=35,
                      command=self.abrir_calendario,
                      fg_color="gray30", hover_color="gray20").pack(side="left")

    def abrir_calendario(self):
        data_atual = self.entry.get().strip()
        DatePicker(self, self.set_data, data_inicial=data_atual if data_atual else None)

    def set_data(self, data):
        self.entry.delete(0, "end")
        if data: self.entry.insert(0, data)

    def get(self): return self.entry.get()
    def delete(self, first, last=None): self.entry.delete(first, last)
    def insert(self, index, string): self.entry.insert(index, string)
