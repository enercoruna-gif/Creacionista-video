---
name: studio-grade-saas-launch-video
description: Skill maestra de dirección de arte, motion design y UI/UX móvil (9:16) que fusiona Remotion Best Practices, Anthropic Frontend Design, UI Craft (ibelick), Emil Kowalski Animations, Rauno Freiberg Interaction Design, Magic UI, Motion Primitives y Apple/Linear/Stripe Keynote Pacing para generar vídeos de lanzamiento de 45s en HTML/GSAP sin fallos visuales.
---

# Studio-Grade SaaS Launch Video Skill (Apple / Linear / Stripe Keynote · 9:16)

## 1. Arquitectura 9:16 Blindada y Jerarquía Óptica
- **Escenario exacto para iPhone:** Usa `width: 100vw; height: 100dvh; overflow: hidden; box-sizing: border-box;` con `display: flex; flex-direction: column; justify-content: space-between; padding: env(safe-area-inset-top, 28px) 20px 84px 20px;`.
- **Anclaje tipográfico absoluto:** Los titulares y etiquetas jamás usan `scale`. Permanecen clavados en su coordenada (`width: 100%; text-align: left; align-items: flex-start;`), entrando con **mask reveal** (`clip-path: inset(0 0 100% 0) -> inset(0 0 0% 0)`) o desplazamiento sutil de `10px` (`opacity: 0 -> 1`).
- **Estabilidad absoluta (*Zero Layout Shift*):** Alturas fijas en tarjetas y `font-variant-numeric: tabular-nums` en todas las cifras, relojes y contadores.
- **Tipografía de precisión Apple/Linear:** Usa `-apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif` con `letter-spacing: -0.035em` y `line-height: 1.08` en titulares principales, `font-weight: 600` (nunca `800`/`900` pesado) y `text-wrap: balance`.

## 2. Sistema de Superficies de Lujo (Materiales, Luz y Profundidad)
- **Paleta y contraste de estudio (sin blancos planos ni negros puros):**
  - *Modo Claro Editorial:* Fondo `#F8F9FA` con radial ambient light `rgba(255,255,255,0.95)`, tarjetas `#FFFFFF` con borde `1px solid rgba(15, 23, 42, 0.07)`.
  - *Modo Oscuro Obsidian (Apple Pro):* Fondo `#09090B` con spotlight superior radial `rgba(255,255,255,0.06)`, tarjetas `#121215` con borde superior iluminado (`border-top: 1px solid rgba(255,255,255,0.14)` y `border-bottom/sides: 1px solid rgba(255,255,255,0.06)`).
- **Bordes especulares (*Hairline Rim Lighting*):** Simula luz cenital en cada tarjeta con:
  `box-shadow: inset 0 1px 0 0 rgba(255,255,255,0.85), 0 1px 2px rgba(0,0,0,0.04), 0 16px 36px -10px rgba(15, 23, 42, 0.09);` (o `rgba(255,255,255,0.12)` en modo oscuro).
- **Textura de grano cinematográfico:** Capa fija `pointer-events: none; z-index: 50; opacity: 0.022;` con SVG `feTurbulence` inline para eliminar bandas de degradado (*color banding*) al grabar pantalla.
- **Subrayado marcador editorial inline:** Aplica sobre `span` inline:
  `display: inline; background-image: linear-gradient(to top, rgba(253, 184, 19, 0.5) 42%, transparent 42%); background-repeat: no-repeat; background-size: 0% 100%; padding: 0 4px; border-radius: 3px;`
  Animado en GSAP solo con `backgroundSize: "100% 100%"` (`ease: "power3.out"`, `duration: 0.65`).
- **Cero duplicación sobre capturas:** Si una imagen adjunta ya contiene textos, badges o precios, **no** superpongas etiquetas HTML encima.

## 3. Componentes Signature (`Magic UI` + `Motion Primitives` + `Stripe`)
- **Border Beam (Haz de luz perimetral):** En la tarjeta protagonista o métrica clave, haz recorrer un punto de luz sutil a lo largo del borde superior/perímetro (`conic-gradient` o gradiente animado en borde `1px`) para dar sensación de hardware/software activo.
- **Number Ticker (Contadores mecánicos):** Cualquier cifra de ingresos, ahorro, tiempo o conversión debe animarse de `0` al valor real usando `gsap.to(obj, { val: target, duration: 1.2, ease: "power3.out", onUpdate: ... })` con formato limpio y `tabular-nums`.
- **Bento Grid asimétrico compacto:** Cuando muestres 3-4 beneficios o métricas en móvil, organízalos en una rejilla Bento de 2 columnas con radios consistentes (`border-radius: 18px`), iconos monocromos finos (`stroke-width: 1.75`) y micro-badges de estado.
- **Trazado SVG vivo (`stroke-dashoffset`):** Gráficos de crecimiento, ondas de audio o iconos de verificación (`✓`) se dibujan en tiempo real animando `strokeDashoffset` de longitud total a `0`.

