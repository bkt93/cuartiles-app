import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Asignador de Cuartiles", layout="centered")

st.title("📊 Asignador de Cuartiles")
st.markdown("Subí un archivo `.xlsx`, seleccioná una columna identificadora y una columna numérica para cuartilizar.")

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

            if st.button("📈 Calcular Cuartiles"):
                # Calcular cuartiles con pandas qcut
                cuartiles, intervalos = pd.qcut(df[col_num], q=4, labels=["Q1", "Q2", "Q3", "Q4"], retbins=True)

                # Crear nuevo dataframe con solo lo necesario
                df_resultado = pd.DataFrame({
                    col_id: df[col_id],
                    col_num: df[col_num],
                    "Cuartil": cuartiles,
                    "Intervalo": pd.cut(df[col_num], bins=intervalos)
                })

                st.success("✅ Cuartiles calculados.")
                st.dataframe(df_resultado)

                # Preparar archivo para descarga
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
