import streamlit as st
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os

# -------------------------
# CONFIGURACIÓN API
# -------------------------
# Crea un archivo .env en la raíz del proyecto con:
#   OPENAI_API_KEY=sk-tu_clave_aqui
# Nunca pongas la clave directamente en el código.

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# -------------------------
# INTERFAZ
# -------------------------

st.title("Asistente Virtual de Cinemática – 4º ESO (v2)")
st.write("Introduce un problema y selecciona el rol del asistente.")

rol = st.radio(
    "Selecciona el rol:",
    ["Profesor", "Alumno"]
)

perfil = None

if rol == "Alumno":
    perfil = st.selectbox(
        "Selecciona el perfil del alumno:",
        ["Competente", "Medio", "Con dificultades"]
    )

problema = st.text_area("Problema:")
intento = st.text_area("Intento de resolución (opcional):")


# -------------------------
# PROMPTS PEDAGÓGICOS
# -------------------------

def prompt_profesor():
    return """
Actúa como profesor de Física de 4º ESO especializado en cinemática.

Tu objetivo NO es dar la solución directamente, sino guiar el razonamiento del alumno.

Sigue esta estructura:

FASE 0 – Diagnóstico
- Identifica qué se pide.
- Determina el tipo de movimiento.
- Detecta errores si hay intento previo.

FASE 1 – Datos
- Pide identificar datos con unidades.

FASE 2 – Modelo físico
- Pregunta qué tipo de movimiento es.
- Relaciona modelo y características.

FASE 3 – Ecuación
- Propón 1 o 2 ecuaciones posibles.
- Pide elegir y justificar.
- No sustituyas valores aún.

FASE 4 – Sustitución
- Guía paso a paso sin dar directamente el resultado final.

FASE 5 – Verificación
- Comprueba unidades.
- Pregunta si el resultado es razonable.

Reglas:
- No des el resultado final sin intento previo.
- Máximo 3 preguntas por intervención.
- Lenguaje claro y propio de 4º ESO.
- Si faltan datos, indícalo.
"""


def prompt_alumno(perfil):

    if perfil == "Competente":
        return """
Actúa como alumno competente de 4º ESO.

- Generalmente eliges bien el modelo.
- Puedes cometer pequeños errores de unidades o cálculo.
- Explicas paso a paso.
- A veces muestras dudas breves.

No seas perfecto siempre.
Usa lenguaje natural de estudiante.
"""

    elif perfil == "Medio":
        return """
Actúa como alumno promedio de 4º ESO.

- A veces dudas entre MRU y MRUA.
- Puedes usar fórmulas sin justificarlas.
- Puedes olvidar velocidad inicial.
- Puedes confundir velocidad y aceleración.
- Puedes equivocarte en unidades.
- No siempre detectas que faltan datos.

Explica lo que intentas hacer aunque no sea correcto.
No seas experto.
Usa lenguaje natural.
"""

    else:
        return """
Actúa como alumno de 4º ESO con dificultades.

- No siempre identificas bien el tipo de movimiento.
- Puedes probar fórmulas al azar.
- Puedes mezclar velocidad y aceleración.
- Puedes cometer errores conceptuales claros.
- Rara vez detectas falta de datos.
- Muestras dudas frecuentes.

Usa lenguaje sencillo y natural.
"""


# -------------------------
# GENERAR MENSAJES
# -------------------------

def generar_mensajes(rol, problema, intento, perfil):

    if rol == "Profesor":
        system_prompt = prompt_profesor()
    else:
        system_prompt = prompt_alumno(perfil)

    user_prompt = f"""
Problema:
{problema}

Intento previo:
{intento}
"""

    return system_prompt, user_prompt


# -------------------------
# GUARDAR INTERACCIÓN
# -------------------------

def guardar_interaccion(rol, perfil, problema, intento, respuesta):

    datos = pd.DataFrame([{
        "fecha": datetime.now(),
        "rol": rol,
        "perfil_alumno": perfil if perfil else "",
        "problema": problema,
        "intento": intento,
        "respuesta": respuesta
    }])

    archivo = "interacciones_prueba_2_perfiles.csv"

    if not os.path.exists(archivo):
        datos.to_csv(archivo, index=False)
    else:
        datos.to_csv(archivo, mode="a", header=False, index=False)


# -------------------------
# BOTÓN GENERAR
# -------------------------

if st.button("Generar respuesta"):

    if problema.strip() == "":
        st.warning("Introduce un problema primero.")
    else:

        system_prompt, user_prompt = generar_mensajes(
            rol, problema, intento, perfil
        )

        with st.spinner("Generando respuesta..."):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            respuesta = response.choices[0].message.content

        st.subheader("Respuesta:")
        st.write(respuesta)

        guardar_interaccion(rol, perfil, problema, intento, respuesta)

        st.success("Interacción guardada correctamente.")
