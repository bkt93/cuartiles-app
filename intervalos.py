import pandas as pd
import numpy as np
import streamlit as st

def construir_tabla_intervalos(df, num_grupos):
    normales = []
    invertidas = []

    for i in range(num_grupos):
        columnas = st.session_state.get(f"colnum_{i}", [])
        invertir = st.session_state.get(f"invertir_{i}", False)

        for col in columnas:
            valores = df[col].dropna()
            if len(valores) == 0:
                continue
            p25, p50, p75 = np.percentile(valores, [25, 50, 75], method="linear")

            # Generar intervalos
            intervalo_q1 = f"[mín, {round(p25,5)})"
            intervalo_q2 = f"[{round(p25,2)}, {round(p50,5)})"
            intervalo_q3 = f"[{round(p50,2)}, {round(p75,5)})"
            intervalo_q4 = f"[{round(p75,5)}, máx]"

            if not invertir:
                normales.append({
                    "Métrica": col,
                    "Q1": intervalo_q1,
                    "Q2": intervalo_q2,
                    "Q3": intervalo_q3,
                    "Q4": intervalo_q4
                })
            else:
                invertidas.append({
                    "Métrica": col,
                    "Q4": intervalo_q1,
                    "Q3": intervalo_q2,
                    "Q2": intervalo_q3,
                    "Q1": intervalo_q4
                })

    # Convertir a DataFrames
    df_normales = pd.DataFrame(normales)
    df_invertidas = pd.DataFrame(invertidas)

    # Insertar separación visual si ambos existen
    if not df_normales.empty and not df_invertidas.empty:
        df_normales = pd.concat([df_normales, pd.DataFrame([[""] * 5], columns=df_normales.columns)])

    return pd.concat([df_normales, df_invertidas], ignore_index=True)
