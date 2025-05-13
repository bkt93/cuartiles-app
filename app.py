import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Asignador de Cuartiles", layout="centered")

st.title("📊 Asignador de Cuartiles")
st.markdown("Subí un archivo `.xlsx`, seleccioná una columna numérica, y calcularemos los cuartiles automáticamente.")

# Subida de archivo
archivo = st.file_uploader("📂 Subí tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo is not None:
    try:
        df = pd.read_excel(archivo)
        st.success("Archivo cargado correctamente.")
        st.dataframe(df.head())

        columnas_numericas = df.select_dtypes(include="number").columns.tolist()

        if not columnas_numericas:
            st.warning("⚠️ El archivo no tiene columnas numéricas para calcular cuartiles.")
        else:
            columna = st.selectbox("📌 Seleccioná la columna para calcular cuartiles:", columnas_numericas)

            if st.button("📈 Calcular Cuartiles"):
                df["Cuartil"] = pd.qcut(df[columna], q=4, labels=["Q1", "Q2", "Q3", "Q4"])
                st.success("✅ Cuartiles calculados.")
                st.dataframe(df[[columna, "Cuartil"]])

                # Descargar resultado
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Resultados")
                st.download_button(
                    label="📥 Descargar Excel con Cuartiles",
                    data=buffer.getvalue(),
                    file_name="resultado_cuartiles.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
