import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(page_title="Asignador de Cuartiles", layout="centered")

st.title("📊 Asignador de Cuartiles por Grupos de Métricas")

# Reinicio
if st.button("🔁 Reiniciar aplicación"):
    st.cache_data.clear()
    st.session_state.clear()
    st.experimental_rerun()

archivo = st.file_uploader("📂 Subí tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo is not None:
    try:
        df = pd.read_excel(archivo)
        st.success("Archivo cargado correctamente.")
        st.dataframe(df.head())

        columnas_totales = df.columns.tolist()
        columnas_numericas = df.select_dtypes(include="number").columns.tolist()

        # Selección de identificadores
        col_ids = st.multiselect("🆔 Seleccioná columnas identificadoras (ej: asesor, líder):", columnas_totales)

        # Inicializar grupos en session_state
        if "grupos" not in st.session_state:
            st.session_state.grupos = [{"columnas": [], "invertir": False}]

        # Mostrar cada conjunto de métricas
        for i, grupo in enumerate(st.session_state.grupos):
            st.markdown(f"### 🔢 Grupo de métricas #{i+1}")
            st.session_state.grupos[i]["columnas"] = st.multiselect(
                f"Seleccioná columnas numéricas para el grupo #{i+1}",
                columnas_numericas,
                default=grupo["columnas"],
                key=f"colnum_{i}"
            )
            st.session_state.grupos[i]["invertir"] = st.checkbox(
                "Asignar Q1 a valores altos (NPS, SAT, etc)",
                value=grupo["invertir"],
                key=f"invertir_{i}"
            )
            st.markdown("---")

        # Botón para agregar más grupos
        if st.button("➕ Agregar nuevo conjunto de métricas"):
            st.session_state.grupos.append({"columnas": [], "invertir": False})

        # Calcular cuartiles
        if st.button("📈 Calcular Cuartiles"):
            df_resultado = df[col_ids].copy() if col_ids else pd.DataFrame()

            for idx, grupo in enumerate(st.session_state.grupos):
                columnas = grupo["columnas"]
                invertir = grupo["invertir"]

                for col in columnas:
                    valores = df[col].dropna()
                    p25, p50, p75 = np.percentile(valores, [25, 50, 75], method="linear")
                    col_red = df[col].round(2)

                    # Asignar cuartil estilo Excel
                    def clasificar(v):
                        if pd.isna(v): return None
                        if v >= p75: return "Q1"
                        elif v >= p50: return "Q2"
                        elif v >= p25: return "Q3"
                        else: return "Q4"

                    cuartil = col_red.apply(clasificar)

                    if invertir:
                        # Si se tilda el checkbox: queremos que Q1 represente valores altos
                        cuartil = cuartil.replace({
                            "Q4": "Q1", "Q3": "Q2", "Q2": "Q3", "Q1": "Q4"
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

            # Exportar resultado
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
