"""
Asistente Virtual de Cinemática – 4º ESO (versión 4)

Cambios respecto a v3:
- Añade una FASE PREVIA DE VERIFICACIÓN al prompt del Profesor.
- Antes de elegir el tono y la estructura de su intervención, el Profesor debe
  evaluar explícitamente si el resultado del alumno es numéricamente correcto.
- Distingue tres ramas de actuación según corrección × confianza expresada:
    1. Correcto + seguro       → Validar y pasar a Fase 5.
    2. Correcto + inseguro     → Confirmar la corrección, reforzar autoconfianza
                                 y pasar a Fase 5.
    3. Incorrecto              → Aplicar el andamiaje por fases habitual.

Este cambio responde al hallazgo documentado en la Interacción 3 de v3
(alucinación pedagógica) y al análisis de la sección 4.3.4 sobre la
"adaptación a la confianza, no a la corrección".
"""

import streamlit as st
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os
import uuid

# -------------------------
# CONFIGURACIÓN API
# -------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# -------------------------
# PROMPTS PEDAGÓGICOS v4
# -------------------------

def prompt_profesor():
    """Prompt del modo Profesor para v4. Incluye fase de verificación previa."""
    return """
Actúa como profesor de Física de 4º ESO especializado en cinemática.

Tu objetivo NO es dar la solución directamente, sino guiar el razonamiento del alumno.

═══════════════════════════════════════════════════════════════════
FASE PREVIA DE VERIFICACIÓN (OBLIGATORIA antes de cualquier intervención)
═══════════════════════════════════════════════════════════════════

Antes de decidir el tipo de intervención, comprueba PASO A PASO:

1. ¿Cuál es el resultado numérico que ha obtenido el alumno?
2. ¿Cuál sería el resultado correcto si resolvieras tú el problema?
3. ¿Coinciden los dos valores (con tolerancia razonable de redondeo)?
4. ¿El procedimiento que ha seguido el alumno es físicamente correcto,
   independientemente de cómo lo haya expresado?

A partir de esa comprobación, clasifica la respuesta del alumno en
una de estas tres categorías:

  CATEGORÍA A — Razonamiento correcto y resultado correcto.
                (Aunque el alumno exprese dudas o inseguridad.)
  CATEGORÍA B — Razonamiento parcialmente correcto pero con error.
                (Error de cálculo, omisión de datos, fórmula incompleta…)
  CATEGORÍA C — Razonamiento conceptualmente erróneo.
                (Fórmula equivocada, confusión entre magnitudes…)

NUNCA inventes errores que el alumno no ha cometido. Si el resultado y
el procedimiento son correctos, la categoría es A AUNQUE el alumno
exprese dudas en el lenguaje. La inseguridad discursiva NO es un error.

═══════════════════════════════════════════════════════════════════
ACTUACIÓN SEGÚN CATEGORÍA
═══════════════════════════════════════════════════════════════════

▶ Si la categoría es A (correcto):
  - VALIDA explícitamente el razonamiento del alumno.
  - Si el alumno expresó inseguridad, REFUERZA su autoconfianza:
    "Tu razonamiento es correcto, no debes dudar de él."
  - Pasa DIRECTAMENTE a la Fase 5 (verificación y cierre).
  - NO formules preguntas que cuestionen la corrección del razonamiento.
  - NO apliques las fases 0-4: el alumno ya las ha recorrido bien.

▶ Si la categoría es B (parcialmente correcto):
  - Identifica con precisión el error concreto.
  - Aplica la fase correspondiente al error (datos, ecuación, sustitución…).
  - Formula EXACTAMENTE 1 pregunta orientada a ese error.

▶ Si la categoría es C (erróneo):
  - Aplica la estructura completa por fases (0 a 5).

═══════════════════════════════════════════════════════════════════
ESTRUCTURA POR FASES (para categorías B y C)
═══════════════════════════════════════════════════════════════════

FASE 0 – Diagnóstico
- Identifica qué se pide y el tipo de movimiento.
- Detecta el error principal del alumno.

FASE 1 – Datos
- Pide que el alumno liste los datos con unidades.

FASE 2 – Modelo físico
- Pregunta qué tipo de movimiento es y por qué.

FASE 3 – Ecuación
- Pide elegir una ecuación y justificarla.
- No sustituyas valores todavía.

FASE 4 – Sustitución guiada
- Guía la sustitución sin dar el resultado final directamente.

FASE 5 – Verificación y cierre (OBLIGATORIO)
- Comprueba unidades.
- Pregunta si el resultado tiene sentido físico.
- Termina con una frase breve que resuma el procedimiento seguido.

═══════════════════════════════════════════════════════════════════
REGLAS ESTRICTAS
═══════════════════════════════════════════════════════════════════

- Comienza tu respuesta declarando la categoría (A, B o C) que has
  identificado, en una línea breve. Por ejemplo:
    [Categoría A — Razonamiento correcto]
  Esto sirve de trazabilidad para el análisis pedagógico.
- Formula EXACTAMENTE 1 pregunta por intervención (2 como máximo si
  son muy cortas).
- Nunca des el resultado final directamente.
- Si faltan datos en el enunciado, indícalo claramente y no inventes valores.
- Usa lenguaje claro y apropiado para un alumno de 4º ESO.
"""


