import streamlit as st
import pandas as pd
import numpy as np
import io
from manual import mostrar_manual  
from intervalos import construir_tabla_intervalos
from openpyxl.styles import Font, PatternFill


st.set_page_config(page_title="Cuartiles y totales", layout="wide")



st.title("📊 Calculadora de cuartiles")
st.info("📘 Antes de continuar, te recomendamos leer el manual para entender cómo funciona esta herramienta.")

st.markdown("---")

archivo = st.file_uploader("📂 Subí tu archivo Excel (.xlsx)", type=["xlsx"])

# Inicializar siempre 2 grupos
num_grupos = 2
num_calculo_totales = 2

if archivo is not None:
    try:
        df = pd.read_excel(archivo)
        # Eliminar filas "Total" que afectan el cálculo
        df = df[~df.iloc[:, 0].astype(str).str.startswith("Total")]

        st.success("Archivo cargado correctamente.")
        #st.dataframe(df.head())

        st.markdown("---")

        columnas_totales = df.columns.tolist()
        columnas_numericas = df.select_dtypes(include="number").columns.tolist()

        # Identificadores
        st.markdown(f"### 🆔 Seleccionar identificador")
        col_ids = st.multiselect("Seleccioná columnas identificadoras (ej: asesor, líder, llamadas):", 
                                columnas_totales,
                                help="Las columnas identificadoras puede ser asesor, líder, usuario t3, id avaya o incluso llamadas.")

        st.markdown("---")

        st.info("⚠️ Métricas como NPS, SAT deben tildar el campo para cuartilizado inverso (Q1 valores altos)")

        cols_metricas = st.columns(2)  # Creamos dos columnas

        for i in range(num_grupos):
            with cols_metricas[i % 2]:  # Alternamos entre la columna izquierda y derecha
                st.markdown(f"### 🔢 Grupo de métricas #{i + 1}")

                st.multiselect(
                    f"Seleccioná columnas numéricas para el grupo #{i + 1}",
                    columnas_numericas,
                    key=f"colnum_{i}",
                    help="Elegí las métricas que querés cuartilizar en este grupo."
                )

                st.checkbox(
                    "Asignar Q1 a valores altos → NPS, SAT, etc",
                    value=False,
                    key=f"invertir_{i}",
                    help="Esta selección invierte el sentido de los cuartiles. Por defecto los Q4 están asignados a valores altos."
                )


        st.markdown("---")

        incluir_intervalos = st.checkbox("📏 Incluir columnas de intervalo por métrica", value=False)

        # Botón de cálculo
        if st.button("📈 Calcular cuartiles/totales"):
            df_resultado = df[col_ids].copy() if col_ids else pd.DataFrame()

            for i in range(num_grupos):
                columnas = st.session_state.get(f"colnum_{i}", [])
                invertir = st.session_state.get(f"invertir_{i}", False)

                for col in columnas:
                    valores = df[col].dropna()
                    p25, p50, p75 = np.percentile(valores, [25, 50, 75], method="linear")
                    col_red = df[col].round(5)

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
                        if v >= p75: return f"[{round(p75,5)}, máx]"
                        elif v >= p50: return f"[{round(p50,5)}, {round(p75,5)})"
                        elif v >= p25: return f"[{round(p25,5)}, {round(p50,5)})"
                        else: return f"[mín, {round(p25,5)})"


                    df_resultado[col] = col_red
                    df_resultado[f"{col}_Cuartil"] = cuartil
                    if incluir_intervalos:
                        df_resultado[f"{col}_Intervalo"] = df[col].apply(intervalo)


            st.success("✅ Cuartiles generados para todos los conjuntos.")
            df_intervalos = construir_tabla_intervalos(df, num_grupos)

            # Exportar a Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_resultado.to_excel(writer, index=True, sheet_name="Resultados")
                df_intervalos.to_excel(writer, index=False, sheet_name="Intervalos")

                workbook = writer.book
                worksheet = writer.sheets["Resultados"]

            st.download_button(
                label="📥 Descargar Excel calculado",
                data=buffer.getvalue(),
                file_name="resultado_cuartiles.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

with st.sidebar:
    #if st.checkbox("📘 Mostrar manual de uso"):
    mostrar_manual()