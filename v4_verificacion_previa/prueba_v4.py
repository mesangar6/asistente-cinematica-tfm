"""
Pruebas v4 — Reproducción de las sesiones críticas de v3 con el prompt corregido.

Este script ejecuta DOS sesiones específicas que en v3 mostraron problemas:

1. Interacción 3 — Caída libre, Perfil Con dificultades.
   En v3 generó alucinación pedagógica: el profesor inventó un error que
   el alumno no había cometido (la sección 4.2.5 del TFM lo documenta).

2. Sesión 5eb573c4 — MRUA con velocidad inicial, Perfil Con dificultades.
   En v3 mostró el patrón "alumno inseguro pero correcto": el profesor
   cuestionó un razonamiento que era correcto solo porque el alumno
   expresaba dudas (la sección 4.3.4 del TFM lo documenta).

El objetivo de v4 es comprobar si la fase previa de verificación
incorporada al prompt del Profesor corrige ambos comportamientos.

Uso:
    1. Configura el .env con OPENAI_API_KEY
    2. Ejecuta: python prueba_v4.py
    3. Las dos sesiones quedan registradas en interacciones_v4.csv
"""

import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os
import uuid

# Importar prompts y utilidades de la app v4
# (Se asume que app_interaccion_v4.py está en la misma carpeta)
from app_interaccion_v4 import (
    prompt_profesor,
    prompt_alumno,
    llamar_api,
    guardar_sesion
)


def ejecutar_sesion(perfil, problema, descripcion):
    """Ejecuta la secuencia completa de tres turnos y guarda el resultado."""
    sesion_id = str(uuid.uuid4())[:8]
    turnos = []

    print("\n" + "═" * 70)
    print(f"SESIÓN {sesion_id} — {descripcion}")
    print(f"Perfil: {perfil}")
    print(f"Problema: {problema}")
    print("═" * 70)

    # T1 — Alumno
    print("\n─── T1: Alumno ───\n")
    user_t1 = f"Problema:\n{problema}\n\nIntento previo:\n(ninguno)"
    resp_alumno = llamar_api(prompt_alumno(perfil), user_t1)
    print(resp_alumno)
    turnos.append({
        "turno": 1, "rol": "Alumno",
        "intento_previo": "", "respuesta": resp_alumno
    })

    # T2 — Profesor (con verificación previa)
    print("\n─── T2: Profesor (v4 con verificación previa) ───\n")
    user_t2 = f"Problema:\n{problema}\n\nIntento previo del alumno:\n{resp_alumno}"
    resp_profesor = llamar_api(prompt_profesor(), user_t2)
    print(resp_profesor)
    turnos.append({
        "turno": 2, "rol": "Profesor",
        "intento_previo": resp_alumno, "respuesta": resp_profesor
    })

    # T3 — Alumno reformula
    print("\n─── T3: Alumno reformula ───\n")
    user_t3 = (
        f"Problema:\n{problema}\n\n"
        f"Mi intento anterior:\n{resp_alumno}\n\n"
        f"Indicaciones del profesor:\n{resp_profesor}"
    )
    resp_reformula = llamar_api(prompt_alumno(perfil), user_t3)
    print(resp_reformula)
    turnos.append({
        "turno": 3, "rol": "Alumno",
        "intento_previo": resp_profesor, "respuesta": resp_reformula
    })

    guardar_sesion(sesion_id, perfil, problema, turnos)
    print("\n" + "═" * 70)
    print(f"✓ Sesión guardada en interacciones_v4.csv (ID: {sesion_id})")
    print("═" * 70 + "\n")

    return sesion_id


if __name__ == "__main__":

    # ───────────────────────────────────────────────────────────────
    # PRUEBA 1 — Reproducción de la Interacción 3 de v3
    # Caída libre, perfil Con dificultades.
    # En v3 produjo alucinación pedagógica.
    # ───────────────────────────────────────────────────────────────
    ejecutar_sesion(
        perfil="Con dificultades",
        problema="Un objeto cae durante 2 segundos. ¿Qué velocidad alcanza?",
        descripcion="REPRO I3 v3 — Caída libre (alucinación pedagógica)"
    )

    # ───────────────────────────────────────────────────────────────
    # PRUEBA 2 — Reproducción de la sesión 5eb573c4 de v3
    # MRUA con velocidad inicial, perfil Con dificultades.
    # En v3 produjo cuestionamiento ante razonamiento correcto pero inseguro.
    # ───────────────────────────────────────────────────────────────
    ejecutar_sesion(
        perfil="Con dificultades",
        problema="Un coche parte con velocidad inicial de 5 m/s y acelera "
                 "a 2 m/s² durante 3 s. ¿Qué velocidad final alcanza?",
        descripcion="REPRO 5eb573c4 v3 — Inseguro pero correcto"
    )

    print("\n✓ Las dos sesiones se han ejecutado y guardado.")
    print("  Compara los resultados con los obtenidos en v3 (interacciones_v3.csv)")
    print("  para evaluar si la verificación previa corrige los problemas.")
