"""
Asistente Virtual de Cinemática – 4º ESO
Versión 4 con interfaz mejorada para estudiantes

Ejecutar con:
    python -m streamlit run app_interfaz_final.py
"""

import streamlit as st
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import os
import uuid

# ─────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─────────────────────────────────────────────────────────
# DISEÑO VISUAL — CSS personalizado
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cinemática 4º ESO",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* ── Tipografía y fondo general ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ── Header personalizado ── */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2rem 1.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1rem;
        margin-top: 0.5rem;
    }

    /* ── Tarjetas de rol ── */
    .role-card {
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
        border: 2px solid transparent;
        transition: all 0.2s ease;
    }
    .role-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .role-profesor {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        border-color: #4caf50;
    }
    .role-alumno {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-color: #2196f3;
    }

    /* ── Turno containers ── */
    .turno-alumno {
        background: #f0f7ff;
        border-left: 4px solid #2196f3;
        border-radius: 0 12px 12px 0;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
    }
    .turno-profesor {
        background: #f0fff0;
        border-left: 4px solid #4caf50;
        border-radius: 0 12px 12px 0;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
    }
    .turno-reformula {
        background: #fff8e1;
        border-left: 4px solid #ff9800;
        border-radius: 0 12px 12px 0;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
    }

    /* ── Perfil badges ── */
    .perfil-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.3rem 0;
    }
    .badge-competente { background: #c8e6c9; color: #2e7d32; }
    .badge-medio { background: #fff9c4; color: #f57f17; }
    .badge-dificultades { background: #ffcdd2; color: #c62828; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5f7ff 0%, #e8ecff 100%);
    }

    /* ── Botón principal ── */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102,126,234,0.4) !important;
    }

    /* ── Info cards ── */
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin: 0.5rem 0;
    }

    /* ── Problema text area ── */
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
        font-size: 1rem !important;
        padding: 1rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.2) !important;
    }

    /* ── Ocultar elementos por defecto de Streamlit ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# PROMPTS PEDAGÓGICOS v4
# ─────────────────────────────────────────────────────────

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

Si A: Valida el razonamiento. Refuerza autoconfianza si hay dudas. Pasa a Fase 5.
Si B: Identifica el error. Formula EXACTAMENTE 1 pregunta orientada.
Si C: Aplica la estructura completa por fases (0 a 5).

FASES:
0 – Diagnóstico | 1 – Datos | 2 – Modelo físico | 3 – Ecuación
4 – Sustitución guiada | 5 – Verificación y cierre (OBLIGATORIO)

Reglas:
- Declara la categoría al inicio: [Categoría X — descripción]
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
- Confundir las unidades (mezclar m/s y km/h sin convertir).
- Dudar entre MRU y MRUA y elegir incorrectamente.
Muestra el razonamiento aunque sea incorrecto.
Usa lenguaje natural de estudiante de secundaria.
"""
    else:
        return """
Actúa como alumno de 4º ESO con dificultades en cinemática.
DEBES mostrar estos comportamientos:
- Usa una fórmula que no corresponde al tipo de movimiento,
  o aplica v = a·t cuando no tienes el dato del tiempo.
- Confunde velocidad con aceleración.
- No detectes que faltan datos; si faltan, inventa un valor.
- Muestra inseguridad explícita: "no sé si esto está bien".
Usa lenguaje sencillo y natural.
"""


# ─────────────────────────────────────────────────────────
# FUNCIONES
# ─────────────────────────────────────────────────────────

def llamar_api(system_prompt, user_prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content


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


# ─────────────────────────────────────────────────────────
# INTERFAZ PRINCIPAL
# ─────────────────────────────────────────────────────────

# Header
st.markdown("""
<div class="main-header">
    <h1>🚀 Asistente de Cinemática</h1>
    <p>Tu compañero de estudio para Física de 4º ESO</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.markdown("---")

    # Modo de uso
    modo = st.radio(
        "📋 ¿Qué quieres hacer?",
        ["👩‍🎓 Modo Alumno", "🧑‍🏫 Modo Profesor"],
        help="Alumno: resuelve problemas con ayuda del profesor. Profesor: ejecuta secuencias simuladas con perfiles."
    )

    st.markdown("---")

    if modo == "🧑‍🏫 Modo Profesor":
        perfil = st.selectbox(
            "👤 Perfil del alumno simulado",
            ["Competente", "Medio", "Con dificultades"],
            help="Selecciona el tipo de alumno que quieres simular."
        )

        # Badge visual del perfil
        badge_class = {
            "Competente": "badge-competente",
            "Medio": "badge-medio",
            "Con dificultades": "badge-dificultades"
        }
        badge_emoji = {"Competente": "🟢", "Medio": "🟡", "Con dificultades": "🔴"}

        st.markdown(f"""
        <span class="perfil-badge {badge_class[perfil]}">
            {badge_emoji[perfil]} {perfil}
        </span>
        """, unsafe_allow_html=True)

        n_turnos = st.radio(
            "🔄 Secuencia",
            ["2 turnos (Alumno → Profesor)",
             "3 turnos (Alumno → Profesor → Alumno)"],
        )
    else:
        perfil = None
        n_turnos = None

    st.markdown("---")
    st.markdown("##### 📊 Problemas de ejemplo")

    if st.button("📌 MRUA con velocidad inicial", use_container_width=True):
        st.session_state.problema_ejemplo = (
            "Un coche parte con velocidad inicial de 5 m/s y "
            "acelera a 2 m/s² durante 3 s. ¿Qué velocidad final alcanza?"
        )
    if st.button("📌 Caída libre", use_container_width=True):
        st.session_state.problema_ejemplo = (
            "Un objeto cae durante 2 segundos. ¿Qué velocidad alcanza?"
        )
    if st.button("📌 Dato insuficiente", use_container_width=True):
        st.session_state.problema_ejemplo = (
            "Un coche tiene una aceleración de 3 m/s². ¿Cuál es su velocidad?"
        )


# ── CONTENIDO PRINCIPAL ──────────────────────────────────

# Campo de problema
default_text = st.session_state.get("problema_ejemplo", "")
problema = st.text_area(
    "✏️ Escribe o pega tu problema de cinemática:",
    value=default_text,
    height=120,
    placeholder="Ejemplo: Un coche parte con velocidad inicial de 5 m/s y acelera a 2 m/s² durante 3 s. ¿Qué velocidad final alcanza?"
)


# ── MODO ALUMNO ──────────────────────────────────────
if modo == "👩‍🎓 Modo Alumno":

    intento = st.text_area(
        "📝 Tu intento de resolución (opcional):",
        height=150,
        placeholder="Escribe aquí cómo intentarías resolver el problema. Si no sabes por dónde empezar, déjalo en blanco y el profesor te guiará."
    )

    if st.button("🎯 Pedir ayuda al profesor"):
        if not problema.strip():
            st.warning("⚠️ Escribe un problema primero.")
        else:
            with st.spinner("🧠 El profesor está analizando tu problema..."):
                user_msg = f"Problema:\n{problema}"
                if intento.strip():
                    user_msg += f"\n\nIntento previo del alumno:\n{intento}"
                else:
                    user_msg += "\n\nIntento previo del alumno:\n(El alumno no ha intentado resolver el problema todavía)"

                respuesta = llamar_api(prompt_profesor(), user_msg)

            st.markdown("""
            <div class="turno-profesor">
                <strong>🧑‍🏫 Tu profesor dice:</strong>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(respuesta)

            # Guardar
            sesion_id = str(uuid.uuid4())[:8]
            guardar_sesion(sesion_id, "Alumno real", problema, [{
                "turno": 1, "rol": "Estudiante",
                "intento_previo": intento,
                "respuesta": respuesta
            }])


# ── MODO PROFESOR ───────────────────────────────────
elif modo == "🧑‍🏫 Modo Profesor":

    if st.button("🚀 Ejecutar secuencia completa"):
        if not problema.strip():
            st.warning("⚠️ Escribe un problema primero.")
        else:
            sesion_id = str(uuid.uuid4())[:8]
            turnos_guardados = []

            # ── T1: Alumno ──
            st.markdown(f"""
            <div class="turno-alumno">
                <strong>👩‍🎓 Turno 1 — Alumno</strong>
                <span class="perfil-badge {badge_class[perfil]}">
                    {badge_emoji[perfil]} {perfil}
                </span>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner(f"Generando respuesta del alumno ({perfil})..."):
                user_t1 = f"Problema:\n{problema}\n\nIntento previo:\n(ninguno)"
                resp_alumno = llamar_api(prompt_alumno(perfil), user_t1)

            st.markdown(resp_alumno)
            turnos_guardados.append({
                "turno": 1, "rol": "Alumno",
                "intento_previo": "", "respuesta": resp_alumno
            })

            # ── T2: Profesor ──
            st.markdown("""
            <div class="turno-profesor">
                <strong>🧑‍🏫 Turno 2 — Profesor</strong>
            </div>
            """, unsafe_allow_html=True)

            with st.spinner("Generando intervención del profesor..."):
                user_t2 = (f"Problema:\n{problema}\n\n"
                          f"Intento previo del alumno:\n{resp_alumno}")
                resp_profesor = llamar_api(prompt_profesor(), user_t2)

            st.markdown(resp_profesor)
            turnos_guardados.append({
                "turno": 2, "rol": "Profesor",
                "intento_previo": resp_alumno, "respuesta": resp_profesor
            })

            # ── T3: Alumno reformula ──
            if "3 turnos" in n_turnos:
                st.markdown(f"""
                <div class="turno-reformula">
                    <strong>🔄 Turno 3 — Alumno reformula</strong>
                    <span class="perfil-badge {badge_class[perfil]}">
                        {badge_emoji[perfil]} {perfil}
                    </span>
                </div>
                """, unsafe_allow_html=True)

                with st.spinner("Generando reformulación del alumno..."):
                    user_t3 = (f"Problema:\n{problema}\n\n"
                              f"Mi intento anterior:\n{resp_alumno}\n\n"
                              f"Indicaciones del profesor:\n{resp_profesor}")
                    resp_reformula = llamar_api(prompt_alumno(perfil), user_t3)

                st.markdown(resp_reformula)
                turnos_guardados.append({
                    "turno": 3, "rol": "Alumno",
                    "intento_previo": resp_profesor, "respuesta": resp_reformula
                })

            # ── Guardar ──
            guardar_sesion(sesion_id, perfil, problema, turnos_guardados)
            st.success(f"✅ Sesión guardada · ID: `{sesion_id}`")


# ── FOOTER ───────────────────────────────────────────────
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🚀 Cinemática 4º ESO")
with col2:
    st.caption("📚 TFM — Melani Sánchez García")
with col3:
    st.caption("🤖 Powered by GPT-4o-mini")