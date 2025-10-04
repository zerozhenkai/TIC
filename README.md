# 🎥🎶🖼️ MediaTools Pro

**MediaTools Pro** é uma aplicação em Python com interface gráfica feita em **Tkinter**, que organiza e processa **imagens, vídeos e áudios** de forma simples e eficiente.  
O programa permite **converter, renomear, visualizar e baixar arquivos de mídia** de diversas fontes online (YouTube, Instagram, TikTok, SoundCloud, entre outros), oferecendo uma interface intuitiva e organizada por abas.

---

## 🚀 Funcionalidades

### 🖼️ Imagens
- Seleção e visualização de imagens.
- Conversão para diversos formatos: `JPEG, PNG, GIF, BMP, WEBP, TIFF, AVIF, ICO, TGA`.
- Ajustes rápidos: **rotacionar, espelhar, brilho**.
- Renomeação de arquivos.
- Download de imagens a partir de URLs.

### 🎬 Vídeos
- Seleção de vídeos locais e exibição de informações (nome, tipo, tamanho).
- Conversão (em futuras versões – requer **FFmpeg**).
- Renomeação de arquivos.
- Download de vídeos de sites suportados: **YouTube, Vimeo, Facebook, Twitter, Instagram, TikTok, Dailymotion**.
- Escolha de qualidade: `144p` até `1080p` ou "Melhor disponível".

### 🎵 Áudio
- Seleção de arquivos de áudio locais.
- Conversão (em futuras versões – requer **FFmpeg**).
- Renomeação de arquivos.
- Download de músicas/podcasts de **YouTube, SoundCloud, Bandcamp, Mixcloud**.
- Escolha de formato de saída: `MP3, WAV, OGG, AAC, FLAC, M4A`.
- Configuração de qualidade (64 kbps a 320 kbps).

---

## 📂 Organização de Arquivos

Os downloads são automaticamente organizados em pastas específicas dentro de `~/Downloads/`:

- `MediaTools_Images`
- `MediaTools_Videos`
- `MediaTools_Audio`

---

## 🛠️ Requisitos

Certifique-se de ter os seguintes pacotes instalados:

```bash
pip install pillow yt-dlp
