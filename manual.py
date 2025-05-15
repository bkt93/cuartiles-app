# manual.py

import streamlit as st

def mostrar_manual():
    with st.expander("📘 Manual paso a paso - Cómo usar esta herramienta"):
        st.markdown("""
### 📊 ¿Qué hace esta herramienta?
Este asignador de cuartiles permite subir un archivo Excel con datos numéricos y asignar cuartiles automáticos a distintas métricas.

### ✅ ¿Qué necesito?
1. Un archivo **.xlsx** que contenga:
   - Columnas con **datos numéricos** (ej: NPS, SAT, ventas).
   - Opcionalmente, columnas identificadoras (como nombre del asesor o líder).

### 🧩 ¿Cómo funciona?
- Seleccionás una o más **columnas identificadoras** (por ejemplo, Asesor y Líder).
- Luego hay **2 grupos** disponibles para analizar métricas:
  - En cada grupo seleccionás **una o más columnas numéricas**.
  - Podés marcar si querés que **Q1 represente valores altos** (por ejemplo, en métricas como NPS, SAT, etc)
  - Si no marcás nada, se considera que **Q4 representa los valores altos** (útil para métricas como TOL, TMO, %Auxiliares, etc)

### 📈 ¿Qué hace el botón 'Calcular Cuartiles'?
Cuando presionás este botón:

- Se procesan todas las columnas numéricas seleccionadas.
- Para cada métrica, se agregan **dos columnas nuevas**:
  - `📌 _Cuartil`: indica en qué cuartil cae cada valor. Pueden ser:
    - **Q1**: valores más bajos
    - **Q4**: valores más altos
    - (esto puede invertirse si marcás la opción correspondiente)
  - `📌 _Intervalo`: muestra el rango exacto del cuartil.

#### 🔍 ¿Qué significan los intervalos?
Los intervalos se generan automáticamente dividiendo los datos en 4 partes iguales. Por ejemplo:

- **Q1 →** `[mín, 424.25)` → Los valores más bajos (25%)
- **Q2 →** `[424.25, 498.76)` → Segundo cuarto
- **Q3 →** `[498.76, 570.01)` → Tercer cuarto
- **Q4 →** `[570.01, máx]` → Los valores más altos (25%)

Esto te permite no solo ver si un asesor está en Q2 o Q4, sino también **cuál es el rango real de valores** para cada cuartil.

---

### 📐 ¿Cómo se calculan los cuartiles?
Esta app utiliza el método de cálculo equivalente a `PERCENTIL.EXC` en Excel:

- Se basa en una lógica **estadística profesional** que excluye los valores extremos (0% y 100%).
- Es ideal para comparar datos distribuidos de forma más realista.
- Los puntos de corte (percentiles 25, 50 y 75) se calculan con la función `np.percentile(..., method="linear")` de forma precisa.

### 📥 ¿Cómo obtengo el resultado?
- Una vez calculado, podés descargar el archivo Excel listo para usar.

---
                    
### 📄 ¿Qué contiene la hoja "Intervalos" del Excel exportado?
Además de los resultados cuartilizados por colaborador, el archivo Excel también incluye una hoja adicional llamada **"Intervalos"**.
                    
🟦 Métricas estándar (Q4 = valores altos, Q1 = valores bajos):

| Métrica | Q1             | Q2                | Q3                | Q4             |
| ------- | -------------- | ----------------- | ----------------- | -------------- |
| Tol     | \[mín, 424.25) | \[424.25, 502.0)  | \[502.0, 564.75)  | \[564.75, máx] |
| Tmo     | \[mín, 429.58) | \[429.58, 521.69) | \[521.69, 590.48) | \[590.48, máx] |

🟩 Métricas invertidas (Q1 = valores altos, Q4 = valores bajos):
                    
| Métrica | Q1            | Q2              | Q3             | Q4           |
| ------- | ------------- | --------------- | -------------- | ------------ |
| Nps     | \[66.67, máx] | \[46.06, 66.67) | \[20.0, 46.06) | \[mín, 20.0) |
| Sat     | \[9.81, máx]  | \[9.27, 9.81)   | \[8.18, 9.27)  | \[mín, 8.18) |

🔎 Esta tabla te permite **consultar rápidamente los límites reales** que se usaron para asignar los cuartiles, sin necesidad de revisar todos los datos uno por uno.

💡 Es útil si querés:
- Interpretar cómo se calculó cada Q.
- Replicar la lógica en otros sistemas o reportes.
- Ver los puntos de corte por métrica de forma centralizada.

---
                    
**Ejemplo de uso**:
- Grupo 1 → TMO, TOL (sin marcar)
- Grupo 2 → NPS, SAT (marcar Q1 como alto ✅)

Así podés comparar todas las métricas con una escala homogénea de cuartiles.
""")
