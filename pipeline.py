import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_skill() -> str:
    skill_path = Path("SKILL.md")
    if skill_path.exists():
        return skill_path.read_text(encoding="utf-8")
    return ""


def generate_image_hf(prompt: str, out_path: Path) -> bool:
    token = os.getenv("HF_TOKEN", "").strip()
    if not token:
        print("Aviso: HF_TOKEN no configurado. Se omite generación de imagen.")
        return False

    url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": f"{prompt}, clean editorial studio render, vertical 9:16 framing, no text overlay",
        "parameters": {"width": 768, "height": 1344},
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=90)
        if res.status_code == 200 and res.headers.get("content-type", "").startswith("image/"):
            out_path.write_bytes(res.content)
            print(f"Imagen generada en: {out_path}")
            return True
        print(f"Error en Hugging Face ({res.status_code}): {res.text[:200]}")
    except Exception as e:
        print(f"Excepción generando imagen: {e}")
    return False


def call_gemini(system_prompt: str, user_prompt: str) -> str | None:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": 0.7},
    }

    try:
        res = requests.post(url, json=payload, timeout=120)
        if res.status_code == 200:
            data = res.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                return "".join(p.get("text", "") for p in parts)
        print(f"Gemini falló ({res.status_code}): {res.text[:200]}")
    except Exception as e:
        print(f"Error llamando a Gemini: {e}")
    return None


def call_openrouter(system_prompt: str, user_prompt: str) -> str | None:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return None

    models = [
        "deepseek/deepseek-chat-v3-0324:free",
        "qwen/qwen-2.5-coder-32b-instruct:free",
    ]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    for model in models:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
        }
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=120)
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            print(f"OpenRouter ({model}) falló ({res.status_code})")
        except Exception as e:
            print(f"Error con {model}: {e}")
    return None


def extract_html(raw_text: str) -> str:
    text = raw_text.strip()
    if "```html" in text:
        text = text.split("```html", 1)[1].split("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0]
    return text.strip()


def generate_html_with_router(idea: str, has_image: bool) -> str:
    skill = load_skill()
    system_prompt = (
        "Eres un director de arte y desarrollador frontend de élite. "
        "Devuelve ÚNICAMENTE un archivo HTML autocontenido válido (sin explicaciones fuera del código). "
        "Incluye GSAP 3 desde CDN y un sistema de micro-sonidos con Web Audio API (sin MP3 externos) "
        "desbloqueado automáticamente y listo para escucharse durante la reproducción.\n\n"
        + skill
    )
    img_note = "Hay una imagen local disponible en './scene_bg.png' que puedes integrar con elegancia." if has_image else "No uses imágenes locales externas; usa diseño tipográfico, tarjetas y gráficos vectoriales/HTML."
    user_prompt = (
        f"Crea una animación de lanzamiento de 45 segundos en formato vertical 9:16 para: {idea}. "
        f"{img_note} Asegúrate de que la animación arranque sola al cargar la página y dispare los micro-sonidos "
        "de Web Audio sincronizados con las escenas y acciones."
    )

    html_raw = call_gemini(system_prompt, user_prompt)
    if not html_raw:
        print("Usando fallback en OpenRouter...")
        html_raw = call_openrouter(system_prompt, user_prompt)

    if not html_raw:
        raise RuntimeError("No se pudo generar el HTML: revisa GEMINI_API_KEY o OPENROUTER_API_KEY.")

    return extract_html(html_raw)


def render_mp4_1080x1920(html_path: Path, mp4_path: Path, duration_sec: int = 45) -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("No se encontró ffmpeg. Instálalo con: sudo apt-get update && sudo apt-get install -y ffmpeg")

    raw_video_dir = OUTPUT_DIR / "pw_video"
    if raw_video_dir.exists():
        shutil.rmtree(raw_video_dir)
    raw_video_dir.mkdir(parents=True, exist_ok=True)

    pulse_running = shutil.which("parecord") is not None
    audio_wav = OUTPUT_DIR / "captured_audio.wav"
    audio_proc = None

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
            window.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true }));
            if (window.UISound && typeof window.UISound.unlock === 'function') {
                window.UISound.unlock();
            }
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

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(recorded_webm),
    ]
    has_audio = audio_wav.exists() and audio_wav.stat().st_size > 1024
    if has_audio:
        cmd += ["-i", str(audio_wav)]

    cmd += [
        "-t",
        str(duration_sec),
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-preset",
        "fast",
        "-crf",
        "18",
    ]

    if has_audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]

    cmd.append(str(mp4_path))
    subprocess.run(cmd, check=True)
    print(f"MP4 listo en: {mp4_path}")


def main():
    if len(sys.argv) < 2:
        print('Uso: python pipeline.py "Descripción del producto o idea del vídeo"')
        sys.exit(1)

    idea = sys.argv[1]
    img_path = OUTPUT_DIR / "scene_bg.png"
    html_path = OUTPUT_DIR / "index.html"
    mp4_path = OUTPUT_DIR / "video_final.mp4"

    has_img = generate_image_hf(idea, img_path)
    html_code = generate_html_with_router(idea, has_img)
    html_path.write_text(html_code, encoding="utf-8")
    print(f"HTML guardado en: {html_path}")

    render_mp4_1080x1920(html_path, mp4_path, duration_sec=45)


if __name__ == "__main__":
    main()
