"""
gui_app.py
Interface profissional - ESTÉTICA MINIMALISTA
VERSÃO FINAL - TROCA SIMPLIFICADA EM UM ÚNICO PASSO
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from datetime import datetime
import sys
import os

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# IMPORTS
from database import init_database
from database_operations import (
    listar_maquinas,
    salvar_maquina,
    deletar_maquina,
    registrar_toner,
    finalizar_toner,
    listar_toners_por_maquina,
    get_toners_ativos_por_maquina,
    get_toner_atual_por_cor,
    get_ultimo_contador_por_maquina,
    calcular_rendimento_por_cor,
    resumo_cores_maquina,
    get_historico_por_cor,
    editar_toner,
    registrar_contador,
    listar_contadores,
    deletar_contador
)
from models import Maquina, Toner
from relatorios import gerar_relatorio_pdf, gerar_relatorio_excel
from calendar_widget import DateEntry

# ========== CONFIGURAÇÃO DE TEMA PERSONALIZADO ==========
CORES_ESCURO = {
    'bg_primary': '#0B0E14',
    'bg_secondary': '#1E1F25',
    'bg_tertiary': '#2A2C33',
    'btn_inativo': 'transparent',   # Botões inativos transparentes no escuro
    'btn_ativo': '#2A2C33',         # Botão ativo no escuro
    'text_primary': '#FFFFFF',
    'text_secondary': '#8B8D93',
    'text_muted': '#5D5F66',
    'accent_blue': '#2C3E50',
    'accent_blue_hover': '#3A4E62',
    'accent_red': '#8B3A3A',
    'accent_red_hover': '#A54A4A',
    'accent_green': '#2C4A3A',
    'accent_green_hover': '#3A5E4A',
    'accent_orange': '#8B5A2C',
    'accent_orange_hover': '#A56E3A',
    'border': '#2A2C33',
    'success': '#2C6B4A',
    'warning': '#8B6B2C',
    'alerta': '#CC3333',
}

CORES_CLARO = {
    'bg_primary': '#F0F2F5',
    'bg_secondary': '#FFFFFF',
    'bg_tertiary': '#DDE1E9',
    'btn_inativo': '#E8EBF0',       # Fundo dos botões inativos no tema claro
    'btn_ativo': '#1A5276',         # Fundo do botão ativo no tema claro
    'text_primary': '#0D0F1A',
    'text_secondary': '#3A3D52',
    'text_muted': '#7A7D8F',
    'accent_blue': '#1A5276',
    'accent_blue_hover': '#1F618D',
    'accent_red': '#C0392B',
    'accent_red_hover': '#E74C3C',
    'accent_green': '#1E8449',
    'accent_green_hover': '#27AE60',
    'accent_orange': '#D35400',
    'accent_orange_hover': '#E67E22',
    'border': '#B0B5C3',
    'success': '#1A7A40',
    'warning': '#B7770D',
    'alerta': '#CC3333',
}

CORES = CORES_CLARO  # Tema padrão: claro


class ControleTonerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ========== CONFIGURAÇÃO DA JANELA ==========
        self.title("Controle de Toner v3.0")

        try:
            # Para Windows
            if os.path.exists("icone.ico"):
                self.iconbitmap("icone.ico")
            # Para Linux (usando PNG)
            elif os.path.exists("icone_app.png"):
                icon = tk.PhotoImage(file="icone_app.png")
                self.iconphoto(True, icon)

        except Exception as e:
            print(f"⚠️ Não foi possível definir o ícone da janela: {e}")
        # Centraliza na tela antes de maximizar (evita abrir deslocada)
        import platform
        largura = 1280
        altura = 720
        self.update_idletasks()
        larg_tela = self.winfo_screenwidth()
        alt_tela = self.winfo_screenheight()
        x = (larg_tela - largura) // 2
        y = (alt_tela - altura) // 2
        self.geometry(f"{largura}x{altura}+{x}+{y}")
        self.minsize(1200, 700)
        # Maximiza após centralizar
        self.after(10, lambda: self.state('zoomed') if platform.system() == "Windows" else self.attributes('-zoomed', True))

        self.tema_atual = "claro"
        ctk.set_appearance_mode("light")
        self.configure(fg_color=CORES['bg_primary'])

        print("📦 Inicializando banco de dados...")
        init_database()
        self._migrar_contadores_de_toners()
        print("✅ Banco de dados inicializado!")

        # Variáveis de controle
        self.maquina_atual = None
        self.toner_selecionado = None

        # Cria a interface
        self.setup_ui()

        # Carrega dados iniciais
        self.carregar_maquinas()



        print("✅ Interface carregada!")


    def _migrar_contadores_de_toners(self):
        """
        Popula a tabela contadores_semanais com dados históricos:
        1. Trocas de toner já registradas
        2. Contador inicial do cadastro de cada máquina (quando > 0)
        Não duplica registros já existentes.
        """
        from database import get_conexao
        conn = get_conexao()
        cursor = conn.cursor()
        inseridos = 0

        # 1. Importa das trocas de toner existentes
        cursor.execute("""
            SELECT maquina_id, data_instalacao, contador_inicial, cor
            FROM toners_individual
            WHERE data_instalacao IS NOT NULL AND contador_inicial > 0
            ORDER BY maquina_id, data_instalacao
        """)
        for maquina_id, data, contador, cor in cursor.fetchall():
            cursor.execute("""
                SELECT id FROM contadores_semanais
                WHERE maquina_id=? AND data=? AND contador=?
            """, (maquina_id, data, contador))
            if cursor.fetchone() is None:
                inseridos += 1  # (trocas de toner não são importadas para contadores)

        # 2. Importa contador_atual do cadastro de cada máquina (se ainda não existir esse valor)
        from datetime import datetime as _dt
        cursor.execute("""
            SELECT id, contador_atual, data_cadastro FROM maquinas
            WHERE contador_atual > 0
        """)
        for maquina_id, contador, data_cadastro in cursor.fetchall():
            # Usa data de cadastro ou hoje
            if data_cadastro:
                data = str(data_cadastro)[:10]
            else:
                data = _dt.now().strftime("%Y-%m-%d")
            # Só insere se não existir registro com exatamente este contador nesta máquina
            cursor.execute("""
                SELECT id FROM contadores_semanais
                WHERE maquina_id=? AND contador=?
            """, (maquina_id, contador))
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO contadores_semanais (maquina_id, data, contador, observacao)
                    VALUES (?, ?, ?, ?)
                """, (maquina_id, data, contador, "Contador atual do cadastro"))
                inseridos += 1

        # Remove registros de troca de toner que possam ter sido inseridos anteriormente
        cursor.execute("""
            DELETE FROM contadores_semanais
            WHERE observacao LIKE 'Troca de toner%'
        """)

        conn.commit()
        conn.close()
        if inseridos:
            print(f"✅ Migração: {inseridos} registros de contador importados.")

    def setup_ui(self):
        """Configura todos os elementos da interface"""

        # Grid layout principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ========== SIDEBAR ==========
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=CORES['bg_secondary']
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=24, pady=(32, 24), sticky="ew")

        self.logo_label = ctk.CTkLabel(
            logo_frame,
            text="◉ Controle Toner",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color=CORES['text_primary']
        )
        self.logo_label.pack(anchor="w")

        self.sub_logo = ctk.CTkLabel(
            logo_frame,
            text="Sistema de Gestão v3.0",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color=CORES['text_secondary']
        )
        self.sub_logo.pack(anchor="w", pady=(4, 0))

        # Menu de navegação
        menu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        menu_frame.grid(row=1, column=0, padx=16, pady=16, sticky="ew")

        self.btn_maquinas = self.criar_botao_menu(
            menu_frame,
            "🏭 Máquinas",
            lambda: self.mostrar_aba("maquinas"),
            0
        )

        self.btn_troca = self.criar_botao_menu(
            menu_frame,
            "🔄 Registrar Troca",
            lambda: self.mostrar_aba("troca"),
            1
        )

        self.btn_relatorios = self.criar_botao_menu(
            menu_frame,
            "📊 Relatórios",
            lambda: self.mostrar_aba("relatorios"),
            2
        )

        self.btn_historico_cores = self.criar_botao_menu(
            menu_frame,
            "🎨 Histórico por Cor",
            lambda: self.mostrar_aba("historico_cores"),
            3
        )

        self.btn_contadores = self.criar_botao_menu(
            menu_frame,
            "📟 Contadores",
            lambda: self.mostrar_aba("contadores"),
            4
        )

        # Espaço flexível
        self.sidebar.grid_rowconfigure(6, weight=1)

        # Rodapé
        footer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer_frame.grid(row=6, column=0, padx=24, pady=24, sticky="ew")

        # Botão de alternância de tema
        self.btn_tema = ctk.CTkButton(
            footer_frame,
            text="🌙  Tema Escuro",
            command=self.alternar_tema,
            height=32,
            fg_color=CORES['bg_tertiary'],
            hover_color=CORES['accent_blue'],
            text_color=CORES['text_secondary'],
            font=ctk.CTkFont(family="Inter", size=11),
            corner_radius=8
        )
        self.btn_tema.pack(fill="x", anchor="w", pady=(0, 12))

        self.status_label = ctk.CTkLabel(
            footer_frame,
            text="● Online",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color=CORES['success']
        )
        self.status_label.pack(anchor="w")

        self.versao_label = ctk.CTkLabel(
            footer_frame,
            text="v3.0 - Troca Simplificada",
            font=ctk.CTkFont(family="Inter", size=10),
            text_color=CORES['text_muted']
        )
        self.versao_label.pack(anchor="w", pady=(4, 0))

        # ========== ÁREA PRINCIPAL ==========
        self.main_area = ctk.CTkFrame(
            self,
            fg_color=CORES['bg_primary'],
            corner_radius=0
        )
        self.main_area.grid(row=0, column=1, padx=24, pady=24, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(0, weight=1)

        # Container para as abas
        self.aba_container = ctk.CTkFrame(
            self.main_area,
            fg_color="transparent"
        )
        self.aba_container.grid(row=0, column=0, sticky="nsew")
        self.aba_container.grid_columnconfigure(0, weight=1)
        self.aba_container.grid_rowconfigure(0, weight=1)

        # Inicia com a aba de máquinas
        self.mostrar_aba("maquinas")

    def alternar_tema(self):
        """Alterna entre tema escuro e claro"""
        global CORES

        if self.tema_atual == "escuro":
            self.tema_atual = "claro"
            CORES = CORES_CLARO
            ctk.set_appearance_mode("light")
            self.btn_tema.configure(text="🌙  Tema Escuro")
        else:
            self.tema_atual = "escuro"
            CORES = CORES_ESCURO
            ctk.set_appearance_mode("dark")
            self.btn_tema.configure(text="🌙  Tema Escuro")

        # Reaplica cores na janela principal e sidebar
        self.configure(fg_color=CORES['bg_primary'])
        self.sidebar.configure(fg_color=CORES['bg_secondary'])
        self.main_area.configure(fg_color=CORES['bg_primary'])
        self.btn_tema.configure(
            fg_color=CORES.get('btn_inativo', CORES['bg_tertiary']),
            hover_color=CORES.get('btn_ativo', CORES['accent_blue']),
            text_color=CORES['text_secondary']
        )


        # Recarrega a aba atual para aplicar as novas cores
        aba_atual = getattr(self, '_aba_atual', 'maquinas')
        self.mostrar_aba(aba_atual)

    def criar_botao_menu(self, parent, texto, comando, row):
        """Cria botão de menu estilizado"""
        btn = ctk.CTkButton(
            parent,
            text=texto,
            command=comando,
            height=44,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color=CORES.get('btn_inativo', 'transparent'),
            text_color=CORES['text_secondary'],
            hover_color=CORES.get('btn_ativo', CORES['bg_tertiary']),
            anchor="w",
            corner_radius=8
        )
        btn.grid(row=row, column=0, padx=0, pady=4, sticky="ew")
        return btn

    def mostrar_aba(self, aba_nome):
        self._aba_atual = aba_nome
        """Alterna entre as abas do sistema"""
        # Resetar cores dos botões
        botoes = [self.btn_maquinas, self.btn_troca, self.btn_relatorios, self.btn_historico_cores, self.btn_contadores]

        for btn in botoes:
            btn.configure(
                fg_color=CORES.get('btn_inativo', 'transparent'),
                text_color=CORES['text_secondary']
            )

        # Destacar botão ativo
        if aba_nome == "maquinas":
            self.btn_maquinas.configure(
                fg_color=CORES.get('btn_ativo', CORES['bg_tertiary']),
                text_color=CORES['text_primary']
            )
        elif aba_nome == "troca":
            self.btn_troca.configure(
                fg_color=CORES.get('btn_ativo', CORES['bg_tertiary']),
                text_color=CORES['text_primary']
            )

        elif aba_nome == "relatorios":
            self.btn_relatorios.configure(
                fg_color=CORES.get('btn_ativo', CORES['bg_tertiary']),
                text_color=CORES['text_primary']
            )
        elif aba_nome == "historico_cores":
            self.btn_historico_cores.configure(
                fg_color=CORES.get('btn_ativo', CORES['bg_tertiary']),
                text_color=CORES['text_primary']
            )
        elif aba_nome == "contadores":
            self.btn_contadores.configure(
                fg_color=CORES.get('btn_ativo', CORES['bg_tertiary']),
                text_color=CORES['text_primary']
            )


        # Limpa o container
        for widget in self.aba_container.winfo_children():
            widget.destroy()

        # Carrega a aba correspondente
        if aba_nome == "maquinas":
            self.aba_maquinas()
        elif aba_nome == "troca":
            self.aba_troca_simplificada()
        elif aba_nome == "relatorios":
            self.aba_relatorios()
        elif aba_nome == "historico_cores":
            self.aba_historico_cores()
        elif aba_nome == "contadores":
            self.aba_contadores()


    # ========== FUNÇÕES AUXILIARES ==========
    def criar_frame_com_scroll(self):
        """Cria um frame com scrollbar"""
        main_frame = ctk.CTkFrame(self.aba_container, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        canvas = ctk.CTkCanvas(main_frame, bg=CORES['bg_primary'], highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(main_frame, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="transparent")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        return main_frame, canvas, scrollable_frame

    def criar_titulo(self, parent, titulo, subtitulo):
        """Cria título com subtítulo"""
        titulo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        titulo_frame.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            titulo_frame,
            text=titulo,
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color=CORES['text_primary']
        ).pack(anchor="w")

        ctk.CTkLabel(
            titulo_frame,
            text=subtitulo,
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).pack(anchor="w", pady=(4, 0))

    def criar_card(self, parent, titulo):
        """Cria um card padrão"""
        card = ctk.CTkFrame(
            parent,
            fg_color=CORES['bg_secondary'],
            corner_radius=12,
            border_width=1,
            border_color=CORES['border']
        )

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text=titulo,
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=CORES['text_primary']
        ).pack(anchor="w")

        return card

    # ========== ABA 1: MÁQUINAS ==========
    def aba_maquinas(self):
        """Interface de cadastro de máquinas"""

        frame = ctk.CTkFrame(
            self.aba_container,
            fg_color="transparent"
        )
        frame.pack(fill="both", expand=True)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Título
        titulo_frame = ctk.CTkFrame(frame, fg_color="transparent")
        titulo_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 24))

        ctk.CTkLabel(
            titulo_frame,
            text="Cadastro de Máquinas",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color=CORES['text_primary']
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            titulo_frame,
            text="Gerencie as impressoras cadastradas no sistema",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        # Card de cadastro
        card_cadastro = ctk.CTkFrame(
            frame,
            fg_color=CORES['bg_secondary'],
            corner_radius=12,
            border_width=1,
            border_color=CORES['border']
        )
        card_cadastro.grid(row=1, column=0, padx=(0, 12), sticky="nsew")
        card_cadastro.grid_columnconfigure(1, weight=1)

        # Header do card
        header_cadastro = ctk.CTkFrame(card_cadastro, fg_color="transparent")
        header_cadastro.grid(row=0, column=0, columnspan=2, padx=24, pady=(20, 10), sticky="ew")

        ctk.CTkLabel(
            header_cadastro,
            text="📋 Nova Máquina",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=CORES['text_primary']
        ).grid(row=0, column=0, sticky="w")

        row = 1

        # Nome
        ctk.CTkLabel(
            card_cadastro,
            text="Nome:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=24, pady=(16, 4), sticky="w")
        row += 1

        self.entry_nome = ctk.CTkEntry(
            card_cadastro,
            placeholder_text="Ex: HP LaserJet M402",
            height=40,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            corner_radius=8
        )
        self.entry_nome.grid(row=row, column=0, columnspan=2, padx=24, pady=(0, 16), sticky="ew")
        row += 1

        # Modelo
        ctk.CTkLabel(
            card_cadastro,
            text="Modelo:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=24, pady=(0, 4), sticky="w")
        row += 1

        self.entry_modelo = ctk.CTkEntry(
            card_cadastro,
            placeholder_text="Ex: M402dn",
            height=40,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            corner_radius=8
        )
        self.entry_modelo.grid(row=row, column=0, columnspan=2, padx=24, pady=(0, 16), sticky="ew")
        row += 1

        # Tipo
        ctk.CTkLabel(
            card_cadastro,
            text="Tipo:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=24, pady=(0, 4), sticky="w")
        row += 1

        self.combo_tipo = ctk.CTkComboBox(
            card_cadastro,
            values=["P&B", "Colorida"],
            state="readonly",
            height=40,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            button_color=CORES['accent_blue'],
            button_hover_color=CORES['accent_blue_hover'],
            dropdown_fg_color=CORES['bg_secondary'],
            dropdown_hover_color=CORES['bg_tertiary'],
            dropdown_text_color=CORES['text_primary']
        )
        self.combo_tipo.set("P&B")
        self.combo_tipo.grid(row=row, column=0, columnspan=2, padx=24, pady=(0, 16), sticky="ew")
        row += 1

        # Contador Inicial
        ctk.CTkLabel(
            card_cadastro,
            text="Contador Inicial:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=24, pady=(0, 4), sticky="w")
        row += 1

        self.entry_contador = ctk.CTkEntry(
            card_cadastro,
            placeholder_text="0",
            height=40,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            corner_radius=8
        )
        self.entry_contador.grid(row=row, column=0, columnspan=2, padx=24, pady=(0, 16), sticky="ew")
        self.entry_contador.insert(0, "0")
        row += 1

        # Data de cadastro
        ctk.CTkLabel(
            card_cadastro,
            text="Data de Cadastro",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary'],
            anchor="w"
        ).grid(row=row, column=0, columnspan=2, padx=24, pady=(0, 6), sticky="w")
        row += 1

        self.entry_data_cadastro = DateEntry(
            card_cadastro,
            height=40,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            corner_radius=8
        )
        self.entry_data_cadastro.grid(row=row, column=0, columnspan=2, padx=24, pady=(0, 24), sticky="w")
        self.entry_data_cadastro.insert(0, datetime.now().strftime("%d/%m/%Y"))
        row += 1

        # Botões
        btn_frame = ctk.CTkFrame(card_cadastro, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, padx=24, pady=(0, 24), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_salvar = ctk.CTkButton(
            btn_frame,
            text="Salvar Máquina",
            command=self.salvar_maquina,
            height=40,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color=CORES['accent_blue'],
            hover_color=CORES['accent_blue_hover'],
            corner_radius=8
        )
        self.btn_salvar.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.btn_novo = ctk.CTkButton(
            btn_frame,
            text="Novo",
            command=self.limpar_form_maquina,
            height=40,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color=CORES['bg_tertiary'],
            hover_color=CORES['border'],
            text_color=CORES['text_primary'],
            corner_radius=8
        )
        self.btn_novo.grid(row=0, column=1, padx=6, sticky="ew")

        self.btn_deletar = ctk.CTkButton(
            btn_frame,
            text="Deletar",
            command=self.deletar_maquina,
            height=40,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color=CORES['accent_red'],
            hover_color=CORES['accent_red_hover'],
            corner_radius=8
        )
        self.btn_deletar.grid(row=0, column=2, padx=(6, 0), sticky="ew")

        # Card de listagem
        card_lista = ctk.CTkFrame(
            frame,
            fg_color=CORES['bg_secondary'],
            corner_radius=12,
            border_width=1,
            border_color=CORES['border']
        )
        card_lista.grid(row=1, column=1, padx=(12, 0), sticky="nsew")
        card_lista.grid_columnconfigure(0, weight=1)
        card_lista.grid_rowconfigure(1, weight=1)

        # Header do card de listagem
        header_lista = ctk.CTkFrame(card_lista, fg_color="transparent")
        header_lista.grid(row=0, column=0, padx=24, pady=(20, 10), sticky="ew")

        ctk.CTkLabel(
            header_lista,
            text="📋 Máquinas Cadastradas",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
            text_color=CORES['text_primary']
        ).grid(row=0, column=0, sticky="w")

        # Treeview
        table_frame = ctk.CTkFrame(card_lista, fg_color="transparent")
        table_frame.grid(row=1, column=0, padx=24, pady=(0, 24), sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Custom.Treeview",
            background=CORES['bg_tertiary'],
            foreground=CORES['text_primary'],
            rowheight=40,
            fieldbackground=CORES['bg_tertiary'],
            bordercolor=CORES['border'],
            borderwidth=0,
            font=('Inter', 11)
        )

        style.configure(
            "Custom.Treeview.Heading",
            background=CORES['bg_secondary'],
            foreground=CORES['text_primary'],
            relief="flat",
            font=('Inter', 12, 'bold')
        )

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.tree_maquinas = ttk.Treeview(
            table_frame,
            columns=("nome", "modelo", "tipo", "contador"),
            show="headings",
            height=12,
            yscrollcommand=scrollbar.set,
            style="Custom.Treeview"
        )
        self.tree_maquinas.grid(row=0, column=0, sticky="nsew")

        scrollbar.config(command=self.tree_maquinas.yview)

        self.tree_maquinas.heading("nome", text="Nome")
        self.tree_maquinas.heading("modelo", text="Modelo")
        self.tree_maquinas.heading("tipo", text="Tipo")
        self.tree_maquinas.heading("contador", text="Contador")

        self.tree_maquinas.column("nome", width=200, anchor="w")
        self.tree_maquinas.column("modelo", width=150, anchor="w")
        self.tree_maquinas.column("tipo", width=80, anchor="center")
        self.tree_maquinas.column("contador", width=100, anchor="center")

        self.tree_maquinas.bind("<<TreeviewSelect>>", self.selecionar_maquina)

        self.carregar_maquinas()

    def carregar_maquinas(self):
        """Carrega a lista de máquinas na treeview"""
        try:
            if hasattr(self, 'tree_maquinas'):
                for item in self.tree_maquinas.get_children():
                    self.tree_maquinas.delete(item)

                maquinas = listar_maquinas()

                for m in maquinas:
                    self.tree_maquinas.insert(
                        "",
                        "end",
                        iid=str(m.id),
                        values=(m.nome, m.modelo, m.tipo, m.contador_atual)
                    )
        except Exception as e:
            print(f"❌ Erro ao carregar máquinas: {e}")

    def salvar_maquina(self):
        """Salva ou atualiza uma máquina"""
        try:
            nome = self.entry_nome.get().strip()
            if not nome:
                messagebox.showerror("Erro", "Nome da máquina é obrigatório!")
                return

            modelo = self.entry_modelo.get().strip()
            tipo = self.combo_tipo.get()

            try:
                contador = int(self.entry_contador.get() or "0")
            except ValueError:
                contador = 0

            data_cad_str = self.entry_data_cadastro.get().strip()
            # Converte DD/MM/YYYY → YYYY-MM-DD para armazenar
            if data_cad_str and '/' in data_cad_str:
                p = data_cad_str.split('/')
                data_cad_iso = f"{p[2]}-{p[1]}-{p[0]}" if len(p) == 3 else data_cad_str
            else:
                data_cad_iso = datetime.now().strftime("%Y-%m-%d")

            maquina = Maquina(
                id=self.maquina_atual.id if self.maquina_atual else None,
                nome=nome,
                modelo=modelo,
                tipo=tipo,
                contador_atual=contador,
                data_cadastro=data_cad_iso
            )

            eh_nova = self.maquina_atual is None
            novo_id = salvar_maquina(maquina)

            if not eh_nova:
                self.maquina_atual.nome = nome
                self.maquina_atual.modelo = modelo
                self.maquina_atual.tipo = tipo
                self.maquina_atual.contador_atual = contador
                print(f"✅ Máquina atualizada: {nome}")
            else:
                # Registra automaticamente o contador inicial na aba Contadores
                if contador > 0:
                    registrar_contador(
                        maquina_id=novo_id,
                        data=data_cad_iso,
                        contador=contador,
                        observacao="Contador inicial do cadastro"
                    )

                # Cria um toner ativo para cada cor automaticamente
                cores = ["Preto", "Ciano", "Magenta", "Amarelo"] if tipo == "Colorida" else ["Preto"]
                for cor in cores:
                    toner_inicial = Toner(
                        maquina_id=novo_id,
                        cor=cor,
                        data_instalacao=data_cad_iso,
                        contador_inicial=contador,
                        custo=0.0,
                        observacao="Toner inicial — cadastro da máquina"
                    )
                    registrar_toner(toner_inicial)

                print(f"✅ Nova máquina criada: {nome} (ID: {novo_id})")

            self.carregar_maquinas()
            self.limpar_form_maquina()

            messagebox.showinfo("Sucesso", f"Máquina '{nome}' salva com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar: {str(e)}")

    def limpar_form_maquina(self):
        """Limpa o formulário de máquinas"""
        self.entry_nome.delete(0, "end")
        self.entry_modelo.delete(0, "end")
        self.combo_tipo.set("P&B")
        self.entry_contador.delete(0, "end")
        self.entry_contador.insert(0, "0")
        self.entry_data_cadastro.delete(0, "end")
        self.entry_data_cadastro.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.maquina_atual = None

    def selecionar_maquina(self, event):
        """Preenche o formulário com a máquina selecionada"""
        selecao = self.tree_maquinas.selection()
        if not selecao:
            return

        try:
            maquina_id = int(selecao[0])
            maquinas = listar_maquinas()

            for m in maquinas:
                if m.id == maquina_id:
                    self.maquina_atual = Maquina(
                        id=m.id,
                        nome=m.nome,
                        modelo=m.modelo,
                        tipo=m.tipo,
                        contador_atual=m.contador_atual
                    )

                    self.entry_nome.delete(0, "end")
                    self.entry_nome.insert(0, m.nome)

                    self.entry_modelo.delete(0, "end")
                    self.entry_modelo.insert(0, m.modelo)

                    self.combo_tipo.set(m.tipo)

                    self.entry_contador.delete(0, "end")
                    self.entry_contador.insert(0, str(m.contador_atual))
                    self.entry_data_cadastro.delete(0, "end")
                    if m.data_cadastro and '-' in str(m.data_cadastro):
                        p = str(m.data_cadastro)[:10].split('-')
                        self.entry_data_cadastro.insert(0, f"{p[2]}/{p[1]}/{p[0]}")
                    else:
                        self.entry_data_cadastro.insert(0, datetime.now().strftime("%d/%m/%Y"))
                    break

        except Exception as e:
            print(f"❌ Erro ao selecionar máquina: {e}")

    def deletar_maquina(self):
        """Deleta a máquina selecionada"""
        if not self.maquina_atual:
            messagebox.showwarning("Aviso", "Selecione uma máquina para deletar!")
            return

        if messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar a máquina {self.maquina_atual.nome}?"):
            deletar_maquina(self.maquina_atual.id)
            self.carregar_maquinas()
            self.limpar_form_maquina()
            messagebox.showinfo("Sucesso", "Máquina deletada com sucesso!")

    # ========== ABA 2: TROCA SIMPLIFICADA ==========
    def aba_troca_simplificada(self):
        """Interface para registrar troca de toner em UM ÚNICO PASSO"""

        main_frame, canvas, scrollable_frame = self.criar_frame_com_scroll()

        self.criar_titulo(scrollable_frame, "Registrar Troca de Toner",
                          "Registre a substituição de um toner em um único passo")

        card = self.criar_card(scrollable_frame, "🔄 Nova Troca")
        card.pack(fill="both", padx=20, pady=10, expand=True)

        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(fill="both", padx=20, pady=10)
        form_frame.grid_columnconfigure(1, weight=1)

        row = 0

        # ========== SELEÇÃO DA MÁQUINA ==========
        ctk.CTkLabel(
            form_frame,
            text="Máquina:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=(0, 10), pady=8, sticky="e")

        maquinas = listar_maquinas()
        nomes_maquinas = ["Selecione uma máquina..."] + [m.nome for m in maquinas]

        self.combo_troca_maquina = ctk.CTkComboBox(
            form_frame,
            values=nomes_maquinas,
            state="readonly",
            width=350,
            height=38,
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            button_color=CORES['accent_blue'],
            button_hover_color=CORES['accent_blue_hover'],
            dropdown_fg_color=CORES['bg_secondary'],
            dropdown_hover_color=CORES['bg_tertiary'],
            dropdown_text_color=CORES['text_primary'],
            command=self.carregar_info_troca
        )
        self.combo_troca_maquina.grid(row=row, column=1, columnspan=2, padx=0, pady=8, sticky="ew")
        self.combo_troca_maquina.set("Selecione uma máquina...")
        row += 1

        # ========== FRAME DE INFORMAÇÕES DO TONER ATUAL ==========
        self.info_frame = ctk.CTkFrame(form_frame, fg_color=CORES['bg_tertiary'], corner_radius=8)
        self.info_frame.grid(row=row, column=0, columnspan=2, padx=0, pady=8, sticky="ew")
        self.info_frame.grid_columnconfigure(0, weight=1)
        row += 1

        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Selecione uma máquina para ver o toner atual",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color=CORES['text_secondary']
        )
        self.info_label.pack(padx=10, pady=10)

        # ========== SEPARADOR VISUAL ==========
        separator = ctk.CTkFrame(form_frame, height=2, fg_color=CORES['border'])
        separator.grid(row=row, column=0, columnspan=2, padx=0, pady=15, sticky="ew")
        row += 1

        # ========== DADOS DO NOVO TONER ==========
        ctk.CTkLabel(
            form_frame,
            text="📦 NOVO TONER",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color=CORES['text_primary']
        ).grid(row=row, column=0, columnspan=2, padx=0, pady=(0, 10), sticky="w")
        row += 1

        # Cor do Novo Toner
        ctk.CTkLabel(
            form_frame,
            text="Cor do Toner:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=(0, 10), pady=8, sticky="e")

        self.combo_troca_cor = ctk.CTkComboBox(
            form_frame,
            values=["Selecione uma máquina primeiro"],
            state="readonly",
            width=200,
            height=38,
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            button_color=CORES['accent_blue'],
            button_hover_color=CORES['accent_blue_hover'],
            dropdown_fg_color=CORES['bg_secondary'],
            dropdown_hover_color=CORES['bg_tertiary'],
            dropdown_text_color=CORES['text_primary']
        )
        self.combo_troca_cor.grid(row=row, column=1, columnspan=2, padx=0, pady=8, sticky="w")
        row += 1

        # Data da Troca
        ctk.CTkLabel(
            form_frame,
            text="Data da Troca:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=(0, 10), pady=8, sticky="e")

        self.troca_data = DateEntry(
            form_frame,
            width=120,
            placeholder_text="DD/MM/AAAA",
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            corner_radius=8
        )
        self.troca_data.grid(row=row, column=1, pady=8, sticky="w")
        self.troca_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        row += 1

        # Contador Atual
        ctk.CTkLabel(
            form_frame,
            text="Contador Atual:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=(0, 10), pady=8, sticky="e")

        frame_contador = ctk.CTkFrame(form_frame, fg_color="transparent")
        frame_contador.grid(row=row, column=1, pady=8, sticky="w")

        self.troca_contador = ctk.CTkEntry(
            frame_contador,
            placeholder_text="Contador da máquina",
            width=150,
            height=38,
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            corner_radius=8
        )
        self.troca_contador.pack(side="left")

        self.troca_contador_info = ctk.CTkLabel(
            frame_contador,
            text="",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color=CORES['text_muted']
        )
        self.troca_contador_info.pack(side="left", padx=(12, 0))
        row += 1

        # Custo do Novo Toner
        ctk.CTkLabel(
            form_frame,
            text="Custo (R$):",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=(0, 10), pady=8, sticky="e")

        self.troca_custo = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ex: 299,90",
            width=150,
            height=38,
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            corner_radius=8
        )
        self.troca_custo.grid(row=row, column=1, pady=8, sticky="w")
        self.troca_custo.insert(0, "636")
        row += 1

        # Observação
        ctk.CTkLabel(
            form_frame,
            text="Observação:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=(0, 10), pady=8, sticky="e")

        self.troca_obs = ctk.CTkEntry(
            form_frame,
            placeholder_text="Opcional",
            width=300,
            height=38,
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            corner_radius=8
        )
        self.troca_obs.grid(row=row, column=1, columnspan=2, pady=8, sticky="w")
        row += 1

        # ========== BOTÃO DE REGISTRO ==========
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))

        btn_registrar = ctk.CTkButton(
            btn_frame,
            text="🔄 Registrar Troca",
            command=self.registrar_troca_unica,
            height=44,
            width=220,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            fg_color=CORES['accent_blue'],
            hover_color=CORES['accent_blue_hover'],
            corner_radius=8
        )
        btn_registrar.pack(side="left", padx=(0, 10))

        btn_limpar = ctk.CTkButton(
            btn_frame,
            text="🧹 Limpar",
            command=self.limpar_form_troca,
            height=44,
            width=120,
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color=CORES['bg_tertiary'],
            hover_color=CORES['border'],
            text_color=CORES['text_primary'],
            corner_radius=8
        )
        btn_limpar.pack(side="left")

    def carregar_info_troca(self, escolha=None):
        """Carrega informações do toner atual quando seleciona uma máquina"""
        nome_maquina = self.combo_troca_maquina.get()

        if nome_maquina and nome_maquina != "Selecione uma máquina...":
            maquinas = listar_maquinas()
            for m in maquinas:
                if m.nome == nome_maquina:
                    self.maquina_atual = m

                    # Busca TODOS os toners ativos (um de cada cor)
                    toneres_ativos = get_toners_ativos_por_maquina(m.id)

                    # Mostra informações dos toners atuais por cor
                    if toneres_ativos:
                        info = "📌 Toners ATUAIS:\n"
                        for t in toneres_ativos:
                            info += f"   • {t.cor}: Instalado em {t.data_instalacao} (Cont: {t.contador_inicial:,})\n"

                        self.info_label.configure(text=info, text_color=CORES['text_primary'])
                    else:
                        self.info_label.configure(
                            text="✅ Nenhum toner ativo - Primeira instalação",
                            text_color=CORES['success']
                        )

                    # Define cores disponíveis baseado no tipo da máquina
                    if m.tipo == "P&B":
                        cores = ["Preto"]
                    else:
                        cores = ["Preto", "Ciano", "Magenta", "Amarelo"]

                    self.combo_troca_cor.configure(values=cores)
                    if cores:
                        self.combo_troca_cor.set(cores[0])

                    # Sugere o MAIOR contador já registrado
                    ultimo = get_ultimo_contador_por_maquina(m.id)
                    self.troca_contador_info.configure(
                        text=f"Maior contador: {ultimo} (use este valor ou maior)"
                    )
                    self.troca_contador.delete(0, "end")
                    self.troca_contador.insert(0, str(ultimo))
                    break

    def registrar_troca_unica(self):
        """Registra uma troca de toner em UM ÚNICO PASSO"""
        try:
            # ========== VALIDAÇÕES ==========
            nome_maquina = self.combo_troca_maquina.get()
            if nome_maquina == "Selecione uma máquina...":
                messagebox.showerror("Erro", "Selecione uma máquina!")
                return

            cor = self.combo_troca_cor.get()
            if not cor or cor == "Selecione uma máquina primeiro":
                messagebox.showerror("Erro", "Selecione a cor do toner!")
                return

            data = self.troca_data.get().strip()
            if not data:
                messagebox.showerror("Erro", "Informe a data da troca!")
                return

            try:
                d, m, a = data.split('/')
                data_sql = f"{a}-{m}-{d}"
            except:
                messagebox.showerror("Erro", "Data inválida! Use DD/MM/AAAA")
                return

            contador_texto = self.troca_contador.get().strip()
            if not contador_texto:
                messagebox.showerror("Erro", "Informe o contador atual!")
                return

            try:
                contador_atual = int(contador_texto.replace('.', ''))
            except:
                messagebox.showerror("Erro", "Contador deve ser um número inteiro!")
                return

            # ========== VERIFICA SE O CONTADOR É MAIOR QUE O ÚLTIMO REGISTRADO ==========
            ultimo_contador = get_ultimo_contador_por_maquina(self.maquina_atual.id)
            if contador_atual < ultimo_contador:
                messagebox.showerror("Erro",
                                     f"Contador não pode ser menor que o último registrado ({ultimo_contador})!\n"
                                     f"O contador da máquina sempre deve aumentar.")
                return

            custo_texto = self.troca_custo.get().strip()
            if not custo_texto:
                messagebox.showerror("Erro", "Informe o custo do toner!")
                return

            try:
                custo_texto = custo_texto.replace(',', '.')
                custo = float(custo_texto)
            except:
                messagebox.showerror("Erro", "Custo inválido!")
                return

            # ========== FINALIZAR TONER ANTERIOR DA MESMA COR (SE EXISTIR) ==========
            from database_operations import get_toner_atual_por_cor

            toner_anterior = get_toner_atual_por_cor(self.maquina_atual.id, cor)

            if toner_anterior:
                # Verifica se contador é maior que o inicial do toner anterior
                if contador_atual <= toner_anterior.contador_inicial:
                    messagebox.showerror("Erro",
                                         f"Contador deve ser maior que o inicial do toner {cor} anterior ({toner_anterior.contador_inicial})!")
                    return

                # Finaliza toner anterior
                finalizar_toner(toner_anterior.id, data_sql, contador_atual)

                # Calcula impressões do toner anterior
                impressoes_anteriores = contador_atual - toner_anterior.contador_inicial
                msg_anterior = (f"✓ Toner {cor} anterior finalizado\n"
                                f"  Impressões: {impressoes_anteriores:,}")
            else:
                msg_anterior = f"✓ Primeiro toner {cor} da máquina"

            # ========== INSTALAR NOVO TONER ==========
            novo_toner = Toner(
                maquina_id=self.maquina_atual.id,
                cor=cor,
                data_instalacao=data_sql,
                contador_inicial=contador_atual,
                custo=custo,
                observacao=self.troca_obs.get()
            )

            novo_id = registrar_toner(novo_toner)

            # ========== MENSAGEM DE SUCESSO ==========
            custo_formatado = f"{custo:.2f}".replace('.', ',')

            msg = (f"✅ Troca registrada com sucesso!\n\n"
                   f"{msg_anterior}\n\n"
                   f"📦 Novo toner {cor} instalado\n"
                   f"💰 Custo: R$ {custo_formatado}\n"
                   f"🔢 Contador: {contador_atual}")

            # Alerta se teve toner anterior com baixo rendimento
            if toner_anterior:
                impressoes_anteriores = contador_atual - toner_anterior.contador_inicial
                if impressoes_anteriores < 14500:
                    msg += f"\n\n⚠️ ATENÇÃO: Toner {cor} anterior teve baixo rendimento!"
                    messagebox.showwarning("Rendimento Baixo", msg)
                else:
                    messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showinfo("Sucesso", msg)

            # ========== LIMPAR FORMULÁRIO ==========
            self.limpar_form_troca()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao registrar troca: {str(e)}")
            print(f"❌ Erro: {e}")

    def aba_historico_cores(self):
        """Interface para visualizar histórico separado por cores"""

        main_frame, canvas, scrollable_frame = self.criar_frame_com_scroll()

        self.criar_titulo(scrollable_frame, "Histórico por Cor",
                          "Visualize o desempenho de cada cor separadamente")

        # Filtros
        filtros_frame = ctk.CTkFrame(scrollable_frame, fg_color=CORES['bg_secondary'], corner_radius=12)
        filtros_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            filtros_frame,
            text="Selecione a máquina:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).pack(side="left", padx=20, pady=15)

        maquinas = listar_maquinas()
        nomes_maquinas = [m.nome for m in maquinas]

        self.combo_hist_cor_maquina = ctk.CTkComboBox(
            filtros_frame,
            values=nomes_maquinas,
            state="readonly",
            width=250,
            height=38,
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            button_color=CORES['accent_blue'],
            button_hover_color=CORES['accent_blue_hover'],
            dropdown_fg_color=CORES['bg_secondary'],
            dropdown_hover_color=CORES['bg_tertiary'],
            dropdown_text_color=CORES['text_primary'],
            command=self.carregar_historico_cores
        )
        self.combo_hist_cor_maquina.pack(side="left", padx=(0, 20), pady=15)

        if maquinas:
            self.combo_hist_cor_maquina.set(maquinas[0].nome)

        # Frame para as abas de cores
        self.notebook = ttk.Notebook(scrollable_frame)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        style = ttk.Style()
        style.configure('TNotebook', background=CORES['bg_secondary'])
        style.configure('TNotebook.Tab', background=CORES['bg_tertiary'], foreground=CORES['text_primary'])
        style.map('TNotebook.Tab', background=[('selected', CORES['accent_blue'])])

        # Carrega dados iniciais
        if maquinas:
            self.carregar_historico_cores()


    def carregar_historico_cores(self, event=None):
        """Carrega o histórico organizado por cores em abas"""

        # Limpa abas existentes
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        nome_maquina = self.combo_hist_cor_maquina.get()
        if not nome_maquina:
            return

        # Busca ID da máquina
        maquinas = listar_maquinas()
        maquina_id = None
        for m in maquinas:
            if m.nome == nome_maquina:
                maquina_id = m.id
                break

        if not maquina_id:
            return

        # Busca resumo por cor
        resumo = resumo_cores_maquina(maquina_id)
        cores = ['Preto', 'Ciano', 'Magenta', 'Amarelo']

        for cor in cores:
            # Busca toner ativo desta cor
            toner_ativo = get_toner_atual_por_cor(maquina_id, cor)

            tab_frame = ctk.CTkFrame(self.notebook, fg_color=CORES['bg_secondary'])
            self.notebook.add(tab_frame, text=f"  {cor}  ")

            # Banner EM USO no topo da aba (se houver toner ativo)
            if toner_ativo:
                em_uso_frame = ctk.CTkFrame(tab_frame, fg_color='#1A3A2A', corner_radius=8)
                em_uso_frame.pack(fill="x", padx=20, pady=(15, 0))

                def fmt_data(d):
                    if d and '-' in d:
                        p = d.split('-')
                        return f"{p[2]}/{p[1]}/{p[0]}"
                    return d or ""

                ctk.CTkLabel(
                    em_uso_frame,
                    text=f"🟢  EM USO  |  Instalado em: {fmt_data(toner_ativo.data_instalacao)}  |  "
                         f"Cont. Inicial: {toner_ativo.contador_inicial:,}".replace(",", ".")
                         + f"  |  Custo: R$ {toner_ativo.custo:.2f}".replace('.', ','),
                    font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                    text_color='#4ADE80'
                ).pack(padx=15, pady=10)

            # Card de resumo (finalizados)
            if cor in resumo:
                r = resumo[cor]

                resumo_frame = ctk.CTkFrame(tab_frame, fg_color=CORES['bg_tertiary'], corner_radius=8)
                resumo_frame.pack(fill="x", padx=20, pady=(10, 10))
                resumo_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

                ctk.CTkLabel(
                    resumo_frame,
                    text=f"Total Finalizados: {r['total_toners']}",
                    font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                    text_color=CORES['text_primary']
                ).grid(row=0, column=0, padx=10, pady=10, sticky="w")

                ctk.CTkLabel(
                    resumo_frame,
                    text=f"Media: {r['media_impressoes']:,.0f} pags".replace(",", "."),
                    font=ctk.CTkFont(family="Inter", size=12),
                    text_color=CORES['text_secondary']
                ).grid(row=0, column=1, padx=10, pady=10, sticky="w")

                ctk.CTkLabel(
                    resumo_frame,
                    text=f"Custo Total: R$ {r['total_custo']:.2f}".replace('.', ','),
                    font=ctk.CTkFont(family="Inter", size=12),
                    text_color=CORES['text_secondary']
                ).grid(row=0, column=2, padx=10, pady=10, sticky="w")

                ctk.CTkLabel(
                    resumo_frame,
                    text=f"R$/pagina: {r['custo_por_pagina']:.4f}".replace('.', ','),
                    font=ctk.CTkFont(family="Inter", size=12),
                    text_color=CORES['text_secondary']
                ).grid(row=0, column=3, padx=10, pady=10, sticky="w")

            elif not toner_ativo:
                ctk.CTkLabel(
                    tab_frame,
                    text=f"Nenhum toner {cor} registrado ainda",
                    font=ctk.CTkFont(family="Inter", size=14),
                    text_color=CORES['text_muted']
                ).pack(expand=True)
                continue

            # Tabela de histórico de finalizados + botão editar
            if cor in resumo:
                # Botão editar acima da tabela
                btn_editar_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
                btn_editar_frame.pack(fill="x", padx=20, pady=(0, 4))

                tree_ref = [None]  # referência mutável para a tree

                def abrir_edicao(t=tab_frame, tr=tree_ref, mid=maquina_id, c=cor):
                    if tr[0] is None:
                        return
                    sel = tr[0].selection()
                    if not sel:
                        messagebox.showwarning("Atencao", "Selecione um registro para editar.")
                        return
                    toner_id = tr[0].set(sel[0], "id")
                    self.janela_editar_toner(int(toner_id), mid)

                ctk.CTkButton(
                    btn_editar_frame,
                    text="✏  Editar Selecionado",
                    height=34,
                    width=200,
                    fg_color=CORES['accent_blue'],
                    hover_color=CORES['accent_blue_hover'],
                    font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                    command=abrir_edicao
                ).pack(side="left")

                table_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
                table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

                style = ttk.Style()
                style.configure("CorHistorico.Treeview",
                    background=CORES['bg_tertiary'], foreground=CORES['text_primary'],
                    rowheight=35, fieldbackground=CORES['bg_tertiary'], font=('Inter', 10))
                style.configure("CorHistorico.Treeview.Heading",
                    background=CORES['bg_secondary'], foreground=CORES['text_primary'],
                    font=('Inter', 11, 'bold'))

                scroll_y = ttk.Scrollbar(table_frame)
                scroll_y.pack(side="right", fill="y")

                # Coluna "id" oculta para identificar o registro
                tree = ttk.Treeview(
                    table_frame,
                    columns=("id", "data_inst", "data_ret", "cont_ini", "cont_fim", "impressoes", "custo", "custo_pag"),
                    show="headings", height=10,
                    yscrollcommand=scroll_y.set, style="CorHistorico.Treeview"
                )
                tree.pack(fill="both", expand=True)
                scroll_y.config(command=tree.yview)
                tree_ref[0] = tree

                tree.heading("id", text="ID")
                tree.heading("data_inst", text="Data Instalacao")
                tree.heading("data_ret", text="Data Retirada")
                tree.heading("cont_ini", text="Cont. Inicial")
                tree.heading("cont_fim", text="Cont. Final")
                tree.heading("impressoes", text="Impressoes")
                tree.heading("custo", text="Custo (R$)")
                tree.heading("custo_pag", text="R$/pagina")

                tree.column("id", width=0, minwidth=0, stretch=False)  # oculta
                for col in ("data_inst","data_ret","cont_ini","cont_fim","impressoes","custo","custo_pag"):
                    tree.column(col, width=120, anchor="center")

                tree.tag_configure('alerta', background=CORES['alerta'])

                # Busca registros com ID do banco
                from database import get_conexao
                conn = get_conexao()
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, data_instalacao, data_retirada, contador_inicial, contador_final, custo "
                    "FROM toners_individual WHERE maquina_id=? AND cor=? AND data_retirada IS NOT NULL "
                    "ORDER BY data_instalacao DESC",
                    (maquina_id, cor)
                )
                rows = cursor.fetchall()
                conn.close()

                def fmt(d):
                    if d and '-' in str(d):
                        p = d.split('-')
                        return f"{p[2]}/{p[1]}/{p[0]}" if len(p)==3 else d
                    return d or ""

                for row in rows:
                    tid, d_inst, d_ret, c_ini, c_fim, custo = row
                    total = (c_fim - c_ini) if c_fim else 0
                    custo_pag = custo / total if total > 0 else 0
                    tags = ('alerta',) if 0 < total < 14500 else ()
                    tree.insert("", "end", values=(
                        tid,
                        fmt(d_inst),
                        fmt(d_ret),
                        f"{c_ini:,}".replace(",", "."),
                        f"{c_fim:,}".replace(",", ".") if c_fim else "-",
                        f"{total:,}".replace(",", "."),
                        f"{custo:.2f}".replace('.', ','),
                        f"{custo_pag:.4f}".replace('.', ',')
                    ), tags=tags)

                # Duplo clique também abre edição
                tree.bind("<Double-1>", lambda e, tr=tree_ref, mid=maquina_id: (
                    self.janela_editar_toner(int(tr[0].set(tr[0].selection()[0], "id")), mid)
                    if tr[0].selection() else None
                ))


    def janela_editar_toner(self, toner_id: int, maquina_id: int):
        """Janela modal para editar um registro de toner"""
        from database import get_conexao
        from calendar_widget import DateEntry

        # Busca dados atuais do toner
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT cor, data_instalacao, data_retirada, contador_inicial, contador_final, custo, observacao "
            "FROM toners_individual WHERE id=?", (toner_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Erro", "Registro nao encontrado.")
            return

        cor_atual, d_inst, d_ret, c_ini, c_fim, custo, obs = row

        def fmt(d):
            if d and '-' in str(d):
                p = d.split('-')
                return f"{p[2]}/{p[1]}/{p[0]}" if len(p)==3 else d
            return d or ""

        janela = ctk.CTkToplevel(self)
        janela.title("Editar Toner")
        janela.geometry("480x560")
        janela.resizable(False, False)
        janela.grab_set()
        janela.focus_set()
        x = self.winfo_rootx() + (self.winfo_width() - 480) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 560) // 2
        janela.geometry(f"+{x}+{y}")

        ctk.CTkLabel(janela, text="Editar Registro de Toner",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                     text_color=CORES['text_primary']).pack(padx=30, pady=(24, 4), anchor="w")
        ctk.CTkLabel(janela, text=f"ID: {toner_id}",
                     font=ctk.CTkFont(family="Inter", size=11),
                     text_color=CORES['text_muted']).pack(padx=30, anchor="w")

        form = ctk.CTkFrame(janela, fg_color="transparent")
        form.pack(padx=30, pady=16, fill="x")
        form.columnconfigure(1, weight=1)

        def label(row, texto):
            ctk.CTkLabel(form, text=texto,
                         font=ctk.CTkFont(family="Inter", size=12),
                         text_color=CORES['text_secondary']
                         ).grid(row=row, column=0, sticky="e", padx=(0,10), pady=6)

        # Cor
        label(0, "Cor:")
        cores_opcoes = ["Preto", "Ciano", "Magenta", "Amarelo"]
        combo_cor = ctk.CTkComboBox(form, values=cores_opcoes, state="readonly",
                                    width=200, height=36,
                                    fg_color=CORES['bg_tertiary'], border_width=0,
                                    button_color=CORES['accent_blue'],
                                    font=ctk.CTkFont(family="Inter", size=12))
        combo_cor.grid(row=0, column=1, sticky="w", pady=6)
        combo_cor.set(cor_atual)

        # Data instalação
        label(1, "Data Instalacao:")
        entry_inst = DateEntry(form, width=160, height=36,
                               fg_color=CORES['bg_tertiary'], border_width=0,
                               font=ctk.CTkFont(family="Inter", size=12))
        entry_inst.grid(row=1, column=1, sticky="w", pady=6)
        entry_inst.insert(0, fmt(d_inst))

        # Data retirada
        label(2, "Data Retirada:")
        entry_ret = DateEntry(form, width=160, height=36,
                              fg_color=CORES['bg_tertiary'], border_width=0,
                              font=ctk.CTkFont(family="Inter", size=12))
        entry_ret.grid(row=2, column=1, sticky="w", pady=6)
        if d_ret:
            entry_ret.insert(0, fmt(d_ret))

        # Cont. Inicial
        label(3, "Cont. Inicial:")
        entry_ini = ctk.CTkEntry(form, width=160, height=36,
                                 fg_color=CORES['bg_tertiary'], border_width=0,
                                 font=ctk.CTkFont(family="Inter", size=12))
        entry_ini.grid(row=3, column=1, sticky="w", pady=6)
        entry_ini.insert(0, str(c_ini or 0))

        # Cont. Final
        label(4, "Cont. Final:")
        entry_fim = ctk.CTkEntry(form, width=160, height=36,
                                 fg_color=CORES['bg_tertiary'], border_width=0,
                                 font=ctk.CTkFont(family="Inter", size=12))
        entry_fim.grid(row=4, column=1, sticky="w", pady=6)
        entry_fim.insert(0, str(c_fim or ""))

        # Custo
        label(5, "Custo (R$):")
        entry_custo = ctk.CTkEntry(form, width=160, height=36,
                                   fg_color=CORES['bg_tertiary'], border_width=0,
                                   font=ctk.CTkFont(family="Inter", size=12))
        entry_custo.grid(row=5, column=1, sticky="w", pady=6)
        entry_custo.insert(0, f"{custo:.2f}".replace('.', ','))

        lbl_erro = ctk.CTkLabel(janela, text="", font=ctk.CTkFont(size=11),
                                text_color="#E74C3C")
        lbl_erro.pack(padx=30, anchor="w")

        def converter_data_para_iso(d):
            d = d.strip()
            if not d:
                return None
            if '/' in d:
                p = d.split('/')
                if len(p) == 3:
                    return f"{p[2]}-{p[1]}-{p[0]}"
            return d

        def salvar():
            nova_cor    = combo_cor.get()
            nova_inst   = converter_data_para_iso(entry_inst.get())
            nova_ret    = converter_data_para_iso(entry_ret.get())
            ini_raw     = entry_ini.get().strip().replace(".", "").replace(",", "")
            fim_raw     = entry_fim.get().strip().replace(".", "").replace(",", "")
            custo_raw   = entry_custo.get().strip().replace(",", ".")

            if not nova_inst:
                lbl_erro.configure(text="Data de instalacao obrigatoria.")
                return
            try:
                novo_ini = int(ini_raw) if ini_raw else 0
            except ValueError:
                lbl_erro.configure(text="Contador inicial invalido.")
                return
            try:
                novo_fim = int(fim_raw) if fim_raw else None
            except ValueError:
                lbl_erro.configure(text="Contador final invalido.")
                return
            try:
                novo_custo = float(custo_raw) if custo_raw else 0.0
            except ValueError:
                lbl_erro.configure(text="Custo invalido.")
                return

            editar_toner(toner_id, nova_cor, nova_inst, nova_ret, novo_ini, novo_fim, novo_custo)
            janela.destroy()
            self.carregar_historico_cores()
            messagebox.showinfo("Sucesso", "Registro atualizado com sucesso!")

        btn_frame = ctk.CTkFrame(janela, fg_color="transparent")
        btn_frame.pack(padx=30, pady=16, fill="x")

        ctk.CTkButton(btn_frame, text="Salvar Alteracoes", height=40,
                      fg_color=CORES['success'], hover_color="#3A7A5A",
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      command=salvar).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(btn_frame, text="Cancelar", height=40,
                      fg_color=CORES['bg_tertiary'], hover_color=CORES['bg_secondary'],
                      font=ctk.CTkFont(family="Inter", size=13),
                      command=janela.destroy).pack(side="left", expand=True, fill="x")

    def limpar_form_troca(self):
        """Limpa o formulário de troca"""
        self.combo_troca_maquina.set("Selecione uma máquina...")
        self.combo_troca_cor.set("Selecione uma máquina primeiro")
        self.troca_data.delete(0, "end")
        self.troca_data.insert(0, datetime.now().strftime("%d/%m/%Y"))
        self.troca_contador.delete(0, "end")
        self.troca_custo.delete(0, "end")
        self.troca_custo.insert(0, "636")
        self.troca_obs.delete(0, "end")
        self.info_label.configure(
            text="Selecione uma máquina para ver o toner atual",
            text_color=CORES['text_secondary']
        )
        self.troca_contador_info.configure(text="")
        self.maquina_atual = None

    # ========== ABA 4: RELATÓRIOS ==========

    # ========== ABA: CONTADORES SEMANAIS ==========
    def aba_contadores(self):
        import tkinter as tk

        main_frame, canvas, scrollable_frame = self.criar_frame_com_scroll()
        self.criar_titulo(scrollable_frame, "Contadores Semanais",
                          "Registre e acompanhe a evolucao do contador de cada maquina")

        maquinas = listar_maquinas()
        if not maquinas:
            ctk.CTkLabel(scrollable_frame, text="Nenhuma maquina cadastrada.",
                         font=ctk.CTkFont(size=14), text_color=CORES['text_muted']).pack(pady=40)
            return

        # ---- Seletor de máquina ----
        sel_frame = ctk.CTkFrame(scrollable_frame, fg_color=CORES['bg_secondary'], corner_radius=12)
        sel_frame.pack(fill="x", padx=20, pady=(0, 14))

        ctk.CTkLabel(sel_frame, text="Maquina:",
                     font=ctk.CTkFont(family="Inter", size=12),
                     text_color=CORES['text_secondary']).pack(side="left", padx=20, pady=14)

        combo_maq = ctk.CTkComboBox(
            sel_frame, values=[m.nome for m in maquinas],
            state="readonly", width=260, height=38,
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color=CORES['bg_tertiary'], border_width=0,
            button_color=CORES['accent_blue'],
            button_hover_color=CORES['accent_blue_hover'],
            dropdown_fg_color=CORES['bg_secondary'],
            dropdown_hover_color=CORES['bg_tertiary'],
            dropdown_text_color=CORES['text_primary']
        )
        combo_maq.pack(side="left", padx=(0, 20), pady=14)
        combo_maq.set(maquinas[0].nome)

        # Contador atual em destaque
        lbl_atual = ctk.CTkLabel(
            sel_frame,
            text="",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color=CORES['accent_blue']
        )
        lbl_atual.pack(side="left", padx=20, pady=14)

        # ---- Formulário de registro ----
        form_card = self.criar_card(scrollable_frame, "Novo Registro")
        form_card.pack(fill="x", padx=20, pady=(0, 14))

        form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
        form_inner.pack(fill="x", padx=20, pady=(0, 16))
        form_inner.columnconfigure(1, weight=1)

        def lbl(row, texto):
            ctk.CTkLabel(form_inner, text=texto,
                         font=ctk.CTkFont(family="Inter", size=12),
                         text_color=CORES['text_secondary']
                         ).grid(row=row, column=0, sticky="e", padx=(0, 12), pady=6)

        lbl(0, "Data:")
        entry_data = DateEntry(form_inner, width=160, height=36,
                               fg_color=CORES['bg_tertiary'], border_width=0,
                               font=ctk.CTkFont(family="Inter", size=12))
        entry_data.grid(row=0, column=1, sticky="w", pady=6)
        entry_data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        lbl(1, "Contador:")
        entry_contador = ctk.CTkEntry(form_inner, width=180, height=36,
                                      placeholder_text="Ex: 125480",
                                      fg_color=CORES['bg_tertiary'], border_width=0,
                                      font=ctk.CTkFont(family="Inter", size=12))
        entry_contador.grid(row=1, column=1, sticky="w", pady=6)

        lbl(2, "Observacao:")
        entry_obs = ctk.CTkEntry(form_inner, width=320, height=36,
                                 placeholder_text="Opcional",
                                 fg_color=CORES['bg_tertiary'], border_width=0,
                                 font=ctk.CTkFont(family="Inter", size=12))
        entry_obs.grid(row=2, column=1, sticky="w", pady=6)

        lbl_erro = ctk.CTkLabel(form_inner, text="",
                                font=ctk.CTkFont(size=11), text_color="#E74C3C")
        lbl_erro.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 4))

        # ---- Área do gráfico e tabela (referências mutáveis) ----
        grafico_frame_ref = [None]
        tree_ref = [None]

        def get_maquina_id():
            nome = combo_maq.get()
            for m in maquinas:
                if m.nome == nome:
                    return m.id
            return None

        def converter_data_iso(d):
            d = d.strip()
            if '/' in d:
                p = d.split('/')
                if len(p) == 3:
                    return f"{p[2]}-{p[1]}-{p[0]}"
            return d

        def fmt_data_br(d):
            if d and '-' in str(d):
                p = d.split('-')
                if len(p) == 3:
                    return f"{p[2]}/{p[1]}/{p[0]}"
            return d or ""

        def registrar():
            mid = get_maquina_id()
            if not mid:
                lbl_erro.configure(text="Selecione uma maquina.")
                return
            data_str = entry_data.get().strip()
            cont_str = entry_contador.get().strip().replace(".", "").replace(",", "")
            if not data_str:
                lbl_erro.configure(text="Informe a data.")
                return
            if not cont_str.isdigit():
                lbl_erro.configure(text="Contador invalido.")
                return
            lbl_erro.configure(text="")
            registrar_contador(mid, converter_data_iso(data_str), int(cont_str), entry_obs.get().strip())
            entry_contador.delete(0, "end")
            entry_obs.delete(0, "end")
            atualizar_tabela_e_grafico()

        ctk.CTkButton(
            form_inner, text="＋  Registrar Contador",
            height=38, width=220,
            fg_color=CORES['success'], hover_color="#3A7A5A",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            command=registrar
        ).grid(row=4, column=1, sticky="w", pady=(8, 0))

        # ---- Gráfico ----
        grafico_card = self.criar_card(scrollable_frame, "Evolucao do Contador")
        grafico_card.pack(fill="x", padx=20, pady=(0, 14))

        grafico_inner = ctk.CTkFrame(grafico_card, fg_color="transparent")
        grafico_inner.pack(fill="x", padx=10, pady=(0, 10))
        grafico_frame_ref[0] = grafico_inner

        # ---- Tabela de histórico ----
        hist_card = self.criar_card(scrollable_frame, "Historico de Leituras")
        hist_card.pack(fill="x", padx=20, pady=(0, 20))

        tbl_frame = ctk.CTkFrame(hist_card, fg_color="transparent")
        tbl_frame.pack(fill="x", padx=10, pady=(0, 10))

        style = ttk.Style()
        style.configure("Cont.Treeview",
            background=CORES['bg_tertiary'], foreground=CORES['text_primary'],
            rowheight=32, fieldbackground=CORES['bg_tertiary'], font=('Inter', 10))
        style.configure("Cont.Treeview.Heading",
            background=CORES['bg_secondary'], foreground=CORES['text_primary'],
            font=('Inter', 11, 'bold'))

        scroll_y = ttk.Scrollbar(tbl_frame)
        scroll_y.pack(side="right", fill="y")

        tree = ttk.Treeview(tbl_frame,
            columns=("data", "contador", "variacao", "obs"),
            show="headings", height=10,
            yscrollcommand=scroll_y.set, style="Cont.Treeview")
        tree.pack(fill="x")
        scroll_y.config(command=tree.yview)
        tree_ref[0] = tree

        tree.heading("data", text="Data")
        tree.heading("contador", text="Contador")
        tree.heading("variacao", text="Variacao (+/-)")
        tree.heading("obs", text="Observacao")
        tree.column("data", width=120, anchor="center")
        tree.column("contador", width=140, anchor="center")
        tree.column("variacao", width=140, anchor="center")
        tree.column("obs", width=300, anchor="w")

        tree.tag_configure("alta", foreground="#27AE60")
        tree.tag_configure("baixa", foreground="#E74C3C")

        # Botão deletar
        def deletar_selecionado():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atencao", "Selecione um registro para deletar.")
                return
            rid = int(tree.set(sel[0], "data").split("__id__")[-1]) if "__id__" in tree.set(sel[0], "data") else None
            # usa iid como id
            rid = int(sel[0])
            if messagebox.askyesno("Confirmar", "Deletar este registro?"):
                deletar_contador(rid)
                atualizar_tabela_e_grafico()

        ctk.CTkButton(
            hist_card, text="🗑  Deletar Selecionado",
            height=32, width=180,
            fg_color="#C0392B", hover_color="#922B21",
            font=ctk.CTkFont(family="Inter", size=11),
            command=deletar_selecionado
        ).pack(anchor="e", padx=10, pady=(0, 10))

        def desenhar_grafico(registros):
            for w in grafico_frame_ref[0].winfo_children():
                w.destroy()

            if len(registros) < 2:
                ctk.CTkLabel(grafico_frame_ref[0],
                             text="Registre ao menos 2 leituras para ver o grafico.",
                             font=ctk.CTkFont(size=12), text_color=CORES['text_muted']
                             ).pack(pady=20)
                return

            # Canvas do gráfico
            largura, altura = 860, 220
            pad_l, pad_r, pad_t, pad_b = 70, 30, 20, 40

            c = tk.Canvas(grafico_frame_ref[0],
                          width=largura, height=altura,
                          bg=CORES['bg_tertiary'], highlightthickness=0)
            c.pack(pady=10)

            dados = list(reversed(registros))  # cronológico
            valores = [r['contador'] for r in dados]
            datas   = [fmt_data_br(r['data'])[:5] for r in dados]  # DD/MM

            vmin, vmax = min(valores), max(valores)
            if vmin == vmax:
                vmin -= 1000; vmax += 1000

            def px(i):
                n = len(dados)
                return pad_l + i * (largura - pad_l - pad_r) / max(n - 1, 1)

            def py(v):
                return pad_t + (1 - (v - vmin) / (vmax - vmin)) * (altura - pad_t - pad_b)

            # Grade
            for i in range(5):
                y = pad_t + i * (altura - pad_t - pad_b) / 4
                v = vmax - i * (vmax - vmin) / 4
                c.create_line(pad_l, y, largura - pad_r, y,
                              fill="#444" if CORES['bg_primary'] == "#1A1B2E" else "#DDD",
                              dash=(4, 4))
                c.create_text(pad_l - 6, y, text=f"{int(v):,}".replace(",", "."),
                              anchor="e", font=("Inter", 8),
                              fill=CORES['text_secondary'])

            # Linha do gráfico
            pontos = [(px(i), py(v)) for i, v in enumerate(valores)]
            for i in range(len(pontos) - 1):
                c.create_line(pontos[i][0], pontos[i][1],
                              pontos[i+1][0], pontos[i+1][1],
                              fill="#4472C4", width=2, smooth=True)

            # Pontos e labels de data
            for i, (x, y) in enumerate(pontos):
                c.create_oval(x-5, y-5, x+5, y+5, fill="#4472C4", outline="white", width=2)
                c.create_text(x, altura - pad_b + 8, text=datas[i],
                              font=("Inter", 8), fill=CORES['text_secondary'])

        def atualizar_tabela_e_grafico():
            mid = get_maquina_id()
            if not mid:
                return
            # Atualiza o label do contador atual buscando direto do banco
            from database import get_conexao
            conn_tmp = get_conexao()
            cur_tmp = conn_tmp.cursor()
            cur_tmp.execute("SELECT contador_atual FROM maquinas WHERE id=?", (mid,))
            row_tmp = cur_tmp.fetchone()
            conn_tmp.close()
            if row_tmp and row_tmp[0]:
                lbl_atual.configure(
                    text=f"Contador Atual: {row_tmp[0]:,}".replace(",", ".")
                )
            else:
                lbl_atual.configure(text="Contador Atual: —")
            registros = listar_contadores(mid)

            # Tabela
            for item in tree.get_children():
                tree.delete(item)

            for i, r in enumerate(registros):
                # registros está ordenado do mais recente ao mais antigo (DESC)
                # variação = atual - anterior (i+1 é o registro mais antigo)
                if i < len(registros) - 1:
                    variacao = r['contador'] - registros[i + 1]['contador']
                    if variacao > 0:
                        var_txt = f"+{variacao:,}".replace(",", ".")
                        tag = "alta"
                    elif variacao < 0:
                        var_txt = f"{variacao:,}".replace(",", ".")
                        tag = "baixa"
                    else:
                        var_txt = "—"
                        tag = ""
                else:
                    # Registro mais antigo: sem anterior para comparar
                    var_txt = "Inicial"
                    tag = ""

                tree.insert("", "end", iid=str(r['id']), values=(
                    fmt_data_br(r['data']),
                    f"{r['contador']:,}".replace(",", "."),
                    var_txt,
                    r['observacao']
                ), tags=(tag,))

            desenhar_grafico(registros)

        # Recarrega ao trocar máquina
        combo_maq.configure(command=lambda e: atualizar_tabela_e_grafico())

        # Carrega dados iniciais
        atualizar_tabela_e_grafico()

    def aba_relatorios(self):
        """Interface para gerar relatórios"""

        main_frame, canvas, scrollable_frame = self.criar_frame_com_scroll()

        self.criar_titulo(scrollable_frame, "Relatórios",
                          "Gere relatórios detalhados de rendimento dos toners")

        card = self.criar_card(scrollable_frame, "📊 Gerar Relatório")
        card.pack(fill="both", padx=20, pady=10, expand=True)

        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack(fill="both", padx=20, pady=10)
        form_frame.grid_columnconfigure(1, weight=1)

        row = 0

        # Máquina
        ctk.CTkLabel(
            form_frame,
            text="Máquina:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=(0, 10), pady=8, sticky="e")

        maquinas = listar_maquinas()
        nomes = ["Todas"] + [m.nome for m in maquinas]

        self.combo_rel_maquina = ctk.CTkComboBox(
            form_frame,
            values=nomes,
            state="readonly",
            width=250,
            height=38,
            font=ctk.CTkFont(family="Inter", size=12),
            fg_color=CORES['bg_tertiary'],
            border_width=0,
            button_color=CORES['accent_blue'],
            button_hover_color=CORES['accent_blue_hover'],
            dropdown_fg_color=CORES['bg_secondary'],
            dropdown_hover_color=CORES['bg_tertiary'],
            dropdown_text_color=CORES['text_primary']
        )
        self.combo_rel_maquina.grid(row=row, column=1, pady=8, sticky="w")
        self.combo_rel_maquina.set("Todas")
        row += 1

        # Período
        ctk.CTkLabel(
            form_frame,
            text="Período:",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color=CORES['text_secondary']
        ).grid(row=row, column=0, padx=(0, 10), pady=8, sticky="e")

        frame_periodo = ctk.CTkFrame(form_frame, fg_color="transparent")
        frame_periodo.grid(row=row, column=1, pady=8, sticky="w")

        ctk.CTkLabel(frame_periodo, text="De:").pack(side="left", padx=(0, 5))
        self.rel_data_inicio = DateEntry(frame_periodo, width=100)
        self.rel_data_inicio.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(frame_periodo, text="Até:").pack(side="left", padx=(0, 5))
        self.rel_data_fim = DateEntry(frame_periodo, width=100)
        self.rel_data_fim.pack(side="left")
        row += 1

        # Botões
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))

        btn_pdf = ctk.CTkButton(
            btn_frame,
            text="📄 Gerar PDF",
            command=lambda: self.gerar_relatorio("pdf"),
            height=42,
            width=150,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color=CORES['accent_blue'],
            hover_color=CORES['accent_blue_hover'],
            corner_radius=8
        )
        btn_pdf.pack(side="left", padx=(0, 10))

        btn_excel = ctk.CTkButton(
            btn_frame,
            text="📗 Gerar Excel",
            command=lambda: self.gerar_relatorio("excel"),
            height=42,
            width=150,
            font=ctk.CTkFont(family="Inter", size=13),
            fg_color=CORES['accent_green'],
            hover_color=CORES['accent_green_hover'],
            corner_radius=8
        )
        btn_excel.pack(side="left", padx=(0, 10))



    def _abrir_gerenciador_apos_salvar(self, caminho):
        """Abre o gerenciador de arquivos na pasta do arquivo salvo (cross-platform)."""
        import subprocess
        import platform
        pasta = os.path.dirname(os.path.abspath(caminho))
        sistema = platform.system()
        try:
            if sistema == "Windows":
                os.startfile(pasta)
            elif sistema == "Darwin":
                subprocess.Popen(["open", pasta])
            else:  # Linux e derivados
                subprocess.Popen(["xdg-open", pasta])
        except Exception as e:
            print(f"Aviso: não foi possível abrir o gerenciador de arquivos: {e}")

    def gerar_relatorio(self, formato):
        """Gera relatório no formato especificado, pedindo destino via filedialog."""
        try:
            maquina_nome = self.combo_rel_maquina.get()
            data_inicio = self.rel_data_inicio.get()
            data_fim = self.rel_data_fim.get()

            data_inicio_sql = None
            data_fim_sql = None

            if data_inicio:
                try:
                    d, m, a = data_inicio.split('/')
                    data_inicio_sql = f"{a}-{m}-{d}"
                except:
                    messagebox.showerror("Erro", "Data inicial inválida!")
                    return

            if data_fim:
                try:
                    d, m, a = data_fim.split('/')
                    data_fim_sql = f"{a}-{m}-{d}"
                except:
                    messagebox.showerror("Erro", "Data final inválida!")
                    return

            periodo = f"{data_inicio or 'Início'} a {data_fim or 'Fim'}"

            dados_maquinas = []

            if maquina_nome == "Todas":
                maquinas = listar_maquinas()
                for m in maquinas:
                    rend_dict = calcular_rendimento_por_cor(
                        maquina_id=m.id,
                        data_inicio=data_inicio_sql,
                        data_fim=data_fim_sql
                    )
                    rendimentos = [r for lst in rend_dict.values() for r in lst]
                    ativos = listar_toners_por_maquina(m.id, apenas_ativos=True)
                    if rendimentos or ativos:
                        dados_maquinas.append({
                            'nome': m.nome,
                            'rendimentos': rendimentos,
                            'ativos': ativos
                        })
            else:
                maquinas = listar_maquinas()
                for m in maquinas:
                    if m.nome == maquina_nome:
                        rend_dict = calcular_rendimento_por_cor(
                            maquina_id=m.id,
                            data_inicio=data_inicio_sql,
                            data_fim=data_fim_sql
                        )
                        rendimentos = [r for lst in rend_dict.values() for r in lst]
                        ativos = listar_toners_por_maquina(m.id, apenas_ativos=True)
                        if rendimentos or ativos:
                            dados_maquinas.append({
                                'nome': m.nome,
                                'rendimentos': rendimentos,
                                'ativos': ativos
                            })
                        break

            if not dados_maquinas:
                messagebox.showinfo("Sem dados", "Nenhum toner registrado no período!")
                return

            import datetime as dt
            timestamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_base = maquina_nome if maquina_nome != "Todas" else "relatorio_toners"
            nome_base = nome_base.replace(" ", "_")

            if formato == "pdf":
                if len(dados_maquinas) == 1:
                    caminho = filedialog.asksaveasfilename(
                        title="Salvar PDF como...",
                        defaultextension=".pdf",
                        filetypes=[("PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
                        initialfile=f"toners_{nome_base}_{timestamp}.pdf"
                    )
                    if not caminho:
                        return
                    arquivo = gerar_relatorio_pdf(
                        dados_maquinas[0]['rendimentos'],
                        dados_maquinas[0]['nome'],
                        periodo,
                        caminho_destino=caminho,
                        toners_ativos=dados_maquinas[0].get('ativos', [])
                    )
                    messagebox.showinfo("Sucesso", f"PDF gerado!\n\n{arquivo}")
                    self._abrir_gerenciador_apos_salvar(arquivo)
                else:
                    pasta = filedialog.askdirectory(title="Escolha a pasta para salvar os PDFs")
                    if not pasta:
                        return
                    arquivos = []
                    for dado in dados_maquinas:
                        nome_arq = os.path.join(pasta, f"toners_{dado['nome'].replace(' ','_')}_{timestamp}.pdf")
                        arq = gerar_relatorio_pdf(dado['rendimentos'], dado['nome'], periodo, caminho_destino=nome_arq, toners_ativos=dado.get('ativos', []))
                        arquivos.append(arq)
                    messagebox.showinfo("Sucesso", f"{len(arquivos)} PDFs salvos em:\n{pasta}")
                    self._abrir_gerenciador_apos_salvar(pasta)

            elif formato == "excel":
                caminho = filedialog.asksaveasfilename(
                    title="Salvar Excel como...",
                    defaultextension=".xlsx",
                    filetypes=[("Excel", "*.xlsx"), ("Todos os arquivos", "*.*")],
                    initialfile=f"toners_{nome_base}_{timestamp}.xlsx"
                )
                if not caminho:
                    return
                arquivo = gerar_relatorio_excel(dados_maquinas, periodo, caminho_destino=caminho)
                messagebox.showinfo("Sucesso", f"Excel gerado!\n\n{arquivo}")
                self._abrir_gerenciador_apos_salvar(arquivo)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")
            print(f"❌ Erro: {e}")


# ========== PONTO DE ENTRADA ==========
if __name__ == "__main__":
    app = ControleTonerApp()
    app.mainloop()