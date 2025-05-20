import streamlit as st
import pandas as pd
import numpy as np
import io
from manual import mostrar_manual  
from intervalos import construir_tabla_intervalos
from openpyxl.styles import Font, PatternFill


st.set_page_config(page_title="Cuartiles y totales", layout="wide")



st.title("📊 Calculadora de cuartiles y totales")

st.markdown("---")

archivo = st.file_uploader("📂 Subí tu archivo Excel (.xlsx)", type=["xlsx"])

# Inicializar siempre 2 grupos
num_grupos = 2
num_calculo_totales = 2

if archivo is not None:
    try:
        df = pd.read_excel(archivo)
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



        # 🟩 Bloque SIEMPRE visible de resumen

        st.markdown("---")

        st.info("⚠️ Para calcular totales, las columnas antes deben haber sido seleccionadas para cuartilizar. En caso de 'Llamadas' elegirla como identificador del colaborador.")

        cols_totales = st.columns(2)  # Creamos 2 columnas de ancho igual

        for i in range(num_calculo_totales):
            with cols_totales[i % 2]:  # Alternamos entre la izquierda (0) y la derecha (1)
                st.markdown(f"### 🧮 Añadir fila de totales #{i + 1}")

                resumen_columnas = st.multiselect(
                    f"Seleccioná columnas para totales #{i + 1}",
                    columnas_numericas,
                    key=f"resumen_cols_selector_{i}"
                )

                tipo_resumen = st.radio(
                    "Tipo de resumen:",
                    ["Promedio", "Sumatoria"],
                    key=f"resumen_tipo_selector_{i}"
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
                        if v >= p75: return f"[{round(p75,5)}, máx]"
                        elif v >= p50: return f"[{round(p50,5)}, {round(p75,5)})"
                        elif v >= p25: return f"[{round(p25,5)}, {round(p50,5)})"
                        else: return f"[mín, {round(p25,5)})"


                    df_resultado[col] = col_red
                    df_resultado[f"{col}_Cuartil"] = cuartil
                    if incluir_intervalos:
                        df_resultado[f"{col}_Intervalo"] = df[col].apply(intervalo)


            # Añadir múltiples filas de resumen
            for i in range(num_calculo_totales):
                resumen_columnas = st.session_state.get(f"resumen_cols_selector_{i}", [])
                tipo_resumen = st.session_state.get(f"resumen_tipo_selector_{i}", "Promedio")

                if resumen_columnas:
                    resumen = {}
                    for col in resumen_columnas:
                        if tipo_resumen == "Promedio":
                            resumen[col] = round(df[col].mean(), 2)
                        else:
                            resumen[col] = round(df[col].sum(), 2)
                    
                    fila_resumen = {col: resumen.get(col, "") for col in df_resultado.columns}
                    df_resultado.loc[f"{tipo_resumen}"] = fila_resumen


            st.success("✅ Cuartiles generados para todos los conjuntos.")
            #st.dataframe(df_resultado)
            #  mostrar_resumen_en_pantalla(df_resultado)
            df_intervalos = construir_tabla_intervalos(df, num_grupos)

            # Exportar a Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_resultado.to_excel(writer, index=True, sheet_name="Resultados")
                df_intervalos.to_excel(writer, index=False, sheet_name="Intervalos")

                workbook = writer.book
                worksheet = writer.sheets["Resultados"]

                # Estilo rojo
                red_fill = PatternFill(start_color="FF9999", end_color="FF9999", fill_type="solid")
                bold_font = Font(bold=True)

                # Buscar filas que contienen "Resumen" (ignorar encabezado)
                for row_idx, row in enumerate(df_resultado.itertuples(), start=2):
                    if str(row.Index).startswith("Promedio") or str(row.Index).startswith("Sumatoria"):
                        for col_idx in range(1, len(df_resultado.columns) + 1):
                            cell = worksheet.cell(row=row_idx, column=col_idx)
                            cell.fill = red_fill
                            cell.font = bold_font
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