import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Casa Mesagne - Spese", layout="centered")

# Dizionario per tradurre i mesi
MESI_TRADUZIONE = {
    "January": "Gennaio", "February": "Febbraio", "March": "Marzo",
    "April": "Aprile", "May": "Maggio", "June": "Giugno",
    "July": "Luglio", "August": "Agosto", "September": "Settembre",
    "October": "Ottobre", "November": "Novembre", "December": "Dicembre"
}

# Connessione a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Lettura dati
df = conn.read(ttl=0)
df = df.dropna(how='all')

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
        # Questa riga qui sotto è quella fondamentale:
        # data.strftime('%d/%m/%Y') trasforma qualsiasi data selezionata
        # nel formato europeo standard 07/02/2026
        data_formattata = data.strftime('%d/%m/%Y')
        
        nuova_riga = pd.DataFrame({
            'Data': [data_formattata], 
            'Categoria': [cat], 
            'Descrizione': [desc], 
            'Importo': [float(prezzo)]
        })
        
        df_aggiornato = pd.concat([df, nuova_riga], ignore_index=True)
        conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_aggiornato)
        st.success(f"Spesa salvata correttamente con data {data_formattata}!")
        st.rerun()

# --- FILTRO PER MESE IN ITALIANO ---
st.divider()
if not df.empty:
    # Specifichiamo che il GIORNO viene prima del mese
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Data'])
    
    df['Mese_Eng'] = df['Data'].dt.strftime('%B')
    df['Anno'] = df['Data'].dt.strftime('%Y')
    df['Mese_Ita'] = df['Mese_Eng'].map(MESI_TRADUZIONE) + " " + df['Anno']
    
    # Ordiniamo le opzioni per data decrescente (il mese più recente in alto)
    elenco_mesi = df.sort_values(by='Data', ascending=False)['Mese_Ita'].unique()
    
    mese_scelto = st.selectbox("Seleziona il mese:", elenco_mesi)
    
    df_filtrato = df[df['Mese_Ita'] == mese_scelto]
    
    st.metric(f"Totale {mese_scelto}", f"€ {df_filtrato['Importo'].sum():.2f}")

    tab1, tab2, tab3 = st.tabs(["Elenco", "Grafico", "Gestione"])

    with tab1:
        st.dataframe(df_filtrato[['Data', 'Categoria', 'Descrizione', 'Importo']], use_container_width=True)

    with tab2:
        # Grafico a barre per categoria
        spese_per_cat = df_filtrato.groupby('Categoria')['Importo'].sum()
        st.bar_chart(spese_per_cat)

    with tab3:
        st.write("Cancellazione:")
        indice = st.selectbox("Quale voce eliminare?", options=df_filtrato.index,
                              format_func=lambda x: f"{df.loc[x, 'Descrizione']} (€{df.loc[x, 'Importo']})")
        
        if st.button("Elimina voce selezionata"):
            df_residuo = df.drop(indice)
            conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_residuo)
            st.warning("Voce eliminata!")
            st.rerun()
else:
    st.info("Inizia aggiungendo la prima spesa!")
