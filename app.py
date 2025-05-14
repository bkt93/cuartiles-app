import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="Asignador de Cuartiles", layout="centered")

st.title("📊 Asignador de Cuartiles")
st.markdown("Subí un archivo `.xlsx`, seleccioná una columna identificadora y una columna numérica para cuartilizar.")

# Botón de reinicio
if st.button("🔁 Reiniciar aplicación"):
    st.cache_data.clear()
    st.experimental_rerun()

# Subida de archivo
archivo = st.file_uploader("📂 Subí tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo is not None:
    try:
        df = pd.read_excel(archivo)
        st.success("Archivo cargado correctamente.")
        st.dataframe(df.head())

        columnas_numericas = df.select_dtypes(include="number").columns.tolist()
        columnas_totales = df.columns.tolist()

        if not columnas_numericas:
            st.warning("⚠️ El archivo no tiene columnas numéricas para calcular cuartiles.")
        else:
            col_id = st.selectbox("🆔 Seleccioná la columna identificadora (por ejemplo: nombre del colaborador):", columnas_totales)
            col_num = st.selectbox("📊 Seleccioná la columna numérica a cuartilizar:", columnas_numericas)

            invertir = st.checkbox("🔄 Invertir orden de cuartiles (Q4 es mejor que Q1)")

            if st.button("📈 Calcular Cuartiles"):
                valores = df[col_num].dropna()

                # Obtener percentiles como en Excel (PERCENTIL.EXC)
                p25, p50, p75 = np.percentile(valores, [25, 50, 75], method="linear")

                # Redondear la columna original
                df[col_num] = df[col_num].round(2)

                # Asignar cuartiles al estilo Excel
                def clasificar(v):
                    if pd.isna(v): return None
                    if v >= p75: return "Q1"
                    elif v >= p50: return "Q2"
                    elif v >= p25: return "Q3"
                    else: return "Q4"

                cuartiles = df[col_num].apply(clasificar)

                if invertir:
                    cuartiles = cuartiles.replace({
                        "Q1": "Q4", "Q2": "Q3", "Q3": "Q2", "Q4": "Q1"
                    })

                # Generar intervalo legible
                def calcular_intervalo(v):
                    if pd.isna(v): return None
                    if v >= p75:
                        return f"[{round(p75,2)}, máx]"
                    elif v >= p50:
                        return f"[{round(p50,2)}, {round(p75,2)})"
                    elif v >= p25:
                        return f"[{round(p25,2)}, {round(p50,2)})"
                    else:
                        return f"[mín, {round(p25,2)})"

                intervalos = df[col_num].apply(calcular_intervalo)

                # Armar resultado final
                df_resultado = pd.DataFrame({
                    col_id: df[col_id],
                    col_num: df[col_num],
                    "Cuartil": cuartiles,
                    "Intervalo": intervalos
                })

                st.success("✅ Cuartiles asignados al estilo Excel (PERCENTIL.EXC)")
                st.dataframe(df_resultado)

                # Exportar a Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df_resultado.to_excel(writer, index=False, sheet_name="Resultados")
                st.download_button(
                    label="📥 Descargar Excel con Cuartiles",
                    data=buffer.getvalue(),
                    file_name="resultado_cuartiles.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
