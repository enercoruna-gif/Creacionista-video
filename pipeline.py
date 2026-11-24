import os
import re
import sys
import time
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("output")
ASSETS_DIR = Path("assets")
TEMPLATE_PATH = Path("templates/base_video.html")
OUTPUT_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def slugify(text: str, max_len: int = 36) -> str:
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "à": "a", "è": "e", "ì": "i", "ò": "o", "ù": "u",
        "ä": "a", "ë": "e", "ï": "i", "ö": "o", "ü": "u",
        "ñ": "n", "ç": "c",
    }
    clean = text.lower()
    for src, dst in replacements.items():
        clean = clean.replace(src, dst)
    clean = re.sub(r"[^a-z0-9]+", "-", clean).strip("-")
    return (clean[:max_len].strip("-") or "video")


def build_run_paths(idea: str) -> tuple[str, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = slugify(idea)
    run_id = f"{stamp}_{slug}"
    html_path = OUTPUT_DIR / f"{run_id}.html"
    mp4_path = OUTPUT_DIR / f"{run_id}.mp4"
    return run_id, html_path, mp4_path


def list_local_assets() -> list[str]:
    exts = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
    files = sorted(
        p.name for p in ASSETS_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in exts
    )
    return [f"./assets/{name}" for name in files]


def call_gemini(system_prompt: str, user_prompt: str) -> str | None:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    for model in ["gemini-3.8-flash", "gemini-3.8-pro", "gemini-flash-latest"]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {"temperature": 0.55},
        }
        try:
            res = requests.post(url, json=payload, timeout=120)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    print(f"HTML generado con {model}")
                    return "".join(p.get("text", "") for p in parts)
            print(f"Gemini {model} ({res.status_code}): {res.text[:160]}")
        except Exception as e:
            print(f"Error llamando a {model}: {e}")
    return None


def call_openrouter(system_prompt: str, user_prompt: str) -> str | None:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openrouter/free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.55,
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=120)
        if res.status_code == 200:
            data = res.json()
            print("HTML generado con OpenRouter (openrouter/free)")
            return data["choices"][0]["message"]["content"]
        print(f"OpenRouter falló ({res.status_code}): {res.text[:160]}")
    except Exception as e:
        print(f"Error OpenRouter: {e}")
    return None


def extract_html(raw_text: str) -> str:
    text = raw_text.strip()
    if "```html" in text:
        text = text.split("```html", 1)[1].split("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0]
    return text.strip()


def generate_html_with_router(idea: str, local_assets: list[str]) -> str:
    skill = load_text(Path("SKILL.md"))
    template_html = load_text(TEMPLATE_PATH)

    system_prompt = (
        "Eres un director de arte y desarrollador frontend experto en vídeos verticales 9:16 (1080x1920) "
        "para ia.cuadrantia.store. Devuelve ÚNICAMENTE un archivo HTML completo válido (sin markdown ni explicaciones). "
        "REGLAS CRÍTICAS:\n"
        "1. Mantén el FONDO CLARO (#F6F7F2 / #f7f7f3 / #ffffff) y acentos lima (#D9F26B / #def27f) de la plantilla de referencia.\n"
        "2. Mantén las animaciones GSAP 3 completas (zoom/paneo en .cam, entrada escalonada de tarjetas/cajetines, "
        "subrayados .hl, escritura .ln y transiciones con desvanecido entre escenas) y Web Audio API.\n"
        "3. Evita cualquier solapamiento en el fotograma 0: cada escena (.sc) debe estar oculta salvo la activa "
        "y los elementos animados deben entrar progresivamente según la timeline.\n\n"
        + skill
    )

    assets_list = "\n".join(f"- {a}" for a in local_assets) if local_assets else "- ./assets/logo_principal.png"
    template_section = (
        f"\n\nPLANTILLA HTML DE REFERENCIA (conserva su estética clara, estructura de escenas, GSAP y sonido):\n{template_html[:22000]}"
        if template_html else ""
    )

    user_prompt = (
        f"Crea la versión animada de 45s (9:16, 1080x1920) sobre: {idea}\n"
        "Céntrate en curiosidades reales y prácticas de design.md, skills de IA y prompts para ChatGPT, Gemini y Claude.\n"
        "Integra estos archivos locales reales cuando corresponda (con <img src=\"...\">):\n"
        f"{assets_list}\n"
        "Asegúrate de que no haya texto ni cajetines amontonados en el primer fotograma y de que todas las "
        "animaciones de zoom, slides, cajetines y transiciones se ejecuten de forma fluida."
        f"{template_section}"
    )

    html_raw = call_gemini(system_prompt, user_prompt)
    if not html_raw:
        print("Usando fallback en OpenRouter...")
        html_raw = call_openrouter(system_prompt, user_prompt)

    if not html_raw:
        raise RuntimeError("No se pudo generar el HTML.")

    return extract_html(html_raw)


def render_mp4_1080x1920(html_path: Path, mp4_path: Path, run_id: str, duration_sec: int = 45) -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("No se encontró ffmpeg.")

    temp_dir = OUTPUT_DIR / f"pw_temp_{run_id}"
    raw_video_dir = temp_dir / "video"
    raw_video_dir.mkdir(parents=True, exist_ok=True)

    pulse_running = shutil.which("parecord") is not None
    audio_wav = temp_dir / "captured_audio.wav"
    audio_proc = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--use-gl=angle",
                    "--use-angle=swiftshader",
                    "--enable-webgl",
                    "--autoplay-policy=no-user-gesture-required",
                ],
            )
            context = browser.new_context(
                viewport={"width": 1080, "height": 1920},
                device_scale_factor=1,
                record_video_dir=str(raw_video_dir),
                record_video_size={"width": 1080, "height": 1920},
            )
            page = context.new_page()

            if pulse_running:
                audio_proc = subprocess.Popen(
                    ["parecord", "--device=default.monitor", "--format=s16le", "--rate=44100", "--channels=2", str(audio_wav)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

            page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            page.evaluate("""() => {
                const ctl = document.getElementById('ctl');
                if (ctl) ctl.style.display = 'none';
                window.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
                if (window.SND && typeof window.SND.unlock === 'function') window.SND.unlock();
                if (window.tl && typeof window.tl.play === 'function') window.tl.play(0);
            }""")

            time.sleep(duration_sec)

            context.close()
            browser.close()

        if audio_proc:
            audio_proc.terminate()
            audio_proc.wait(timeout=5)

        recorded_webm = next(raw_video_dir.glob("*.webm"), None)
        if not recorded_webm:
            raise RuntimeError("Playwright no generó el vídeo base (.webm).")

        cmd = ["ffmpeg", "-y", "-i", str(recorded_webm)]
        has_audio = audio_wav.exists() and audio_wav.stat().st_size > 1024
        if has_audio:
            cmd += ["-i", str(audio_wav)]

        cmd += [
            "-t", str(duration_sec),
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "18",
        ]
        if has_audio:
            cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]

        cmd.append(str(mp4_path))
        subprocess.run(cmd, check=True)
        print(f"MP4 listo en: {mp4_path}")
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    if len(sys.argv) < 2:
        print('Uso: python3 pipeline.py "Idea del vídeo"')
        sys.exit(1)

    idea = sys.argv[1]
    run_id, html_path, mp4_path = build_run_paths(idea)

    local_assets = list_local_assets()
    html_code = generate_html_with_router(idea, local_assets)
    html_path.write_text(html_code, encoding="utf-8")
    print(f"HTML guardado en: {html_path}")

    render_mp4_1080x1920(html_path, mp4_path, run_id=run_id, duration_sec=45)


if __name__ == "__main__":
    main()
