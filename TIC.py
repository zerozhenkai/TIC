import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageEnhance
import yt_dlp
import threading
from datetime import datetime
import shutil

class MediaToolsPro:
    def __init__(self, root):
        self.root = root
        self.root.title("MediaTools Pro - Organizado por Mídia")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f5f5f5')
        
        # Variáveis de controle
        self.current_file = ""
        self.batch_files = []
        self.current_file_index = 0
        self.downloading = False
        self.preview_image = None
        self.original_image = None
        self.download_folders = {
            'images': os.path.expanduser("~/Downloads/MediaTools_Images"),
            'videos': os.path.expanduser("~/Downloads/MediaTools_Videos"),
            'audio': os.path.expanduser("~/Downloads/MediaTools_Audio")
        }
        
        # Criar pastas de downloads se não existirem
        for folder in self.download_folders.values():
            os.makedirs(folder, exist_ok=True)
        
        # Formatos suportados para cada tipo de mídia
        self.supported_formats = {
            'images': {
                "JPEG": ".jpg", "PNG": ".png", "GIF": ".gif", 
                "BMP": ".bmp", "WEBP": ".webp", "TIFF": ".tiff", 
                "AVIF": ".avif", "ICO": ".ico", "TGA": ".tga"
            },
            'videos': {
                "MP4": ".mp4", "MOV": ".mov", "AVI": ".avi",
                "MKV": ".mkv", "WEBM": ".webm", "MPEG": ".mpeg",
                "GIF": ".gif"
            },
            'audio': {
                "MP3": ".mp3", "WAV": ".wav", "OGG": ".ogg",
                "AAC": ".aac", "FLAC": ".flac", "M4A": ".m4a"
            }
        }
        
        # Sites suportados para download organizados por tipo
        self.supported_sites = {
            'images': ["Qualquer URL de imagem"],
            'videos': ["YouTube", "Vimeo", "Facebook", "Twitter", "Instagram", "TikTok", "Dailymotion"],
            'audio': ["YouTube", "SoundCloud", "Bandcamp", "Mixcloud"]
        }
        
        # Configurar estilo
        self.setup_styles()
        
        # Configurar interface
        self.setup_ui()
    
    def setup_styles(self):
        """Configura os estilos visuais da aplicação"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurações gerais
        style.configure('.', background='#f5f5f5', foreground='#333', font=('Segoe UI', 9))
        style.configure('TNotebook', background='#f5f5f5', borderwidth=0)
        style.configure('TNotebook.Tab', 
                      padding=[15, 5], 
                      background='#e0e0e0', 
                      foreground='#555',
                      font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab', 
                 background=[('selected', '#4a6baf')], 
                 foreground=[('selected', 'white')])
        
        # Botões
        style.configure('TButton', 
                       padding=6, 
                       relief='flat', 
                       background='#4a6baf', 
                       foreground='white',
                       font=('Segoe UI', 9, 'bold'))
        style.map('TButton', 
                 background=[('active', '#3a5a9f'), ('disabled', '#cccccc')])
        
        # Estilos específicos para tipos de mídia
        style.configure('Image.TFrame', background='#fff5f5')
        style.configure('Video.TFrame', background='#f5f5ff')
        style.configure('Audio.TFrame', background='#f5fff5')
        
        # Barra de progresso
        style.configure('Horizontal.TProgressbar', 
                      thickness=22, 
                      troughcolor='#e0e0e0',
                      background='#4a6baf')
    
    def setup_ui(self):
        """Configura a interface gráfica com abas organizadas por tipo de mídia"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook (abas por tipo de mídia)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Abas para cada tipo de mídia
        self.setup_image_tab()
        self.setup_video_tab()
        self.setup_audio_tab()
        
        # Rodapé
        footer = ttk.Frame(main_frame)
        footer.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(footer, 
                 text="MediaTools Pro - Organizado por Tipo de Mídia © 2023", 
                 foreground='#666',
                 font=('Segoe UI', 8)).pack(side=tk.RIGHT)
    
    def setup_image_tab(self):
        """Configura a aba para processamento de imagens"""
        tab_image = ttk.Frame(self.notebook, style='Image.TFrame')
        self.notebook.add(tab_image, text="  🖼️ Processador de Imagens  ")
        
        # Layout principal com dois painéis lado a lado
        main_panel = ttk.Frame(tab_image)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Painel esquerdo - Controles (60%)
        left_panel = ttk.Frame(main_panel)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Painel direito - Visualização (40%)
        right_panel = ttk.Frame(main_panel)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # ===== PAINEL ESQUERDO - CONTROLES =====
        
        # Seção de seleção de arquivo
        file_frame = ttk.LabelFrame(left_panel, text=" Seleção de Arquivos ", padding=10)
        file_frame.pack(fill=tk.X, pady=5)
        
        # Botões de seleção
        select_buttons_frame = ttk.Frame(file_frame)
        select_buttons_frame.pack(fill=tk.X, pady=5)
        
        btn_select = ttk.Button(select_buttons_frame, 
                              text="📁 Selecionar Imagem", 
                              command=lambda: self.select_file('images'))
        btn_select.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_select_batch = ttk.Button(select_buttons_frame, 
                                    text="📂 Selecionar Múltiplas", 
                                    command=lambda: self.select_batch_files('images'))
        btn_select_batch.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Navegação entre arquivos
        nav_frame = ttk.Frame(file_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        btn_prev = ttk.Button(nav_frame, 
                            text="◀ Anterior", 
                            command=lambda: self.navigate_files('prev', 'images'))
        btn_prev.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        btn_next = ttk.Button(nav_frame, 
                            text="Próximo ▶", 
                            command=lambda: self.navigate_files('next', 'images'))
        btn_next.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        # Labels de informação
        self.lbl_image_file = ttk.Label(file_frame, text="Nenhuma imagem selecionada")
        self.lbl_image_file.pack(pady=2)
        
        self.lbl_batch_images = ttk.Label(file_frame, text="", foreground='#4a6baf')
        self.lbl_batch_images.pack(pady=2)
        
        # Seção de conversão e ajustes lado a lado
        tools_frame = ttk.Frame(left_panel)
        tools_frame.pack(fill=tk.X, pady=5)
        
        # Coluna 1 - Conversão
        convert_col = ttk.Frame(tools_frame)
        convert_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        convert_frame = ttk.LabelFrame(convert_col, text=" Conversão ", padding=8)
        convert_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(convert_frame, text="Formato de Saída:").pack(anchor=tk.W)
        self.image_format_var = tk.StringVar(value="JPEG")
        format_menu = ttk.Combobox(convert_frame, 
                                 textvariable=self.image_format_var, 
                                 values=list(self.supported_formats['images'].keys()), 
                                 state="readonly")
        format_menu.pack(fill=tk.X, pady=2)
        
        # Controle de qualidade
        self.image_quality_var = tk.IntVar(value=90)
        quality_frame = ttk.Frame(convert_frame)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="Qualidade:").pack(side=tk.LEFT)
        ttk.Scale(quality_frame, 
                 from_=1, 
                 to=100, 
                 orient=tk.HORIZONTAL,
                 variable=self.image_quality_var,
                 command=lambda v: self.image_quality_var.set(int(float(v)))).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(quality_frame, textvariable=self.image_quality_var).pack(side=tk.LEFT, padx=5)
        
        # Botões de conversão
        btn_convert = ttk.Button(convert_frame, 
                               text="🔄 Converter Imagem", 
                               command=self.convert_image)
        btn_convert.pack(fill=tk.X, pady=2)
        
        btn_convert_batch = ttk.Button(convert_frame, 
                                     text="🔄 Converter Lote", 
                                     command=self.convert_image_batch)
        btn_convert_batch.pack(fill=tk.X, pady=2)
        
        # Coluna 2 - Ajustes
        adjust_col = ttk.Frame(tools_frame)
        adjust_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        adjust_frame = ttk.LabelFrame(adjust_col, text=" Ajustes Rápidos ", padding=8)
        adjust_frame.pack(fill=tk.BOTH, expand=True)
        
        # Botões de ajuste em grid
        btn_rotate = ttk.Button(adjust_frame, 
                              text="↻ Girar 90°", 
                              command=lambda: self.adjust_image('rotate'))
        btn_rotate.pack(fill=tk.X, pady=1)
        
        btn_mirror = ttk.Button(adjust_frame, 
                              text="↔ Espelhar", 
                              command=lambda: self.adjust_image('mirror'))
        btn_mirror.pack(fill=tk.X, pady=1)
        
        btn_brightness_plus = ttk.Button(adjust_frame, 
                                       text="☀ Brilho +", 
                                       command=lambda: self.adjust_image('brightness'))
        btn_brightness_plus.pack(fill=tk.X, pady=1)
        
        btn_brightness_minus = ttk.Button(adjust_frame, 
                                        text="☀ Brilho -", 
                                        command=lambda: self.adjust_image('darkness'))
        btn_brightness_minus.pack(fill=tk.X, pady=1)
        
        # Seção de renomeação
        rename_frame = ttk.LabelFrame(left_panel, text=" Renomeação ", padding=8)
        rename_frame.pack(fill=tk.X, pady=5)
        
        rename_input_frame = ttk.Frame(rename_frame)
        rename_input_frame.pack(fill=tk.X, pady=2)
        
        self.image_name_var = tk.StringVar()
        ttk.Entry(rename_input_frame, textvariable=self.image_name_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_rename = ttk.Button(rename_input_frame, 
                              text="✏️ Renomear", 
                              command=self.rename_image)
        btn_rename.pack(side=tk.RIGHT)
        
        # Seção de download
        download_frame = ttk.LabelFrame(left_panel, text=" Download ", padding=8)
        download_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(download_frame, text="URL da Imagem:").pack(anchor=tk.W)
        self.image_url_entry = ttk.Entry(download_frame)
        self.image_url_entry.pack(fill=tk.X, pady=2)
        
        download_buttons_frame = ttk.Frame(download_frame)
        download_buttons_frame.pack(fill=tk.X, pady=2)
        
        btn_download = ttk.Button(download_buttons_frame, 
                                text="⬇️ Baixar Imagem", 
                                command=self.download_image)
        btn_download.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_open_folder = ttk.Button(download_buttons_frame, 
                                   text="📂 Abrir Pasta", 
                                   command=lambda: self.open_download_folder('images'))
        btn_open_folder.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # ===== PAINEL DIREITO - VISUALIZAÇÃO =====
        self.setup_image_preview(right_panel)
    
    def setup_image_preview(self, parent):
        """Configura o painel de visualização de imagens"""
        preview_frame = ttk.LabelFrame(parent, text=" Visualização ", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Container da imagem com borda
        img_container = tk.Frame(preview_frame, 
                                bg='white', 
                                bd=1, 
                                relief=tk.SOLID)
        img_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.image_preview_label = tk.Label(img_container, 
                                          bg='white',
                                          bd=0)
        self.image_preview_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.image_preview_label.config(text="Selecione uma imagem para visualizar",
                                      font=('Segoe UI', 10),
                                      fg='#999')
        
        # Informações da imagem
        info_frame = ttk.Frame(preview_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.image_info_label = ttk.Label(info_frame, 
                                        text="",
                                        justify=tk.LEFT,
                                        font=('Segoe UI', 8))
        self.image_info_label.pack(anchor=tk.W)
    
    def setup_image_controls(self, parent):
        """Configura controles específicos para imagens"""
        # Controle de qualidade
        self.image_quality_var = tk.IntVar(value=90)
        quality_frame = ttk.Frame(parent)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="Qualidade:").pack(side=tk.LEFT)
        ttk.Scale(quality_frame, 
                 from_=1, 
                 to=100, 
                 orient=tk.HORIZONTAL,
                 variable=self.image_quality_var,
                 command=lambda v: self.image_quality_var.set(int(float(v)))).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(quality_frame, textvariable=self.image_quality_var).pack(side=tk.LEFT, padx=5)
        
        # Controles de ajuste de imagem
        adjust_frame = ttk.Frame(parent)
        adjust_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(adjust_frame, 
                 text="↻ Girar 90°", 
                 command=lambda: self.adjust_image('rotate')).pack(side=tk.LEFT, padx=2)
        ttk.Button(adjust_frame, 
                 text="↔ Espelhar", 
                 command=lambda: self.adjust_image('mirror')).pack(side=tk.LEFT, padx=2)
        ttk.Button(adjust_frame, 
                 text="☀ Brilho +", 
                 command=lambda: self.adjust_image('brightness')).pack(side=tk.LEFT, padx=2)
        ttk.Button(adjust_frame, 
                 text="☀ Brilho -", 
                 command=lambda: self.adjust_image('darkness')).pack(side=tk.LEFT, padx=2)

    def setup_video_tab(self):
        """Configura a aba para processamento de vídeos"""
        tab_video = ttk.Frame(self.notebook, style='Video.TFrame')
        self.notebook.add(tab_video, text="  🎬 Processador de Vídeos  ")
        
        # Layout principal
        main_panel = ttk.Frame(tab_video)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Painel esquerdo - Controles
        left_panel = ttk.Frame(main_panel)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Painel direito - Visualização
        right_panel = ttk.Frame(main_panel)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # ===== PAINEL ESQUERDO - CONTROLES =====
        
        # Seção de seleção de arquivo
        file_frame = ttk.LabelFrame(left_panel, text=" Seleção de Arquivos ", padding=8)
        file_frame.pack(fill=tk.X, pady=5)
        
        select_buttons_frame = ttk.Frame(file_frame)
        select_buttons_frame.pack(fill=tk.X, pady=2)
        
        btn_select = ttk.Button(select_buttons_frame, 
                              text="📁 Selecionar Vídeo", 
                              command=lambda: self.select_file('videos'))
        btn_select.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_select_batch = ttk.Button(select_buttons_frame, 
                                    text="📂 Selecionar Múltiplos", 
                                    command=lambda: self.select_batch_files('videos'))
        btn_select_batch.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Navegação
        nav_frame = ttk.Frame(file_frame)
        nav_frame.pack(fill=tk.X, pady=2)
        
        btn_prev = ttk.Button(nav_frame, 
                            text="◀ Anterior", 
                            command=lambda: self.navigate_files('prev', 'videos'))
        btn_prev.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        btn_next = ttk.Button(nav_frame, 
                            text="Próximo ▶", 
                            command=lambda: self.navigate_files('next', 'videos'))
        btn_next.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        self.lbl_video_file = ttk.Label(file_frame, text="Nenhum vídeo selecionado")
        self.lbl_video_file.pack(pady=2)
        
        self.lbl_batch_videos = ttk.Label(file_frame, text="", foreground='#4a6baf')
        self.lbl_batch_videos.pack(pady=2)
        
        # Seção de conversão
        convert_frame = ttk.LabelFrame(left_panel, text=" Conversão ", padding=8)
        convert_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(convert_frame, text="Formato de Saída:").pack(anchor=tk.W)
        self.video_format_var = tk.StringVar(value="MP4")
        format_menu = ttk.Combobox(convert_frame, 
                                 textvariable=self.video_format_var, 
                                 values=list(self.supported_formats['videos'].keys()), 
                                 state="readonly")
        format_menu.pack(fill=tk.X, pady=2)
        
        # Botões de conversão
        btn_convert = ttk.Button(convert_frame, 
                               text="🔄 Converter Vídeo", 
                               command=self.convert_video)
        btn_convert.pack(fill=tk.X, pady=2)
        
        btn_convert_batch = ttk.Button(convert_frame, 
                                     text="🔄 Converter Lote", 
                                     command=self.convert_video_batch)
        btn_convert_batch.pack(fill=tk.X, pady=2)
        
        # Seção de renomeação
        rename_frame = ttk.LabelFrame(left_panel, text=" Renomeação ", padding=8)
        rename_frame.pack(fill=tk.X, pady=5)
        
        rename_input_frame = ttk.Frame(rename_frame)
        rename_input_frame.pack(fill=tk.X, pady=2)
        
        self.video_name_var = tk.StringVar()
        ttk.Entry(rename_input_frame, textvariable=self.video_name_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_rename = ttk.Button(rename_input_frame, 
                              text="✏️ Renomear", 
                              command=self.rename_video)
        btn_rename.pack(side=tk.RIGHT)
        
        # Seção de download
        download_frame = ttk.LabelFrame(left_panel, text=" Download ", padding=8)
        download_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(download_frame, text="URL do Vídeo:").pack(anchor=tk.W)
        self.video_url_entry = ttk.Entry(download_frame)
        self.video_url_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(download_frame, text="Site:").pack(anchor=tk.W)
        self.video_site_var = tk.StringVar(value="YouTube")
        ttk.Combobox(download_frame, 
                    textvariable=self.video_site_var, 
                    values=self.supported_sites['videos'], 
                    state="readonly").pack(fill=tk.X, pady=2)
        
        ttk.Label(download_frame, text="Qualidade:").pack(anchor=tk.W)
        self.video_quality_var = tk.StringVar(value="720p")
        ttk.Combobox(download_frame, 
                    textvariable=self.video_quality_var, 
                    values=["144p", "240p", "360p", "480p", "720p", "1080p", "Melhor disponível"], 
                    state="readonly").pack(fill=tk.X, pady=2)
        
        download_buttons_frame = ttk.Frame(download_frame)
        download_buttons_frame.pack(fill=tk.X, pady=2)
        
        btn_download = ttk.Button(download_buttons_frame, 
                                text="⬇️ Baixar Vídeo", 
                                command=self.download_video)
        btn_download.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_open_folder = ttk.Button(download_buttons_frame, 
                                   text="📂 Abrir Pasta", 
                                   command=lambda: self.open_download_folder('videos'))
        btn_open_folder.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # ===== PAINEL DIREITO - VISUALIZAÇÃO =====
        self.setup_video_preview(right_panel)
    
    def setup_video_preview(self, parent):
        """Configura o painel de visualização de vídeos"""
        preview_frame = ttk.LabelFrame(parent, text=" Informações do Vídeo ", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Container de informações
        info_container = tk.Frame(preview_frame, 
                                bg='white', 
                                bd=1, 
                                relief=tk.SOLID)
        info_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.video_info_label = tk.Label(info_container, 
                                       bg='white',
                                       bd=0,
                                       justify=tk.LEFT,
                                       anchor=tk.NW,
                                       padx=10,
                                       pady=10,
                                       font=('Segoe UI', 9))
        self.video_info_label.pack(fill=tk.BOTH, expand=True)
        self.video_info_label.config(text="Selecione um vídeo para visualizar informações",
                                   fg='#999')
    
    def setup_audio_tab(self):
        """Configura a aba para processamento de áudio"""
        tab_audio = ttk.Frame(self.notebook, style='Audio.TFrame')
        self.notebook.add(tab_audio, text="  🎵 Processador de Áudio  ")
        
        # Layout principal
        main_panel = ttk.Frame(tab_audio)
        main_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Painel esquerdo - Controles
        left_panel = ttk.Frame(main_panel)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Painel direito - Visualização
        right_panel = ttk.Frame(main_panel)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # ===== PAINEL ESQUERDO - CONTROLES =====
        
        # Seção de seleção de arquivo
        file_frame = ttk.LabelFrame(left_panel, text=" Seleção de Arquivos ", padding=8)
        file_frame.pack(fill=tk.X, pady=5)
        
        select_buttons_frame = ttk.Frame(file_frame)
        select_buttons_frame.pack(fill=tk.X, pady=2)
        
        btn_select = ttk.Button(select_buttons_frame, 
                              text="📁 Selecionar Áudio", 
                              command=lambda: self.select_file('audio'))
        btn_select.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_select_batch = ttk.Button(select_buttons_frame, 
                                    text="📂 Selecionar Múltiplos", 
                                    command=lambda: self.select_batch_files('audio'))
        btn_select_batch.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Navegação
        nav_frame = ttk.Frame(file_frame)
        nav_frame.pack(fill=tk.X, pady=2)
        
        btn_prev = ttk.Button(nav_frame, 
                            text="◀ Anterior", 
                            command=lambda: self.navigate_files('prev', 'audio'))
        btn_prev.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        btn_next = ttk.Button(nav_frame, 
                            text="Próximo ▶", 
                            command=lambda: self.navigate_files('next', 'audio'))
        btn_next.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        self.lbl_audio_file = ttk.Label(file_frame, text="Nenhum áudio selecionado")
        self.lbl_audio_file.pack(pady=2)
        
        self.lbl_batch_audio = ttk.Label(file_frame, text="", foreground='#4a6baf')
        self.lbl_batch_audio.pack(pady=2)
        
        # Seção de conversão
        convert_frame = ttk.LabelFrame(left_panel, text=" Conversão ", padding=8)
        convert_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(convert_frame, text="Formato de Saída:").pack(anchor=tk.W)
        self.audio_format_var = tk.StringVar(value="MP3")
        format_menu = ttk.Combobox(convert_frame, 
                                 textvariable=self.audio_format_var, 
                                 values=list(self.supported_formats['audio'].keys()), 
                                 state="readonly")
        format_menu.pack(fill=tk.X, pady=2)
        
        # Controle de qualidade
        self.audio_quality_var = tk.StringVar(value="192")
        ttk.Label(convert_frame, text="Qualidade (kbps):").pack(anchor=tk.W)
        ttk.Combobox(convert_frame, 
                    textvariable=self.audio_quality_var, 
                    values=["64", "96", "128", "160", "192", "256", "320"], 
                    state="readonly").pack(fill=tk.X, pady=2)
        
        # Botões de conversão
        btn_convert = ttk.Button(convert_frame, 
                               text="🔄 Converter Áudio", 
                               command=self.convert_audio)
        btn_convert.pack(fill=tk.X, pady=2)
        
        btn_convert_batch = ttk.Button(convert_frame, 
                                     text="🔄 Converter Lote", 
                                     command=self.convert_audio_batch)
        btn_convert_batch.pack(fill=tk.X, pady=2)
        
        # Seção de renomeação
        rename_frame = ttk.LabelFrame(left_panel, text=" Renomeação ", padding=8)
        rename_frame.pack(fill=tk.X, pady=5)
        
        rename_input_frame = ttk.Frame(rename_frame)
        rename_input_frame.pack(fill=tk.X, pady=2)
        
        self.audio_name_var = tk.StringVar()
        ttk.Entry(rename_input_frame, textvariable=self.audio_name_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_rename = ttk.Button(rename_input_frame, 
                              text="✏️ Renomear", 
                              command=self.rename_audio)
        btn_rename.pack(side=tk.RIGHT)
        
        # Seção de download
        download_frame = ttk.LabelFrame(left_panel, text=" Download ", padding=8)
        download_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(download_frame, text="URL do Áudio:").pack(anchor=tk.W)
        self.audio_url_entry = ttk.Entry(download_frame)
        self.audio_url_entry.pack(fill=tk.X, pady=2)
        
        ttk.Label(download_frame, text="Site:").pack(anchor=tk.W)
        self.audio_site_var = tk.StringVar(value="YouTube")
        ttk.Combobox(download_frame, 
                    textvariable=self.audio_site_var, 
                    values=self.supported_sites['audio'], 
                    state="readonly").pack(fill=tk.X, pady=2)
        
        download_buttons_frame = ttk.Frame(download_frame)
        download_buttons_frame.pack(fill=tk.X, pady=2)
        
        btn_download = ttk.Button(download_buttons_frame, 
                                text="⬇️ Baixar Áudio", 
                                command=self.download_audio)
        btn_download.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_open_folder = ttk.Button(download_buttons_frame, 
                                   text="📂 Abrir Pasta", 
                                   command=lambda: self.open_download_folder('audio'))
        btn_open_folder.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # ===== PAINEL DIREITO - VISUALIZAÇÃO =====
        self.setup_audio_preview(right_panel)
    
    def setup_audio_preview(self, parent):
        """Configura o painel de informações de áudio"""
        preview_frame = ttk.LabelFrame(parent, text=" Informações do Áudio ", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Container de informações
        info_container = tk.Frame(preview_frame, 
                                bg='white', 
                                bd=1, 
                                relief=tk.SOLID)
        info_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.audio_info_label = tk.Label(info_container, 
                                       bg='white',
                                       bd=0,
                                       justify=tk.LEFT,
                                       anchor=tk.NW,
                                       padx=10,
                                       pady=10,
                                       font=('Segoe UI', 9))
        self.audio_info_label.pack(fill=tk.BOTH, expand=True)
        self.audio_info_label.config(text="Selecione um arquivo de áudio para visualizar informações",
                                   fg='#999')
    
    # Métodos de navegação
    def navigate_files(self, direction, media_type):
        """Navega entre os arquivos selecionados"""
        if not self.batch_files:
            messagebox.showwarning("Aviso", "Selecione múltiplos arquivos primeiro")
            return
        
        if direction == 'next':
            self.current_file_index = (self.current_file_index + 1) % len(self.batch_files)
        else:  # prev
            self.current_file_index = (self.current_file_index - 1) % len(self.batch_files)
        
        self.current_file = self.batch_files[self.current_file_index]
        filename = os.path.basename(self.current_file)
        
        # Atualiza a interface conforme o tipo de mídia
        if media_type == 'images':
            self.lbl_image_file.config(text=f"Arquivo: {filename} ({self.current_file_index + 1}/{len(self.batch_files)})")
            self.image_name_var.set(os.path.splitext(filename)[0])
            self.show_image_preview(self.current_file)
        elif media_type == 'videos':
            self.lbl_video_file.config(text=f"Arquivo: {filename} ({self.current_file_index + 1}/{len(self.batch_files)})")
            self.video_name_var.set(os.path.splitext(filename)[0])
            self.show_video_info(self.current_file)
        elif media_type == 'audio':
            self.lbl_audio_file.config(text=f"Arquivo: {filename} ({self.current_file_index + 1}/{len(self.batch_files)})")
            self.audio_name_var.set(os.path.splitext(filename)[0])
            self.show_audio_info(self.current_file)
    
    # Métodos compartilhados (mantidos iguais do código anterior)
    def select_file(self, media_type):
        """Seleciona um arquivo individual"""
        file_types = {
            'images': [
                ("Imagens", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.avif *.ico *.tga"),
                ("Todos os arquivos", "*.*")
            ],
            'videos': [
                ("Vídeos", "*.mp4 *.mov *.avi *.mkv *.webm *.mpeg *.gif"),
                ("Todos os arquivos", "*.*")
            ],
            'audio': [
                ("Áudio", "*.mp3 *.wav *.ogg *.aac *.flac *.m4a"),
                ("Todos os arquivos", "*.*")
            ]
        }
        
        filename = filedialog.askopenfilename(
            title=f"Selecionar {media_type[:-1]}",
            filetypes=file_types[media_type]
        )
        
        if filename:
            self.current_file = filename
            self.batch_files = [filename]
            self.current_file_index = 0
            
            # Atualiza a interface conforme o tipo de mídia
            if media_type == 'images':
                self.lbl_image_file.config(text=f"Arquivo: {os.path.basename(filename)}")
                self.image_name_var.set(os.path.splitext(os.path.basename(filename))[0])
                self.show_image_preview(filename)
            elif media_type == 'videos':
                self.lbl_video_file.config(text=f"Arquivo: {os.path.basename(filename)}")
                self.video_name_var.set(os.path.splitext(os.path.basename(filename))[0])
                self.show_video_info(filename)
            elif media_type == 'audio':
                self.lbl_audio_file.config(text=f"Arquivo: {os.path.basename(filename)}")
                self.audio_name_var.set(os.path.splitext(os.path.basename(filename))[0])
                self.show_audio_info(filename)
    
    def select_batch_files(self, media_type):
        """Seleciona múltiplos arquivos"""
        file_types = {
            'images': [
                ("Imagens", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.avif *.ico *.tga"),
                ("Todos os arquivos", "*.*")
            ],
            'videos': [
                ("Vídeos", "*.mp4 *.mov *.avi *.mkv *.webm *.mpeg *.gif"),
                ("Todos os arquivos", "*.*")
            ],
            'audio': [
                ("Áudio", "*.mp3 *.wav *.ogg *.aac *.flac *.m4a"),
                ("Todos os arquivos", "*.*")
            ]
        }
        
        filenames = filedialog.askopenfilenames(
            title=f"Selecionar {media_type}",
            filetypes=file_types[media_type]
        )
        
        if filenames:
            self.batch_files = list(filenames)
            self.current_file_index = 0
            self.current_file = self.batch_files[0]
            filename = os.path.basename(self.current_file)
            
            # Atualiza a interface conforme o tipo de mídia
            if media_type == 'images':
                self.lbl_image_file.config(text=f"Arquivo: {filename} (1/{len(self.batch_files)})")
                self.lbl_batch_images.config(text=f"Total: {len(self.batch_files)} imagens selecionadas")
                self.image_name_var.set(os.path.splitext(filename)[0])
                self.show_image_preview(self.current_file)
            elif media_type == 'videos':
                self.lbl_video_file.config(text=f"Arquivo: {filename} (1/{len(self.batch_files)})")
                self.lbl_batch_videos.config(text=f"Total: {len(self.batch_files)} vídeos selecionados")
                self.video_name_var.set(os.path.splitext(filename)[0])
                self.show_video_info(self.current_file)
            elif media_type == 'audio':
                self.lbl_audio_file.config(text=f"Arquivo: {filename} (1/{len(self.batch_files)})")
                self.lbl_batch_audio.config(text=f"Total: {len(self.batch_files)} áudios selecionados")
                self.audio_name_var.set(os.path.splitext(filename)[0])
                self.show_audio_info(self.current_file)
    
    def show_image_preview(self, image_path):
        """Exibe preview da imagem"""
        try:
            self.original_image = Image.open(image_path)
            
            # Redimensiona para caber no preview mantendo aspect ratio
            preview_size = (400, 400)
            image = self.original_image.copy()
            image.thumbnail(preview_size, Image.Resampling.LANCZOS)
            
            # Converte para PhotoImage
            self.preview_image = ImageTk.PhotoImage(image)
            
            # Atualiza o label
            self.image_preview_label.config(image=self.preview_image, text="")
            
            # Atualiza informações
            width, height = self.original_image.size
            file_size = os.path.getsize(image_path) / 1024  # KB
            info_text = f"Dimensões: {width} x {height} px\n"
            info_text += f"Tamanho: {file_size:.1f} KB\n"
            info_text += f"Formato: {self.original_image.format}\n"
            info_text += f"Modo: {self.original_image.mode}"
            
            self.image_info_label.config(text=info_text)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar imagem: {str(e)}")
    
    def show_video_info(self, video_path):
        """Exibe informações do vídeo"""
        try:
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            file_name = os.path.basename(video_path)
            file_ext = os.path.splitext(file_name)[1].upper()
            
            info_text = f"Arquivo: {file_name}\n"
            info_text += f"Formato: {file_ext}\n"
            info_text += f"Tamanho: {file_size:.2f} MB\n"
            info_text += f"Caminho: {video_path}\n\n"
            info_text += "⚠️ Preview de vídeo não disponível nesta versão"
            
            self.video_info_label.config(text=info_text, fg='#333')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar informações do vídeo: {str(e)}")
    
    def show_audio_info(self, audio_path):
        """Exibe informações do áudio"""
        try:
            file_size = os.path.getsize(audio_path) / 1024  # KB
            file_name = os.path.basename(audio_path)
            file_ext = os.path.splitext(file_name)[1].upper()
            
            info_text = f"Arquivo: {file_name}\n"
            info_text += f"Formato: {file_ext}\n"
            info_text += f"Tamanho: {file_size:.2f} KB\n"
            info_text += f"Caminho: {audio_path}\n\n"
            info_text += "🔊 Preview de áudio não disponível nesta versão"
            
            self.audio_info_label.config(text=info_text, fg='#333')
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar informações do áudio: {str(e)}")
    
    def adjust_image(self, adjustment):
        """Aplica ajustes na imagem"""
        if not self.current_file or not self.original_image:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro")
            return
        
        try:
            image = self.original_image.copy()
            
            if adjustment == 'rotate':
                image = image.rotate(90, expand=True)
            elif adjustment == 'mirror':
                image = ImageOps.mirror(image)
            elif adjustment == 'brightness':
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.2)
            elif adjustment == 'darkness':
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(0.8)
            
            # Atualiza a imagem original
            self.original_image = image
            
            # Atualiza o preview
            preview_size = (400, 400)
            preview_image = image.copy()
            preview_image.thumbnail(preview_size, Image.Resampling.LANCZOS)
            self.preview_image = ImageTk.PhotoImage(preview_image)
            self.image_preview_label.config(image=self.preview_image)
            
            messagebox.showinfo("Sucesso", f"Ajuste '{adjustment}' aplicado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar ajuste: {str(e)}")
    
    def convert_image(self):
        """Converte uma imagem individual"""
        if not self.current_file:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro")
            return
        
        self._convert_single_file(self.current_file, 'images')
    
    def convert_image_batch(self):
        """Converte múltiplas imagens"""
        if not self.batch_files:
            messagebox.showwarning("Aviso", "Selecione múltiplas imagens primeiro")
            return
        
        self._convert_batch_files('images')
    
    def convert_video(self):
        """Converte um vídeo individual"""
        if not self.current_file:
            messagebox.showwarning("Aviso", "Selecione um vídeo primeiro")
            return
        
        messagebox.showinfo("Info", "Conversão de vídeo será implementada em versão futura")
    
    def convert_video_batch(self):
        """Converte múltiplos vídeos"""
        if not self.batch_files:
            messagebox.showwarning("Aviso", "Selecione múltiplos vídeos primeiro")
            return
        
        messagebox.showinfo("Info", "Conversão em lote de vídeos será implementada em versão futura")
    
    def convert_audio(self):
        """Converte um áudio individual"""
        if not self.current_file:
            messagebox.showwarning("Aviso", "Selecione um áudio primeiro")
            return
        
        messagebox.showinfo("Info", "Conversão de áudio será implementada em versão futura")
    
    def convert_audio_batch(self):
        """Converte múltiplos áudios"""
        if not self.batch_files:
            messagebox.showwarning("Aviso", "Selecione múltiplos áudios primeiro")
            return
        
        messagebox.showinfo("Info", "Conversão em lote de áudio será implementada em versão futura")
    
    def _convert_single_file(self, file_path, media_type):
        """Converte um arquivo individual"""
        try:
            if media_type == 'images':
                format_name = self.image_format_var.get()
                extension = self.supported_formats['images'][format_name]
                quality = self.image_quality_var.get()
                
                # Abre a imagem
                image = Image.open(file_path)
                
                # Define o nome do arquivo de saída
                output_dir = self.download_folders['images']
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(output_dir, f"{base_name}_converted{extension}")
                
                # Salva no novo formato
                if format_name in ['JPEG', 'WEBP']:
                    image.save(output_path, format=format_name, quality=quality, optimize=True)
                else:
                    image.save(output_path, format=format_name, optimize=True)
                
                messagebox.showinfo("Sucesso", f"Imagem convertida com sucesso!\nSalva em: {output_path}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao converter arquivo: {str(e)}")
    
    def _convert_batch_files(self, media_type):
        """Converte múltiplos arquivos em lote"""
        try:
            if media_type == 'images':
                format_name = self.image_format_var.get()
                extension = self.supported_formats['images'][format_name]
                quality = self.image_quality_var.get()
                output_dir = self.download_folders['images']
                
                converted_count = 0
                
                for file_path in self.batch_files:
                    try:
                        image = Image.open(file_path)
                        base_name = os.path.splitext(os.path.basename(file_path))[0]
                        output_path = os.path.join(output_dir, f"{base_name}_converted{extension}")
                        
                        if format_name in ['JPEG', 'WEBP']:
                            image.save(output_path, format=format_name, quality=quality, optimize=True)
                        else:
                            image.save(output_path, format=format_name, optimize=True)
                        
                        converted_count += 1
                        
                    except Exception as e:
                        print(f"Erro ao converter {file_path}: {str(e)}")
                        continue
                
                messagebox.showinfo("Sucesso", f"{converted_count} de {len(self.batch_files)} imagens convertidas!\nSalvas em: {output_dir}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro no processamento em lote: {str(e)}")
    
    def rename_image(self):
        """Renomeia a imagem atual"""
        self._rename_file('images')
    
    def rename_video(self):
        """Renomeia o vídeo atual"""
        self._rename_file('videos')
    
    def rename_audio(self):
        """Renomeia o áudio atual"""
        self._rename_file('audio')
    
    def _rename_file(self, media_type):
        """Renomeia o arquivo atual"""
        if not self.current_file:
            messagebox.showwarning("Aviso", f"Selecione um {media_type[:-1]} primeiro")
            return
        
        new_name = ""
        if media_type == 'images':
            new_name = self.image_name_var.get().strip()
        elif media_type == 'videos':
            new_name = self.video_name_var.get().strip()
        elif media_type == 'audio':
            new_name = self.audio_name_var.get().strip()
        
        if not new_name:
            messagebox.showwarning("Aviso", "Digite um novo nome para o arquivo")
            return
        
        try:
            directory = os.path.dirname(self.current_file)
            extension = os.path.splitext(self.current_file)[1]
            new_path = os.path.join(directory, new_name + extension)
            
            # Verifica se o arquivo de destino já existe
            if os.path.exists(new_path):
                messagebox.showerror("Erro", "Já existe um arquivo com este nome")
                return
            
            os.rename(self.current_file, new_path)
            self.current_file = new_path
            self.batch_files[self.current_file_index] = new_path
            
            # Atualiza a interface
            if media_type == 'images':
                self.lbl_image_file.config(text=f"Arquivo: {os.path.basename(new_path)}")
                self.show_image_preview(new_path)
            elif media_type == 'videos':
                self.lbl_video_file.config(text=f"Arquivo: {os.path.basename(new_path)}")
                self.show_video_info(new_path)
            elif media_type == 'audio':
                self.lbl_audio_file.config(text=f"Arquivo: {os.path.basename(new_path)}")
                self.show_audio_info(new_path)
            
            messagebox.showinfo("Sucesso", "Arquivo renomeado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao renomear arquivo: {str(e)}")
    
    def download_image(self):
        """Faz download de uma imagem da URL"""
        self._download_media('images')
    
    def download_video(self):
        """Faz download de um vídeo da URL"""
        self._download_media('videos')
    
    def download_audio(self):
        """Faz download de um áudio da URL"""
        self._download_media('audio')
    
    def _download_media(self, media_type):
        """Faz download de mídia da URL"""
        url = ""
        if media_type == 'images':
            url = self.image_url_entry.get().strip()
        elif media_type == 'videos':
            url = self.video_url_entry.get().strip()
        elif media_type == 'audio':
            url = self.audio_url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Aviso", "Digite uma URL válida")
            return
        
        if self.downloading:
            messagebox.showwarning("Aviso", "Já existe um download em andamento")
            return
        
        self.downloading = True
        
        # Inicia o download em uma thread separada
        thread = threading.Thread(target=self._download_thread, args=(url, media_type))
        thread.daemon = True
        thread.start()
    
    def _download_thread(self, url, media_type):
        """Thread para download de mídia"""
        try:
            output_dir = self.download_folders[media_type]
            
            if media_type == 'images':
                # Para imagens, usa uma abordagem simples
                import requests
                from urllib.parse import urlparse
                
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                # Extrai o nome do arquivo da URL
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename:
                    filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                
                output_path = os.path.join(output_dir, filename)
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.root.after(0, lambda: messagebox.showinfo("Sucesso", f"Imagem baixada com sucesso!\nSalva em: {output_path}"))
                
            else:
                # Para vídeos e áudio, usa yt-dlp
                ydl_opts = {
                    'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
                    'quiet': True,
                }
                
                if media_type == 'audio':
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    })
                elif media_type == 'videos':
                    quality = self.video_quality_var.get()
                    if quality == "Melhor disponível":
                        ydl_opts['format'] = 'best'
                    else:
                        ydl_opts['format'] = f'best[height<={quality[:-1]}]'
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                self.root.after(0, lambda: messagebox.showinfo("Sucesso", f"Download concluído!\nSalvo em: {output_dir}"))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro no download: {str(e)}"))
        
        finally:
            self.downloading = False
    
    def open_download_folder(self, media_type):
        """Abre a pasta de downloads do tipo de mídia especificado"""
        folder_path = self.download_folders[media_type]
        if os.path.exists(folder_path):
            os.startfile(folder_path)
        else:
            messagebox.showerror("Erro", f"Pasta {folder_path} não encontrada")

def main():
    """Função principal"""
    root = tk.Tk()
    app = MediaToolsPro(root)
    root.mainloop()

if __name__ == "__main__":
    main()
