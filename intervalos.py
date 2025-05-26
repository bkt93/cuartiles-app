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
            vmin, vmax = round(valores.min(), 5), round(valores.max(), 5)

            # Medias por cuartil
            media_q1 = round(np.mean(valores[valores < p25]), 2)
            media_q2 = round(np.mean(valores[(valores >= p25) & (valores < p50)]), 2)
            media_q3 = round(np.mean(valores[(valores >= p50) & (valores < p75)]), 2)
            media_q4 = round(np.mean(valores[valores >= p75]), 2)

            # Intervalos reales
            intervalo_q1 = f"[{vmin}, {round(p25, 5)})"
            intervalo_q2 = f"[{round(p25, 5)}, {round(p50, 5)})"
            intervalo_q3 = f"[{round(p50, 5)}, {round(p75, 5)})"
            intervalo_q4 = f"[{round(p75, 5)}, {vmax}]"

            if not invertir:
                normales.append({
                    "Métrica": col,
                    "Q1": intervalo_q1,
                    "Q2": intervalo_q2,
                    "Q3": intervalo_q3,
                    "Q4": intervalo_q4,
                    "Media Q1": media_q1,
                    "Media Q2": media_q2,
                    "Media Q3": media_q3,
                    "Media Q4": media_q4
                })
            else:
                invertidas.append({
                    "Métrica": col,
                    "Q4": intervalo_q1,
                    "Q3": intervalo_q2,
                    "Q2": intervalo_q3,
                    "Q1": intervalo_q4,
                    "Media Q4": media_q1,
                    "Media Q3": media_q2,
                    "Media Q2": media_q3,
                    "Media Q1": media_q4
                })

    df_normales = pd.DataFrame(normales)
    df_invertidas = pd.DataFrame(invertidas)

    if not df_normales.empty and not df_invertidas.empty:
        df_normales = pd.concat(
            [df_normales, pd.DataFrame([[""] * len(df_normales.columns)], columns=df_normales.columns)]
        )

    return pd.concat([df_normales, df_invertidas], ignore_index=True)
