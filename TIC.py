import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import yt_dlp
import threading
from datetime import datetime

class MediaToolsPro:
    def __init__(self, root):
        self.root = root
        self.root.title("TIC(The Inative Core) - Organizado por Mídia")
        self.root.geometry("1100x850")
        self.root.configure(bg='#f5f5f5')
        
        # Variáveis de controle
        self.current_file = ""
        self.downloading = False
        self.preview_image = None
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
                       padding=8, 
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
        
        # Frame de conteúdo
        content_frame = ttk.Frame(tab_image)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Painel esquerdo (controles)
        control_frame = ttk.Frame(content_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Título
        ttk.Label(control_frame, 
                 text="Processador de Imagens", 
                 font=('Segoe UI', 12, 'bold'),
                 foreground='#4a6baf').pack(pady=(0, 15))
        
        # Seção de seleção de arquivo
        file_frame = ttk.LabelFrame(control_frame, text=" Arquivo de Imagem ", padding=10)
        file_frame.pack(fill=tk.X, pady=5)
        
        btn_select = ttk.Button(file_frame, 
                              text="📁 Selecionar Imagem", 
                              command=lambda: self.select_file('images'))
        btn_select.pack(fill=tk.X, pady=5)
        
        self.lbl_image_file = ttk.Label(file_frame, text="Nenhuma imagem selecionada")
        self.lbl_image_file.pack(pady=5)
        
        # Seção de visualização
        self.setup_image_preview(content_frame)
        
        # Seção de conversão
        convert_frame = ttk.LabelFrame(control_frame, text=" Conversão de Imagem ", padding=10)
        convert_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(convert_frame, text="Formato de Saída:").pack(anchor=tk.W)
        self.image_format_var = tk.StringVar(value="JPEG")
        format_menu = ttk.Combobox(convert_frame, 
                                 textvariable=self.image_format_var, 
                                 values=list(self.supported_formats['images'].keys()), 
                                 state="readonly")
        format_menu.pack(fill=tk.X, pady=5)
        
        # Controles de qualidade e ajustes
        self.setup_image_controls(convert_frame)
        
        # Seção de renomeação
        rename_frame = ttk.LabelFrame(control_frame, text=" Renomeação ", padding=10)
        rename_frame.pack(fill=tk.X, pady=10)
        
        self.image_name_var = tk.StringVar()
        ttk.Entry(rename_frame, textvariable=self.image_name_var).pack(fill=tk.X, pady=5)
        
        btn_rename = ttk.Button(rename_frame, 
                              text="✏️ Renomear Imagem", 
                              command=self.rename_image)
        btn_rename.pack(fill=tk.X, pady=5)
        
        # Seção de download de imagens
        download_frame = ttk.LabelFrame(control_frame, text=" Download de Imagens ", padding=10)
        download_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(download_frame, text="URL da Imagem:").pack(anchor=tk.W)
        self.image_url_entry = ttk.Entry(download_frame)
        self.image_url_entry.pack(fill=tk.X, pady=5)
        
        btn_download = ttk.Button(download_frame, 
                                text="⬇️ Baixar Imagem", 
                                command=self.download_image)
        btn_download.pack(fill=tk.X, pady=5)
        
        ttk.Button(download_frame, 
                 text="📂 Abrir Pasta de Imagens", 
                 command=lambda: self.open_download_folder('images')).pack(fill=tk.X)
        
        # Botão de conversão
        btn_convert = ttk.Button(control_frame, 
                               text="🔄 Converter Imagem", 
                               command=self.convert_image)
        btn_convert.pack(fill=tk.X, pady=10)
    
    def setup_image_preview(self, parent):
        """Configura o painel de visualização de imagens"""
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(preview_frame, 
                 text="Visualização da Imagem", 
                 font=('Segoe UI', 11, 'bold'),
                 foreground='#4a6baf').pack(pady=(0, 10))
        
        # Container da imagem com borda
        img_container = tk.Frame(preview_frame, 
                                bg='white', 
                                bd=1, 
                                relief=tk.SOLID)
        img_container.pack(fill=tk.BOTH, expand=True)
        
        self.image_preview_label = tk.Label(img_container, 
                                          bg='white',
                                          bd=0)
        self.image_preview_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.image_preview_label.config(text="Selecione uma imagem para visualizar",
                                      font=('Segoe UI', 10),
                                      fg='#999')
    
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
                 text="☀ Brilho", 
                 command=lambda: self.adjust_image('brightness')).pack(side=tk.LEFT, padx=2)
    
    def setup_video_tab(self):
        """Configura a aba para processamento de vídeos"""
        tab_video = ttk.Frame(self.notebook, style='Video.TFrame')
        self.notebook.add(tab_video, text="  🎬 Processador de Vídeos  ")
        
        # Frame principal
        main_frame = ttk.Frame(tab_video)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Painel esquerdo (controles)
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Título
        ttk.Label(control_frame, 
                 text="Processador de Vídeos", 
                 font=('Segoe UI', 12, 'bold'),
                 foreground='#4a6baf').pack(pady=(0, 15))
        
        # Seção de arquivo local
        file_frame = ttk.LabelFrame(control_frame, text=" Arquivo de Vídeo ", padding=10)
        file_frame.pack(fill=tk.X, pady=5)
        
        btn_select = ttk.Button(file_frame, 
                              text="📁 Selecionar Vídeo", 
                              command=lambda: self.select_file('videos'))
        btn_select.pack(fill=tk.X, pady=5)
        
        self.lbl_video_file = ttk.Label(file_frame, text="Nenhum vídeo selecionado")
        self.lbl_video_file.pack(pady=5)
        
        # Seção de visualização
        self.setup_video_preview(main_frame)
        
        # Seção de conversão
        convert_frame = ttk.LabelFrame(control_frame, text=" Conversão de Vídeo ", padding=10)
        convert_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(convert_frame, text="Formato de Saída:").pack(anchor=tk.W)
        self.video_format_var = tk.StringVar(value="MP4")
        format_menu = ttk.Combobox(convert_frame, 
                                 textvariable=self.video_format_var, 
                                 values=list(self.supported_formats['videos'].keys()), 
                                 state="readonly")
        format_menu.pack(fill=tk.X, pady=5)
        
        # Seção de renomeação
        rename_frame = ttk.LabelFrame(control_frame, text=" Renomeação ", padding=10)
        rename_frame.pack(fill=tk.X, pady=10)
        
        self.video_name_var = tk.StringVar()
        ttk.Entry(rename_frame, textvariable=self.video_name_var).pack(fill=tk.X, pady=5)
        
        btn_rename = ttk.Button(rename_frame, 
                              text="✏️ Renomear Vídeo", 
                              command=self.rename_video)
        btn_rename.pack(fill=tk.X, pady=5)
        
        # Seção de download de vídeos
        download_frame = ttk.LabelFrame(control_frame, text=" Download de Vídeos ", padding=10)
        download_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(download_frame, text="URL do Vídeo:").pack(anchor=tk.W)
        self.video_url_entry = ttk.Entry(download_frame)
        self.video_url_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(download_frame, text="Site:").pack(anchor=tk.W)
        self.video_site_var = tk.StringVar(value="YouTube")
        ttk.Combobox(download_frame, 
                    textvariable=self.video_site_var, 
                    values=self.supported_sites['videos'], 
                    state="readonly").pack(fill=tk.X, pady=5)
        
        ttk.Label(download_frame, text="Qualidade:").pack(anchor=tk.W)
        self.video_quality_var = tk.StringVar(value="720p")
        ttk.Combobox(download_frame, 
                    textvariable=self.video_quality_var, 
                    values=["144p", "240p", "360p", "480p", "720p", "1080p", "Melhor disponível"], 
                    state="readonly").pack(fill=tk.X, pady=5)
        
        btn_download = ttk.Button(download_frame, 
                                text="⬇️ Baixar Vídeo", 
                                command=self.download_video)
        btn_download.pack(fill=tk.X, pady=5)
        
        ttk.Button(download_frame, 
                 text="📂 Abrir Pasta de Vídeos", 
                 command=lambda: self.open_download_folder('videos')).pack(fill=tk.X)
        
        # Botão de conversão (simplificado - implementação real requer ffmpeg)
        btn_convert = ttk.Button(control_frame, 
                               text="🔄 Converter Vídeo", 
                               command=self.convert_video)
        btn_convert.pack(fill=tk.X, pady=10)
    
    def setup_video_preview(self, parent):
        """Configura o painel de visualização de vídeos"""
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(preview_frame, 
                 text="Informações do Vídeo", 
                 font=('Segoe UI', 11, 'bold'),
                 foreground='#4a6baf').pack(pady=(0, 10))
        
        # Container de informações
        info_container = tk.Frame(preview_frame, 
                                bg='white', 
                                bd=1, 
                                relief=tk.SOLID)
        info_container.pack(fill=tk.BOTH, expand=True)
        
        self.video_info_label = tk.Label(info_container, 
                                       bg='white',
                                       bd=0,
                                       justify=tk.LEFT,
                                       anchor=tk.NW,
                                       padx=10,
                                       pady=10)
        self.video_info_label.pack(fill=tk.BOTH, expand=True)
        self.video_info_label.config(text="Selecione um vídeo para visualizar informações",
                                   font=('Segoe UI', 10),
                                   fg='#999')
    
    def setup_audio_tab(self):
        """Configura a aba para processamento de áudio"""
        tab_audio = ttk.Frame(self.notebook, style='Audio.TFrame')
        self.notebook.add(tab_audio, text="  🎵 Processador de Áudio  ")
        
        # Frame principal
        main_frame = ttk.Frame(tab_audio)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Painel esquerdo (controles)
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        # Título
        ttk.Label(control_frame, 
                 text="Processador de Áudio", 
                 font=('Segoe UI', 12, 'bold'),
                 foreground='#4a6baf').pack(pady=(0, 15))
        
        # Seção de arquivo local
        file_frame = ttk.LabelFrame(control_frame, text=" Arquivo de Áudio ", padding=10)
        file_frame.pack(fill=tk.X, pady=5)
        
        btn_select = ttk.Button(file_frame, 
                              text="📁 Selecionar Áudio", 
                              command=lambda: self.select_file('audio'))
        btn_select.pack(fill=tk.X, pady=5)
        
        self.lbl_audio_file = ttk.Label(file_frame, text="Nenhum áudio selecionado")
        self.lbl_audio_file.pack(pady=5)
        
        # Seção de visualização
        self.setup_audio_preview(main_frame)
        
        # Seção de conversão
        convert_frame = ttk.LabelFrame(control_frame, text=" Conversão de Áudio ", padding=10)
        convert_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(convert_frame, text="Formato de Saída:").pack(anchor=tk.W)
        self.audio_format_var = tk.StringVar(value="MP3")
        format_menu = ttk.Combobox(convert_frame, 
                                 textvariable=self.audio_format_var, 
                                 values=list(self.supported_formats['audio'].keys()), 
                                 state="readonly")
        format_menu.pack(fill=tk.X, pady=5)
        
        # Controle de qualidade
        self.audio_quality_var = tk.StringVar(value="192")
        ttk.Label(convert_frame, text="Qualidade (kbps):").pack(anchor=tk.W)
        ttk.Combobox(convert_frame, 
                    textvariable=self.audio_quality_var, 
                    values=["64", "96", "128", "160", "192", "256", "320"], 
                    state="readonly").pack(fill=tk.X, pady=5)
        
        # Seção de renomeação
        rename_frame = ttk.LabelFrame(control_frame, text=" Renomeação ", padding=10)
        rename_frame.pack(fill=tk.X, pady=10)
        
        self.audio_name_var = tk.StringVar()
        ttk.Entry(rename_frame, textvariable=self.audio_name_var).pack(fill=tk.X, pady=5)
        
        btn_rename = ttk.Button(rename_frame, 
                              text="✏️ Renomear Áudio", 
                              command=self.rename_audio)
        btn_rename.pack(fill=tk.X, pady=5)
        
        # Seção de download de áudio
        download_frame = ttk.LabelFrame(control_frame, text=" Download de Áudio ", padding=10)
        download_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(download_frame, text="URL do Áudio:").pack(anchor=tk.W)
        self.audio_url_entry = ttk.Entry(download_frame)
        self.audio_url_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(download_frame, text="Site:").pack(anchor=tk.W)
        self.audio_site_var = tk.StringVar(value="YouTube")
        ttk.Combobox(download_frame, 
                    textvariable=self.audio_site_var, 
                    values=self.supported_sites['audio'], 
                    state="readonly").pack(fill=tk.X, pady=5)
        
        btn_download = ttk.Button(download_frame, 
                                text="⬇️ Baixar Áudio", 
                                command=self.download_audio)
        btn_download.pack(fill=tk.X, pady=5)
        
        ttk.Button(download_frame, 
                 text="📂 Abrir Pasta de Áudios", 
                 command=lambda: self.open_download_folder('audio')).pack(fill=tk.X)
        
        # Botão de conversão (simplificado - implementação real requer ffmpeg)
        btn_convert = ttk.Button(control_frame, 
                               text="🔄 Converter Áudio", 
                               command=self.convert_audio)
        btn_convert.pack(fill=tk.X, pady=10)
    
    def setup_audio_preview(self, parent):
        """Configura o painel de informações de áudio"""
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(preview_frame, 
                 text="Informações do Áudio", 
                 font=('Segoe UI', 11, 'bold'),
                 foreground='#4a6baf').pack(pady=(0, 10))
        
        # Container de informações
        info_container = tk.Frame(preview_frame, 
                                bg='white', 
                                bd=1, 
                                relief=tk.SOLID)
        info_container.pack(fill=tk.BOTH, expand=True)
        
        self.audio_info_label = tk.Label(info_container, 
                                       bg='white',
                                       bd=0,
                                       justify=tk.LEFT,
                                       anchor=tk.NW,
                                       padx=10,
                                       pady=10)
        self.audio_info_label.pack(fill=tk.BOTH, expand=True)
        self.audio_info_label.config(text="Selecione um arquivo de áudio para visualizar informações",
                                   font=('Segoe UI', 10),
                                   fg='#999')
    
    # Métodos compartilhados
    def select_file(self, media_type):
        """Seleciona um arquivo do tipo especificado"""
        filetypes = {
            'images': [("Imagens", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp *.avif *.ico *.tga")],
            'videos': [("Vídeos", "*.mp4 *.mov *.avi *.mkv *.webm *.mpeg *.mpg *.flv *.wmv")],
            'audio': [("Áudios", "*.mp3 *.wav *.ogg *.aac *.flac *.m4a")]
        }
        
        file_path = filedialog.askopenfilename(
            title=f"Selecione um arquivo de {media_type}",
            filetypes=filetypes[media_type],
            initialdir=os.path.expanduser("~")
        )
        
        if not file_path:
            return
        
        self.current_file = file_path
        filename = os.path.basename(file_path)
        
        # Atualiza a interface conforme o tipo de mídia
        if media_type == 'images':
            self.lbl_image_file.config(text=f"Arquivo: {filename}")
            self.image_name_var.set(os.path.splitext(filename)[0])
            self.show_image_preview(file_path)
        elif media_type == 'videos':
            self.lbl_video_file.config(text=f"Arquivo: {filename}")
            self.video_name_var.set(os.path.splitext(filename)[0])
            self.show_video_info(file_path)
        elif media_type == 'audio':
            self.lbl_audio_file.config(text=f"Arquivo: {filename}")
            self.audio_name_var.set(os.path.splitext(filename)[0])
            self.show_audio_info(file_path)
    
    def show_image_preview(self, file_path):
        """Mostra a pré-visualização de uma imagem"""
        try:
            image = Image.open(file_path)
            image.thumbnail((500, 500))
            self.preview_image = ImageTk.PhotoImage(image)
            self.image_preview_label.config(image=self.preview_image, text="")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem: {e}")
            self.image_preview_label.config(image=None, text="Erro ao carregar imagem")
    
    def show_video_info(self, file_path):
        """Mostra informações sobre o vídeo selecionado"""
        try:
            file_size = os.path.getsize(file_path)
            file_info = (
                f"Arquivo: {os.path.basename(file_path)}\n\n"
                f"Tamanho: {self.format_size(file_size)}\n"
                f"Tipo: {os.path.splitext(file_path)[1].upper()}\n"
                f"Caminho: {file_path}\n\n"
                f"⚠ Conversão de vídeo requer FFmpeg instalado"
            )
            self.video_info_label.config(text=file_info)
        except Exception as e:
            self.video_info_label.config(text=f"Erro ao obter informações do vídeo: {e}")
    
    def show_audio_info(self, file_path):
        """Mostra informações sobre o áudio selecionado"""
        try:
            file_size = os.path.getsize(file_path)
            file_info = (
                f"Arquivo: {os.path.basename(file_path)}\n\n"
                f"Tamanho: {self.format_size(file_size)}\n"
                f"Tipo: {os.path.splitext(file_path)[1].upper()}\n"
                f"Caminho: {file_path}\n\n"
                f"⚠ Conversão de áudio requer FFmpeg instalado"
            )
            self.audio_info_label.config(text=file_info)
        except Exception as e:
            self.audio_info_label.config(text=f"Erro ao obter informações do áudio: {e}")
    
    # Métodos para imagens
    def adjust_image(self, operation):
        """Aplica ajustes à imagem (rotação, espelhamento, etc.)"""
        if not self.current_file or not self.current_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            messagebox.showwarning("Aviso", "Selecione uma imagem válida primeiro")
            return
        
        try:
            img = Image.open(self.current_file)
            
            if operation == 'rotate':
                img = img.rotate(90, expand=True)
            elif operation == 'mirror':
                img = ImageOps.mirror(img)
            elif operation == 'brightness':
                # Implementação simplificada - poderia usar ImageEnhance
                img = img.point(lambda p: p * 1.2)
            
            # Atualiza a visualização
            img.thumbnail((500, 500))
            self.preview_image = ImageTk.PhotoImage(img)
            self.image_preview_label.config(image=self.preview_image)
            
            # Atualiza o arquivo atual (salva temporariamente)
            temp_path = os.path.join(self.download_folders['images'], "temp_edit.jpg")
            img.save(temp_path)
            self.current_file = temp_path
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ajustar a imagem: {e}")
    
    def rename_image(self):
        """Renomeia a imagem selecionada"""
        new_name = self.image_name_var.get().strip()
        if not new_name or not self.current_file:
            messagebox.showwarning("Aviso", "Selecione uma imagem e insira um novo nome")
            return
            
        self.rename_file(self.current_file, new_name, 'images')
    
    def convert_image(self):
        """Converte a imagem para o formato selecionado"""
        if not self.current_file:
            messagebox.showwarning("Aviso", "Selecione uma imagem primeiro")
            return
            
        selected_format = self.image_format_var.get()
        extension = self.supported_formats['images'][selected_format]
        quality = self.image_quality_var.get()
        
        output_path = filedialog.asksaveasfilename(
            title="Salvar imagem como",
            defaultextension=extension,
            filetypes=[(f"{selected_format} Files", f"*{extension}")],
            initialfile=f"{os.path.splitext(os.path.basename(self.current_file))[0]}{extension}"
        )
        
        if not output_path:
            return
            
        try:
            img = Image.open(self.current_file)
            
            save_kwargs = {}
            if selected_format == "JPEG":
                save_kwargs["quality"] = quality
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
            
            img.save(output_path, format=selected_format, **save_kwargs)
            messagebox.showinfo("Sucesso", f"Imagem convertida e salva como:\n{os.path.basename(output_path)}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível converter a imagem: {e}")
    
    def download_image(self):
        """Baixa uma imagem da URL fornecida"""
        url = self.image_url_entry.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Insira uma URL válida")
            return
        
        try:
            # Usando yt-dlp que também funciona com imagens
            ydl_opts = {
                'outtmpl': os.path.join(self.download_folders['images'], '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
            }
            
            self.status_label = self.image_preview_label
            self.status_label.config(text="Baixando imagem...")
            
            threading.Thread(
                target=self.run_download,
                args=(url, ydl_opts, 'images'),
                daemon=True
            ).start()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível baixar a imagem: {e}")
    
    # Métodos para vídeos
    def rename_video(self):
        """Renomeia o vídeo selecionado"""
        new_name = self.video_name_var.get().strip()
        if not new_name or not self.current_file:
            messagebox.showwarning("Aviso", "Selecione um vídeo e insira um novo nome")
            return
            
        self.rename_file(self.current_file, new_name, 'videos')
    
    def convert_video(self):
        """Converte o vídeo para o formato selecionado"""
        if not self.current_file:
            messagebox.showwarning("Aviso", "Selecione um vídeo primeiro")
            return
            
        messagebox.showinfo("Informação", "Conversão de vídeo requer FFmpeg instalado.\n"
                         "Esta funcionalidade será implementada em uma versão futura.")
    
    def download_video(self):
        """Baixa um vídeo da URL fornecida"""
        url = self.video_url_entry.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Insira uma URL válida")
            return
            
        site = self.video_site_var.get()
        quality = self.video_quality_var.get()
        
        ydl_opts = {
            'outtmpl': os.path.join(self.download_folders['videos'], f'%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        }
        
        if quality == "Melhor disponível":
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            ydl_opts['format'] = f'bestvideo[height<={quality[:-1]}]+bestaudio/best'
        
        self.run_download(url, ydl_opts, 'videos')
    
    # Métodos para áudio
    def rename_audio(self):
        """Renomeia o áudio selecionado"""
        new_name = self.audio_name_var.get().strip()
        if not new_name or not self.current_file:
            messagebox.showwarning("Aviso", "Selecione um áudio e insira um novo nome")
            return
            
        self.rename_file(self.current_file, new_name, 'audio')
    
    def convert_audio(self):
        """Converte o áudio para o formato selecionado"""
        if not self.current_file:
            messagebox.showwarning("Aviso", "Selecione um áudio primeiro")
            return
            
        messagebox.showinfo("Informação", "Conversão de áudio requer FFmpeg instalado.\n"
                         "Esta funcionalidade será implementada em uma versão futura.")
    
    def download_audio(self):
        """Baixa um áudio da URL fornecida"""
        url = self.audio_url_entry.get().strip()
        if not url:
            messagebox.showwarning("Aviso", "Insira uma URL válida")
            return
            
        site = self.audio_site_var.get()
        quality = self.audio_quality_var.get()
        
        ydl_opts = {
            'outtmpl': os.path.join(self.download_folders['audio'], f'%(title)s.%(ext)s'),
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        }
        
        self.run_download(url, ydl_opts, 'audio')
    
    # Métodos utilitários
    def rename_file(self, file_path, new_name, media_type):
        """Renomeia um arquivo genérico"""
        directory = os.path.dirname(file_path)
        extension = os.path.splitext(file_path)[1]
        new_path = os.path.join(directory, new_name + extension)
        
        try:
            os.rename(file_path, new_path)
            messagebox.showinfo("Sucesso", f"Arquivo renomeado para:\n{new_name + extension}")
            self.current_file = new_path
            
            # Atualiza a interface conforme o tipo de mídia
            if media_type == 'images':
                self.lbl_image_file.config(text=f"Arquivo: {new_name + extension}")
            elif media_type == 'videos':
                self.lbl_video_file.config(text=f"Arquivo: {new_name + extension}")
            elif media_type == 'audio':
                self.lbl_audio_file.config(text=f"Arquivo: {new_name + extension}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível renomear o arquivo: {e}")
    
    def run_download(self, url, ydl_opts, media_type):
        """Executa o download em uma thread separada"""
        if self.downloading:
            return
            
        self.downloading = True
        if media_type == 'images':
            self.status_label = self.image_preview_label
        elif media_type == 'videos':
            self.status_label = self.video_info_label
        elif media_type == 'audio':
            self.status_label = self.audio_info_label
        
        self.status_label.config(text="Preparando download...")
        
        def download_thread():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                messagebox.showinfo("Sucesso", "Download concluído com sucesso!")
                
            except Exception as error:
                messagebox.showerror("Erro", f"Falha no download: {str(error)}")
            finally:
                self.downloading = False
                self.status_label.config(text="Download concluído. Pronto para novo download.")
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def open_download_folder(self, media_type):
        """Abre a pasta de downloads do tipo especificado"""
        try:
            os.startfile(self.download_folders[media_type])
        except:
            try:
                os.system(f'open "{self.download_folders[media_type]}"')
            except:
                messagebox.showerror("Erro", f"Não foi possível abrir a pasta de {media_type}")
    
    def format_size(self, bytes_size):
        """Formata o tamanho em bytes para uma string legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaToolsPro(root)
    root.mainloop()