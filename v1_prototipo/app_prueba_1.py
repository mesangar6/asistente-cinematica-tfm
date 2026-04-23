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

st.title("Asistente Virtual de Cinemática – 4º ESO (v1)")
st.write("Introduce un problema y selecciona el rol del asistente.")

rol = st.radio(
    "Selecciona el rol:",
    ["Profesor", "Alumno"]
)

problema = st.text_area("Problema:")
intento = st.text_area("Intento de resolución (opcional):")


# -------------------------
# FUNCIÓN PARA GENERAR PROMPT
# -------------------------

def generar_mensajes(rol, problema, intento):

    if rol == "Profesor":
        system_prompt = """
        Actúa como profesor de Física de 4º ESO especializado en cinemática.
        No proporciones la solución final directamente.
        Guía mediante preguntas.
        Detecta errores conceptuales típicos.
        Fomenta el razonamiento.
        """
    else:
        system_prompt = """
        Actúa como estudiante de 4º ESO resolviendo un problema de cinemática.
        Razona paso a paso.
        Comete errores típicos cuando sea plausible.
        Usa lenguaje natural de alumno.
        """

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

def guardar_interaccion(rol, problema, intento, respuesta):

    datos = pd.DataFrame([{
        "fecha": datetime.now(),
        "rol": rol,
        "problema": problema,
        "intento": intento,
        "respuesta": respuesta
    }])

    archivo = "interacciones_prueba_1.csv"

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

        system_prompt, user_prompt = generar_mensajes(rol, problema, intento)

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

        guardar_interaccion(rol, problema, intento, respuesta)

        st.success("Interacción guardada correctamente.")
