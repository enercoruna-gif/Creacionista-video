# Identidad Visual — ia.cuadrantia.store

- **Formato:** Vertical 9:16 (`1080x1920`), ritmo dinámico y limpio, sin saturar de texto.
- **Paleta principal (Logo / Modo oscuro de acento):**
  - Fondo oscuro principal: `#0b1110` y `#0a0f0e`
  - Acento principal verde menta/neón: `#9af3b9` / `#9cf7bc`
- **Paleta secundaria (Web / Tarjetas editoriales claras):**
  - Fondos claros / marfil / blanco: `#ffffff`, `#f7f7f3`, `#f8f8f4`, `#f9f9f5`, `#f6f6f2`
  - Acento lima/verde suave: `#def27f`
- **Activos locales disponibles en `./assets/`:**
  - `./assets/logo_principal.png` (logo principal de marca)
  - `./assets/web_01.png`, `./assets/web_02.png`, `./assets/web_03.png` (capturas reales de la web)
- **Temática:** Curiosidades reales, prácticas y directas sobre `design.md`, skills de agentes de IA y prompts para ChatGPT, Gemini y Claude.
# Reglas de Estilo y Animación — ia.cuadrantia.store

- **Tema obligatorio:** Fondo CLARO editorial (`#F6F7F2` / `#f7f7f3` / `#ffffff`), textos oscuros (`#111111`, `#4B5042`) y acentos lima (`#D9F26B` / `#def27f`), tal como en la plantilla HTML de referencia. NO usar fondo oscuro de pantalla completa.
- **Formato:** Vertical `9:16` (`1080x1920`), duración total `45s` repartida en escenas limpias.
- **Anti-solapamiento en el fotograma 0:** Solo la escena 0 es visible al inicio (`t=0`); las demás escenas empiezan ocultas (`autoAlpha: 0`) y solo entran cuando su tramo de la timeline GSAP lo indica. Nada puede mostrarse pegado o superpuesto.
- **Animaciones obligatorias con GSAP 3:**
  - Zoom o paneo suave de cámara en `.cam` por escena.
  - Entrada escalonada con movimiento (`y`, `scale`, `opacity`) en títulos, cajetines/tarjetas y pasos.
  - Desvanecido suave (`autoAlpha` / `scale` / `blur`) al cambiar de escena.
- **Activos locales a integrar:** Usar `./assets/logo_principal.png` y las capturas `./assets/web_01.png`, `./assets/web_02.png`, `./assets/web_03.png` cuando aplique.
- **Contenido:** Curiosidades técnicas reales y concisas sobre `design.md`, skills de IA y prompts para ChatGPT, Gemini y Claude.
