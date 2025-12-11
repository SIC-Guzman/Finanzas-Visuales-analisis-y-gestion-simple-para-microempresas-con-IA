## Analizador Financiero Inteligente para Microempresas (AFIME) 
## Finanzas-Visuales-analisis-y-gestion-simple-para-microempresas-con-IA

GRUPO 4

> Analiza tu empresa de forma inteligente usando métricas financieras, Machine Learning y una interfaz web sencilla.  
> Pensado para emprendedores y microempresas que no son expertos en contabilidad, pero necesitan entender sus números.

---

## Objetivo del proyecto

El objetivo principal es ayudar a dueños de pequeños negocios a entender la salud financiera de su empresa de forma rápida y visual, usando:

- Estados financieros básicos (Estado de Resultados y Balance General).
- Cálculos automáticos de indicadores clave.
- Módulos de IA que predicen ventas y costos** y **detectan anomalías financieras.
- Un panel web que resume todo en gráficos, tablas e insights en lenguaje simple.

---

## Problema que resuelve

En la práctica, muchas microempresas:

- No tienen acceso a un analista financiero o contador de planta.
- Toman decisiones “por intuición” (comprar más, endeudarse, subir precios) sin ver el impacto real.
- Desconocen métricas básicas como liquidez, rentabilidad o punto de equilibrio, lo que aumenta el riesgo de quiebra.

Este proyecto propone una solución digital, simple y accesible:  
el usuario carga su información en una plantilla y la aplicación se encarga del análisis, las alertas y las recomendaciones.

---

## ¿Qué hace la aplicación?

Al subir un archivo Excel con la estructura esperada, la herramienta genera un dashboard financiero completo con:

### 1. Análisis financiero clásico
- **Análisis vertical y horizontal** del Estado de Resultados y Balance General.
- **Razones financieras** (liquidez, endeudamiento, rentabilidad, etc.).
- **Punto de equilibrio** (en unidades y en moneda).
- **Margen de seguridad** y estructura de costos e ingresos.

### 2. Módulos de IA y ML integrados

#### Predicción de ventas y costos (Regresión Lineal)
- Usa datos históricos de ventas y costos anuales.
- Aplica **Linear Regression** para estimar cómo se comportarán en los próximos **3 años**.
- Permite anticipar:
  - Si las ventas crecen o se estancan.
  - Si los costos están creciendo más rápido que los ingresos.
  - Riesgos de rentabilidad futura.

#### Detección de anomalías financieras  
( Isolation Forest + reglas financieras)

Enfoque híbrido:

1. **Reglas financieras tradicionales**  
   - Variaciones % demasiado altas entre años.  
   - Márgenes negativos inesperados.  
   - Costos creciendo más rápido que las ventas.  
   - Razones financieras fuera de rangos saludables.  
   - Descuadres entre activos, pasivos y patrimonio.

2. **Modelo de Machine Learning – Isolation Forest**  
   - Analiza tendencias de ingresos, costos, activos, pasivos y márgenes. 
   - Marca como anomalía cualquier comportamiento “extraño” respecto a la historia de la empresa.  
   - Para cada caso calcula:
     - `prob_anomalia`
     - Nivel de riesgo: **BAJO, MEDIO o ALTO**.

Esto ayuda a detectar tanto errores contables como riesgos financieros reales antes de que sea tarde.

#### Generación automática de insights

Un módulo adicional procesa:

- Totales financieros.
- Resultados horizontal y vertical.
- Razones financieras.
- Predicciones de IA.
- Anomalías detectadas.

Y genera insights en lenguaje natural, por ejemplo:

- “Costos operativos crecieron más rápido que tus ventas.”  
- “Liquidez actual es saludable, pero tu deuda de largo plazo está ganando peso.”  
- “Se detectó un posible riesgo de flujo de caja en los próximos años.”

---

## Flujo de uso

1. **Descargar una plantilla** desde la aplicación (Excel simple, avanzado o CSV).
2. Completar los datos de la empresa:
   - Datos de cabecera (nombre, tipo de negocio, moneda, fecha de corte).
   - **Estado de resultados** (2 años consecutivos).
   - **Balance general** (2 años consecutivos).
   - Datos para **punto de equilibrio** (precio, costo variable, costos fijos, unidades).  
