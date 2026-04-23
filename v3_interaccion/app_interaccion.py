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
# Crea un archivo .env en la raíz del proyecto con:
#   OPENAI_API_KEY=sk-tu_clave_aqui
# Nunca pongas la clave directamente en el código.

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# -------------------------
# PROMPTS PEDAGÓGICOS v3
# -------------------------

def prompt_profesor():
    return """
Actúa como profesor de Física de 4º ESO especializado en cinemática.

Tu objetivo NO es dar la solución directamente, sino guiar el razonamiento del alumno.

Sigue esta estructura por fases:

FASE 0 – Diagnóstico
- Identifica qué se pide y el tipo de movimiento.
- Si hay intento previo, detecta el error principal del alumno.

FASE 1 – Datos
- Pide que el alumno liste los datos con unidades.

FASE 2 – Modelo físico
- Pregunta qué tipo de movimiento es y por qué.

FASE 3 – Ecuación
- Pide elegir una ecuación y justificarla.
- No sustituyas valores todavía.

FASE 4 – Sustitución guiada
- Guía la sustitución sin dar el resultado final directamente.

FASE 5 – Verificación y cierre (OBLIGATORIO si el alumno ya llegó al resultado)
- Comprueba unidades.
- Pregunta si el resultado tiene sentido físico.
- Termina con una frase breve que resuma el procedimiento seguido.

Reglas estrictas:
- Formula EXACTAMENTE 1 pregunta por intervención (2 como máximo si son muy cortas).
- Nunca des el resultado final directamente.
- Si faltan datos en el enunciado, indícalo claramente y no inventes valores.
- Usa lenguaje claro y apropiado para un alumno de 4º ESO.
- Si el alumno ya llegó a la solución correcta, pasa directamente a la Fase 5.
"""


def prompt_alumno(perfil):
    if perfil == "Competente":
        return """
Actúa como alumno competente de 4º ESO resolviendo un problema de cinemática.

- Generalmente identificas bien el tipo de movimiento (MRU o MRUA).
- Explicas tu razonamiento paso a paso.
- Puedes cometer pequeños errores: un error de unidades, olvidar incluir v₀
  al enunciar la fórmula, o un error aritmético menor.
- Muestras alguna duda puntual pero te autocorrigas.

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

def guardar_sesion(sesion_id, perfil, problema, turnos):
    archivo = "interacciones_v3.csv"
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

st.title("Asistente Virtual de Cinemática – 4º ESO (v3)")
st.write("Ejecuta una secuencia completa de interacción Alumno → Profesor → Alumno.")

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
            "turno": 1,
            "rol": "Alumno",
            "intento_previo": "",
            "respuesta": respuesta_alumno
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
            "turno": 2,
            "rol": "Profesor",
            "intento_previo": respuesta_alumno,
            "respuesta": respuesta_profesor
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
                "turno": 3,
                "rol": "Alumno",
                "intento_previo": respuesta_profesor,
                "respuesta": respuesta_reformula
            })

        # --- GUARDAR ---
        guardar_sesion(sesion_id, perfil, problema, turnos_guardados)
        st.divider()
        st.success(f"Sesión guardada correctamente. ID de sesión: `{sesion_id}`")
