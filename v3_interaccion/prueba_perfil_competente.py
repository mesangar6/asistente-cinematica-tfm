"""
Script para ejecutar la interacción 4 — MRUA con velocidad inicial, perfil Competente.

Este script reproduce la lógica de v3 pero sin interfaz Streamlit, para poder
ejecutarlo directamente desde la consola y obtener la sesión completa T1→T2→T3
en formato legible y guardada en CSV.

Uso:
    1. Asegúrate de tener el archivo .env con OPENAI_API_KEY en la misma carpeta
    2. Ejecuta: python prueba_perfil_competente.py
    3. La sesión se guarda en interacciones_v3.csv y se imprime por pantalla

Salida esperada:
    - Tres turnos completos del alumno Competente, profesor y reformulación
    - Identificador de sesión único de 8 caracteres
    - Archivo CSV actualizado con las tres filas correspondientes
"""

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

def guardar_sesion(sesion_id, perfil, problema, turnos, archivo="interacciones_v3.csv"):
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
# EJECUCIÓN DE LA SESIÓN
# -------------------------

def ejecutar_sesion(perfil, problema):
    sesion_id = str(uuid.uuid4())[:8]
    turnos = []

    print("=" * 70)
    print(f"SESIÓN {sesion_id} — Perfil: {perfil}")
    print(f"Problema: {problema}")
    print("=" * 70)

    # T1 — Alumno
    print("\n--- T1: Alumno ---\n")
    user_t1 = f"Problema:\n{problema}\n\nIntento previo:\n(ninguno)"
    resp_alumno = llamar_api(prompt_alumno(perfil), user_t1)
    print(resp_alumno)
    turnos.append({"turno": 1, "rol": "Alumno", "intento_previo": "", "respuesta": resp_alumno})

    # T2 — Profesor
    print("\n--- T2: Profesor ---\n")
    user_t2 = f"Problema:\n{problema}\n\nIntento previo del alumno:\n{resp_alumno}"
    resp_profesor = llamar_api(prompt_profesor(), user_t2)
    print(resp_profesor)
    turnos.append({"turno": 2, "rol": "Profesor", "intento_previo": resp_alumno, "respuesta": resp_profesor})

    # T3 — Alumno reformula
    print("\n--- T3: Alumno reformula ---\n")
    user_t3 = (
        f"Problema:\n{problema}\n\n"
        f"Mi intento anterior:\n{resp_alumno}\n\n"
        f"Indicaciones del profesor:\n{resp_profesor}"
    )
    resp_reformula = llamar_api(prompt_alumno(perfil), user_t3)
    print(resp_reformula)
    turnos.append({"turno": 3, "rol": "Alumno", "intento_previo": resp_profesor, "respuesta": resp_reformula})

    # Guardar
    guardar_sesion(sesion_id, perfil, problema, turnos)
    print("\n" + "=" * 70)
    print(f"✓ Sesión guardada en interacciones_v3.csv (ID: {sesion_id})")
    print("=" * 70)

    return sesion_id, turnos


# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":
    # INTERACCIÓN 4 — MRUA con velocidad inicial, perfil Competente
    # Reutilizamos el mismo enunciado que en interacción 1 para permitir
    # comparación directa entre los tres perfiles sobre el mismo problema.
    PROBLEMA = (
        "Un coche parte con velocidad inicial de 5 m/s y acelera a 2 m/s² "
        "durante 3 s. ¿Qué velocidad final alcanza?"
    )

    ejecutar_sesion(perfil="Competente", problema=PROBLEMA)
