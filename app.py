import streamlit as st
import pandas as pd
import os

NOME_FILE = 'spese_famiglia.xlsx'

# Configurazione Pagina
st.set_page_config(page_title="Casa Mesagne - Spese", layout="centered")

st.title("📊 Gestione Spese Famiglia")
st.write("Segna le spese per i bimbi o per la casa direttamente da qui!")

# Caricamento dati
if os.path.exists(NOME_FILE):
    df = pd.read_excel(NOME_FILE)
else:
    df = pd.DataFrame(columns=['Data', 'Categoria', 'Descrizione', 'Importo'])

# --- SEZIONE AGGIUNGI ---
with st.expander("➕ Aggiungi Nuova Spesa"):
    data = st.date_input("Quando?")
    cat = st.selectbox("Categoria", ["Supermercato", "Bimbi", "Bollette", "Svago", "Altro"])
    desc = st.text_input("Cosa hai comprato?")
    prezzo = st.number_input("Quanto hai speso? (€)", min_value=0.0, step=0.10)
    
    if st.button("Salva Spesa"):
        nuova_riga = pd.DataFrame({'Data': [data], 'Categoria': [cat], 'Descrizione': [desc], 'Importo': [prezzo]})
        df = pd.concat([df, nuova_riga], ignore_index=True)
        df.to_excel(NOME_FILE, index=False)
        st.success("Spesa registrata correttamente!")

# --- SEZIONE VISUALIZZA ---
st.divider()
st.subheader("Riepilogo")

if not df.empty:
    col1, col2 = st.columns(2)
    col1.metric("Totale Speso", f"€ {df['Importo'].sum():.2f}")
    col2.metric("N. Operazioni", len(df))

    tab1, tab2 = st.tabs(["Tabella", "Grafico"])
    
    with tab1:
        st.dataframe(df.sort_values(by='Data', ascending=False), use_container_width=True)
    
    with tab2:
        st.bar_chart(df.groupby('Categoria')['Importo'].sum())
else:
    st.info("Non ci sono ancora spese registrate.")
