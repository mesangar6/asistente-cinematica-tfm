"""
Comparativa 3×1: Mismo enunciado de MRUA con velocidad inicial,
ejecutado con los tres perfiles (Competente, Medio, Con dificultades).

Objetivo: observar cómo el Profesor adapta su intervención en función
del perfil del Alumno. Los tres resultados se guardan en un único CSV
para facilitar el análisis comparativo.

Usa el prompt de v4 (con verificación previa) para el Profesor.

Uso:
    1. Configura .env con OPENAI_API_KEY
    2. Ejecuta: python prueba_comparativa_3x1.py
    3. Los resultados quedan en comparativa_3x1.csv
"""

import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os
import uuid

# -------------------------
# CONFIGURACIÓN
# -------------------------
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROBLEMA = (
    "Un coche parte con velocidad inicial de 5 m/s y acelera a 2 m/s² "
    "durante 3 s. ¿Qué velocidad final alcanza?"
)


# -------------------------
# PROMPTS (v4)
# -------------------------

def prompt_profesor():
    return """
Actúa como profesor de Física de 4º ESO especializado en cinemática.

Tu objetivo NO es dar la solución directamente, sino guiar el razonamiento del alumno.

FASE PREVIA DE VERIFICACIÓN (OBLIGATORIA antes de cualquier intervención)

Antes de decidir el tipo de intervención, comprueba PASO A PASO:
1. ¿Cuál es el resultado numérico que ha obtenido el alumno?
2. ¿Cuál sería el resultado correcto si resolvieras tú el problema?
3. ¿Coinciden los dos valores?
4. ¿El procedimiento es físicamente correcto?

Clasifica la respuesta en:
  CATEGORÍA A — Razonamiento correcto y resultado correcto.
  CATEGORÍA B — Razonamiento parcialmente correcto pero con error.
  CATEGORÍA C — Razonamiento conceptualmente erróneo.

NUNCA inventes errores que el alumno no ha cometido.
La inseguridad discursiva NO es un error.

ACTUACIÓN SEGÚN CATEGORÍA:

Si A: Valida el razonamiento. Si el alumno expresó inseguridad, refuerza
su autoconfianza. Pasa a Fase 5 (verificación y cierre).

Si B: Identifica el error concreto. Aplica la fase correspondiente.
Formula EXACTAMENTE 1 pregunta orientada a ese error.

Si C: Aplica la estructura completa por fases (0 a 5).

ESTRUCTURA POR FASES (para B y C):
FASE 0 – Diagnóstico
FASE 1 – Datos (pide listar con unidades)
FASE 2 – Modelo físico (pregunta tipo de movimiento)
FASE 3 – Ecuación (pide elegir y justificar)
FASE 4 – Sustitución guiada
FASE 5 – Verificación y cierre (OBLIGATORIO)

Reglas:
- Comienza declarando la categoría: [Categoría X — descripción]
- Formula EXACTAMENTE 1 pregunta por intervención.
- Nunca des el resultado final directamente.
- Usa lenguaje claro para un alumno de 4º ESO.
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
Muestra el razonamiento aunque sea incorrecto.
Usa lenguaje natural de estudiante de secundaria.
"""
    else:
        return """
Actúa como alumno de 4º ESO con dificultades en cinemática.
DEBES mostrar estos comportamientos en tu respuesta:
- Usa una fórmula que no corresponde al tipo de movimiento del problema,
  o aplica v = a·t cuando no tienes el dato del tiempo.
- Confunde velocidad con aceleración.
- No detectes que faltan datos; si faltan, inventa un valor o ignóralo.
- Muestra inseguridad explícita: "no sé si esto está bien",
  "creo que es esta fórmula pero no estoy seguro".
Usa lenguaje sencillo y natural. Muestra el proceso aunque esté equivocado.
"""


# -------------------------
# UTILIDADES
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


def ejecutar_sesion(perfil):
    sesion_id = str(uuid.uuid4())[:8]
    turnos = []

    print(f"\n{'═' * 70}")
    print(f"SESIÓN {sesion_id} — Perfil: {perfil}")
    print(f"{'═' * 70}")

    # T1
    print(f"\n─── T1: Alumno ({perfil}) ───\n")
    user_t1 = f"Problema:\n{PROBLEMA}\n\nIntento previo:\n(ninguno)"
    resp_alumno = llamar_api(prompt_alumno(perfil), user_t1)
    print(resp_alumno[:500] + "..." if len(resp_alumno) > 500 else resp_alumno)
    turnos.append({"turno": 1, "rol": "Alumno", "intento_previo": "",
                   "respuesta": resp_alumno})

    # T2
    print(f"\n─── T2: Profesor (v4) ───\n")
    user_t2 = f"Problema:\n{PROBLEMA}\n\nIntento previo del alumno:\n{resp_alumno}"
    resp_profesor = llamar_api(prompt_profesor(), user_t2)
    print(resp_profesor[:500] + "..." if len(resp_profesor) > 500 else resp_profesor)
    turnos.append({"turno": 2, "rol": "Profesor", "intento_previo": resp_alumno,
                   "respuesta": resp_profesor})

    # T3
    print(f"\n─── T3: Alumno reformula ───\n")
    user_t3 = (f"Problema:\n{PROBLEMA}\n\nMi intento anterior:\n{resp_alumno}\n\n"
               f"Indicaciones del profesor:\n{resp_profesor}")
    resp_reformula = llamar_api(prompt_alumno(perfil), user_t3)
    print(resp_reformula[:500] + "..." if len(resp_reformula) > 500 else resp_reformula)
    turnos.append({"turno": 3, "rol": "Alumno", "intento_previo": resp_profesor,
                   "respuesta": resp_reformula})

    return sesion_id, turnos


def guardar_todo(resultados, archivo="comparativa_3x1.csv"):
    filas = []
    for perfil, sesion_id, turnos in resultados:
        for t in turnos:
            filas.append({
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sesion_id": sesion_id,
                "perfil": perfil,
                "turno": t["turno"],
                "rol": t["rol"],
                "problema": PROBLEMA,
                "intento_previo": t["intento_previo"],
                "respuesta": t["respuesta"]
            })
    pd.DataFrame(filas).to_csv(archivo, index=False)
    print(f"\n✓ Resultados guardados en {archivo}")


# -------------------------
# MAIN
# -------------------------

if __name__ == "__main__":
    resultados = []
    for perfil in ["Competente", "Medio", "Con dificultades"]:
        sesion_id, turnos = ejecutar_sesion(perfil)
        resultados.append((perfil, sesion_id, turnos))

    guardar_todo(resultados)

    print("\n" + "═" * 70)
    print("RESUMEN DE CATEGORÍAS ASIGNADAS POR EL PROFESOR")
    print("═" * 70)
    for perfil, sid, turnos in resultados:
        t2 = turnos[1]["respuesta"]
        cat = t2.split("]")[0] + "]" if "[" in t2 else "(categoría no declarada)"
        print(f"  {perfil:20s} → {cat}")
    print("═" * 70)