3. Entrar a la app (`/upload`) y **subir el archivo**.
4. Revisar la pantalla de **confirmación de datos cargados**.
5. Generar el **análisis completo**, navegar por las pestañas:
   - Resumen
   - Análisis horizontal
   - Análisis vertical
   - Razones financieras
   - Punto de equilibrio
   - Predicciones e IA
   - Anomalías financieras
   - Insights automáticos
6. Opcional: **descargar reporte PDF** con el resumen del análisis.

---

## Tecnologías utilizadas

Basado en los archivos de dependencias del proyecto. :contentReference[oaicite:0]{index=0}

| Capa | Tecnologías | Uso principal |
|------|-------------|---------------|
| **Backend** | Python, Flask | Servidor web, rutas, carga de archivos y orquestación del análisis. |
| **Análisis** | `pandas`, `numpy`, `openpyxl` | Lectura de Excel/CSV, limpieza de datos, cálculos financieros. |
| **ML / IA** | `scikit-learn` (Linear Regression, Isolation Forest) | Predicción de ventas y costos, detección de anomalías. |
| **Reportes** | `matplotlib`, `reportlab` | Generación de gráficos y reporte PDF descargable. |
| **Frontend** | HTML, CSS, Bootstrap 5, JavaScript, Chart.js | Interfaz web, visualización de métricas e indicadores. |
| **Utilidades** | `Werkzeug`, `Pathlib`, módulos propios en `utils/` | Manejo de archivos, plantillas, helpers. |

---

## Estructura general del proyecto

*(Los nombres pueden variar ligeramente según el repositorio real)* :contentReference[oaicite:1]{index=1}

```bash
Finanzas-Visuales-analisis-y-gestion-simple-para-microempresas-con-IA/
├── app.py                  # Aplicación Flask principal (rutas y flujo de análisis)
├── requirements.txt        # Dependencias del proyecto
├── templates/              # Vistas HTML (home, upload, confirm_data, results, parciales)
├── static/                 # CSS, JS, imágenes y reports PDF generados
├── utils/                  # Lógica de negocio y módulos de análisis
│   ├── analizador_financiero1.py
│   ├── ia_ventas_costos.py
│   ├── ia_anomalias_financieras.py
│   ├── generador_insights.py
│   └── pdf_generator.py
├── plantillas/             # Plantillas Excel/CSV que el usuario puede descargar
└── uploads/                # Archivos subidos por el usuario (se crean en ejecución)

```
#### Cómo empezar
## Clonar el repositorio
```
git clone https://github.com/SIC-Guzman/Finanzas-Visuales-analisis-y-gestion-simple-para-microempresas-con-IA.git
cd Finanzas-Visuales-analisis-y-gestion-simple-para-microempresas-con-IA
```
## Crear y activar un entorno virtual (opcional pero recomendado)
```
python -m venv venv
```

# Windows
```
venv\Scripts\activate
```
# Linux / macOS
```
source venv/bin/activate
```
## Instalar dependencias
```
pip install -r requirements.txt
```

## Ejecutar la aplicación
```
python app.py
```
## Abrir el navegador en:
```
http://localhost:5000
```
Datos de ejemplo y demo

## El proyecto incluye:

Página de demo (/analysis) con datos ficticios para ver el tipo de análisis que genera la herramienta.

Plantillas descargables desde la interfaz:

- Excel simple.
- Excel avanzado.
- CSV (texto plano para evitar problemas de acentos o formatos).
- Estas plantillas ya traen la estructura esperada para:
- Datos de la empresa.
- Estado de resultados.
- Balance general.
- Punto de equilibrio.

Solo necesitas reemplazar los valores de ejemplo por los de tu negocio.

### Equipo del proyecto (roles técnicos)

- Roberto Dávila – Desarrollador IA de insights automáticos
- Fernando López – Desarrollador de módulo de predicción de ventas y costos
- Jaquelin Calanche – Desarrolladora de detección de anomalías financieras
- Angela Canel – Desarrolladora de documentación y experiencia de usuario 
- Carlos Gutiérrez – Integrador full-stack y refactorización del proyecto (unificación y corrección de errores)

