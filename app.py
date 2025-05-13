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

            # Checkbox para invertir cuartiles
            invertir = st.checkbox("🔄 Invertir orden de cuartiles (Dependiendo la métrica, por defecto Q4 para valores altos)")

            if st.button("📈 Calcular Cuartiles"):
                # Etiquetas según si se invierten o no
                etiquetas = ["Q1", "Q2", "Q3", "Q4"]
                if invertir:
                    etiquetas = etiquetas[::-1]  # ["Q4", "Q3", "Q2", "Q1"]

                # Calcular cuartiles y los intervalos
                cuartiles, intervalos = pd.qcut(df[col_num], q=4, labels=etiquetas, retbins=True)

                # Redondear valores originales a 2 decimales
                col_numerica_redondeada = df[col_num].round(2)

                # Convertir intervalos a texto legible con 2 decimales
                def format_interval(valor):
                    left = f"{valor.left:.2f}".replace('.', ',')
                    right = f"{valor.right:.2f}".replace('.', ',')
                    return f"({left}, {right}]"

                intervalos_str = pd.cut(df[col_num], bins=intervalos).apply(format_interval)

                # Crear dataframe de resultado
                df_resultado = pd.DataFrame({
                    col_id: df[col_id],
                    col_num: col_numerica_redondeada,
                    "Cuartil": cuartiles,
                    "Intervalo": intervalos_str
                })

                st.success("✅ Cuartiles calculados.")
                st.dataframe(df_resultado)

                # Exportar Excel
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