## 4. Coreografía, Stagger y Física de Movimiento (`Emil Kowalski` + `Rauno Freiberg`)
- **Línea de tiempo maestra determinista:** Una única `gsap.timeline()` de 45s exactos. Transición entre escenas con solapamiento limpio de `0.35s` usando `autoAlpha: 0` (`opacity: 0; visibility: hidden;`) en la escena saliente.
- **Curvas físicas de alto nivel (prohibido `linear` y `bounce`):**
  - *Entrada de tarjetas y modales:* `ease: "expo.out"` (`0.65s - 0.8s`).
  - *Aparición con enfoque óptico (Emil Kowalski signature):* Elementos clave entran desde `opacity: 0, y: 10, filter: "blur(6px)"` hasta `opacity: 1, y: 0, filter: "blur(0px)"` en `0.55s`.
  - *Micro-sellos, checks y pills:* `ease: "back.out(1.4)"` en `0.45s`.
  - *Barras de progreso y contadores:* `ease: "power2.out"`.
- **Coreografía en cascada (*Orchestrated Stagger*):** Nunca animes toda la escena a la vez:
  1. `0.0s`: Eyebrow/etiqueta superior (`y: 6 -> 0`).
  2. `0.12s`: Titular principal (`mask reveal` o `y: 10 -> 0`).
  3. `0.28s`: Tarjeta/mockup protagonista (`y: 16 -> 0`, `blur(6px) -> 0`).
  4. `0.55s`: Elementos internos en `stagger: 0.08` (máximo 3-4 elementos).
  5. `1.2s - 2.2s`: Acción principal (toque táctil, cambio de estado, gráfico o subrayado).
  6. `2.2s - 6.0s`: Reposo activo con micro-respiración ambiental (luz *shimmer* sutil o pulso de estado vivo) para lectura cómoda.

## 5. Micro-interacciones Táctiles y Acabado de Producto Real
- **Cursor táctil anclado dentro del botón:** Hijo directo dentro del botón (`position: relative` en el botón; cursor en `top: 50%; left: 50%; transform: translate(-50%, -50%)`). Secuencia táctil realista:
  1. Aproximación suave al centro del botón.
  2. Compresión física del botón (`scale: 0.96`, `duration: 0.12`, `ease: "power2.in"`).
  3. Onda expansiva concéntrica (`scale: 0.5 -> 2.2`, `opacity: 0.45 -> 0`) + liberación elástica (`scale: 1`, `duration: 0.25`, `ease: "back.out(1.8)"`).
  4. Cambio de estado instantáneo (ej. *Confirmar* -> *Confirmado ✓* con cambio de color y brillo).
- **CTA Final con luz especular (*Apple Keynote Shimmer*):** En la última escena, haz pasar un destello diagonal (`linear-gradient(110deg, transparent 30%, rgba(255,255,255,0.45) 50%, transparent 70%)`) sobre el botón principal y mantén la escena congelada y nítida los últimos `4s` para cierre limpio.

## 6. Barra de Controles Compacta para iPhone (Zero-Overflow)
- Barra flotante inferior centrada (`position: fixed; bottom: max(14px, env(safe-area-inset-bottom)); left: 50%; transform: translateX(-50%); max-width: 92vw; white-space: nowrap; font-size: 12px; gap: 6px; padding: 6px 10px; border-radius: 999px; background: rgba(18,18,21,0.82); color: #fff; backdrop-filter: blur(14px); border: 1px solid rgba(255,255,255,0.12); z-index: 100;`) con exactamente 4 botones/indicadores cortos:
  1. **"Pausar"** (alterna a **"Seguir"**)
  2. **"Reiniciar"**
  3. **"00:00 / 00:45"** (`tabular-nums`)
  4. **"Grabar"** (oculta la barra con `opacity: 0; pointer-events: none;`, reinicia el timeline desde `00:00` con `0.4s` de margen para grabar pantalla limpia en 1080p y la restaura al segundo 45).

## 7. Micro-Sonido UI (Web Audio API · Zero MP3s)
- **Síntesis nativa sin archivos externos:** Genera micro-efectos de estudio (`click`, `slide`, `pop`, `confirm`) mediante `AudioContext` y nodos `OscillatorNode` / `BiquadFilterNode` / ruido blanco corto, con volúmenes bajos (`gain` `0.03` - `0.08`) y duración corta (`30ms - 140ms`).
- **Desbloqueo en iOS/Safari:** Inicializa o reanuda `audioCtx.resume()` en el primer `pointerdown`/`touchstart` del usuario. Si el usuario pulsa **"Grabar"** para captura limpia de 45s, silencia automáticamente los efectos salvo que active audio explícitamente.
- **Regla anti-saturación en scroll:** Nunca dispares sonido en cada píxel de `scroll`. Limítalo a cambios de sección/snap o **throttled** (mínimo `180ms` entre disparos) para que suene a mecanismo de precisión y no a ruido continuo.
