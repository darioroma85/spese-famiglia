import streamlit as st
import pandas as pd
import os

NOME_FILE = 'spese_famiglia.xlsx'

st.set_page_config(page_title="Casa Mesagne - Spese", layout="centered")

# --- CARICAMENTO DATI ---
if os.path.exists(NOME_FILE):
    df = pd.read_excel(NOME_FILE)
    # Assicuriamoci che la colonna Data sia in formato data vero
    df['Data'] = pd.to_datetime(df['Data'])
else:
    df = pd.DataFrame(columns=['Data', 'Categoria', 'Descrizione', 'Importo'])

st.title("📊 Gestione Spese Famiglia")

# --- AGGIUNTA NUOVA SPESA ---
with st.expander("➕ Aggiungi Nuova Spesa"):
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data")
    with col2:
        cat = st.selectbox("Categoria", ["Supermercato", "Bimbi", "Bollette", "Svago", "Altro"])
    
    desc = st.text_input("Descrizione")
    prezzo = st.number_input("Importo (€)", min_value=0.0, step=0.01)
    
    if st.button("Salva Spesa"):
        nuova_riga = pd.DataFrame({'Data': [pd.to_datetime(data)], 'Categoria': [cat], 'Descrizione': [desc], 'Importo': [prezzo]})
        df = pd.concat([df, nuova_riga], ignore_index=True)
        df.to_excel(NOME_FILE, index=False)
        st.success("Spesa salvata!")
        st.rerun()

# --- FILTRO PER MESE ---
st.divider()
if not df.empty:
    # Creiamo una colonna Mese-Anno per il menu a tendina
    df['Mese_Anno'] = df['Data'].dt.strftime('%B %Y')
    elenco_mesi = df['Mese_Anno'].unique()
    
    mese_scelto = st.selectbox("Seleziona il mese da visualizzare:", elenco_mesi)
    
    # Filtriamo il database in base alla scelta
    df_filtrato = df[df['Mese_Anno'] == mese_scelto]
    
    st.subheader(f"Resoconto di {mese_scelto}")
    st.metric("Totale Mese", f"€ {df_filtrato['Importo'].sum():.2f}")

    tab1, tab2, tab3 = st.tabs(["Elenco", "Grafico", "Gestione"])

    with tab1:
        st.dataframe(df_filtrato[['Data', 'Categoria', 'Descrizione', 'Importo']], use_container_width=True)

    with tab2:
        st.bar_chart(df_filtrato.groupby('Categoria')['Importo'].sum())

    with tab3:
        st.write("Cancellazione voci:")
        # Permette di scegliere quale spesa eliminare (mostra descrizione e importo)
        indice_da_eliminare = st.selectbox("Quale spesa vuoi eliminare?", 
                                          options=df_filtrato.index,
                                          format_func=lambda x: f"{df.loc[x, 'Descrizione']} (€{df.loc[x, 'Importo']})")
        
        if st.button("Elimina Voce Selezionata"):
            df = df.drop(indice_da_eliminare)
            df.to_excel(NOME_FILE, index=False)
            st.warning("Voce eliminata!")
            st.rerun()

        st.divider()
        if st.button("🗑️ CANCELLA INTERA LISTA"):
            if st.checkbox("Confermo di voler cancellare TUTTI i dati"):
                os.remove(NOME_FILE)
                st.error("Dati resettati!")
                st.rerun()
else:
    st.info("Nessuna spesa registrata.")
