# Studio-Grade 9:16 SaaS Launch Video Factory

Pipeline automatizado para generar vídeos verticales `9:16` (`1080x1920`) de 45 segundos con animaciones HTML/GSAP, micro-sonidos con Web Audio API y renderizado a MP4 desde **GitHub Codespaces** (incluso trabajando desde iPhone en Safari).

## Estructura del repositorio
- `SKILL.md`: Reglas de dirección de arte, física de movimiento, componentes y Web Audio API (útil tanto para el pipeline como para pegarla en Claude).
- `pipeline.py`: Genera imagen de apoyo (Hugging Face FLUX), genera HTML con sonido (Gemini con fallback a OpenRouter) y exporta a `output/video_final.mp4` (`1080x1920`) con Playwright + `ffmpeg`.
- `requirements.txt`: Dependencias Python (`requests`, `playwright`).
- `.devcontainer/devcontainer.json` y `setup.sh`: Instalación automática de `ffmpeg`, `pulseaudio`, Playwright y Chromium en Codespaces.
- `.gitignore`: Evita subir archivos temporales o renders pesados al repositorio.
- `output/`: Carpeta donde se guardan `index.html` y `video_final.mp4`.

## Uso rápido en GitHub Codespaces
1. Abre este repositorio en **GitHub Codespaces**.
2. Si no corrió `.devcontainer/devcontainer.json`, ejecuta:
   ```bash
   bash setup.sh
   ```
3. Configura tus variables de entorno (al menos `GEMINI_API_KEY` o `OPENROUTER_API_KEY`):
   ```bash
   export GEMINI_API_KEY="tu_clave_aqui"
   export OPENROUTER_API_KEY="tu_clave_aqui"
   export HF_TOKEN="tu_token_aqui"
   ```
4. Genera tu vídeo de 45s en `1080x1920`:
   ```bash
   python pipeline.py "App de reservas y recordatorios automáticos por WhatsApp en modo oscuro"
   ```
5. Descarga `output/video_final.mp4` desde el explorador de archivos.
