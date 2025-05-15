import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="Asignador de Cuartiles", layout="centered")
st.title("📊 Asignador de Cuartiles por Grupos de Métricas")

archivo = st.file_uploader("📂 Subí tu archivo Excel (.xlsx)", type=["xlsx"])

# Inicializar siempre 2 grupos
num_grupos = 2

if archivo is not None:
    try:
        df = pd.read_excel(archivo)
        st.success("Archivo cargado correctamente.")
        st.dataframe(df.head())

        columnas_totales = df.columns.tolist()
        columnas_numericas = df.select_dtypes(include="number").columns.tolist()

        # Identificadores
        col_ids = st.multiselect("🆔 Seleccioná columnas identificadoras (ej: asesor, líder):", columnas_totales)

        # Grupos de métricas
        for i in range(num_grupos):
            st.markdown(f"### 🔢 Grupo de métricas #{i + 1}")

            st.multiselect(
                f"Seleccioná columnas numéricas para el grupo #{i+1}",
                columnas_numericas,
                key=f"colnum_{i}"
            )

            st.checkbox(
                "Asignar Q1 a valores altos → NPS, SAT, etc",
                value=False,
                key=f"invertir_{i}"
            )

            st.markdown("---")

        # Botón de cálculo
        if st.button("📈 Calcular Cuartiles"):
            df_resultado = df[col_ids].copy() if col_ids else pd.DataFrame()

            for i in range(num_grupos):
                columnas = st.session_state.get(f"colnum_{i}", [])
                invertir = st.session_state.get(f"invertir_{i}", False)

                for col in columnas:
                    valores = df[col].dropna()
                    p25, p50, p75 = np.percentile(valores, [25, 50, 75], method="linear")
                    col_red = df[col].round(2)

                    def clasificar(v):
                        if pd.isna(v): return None
                        if v >= p75: return "Q4"
                        elif v >= p50: return "Q3"
                        elif v >= p25: return "Q2"
                        else: return "Q1"

                    cuartil = col_red.apply(clasificar)

                    if invertir:
                        cuartil = cuartil.replace({
                            "Q1": "Q4", "Q2": "Q3", "Q3": "Q2", "Q4": "Q1"
                        })

                    def intervalo(v):
                        if pd.isna(v): return None
                        if v >= p75: return f"[{round(p75,2)}, máx]"
                        elif v >= p50: return f"[{round(p50,2)}, {round(p75,2)})"
                        elif v >= p25: return f"[{round(p25,2)}, {round(p50,2)})"
                        else: return f"[mín, {round(p25,2)})"

                    df_resultado[col] = col_red
                    df_resultado[f"{col}_Cuartil"] = cuartil
                    df_resultado[f"{col}_Intervalo"] = df[col].apply(intervalo)

            st.success("✅ Cuartiles generados para todos los conjuntos.")
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
