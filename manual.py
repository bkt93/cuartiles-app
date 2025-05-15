import streamlit as st

def mostrar_manual():
    st.markdown("""
## 📘 Manual - Cómo usar esta herramienta

### 📊 ¿Qué hace esta herramienta?
Este asignador de cuartiles permite subir un archivo Excel con datos numéricos y asignar cuartiles automáticos a distintas métricas. También permite **agregar filas de resumen** con sumatorias o promedios seleccionados.

---

### ✅ ¿Qué necesito?
1. Un archivo **.xlsx** que contenga:
   - Columnas con **datos numéricos** (ej: NPS, SAT, Ventas, TMO).
   - Opcionalmente, columnas identificadoras (como nombre del asesor o líder).

---

### 🧩 ¿Cómo funciona?
- Seleccionás una o más **columnas identificadoras** (por ejemplo, Asesor y Líder).
- Luego hay **2 grupos** para cuartilizar métricas:
  - En cada grupo seleccionás **una o más columnas numéricas**.
  - Podés marcar si querés que **Q1 represente valores altos** (por ejemplo, NPS, SAT).
  - Si no marcás nada, se asume que **Q4 representa valores altos** (ej: TMO, TOL).

---

### 🧮 ¿Qué son las filas de resumen?
Antes de calcular, podés configurar **dos filas de resumen**:

- En cada fila:
  - Elegís columnas numéricas para resumir.
  - Elegís si querés mostrar su **Promedio** o **Sumatoria**.
- Estas filas se agregarán automáticamente al final del Excel exportado.
- Aparecen con fondo rojo y fuente en negrita.
- El nombre de la fila indica el tipo: `Promedio` o `Sumatoria`.

---

### 📈 ¿Qué hace el botón 'Calcular Cuartiles'?
Cuando presionás este botón:

1. Se procesan los dos grupos de métricas.
2. Para cada métrica, se agregan **dos columnas nuevas**:
   - `🟢 _Cuartil`: indica si el valor está en Q1, Q2, Q3 o Q4.
   - `🟡 _Intervalo`: muestra el rango de cada cuartil.
3. Se agregan las **filas de resumen** que configuraste.
4. Podés **descargar el Excel** completo con los resultados.

---

### 🔍 ¿Qué significan los cuartiles e intervalos?
Los intervalos se generan automáticamente dividiendo los datos en 4 partes iguales. Por ejemplo:

- **Q1 →** `[mín, 424.25)` → Los valores más bajos (25%)
- **Q2 →** `[424.25, 498.76)`
- **Q3 →** `[498.76, 570.01)`
- **Q4 →** `[570.01, máx]` → Los valores más altos (25%)

---

### 📐 ¿Cómo se calculan los cuartiles?
- Se utiliza el método `PERCENTIL.EXC` como en Excel.
- Se excluyen los extremos (0% y 100%) para mayor precisión.
- Se implementa con `np.percentile(..., method="linear")`.

---

### 📥 ¿Qué incluye el Excel descargado?
1. **Hoja "Resultados"**:
   - Datos con columnas cuartilizadas.
   - Filas de resumen configuradas (Promedio / Sumatoria).
   - Las filas de resumen están en **color rojo** para identificarlas fácilmente.

2. **Hoja "Intervalos"**:
   - Tabla con los rangos utilizados para cada cuartil.
   - Se muestran tanto métricas estándar como invertidas.

---

### 📄 ¿Cómo interpretar la hoja "Intervalos"?

🟦 Métricas estándar (Q4 = valores altos):

| Métrica | Q1             | Q2                | Q3                | Q4             |
| ------- | -------------- | ----------------- | ----------------- | -------------- |
| Tol     | \[mín, 424.25) | \[424.25, 502.0)  | \[502.0, 564.75)  | \[564.75, máx] |
| Tmo     | \[mín, 429.58) | \[429.58, 521.69) | \[521.69, 590.48) | \[590.48, máx] |

🟩 Métricas invertidas (Q1 = valores altos, Q4 = valores bajos):

| Métrica | Q1            | Q2              | Q3             | Q4           |
| ------- | ------------- | --------------- | -------------- | ------------ |
| Nps     | \[66.67, máx] | \[46.06, 66.67) | \[20.0, 46.06) | \[mín, 20.0) |
| Sat     | \[9.81, máx]  | \[9.27, 9.81)   | \[8.18, 9.27)  | \[mín, 8.18) |

💡 Esta tabla te permite interpretar rápidamente cómo se definieron los cuartiles para cada métrica.

---

### ✨ Ejemplo de configuración sugerida

- **Grupo 1:** TMO, TOL → (sin invertir)
- **Grupo 2:** NPS, SAT → (invertido ✅)
- **Resumen 1:** Promedio de TMO y TOL
- **Resumen 2:** Sumatoria de llamadas

Así podés:
- Comparar métricas con escala homogénea.
- Ver qué asesores están en qué cuartil.
- Descargar un Excel listo para análisis o reportes.

""")
