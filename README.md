# Asistente Virtual de Cinemática – 4º ESO

**TFM:** *Generación asistida por IA de un profesor ayudante virtual para apoyar a estudiantes de STEM en secundaria*  
**Autora:** Melani Sánchez García  
**Curso:** Máster Universitario en [nombre de tu máster]  
**Año:** 2024-2025

---

## ¿Qué es este proyecto?

Este repositorio contiene el código, los datos y la documentación del sistema desarrollado para el TFM. El proyecto implementa un **asistente virtual de doble rol** (Profesor y Alumno simulado) para apoyar el aprendizaje de cinemática en 4º ESO, basado en el principio pedagógico del **andamiaje progresivo**.

El sistema utiliza la API de OpenAI (modelo `gpt-4o-mini`) y una interfaz web desarrollada con **Streamlit**.

---

## Estructura del repositorio

```
asistente-cinematica-tfm/
│
├── v1_prototipo/
│   └── app_prueba_1.py         # Versión 1: prototipo básico sin perfiles
│
├── v2_perfiles/
│   └── app_perfiles.py         # Versión 2: perfiles de alumno diferenciados
│
├── v3_interaccion/
│   └── app_interaccion.py      # Versión 3: secuencia automatizada Alumno→Profesor→Alumno
│
├── datos/
│   ├── interacciones_prueba_1.csv           # Interacciones registradas en v1
│   ├── interacciones_prueba_2_perfiles.csv  # Interacciones registradas en v2
│   ├── interacciones_v3.csv                 # Interacciones registradas en v3
│   └── interacciones_v3_con_dific.csv       # Interacciones v3 – perfil Con dificultades
│
├── requirements.txt            # Dependencias del proyecto
├── .gitignore                  # Excluye venv, .env y archivos temporales
└── README.md                   # Este archivo
```

---

## Instalación y uso

### 1. Clona el repositorio

```bash
git clone https://github.com/TU_USUARIO/asistente-cinematica-tfm.git
cd asistente-cinematica-tfm
```

### 2. Crea un entorno virtual e instala dependencias

```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configura tu API key de OpenAI

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
OPENAI_API_KEY=sk-tu_clave_aqui
```

> ⚠️ **Nunca compartas tu API key públicamente.** El archivo `.env` está incluido en `.gitignore` para que no se suba a GitHub.

### 4. Ejecuta la versión que quieras probar

```bash
# Versión 1 – Prototipo básico
python -m streamlit run v1_prototipo/app_prueba_1.py

# Versión 2 – Con perfiles de alumno
python -m streamlit run v2_perfiles/app_perfiles.py

# Versión 3 – Secuencia automatizada (versión final)
python -m streamlit run v3_interaccion/app_interaccion.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`.

---

## Descripción del sistema

### Modo Profesor
El agente Profesor sigue una **estructura pedagógica por fases**:
- **Fase 0 – Diagnóstico:** identifica el tipo de movimiento y los errores del alumno
- **Fase 1 – Datos:** solicita listar magnitudes con unidades
- **Fase 2 – Modelo físico:** trabaja el concepto antes que la fórmula
- **Fase 3 – Ecuación:** pide elegir y justificar la ecuación
- **Fase 4 – Sustitución guiada:** acompaña el cálculo sin dar el resultado
- **Fase 5 – Verificación (obligatoria):** cierre reflexivo con comprobación de unidades y sentido físico

### Modo Alumno – Perfiles diferenciados
| Perfil | Características |
|--------|----------------|
| **Competente** | Elige bien el modelo, razona paso a paso, comete errores menores puntuales |
| **Medio** | Puede olvidar v₀, confundir MRU/MRUA, usar fórmulas sin justificar |
| **Con dificultades** | Errores conceptuales claros, inventa datos ausentes, inseguridad explícita |

### Evolución entre versiones
| Versión | Mejoras principales |
|---------|---------------------|
| v1 | Prototipo funcional, un único modo, sin perfiles |
| v2 | Perfiles de alumno, registro estructurado en CSV |
| v3 | Secuencia automatizada de 3 turnos, prompts más directivos, identificador de sesión |

---

## Datos de interacciones

La carpeta `datos/` contiene los registros CSV de todas las interacciones generadas durante las fases de prueba. Cada fila corresponde a un turno de interacción con las siguientes columnas:

| Columna | Descripción |
|---------|-------------|
| `fecha` | Fecha y hora de la generación |
| `sesion_id` | Identificador único de sesión (v3) |
| `turno` | Número de turno en la secuencia (v3) |
| `rol` | Profesor o Alumno |
| `perfil_alumno` | Perfil del alumno simulado |
| `problema` | Enunciado del problema |
| `intento_previo` | Contexto del turno anterior |
| `respuesta` | Respuesta generada por el modelo |

---

## Tecnologías utilizadas

- **Python 3.10+**
- **Streamlit** – interfaz web
- **OpenAI API** (`gpt-4o-mini`) – generación de respuestas
- **Pandas** – registro y gestión de datos

---

## Licencia

Este proyecto está publicado bajo la licencia **MIT**. Puedes usarlo, modificarlo y distribuirlo libremente, siempre que incluyas la atribución original.

---

## Contacto

Si tienes preguntas sobre el proyecto o el TFM, puedes contactar a través de GitHub o del repositorio institucional de la universidad.
