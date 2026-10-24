# Σstadi · Calculadora estadística con tutor IA

Calculadora de estadística descriptiva con **backend en Python (FastAPI)**, **frontend en React**, **base de datos SQLite** y **tutor de IA con Google Gemini**.

## Qué hace

- **Datos no agrupados:** media, mediana, moda, media geométrica y armónica, varianza y desviación (muestral y poblacional), CV, desviación media, error estándar, cuartiles, deciles, percentiles, RIC, asimetría (Pearson y Fisher), curtosis y datos atípicos.
- **Datos agrupados:** tabla de frecuencias completa (xi, fi, Fi, fr, Fr, %, xi·fi, xi²·fi). Se puede armar con Sturges, √n o k manual, con límites continuos o aparentes/reales. También acepta una **tabla ya hecha** (intervalos + frecuencias), como viene en los ejercicios.
- **Medidas agrupadas:** media, mediana, moda (Czuber), varianza, desviación, CV, cuartiles, deciles, percentiles, asimetría (Pearson, Bowley, Fisher) y curtosis (percentílica y momentos).
- **Procedimiento paso a paso:** fórmula, sustitución y resultado de cada medida.
- **Gráficas:** histograma con polígono, ojivas "menor que" y "mayor que", pastel porcentual, diagrama de caja y barras.
- **Tutor IA (Gemini):** interpretación para el reporte y chat para dudas. Si no hay clave, funciona en modo local.
- **Base de datos:** guarda análisis, conversaciones con la IA e historial de operaciones.
- Importa **CSV / TXT / Excel** y exporta a **PDF**.

## Requisitos

- Python 3.12 o más nuevo (marca "Add python.exe to PATH" al instalar)
- Node.js LTS
- Clave gratis de Gemini: https://aistudio.google.com/apikey

## Cómo correrlo (Windows)

1. Doble clic en **`instalar.bat`** (solo la primera vez).
2. Abre `backend\.env` con el Bloc de notas y pega tu clave en `GEMINI_API_KEY=`.
3. Doble clic en **`iniciar.bat`**. Se abren dos ventanas negras (no las cierres) y el navegador en http://localhost:5173.

Para apagarlo, cierra las dos ventanas negras.

### Manual (cualquier sistema)

```bash
# Terminal 1: backend
cd backend
python -m venv .venv
.venv\Scripts\activate        # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env        # Mac/Linux: cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Terminal 2: frontend
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173
- Documentación de la API (Swagger): http://localhost:8000/docs
- Pruebas: `pruebas.bat` o `cd backend && python -m pytest -v`

## Estructura

```
calculadora-estadistica/
├── instalar.bat / iniciar.bat / pruebas.bat
├── backend/                         Python + FastAPI
│   ├── requirements.txt
│   ├── .env.example                 copiar como .env
│   ├── app/
│   │   ├── main.py                  arranque de la API
│   │   ├── config.py                lee el .env
│   │   ├── database.py              SQLite: analisis, historial, mensajes
│   │   ├── esquemas.py              validación de entradas (Pydantic)
│   │   ├── ia.py                    tutor Gemini + respaldo local
│   │   ├── importar.py              lectura de CSV / Excel
│   │   ├── estadistica/
│   │   │   ├── no_agrupados.py      motor para datos sueltos
│   │   │   ├── agrupados.py         motor para tabla de frecuencias
│   │   │   └── utilidades.py
│   │   └── rutas/                   endpoints: analisis, ia, historial
│   ├── tests/                       pruebas con pytest
│   └── datos/estadistica.db         base de datos (se crea sola)
└── frontend/                        React + Vite + Chart.js
    └── src/
        ├── App.jsx
        ├── api/cliente.js           llamadas al backend
        ├── estilos.css
        └── components/              PanelEntrada, TablaFrecuencias, Medidas,
                                     Graficas, DiagramaCaja, Procedimiento,
                                     Tutor, Guardados, Historial
```

## API

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/api/salud` | Estado del servidor y de la IA |
| GET | `/api/ejemplo` | Datos de ejemplo |
| POST | `/api/analizar` | Calcula todo (agrupados o no agrupados) |
| POST | `/api/importar` | Lee números de un CSV / TXT / Excel |
| GET / POST | `/api/analisis` | Lista / guarda análisis |
| GET / DELETE | `/api/analisis/{id}` | Abre / elimina un análisis |
| POST | `/api/ia/interpretar` | Interpretación con Gemini |
| POST | `/api/ia/chat` | Chat con el tutor |
| GET / DELETE | `/api/historial` | Historial de operaciones |

## Base de datos (SQLite)

| Tabla | Contenido |
|---|---|
| `analisis` | Cada análisis guardado: entrada, opciones, resultado completo e interpretación |
| `mensajes` | Conversación con el tutor IA ligada a un análisis |
| `historial` | Bitácora: ANALIZAR, GUARDAR, ELIMINAR, IMPORTAR, IA_INTERPRETAR, IA_CHAT |

Para verla puedes usar **DB Browser for SQLite** (gratis) y abrir `backend/datos/estadistica.db`.

## Problemas comunes

- **"python no se reconoce"**: reinstala Python marcando "Add python.exe to PATH" y reinicia la compu.
- **Se abre la Microsoft Store al escribir python**: Configuración → Aplicaciones → Configuración avanzada → Alias de ejecución → apaga los de Python.
- **Arriba dice "IA: modo local"**: falta la clave en `backend/.env` o es inválida. Después de cambiarla, cierra y vuelve a abrir `iniciar.bat`.
- **"Backend apagado"**: la ventana del backend se cerró o tiene un error; revísala.