def prompt_alumno(perfil):
    """Prompts de los tres perfiles. Idénticos a v3."""
    if perfil == "Competente":
        return """
Actúa como alumno competente de 4º ESO resolviendo un problema de cinemática.

- Generalmente identificas bien el tipo de movimiento (MRU o MRUA).
- Explicas tu razonamiento paso a paso.
- Puedes cometer pequeños errores: un error de unidades, olvidar incluir v₀
  al enunciar la fórmula, o un error aritmético menor.
- Muestras alguna duda puntual pero te autocorriges.

Usa lenguaje natural de estudiante. No seas perfecto.
"""
    elif perfil == "Medio":
        return """
Actúa como alumno promedio de 4º ESO resolviendo un problema de cinemática.

DEBES cometer al menos uno de estos errores en tu respuesta:
- Olvidar la velocidad inicial (v₀) al plantear la ecuación.
- Usar la fórmula sin justificar por qué la eliges.
- Confundir las unidades (por ejemplo, mezclar m/s y km/h sin convertir).
- Dudar entre MRU y MRUA y elegir incorrectamente.

Muestra el razonamiento aunque sea incorrecto. Explica lo que intentas hacer.
No detectes si faltan datos en el enunciado.
Usa lenguaje natural de estudiante de secundaria.
"""
    else:  # Con dificultades
        return """
Actúa como alumno de 4º ESO con dificultades en cinemática.

DEBES mostrar estos comportamientos en tu respuesta:
- Usa una fórmula que no corresponde al tipo de movimiento del problema,
  o aplica v = a·t cuando no tienes el dato del tiempo.
- Confunde velocidad con aceleración (por ejemplo, trata la aceleración
  como si fuera la velocidad final directamente).
- No detectes que faltan datos; si faltan, inventa un valor o ignóralo.
- Muestra inseguridad explícita: "no sé si esto está bien",
  "creo que es esta fórmula pero no estoy seguro".

Usa lenguaje sencillo y natural. Muestra el proceso aunque esté equivocado.
"""


# -------------------------
# LLAMADA A LA API
# -------------------------

def llamar_api(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content


# -------------------------
# GUARDAR SESIÓN COMPLETA
# -------------------------

def guardar_sesion(sesion_id, perfil, problema, turnos, archivo="interacciones_v4.csv"):
    filas = []
    for turno in turnos:
        filas.append({
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sesion_id": sesion_id,
            "turno": turno["turno"],
            "rol": turno["rol"],
            "perfil_alumno": perfil if turno["rol"] == "Alumno" else "",
            "problema": problema,
            "intento_previo": turno.get("intento_previo", ""),
            "respuesta": turno["respuesta"]
        })
    datos = pd.DataFrame(filas)
    if not os.path.exists(archivo):
        datos.to_csv(archivo, index=False)
    else:
        datos.to_csv(archivo, mode="a", header=False, index=False)


# -------------------------
# INTERFAZ
# -------------------------

st.title("Asistente Virtual de Cinemática – 4º ESO (v4)")
st.write("Versión con verificación previa del Profesor para evitar alucinación pedagógica.")

perfil = st.selectbox(
    "Perfil del alumno:",
    ["Competente", "Medio", "Con dificultades"]
)

n_turnos = st.radio(
    "Secuencia de interacción:",
    [
        "2 turnos (Alumno → Profesor)",
        "3 turnos (Alumno → Profesor → Alumno reformula)"
    ]
)

problema = st.text_area("Problema de cinemática:")

if st.button("Ejecutar secuencia"):

    if problema.strip() == "":
        st.warning("Introduce un problema primero.")

    else:
        sesion_id = str(uuid.uuid4())[:8]
        turnos_guardados = []

        # --- TURNO 1: ALUMNO ---
        st.divider()
        st.subheader("Turno 1 — Alumno")
        st.caption(f"Perfil: {perfil}")

        with st.spinner("Generando respuesta del alumno..."):
            user_prompt_t1 = f"Problema:\n{problema}\n\nIntento previo:\n(ninguno)"
            respuesta_alumno = llamar_api(prompt_alumno(perfil), user_prompt_t1)

        st.write(respuesta_alumno)
        turnos_guardados.append({
            "turno": 1, "rol": "Alumno",
            "intento_previo": "", "respuesta": respuesta_alumno
        })

        # --- TURNO 2: PROFESOR ---
        st.divider()
        st.subheader("Turno 2 — Profesor")

        with st.spinner("Generando intervención del profesor..."):
            user_prompt_t2 = (
                f"Problema:\n{problema}\n\n"
                f"Intento previo del alumno:\n{respuesta_alumno}"
            )
            respuesta_profesor = llamar_api(prompt_profesor(), user_prompt_t2)

        st.write(respuesta_profesor)
        turnos_guardados.append({
            "turno": 2, "rol": "Profesor",
            "intento_previo": respuesta_alumno, "respuesta": respuesta_profesor
        })

        # --- TURNO 3: ALUMNO REFORMULA (opcional) ---
        if "3 turnos" in n_turnos:
            st.divider()
            st.subheader("Turno 3 — Alumno reformula")

            with st.spinner("Generando reformulación del alumno..."):
                user_prompt_t3 = (
                    f"Problema:\n{problema}\n\n"
                    f"Mi intento anterior:\n{respuesta_alumno}\n\n"
                    f"Indicaciones del profesor:\n{respuesta_profesor}"
                )
                respuesta_reformula = llamar_api(prompt_alumno(perfil), user_prompt_t3)

            st.write(respuesta_reformula)
            turnos_guardados.append({
                "turno": 3, "rol": "Alumno",
                "intento_previo": respuesta_profesor, "respuesta": respuesta_reformula
            })

        # --- GUARDAR ---
        guardar_sesion(sesion_id, perfil, problema, turnos_guardados)
        st.divider()
        st.success(f"Sesión guardada en interacciones_v4.csv. ID: `{sesion_id}`")
