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
            col_ids = st.multiselect("🆔 Seleccioná una o más columnas identificadoras (por ejemplo: asesor, líder):", columnas_totales)
            col_nums = st.multiselect("📊 Seleccioná una o más columnas numéricas a cuartilizar:", columnas_numericas)

            invertir = st.checkbox("🔄 Invertir cuartiles (valores altos corresponden a Q4)")

            if st.button("📈 Calcular Cuartiles"):
                df_resultado = df[col_ids].copy()  # arrancamos con identificadores

                for col in col_nums:
                    valores = df[col].dropna()
                    p25, p50, p75 = np.percentile(valores, [25, 50, 75], method="linear")
                    col_redondeada = df[col].round(2)

                    # Asignar cuartil
                    def clasificar(v):
                        if pd.isna(v): return None
                        if v >= p75: return "Q1"
                        elif v >= p50: return "Q2"
                        elif v >= p25: return "Q3"
                        else: return "Q4"

                    cuartil = col_redondeada.apply(clasificar)

                    # Invertir cuartil si se tilda
                    if invertir:
                        cuartil = cuartil.replace({
                            "Q1": "Q4", "Q2": "Q3", "Q3": "Q2", "Q4": "Q1"
                        })

                    # Intervalo
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

                    intervalo = df[col].apply(calcular_intervalo)

                    # Agregar columnas al resultado
                    df_resultado[col] = col_redondeada
                    df_resultado[f"{col}_Cuartil"] = cuartil
                    df_resultado[f"{col}_Intervalo"] = intervalo

                st.success("✅ Cuartiles calculados para todas las columnas seleccionadas.")
                st.dataframe(df_resultado)

                # Exportar a Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df_resultado.to_excel(writer, index=False, sheet_name="Resultados")
                st.download_button(
                    label="📥 Descargar Excel con Cuartiles",
                    data=buffer.getvalue(),
                    file_name="resultado_cuartiles_multiples.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
