import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px # Importiamo Plotly qui

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
        data_formattata = data.strftime('%d/%m/%Y')
        
        nuova_riga = pd.DataFrame({
            'Data': [data_formattata], 
            'Categoria': [cat], 
            'Descrizione': [desc], 
            'Importo': [float(prezzo)]
        })
        
        df_aggiornato = pd.concat([df, nuova_riga], ignore_index=True)
        
        # Forza il formato data prima di inviare a Google
        df_aggiornato['Data'] = pd.to_datetime(df_aggiornato['Data'], dayfirst=True).dt.strftime('%d/%m/%Y')
        
        conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_aggiornato)
        st.success(f"Spesa salvata correttamente con data {data_formattata}!")
        st.rerun()

# --- FILTRO E VISUALIZZAZIONE ---
st.divider()
if not df.empty:
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Data'])
    
    df['Mese_Eng'] = df['Data'].dt.strftime('%B')
    df['Anno'] = df['Data'].dt.strftime('%Y')
    df['Mese_Ita'] = df['Mese_Eng'].map(MESI_TRADUZIONE) + " " + df['Anno']
    
    elenco_mesi = df.sort_values(by='Data', ascending=False)['Mese_Ita'].unique()
    mese_scelto = st.selectbox("Seleziona il mese:", elenco_mesi)
    
    df_filtrato = df[df['Mese_Ita'] == mese_scelto]
    
    st.metric(f"Totale {mese_scelto}", f"€ {df_filtrato['Importo'].sum():.2f}")

    tab1, tab2, tab3 = st.tabs(["Elenco", "Grafico", "Gestione"])

    with tab1:
        df_tabella = df_filtrato.copy()
        df_tabella['Data'] = df_tabella['Data'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_tabella[['Data', 'Categoria', 'Descrizione', 'Importo']], use_container_width=True)

    with tab2:
        # --- QUI C'È LA MODIFICA PER IL GRAFICO A TORTA ---
        spese_per_cat = df_filtrato.groupby('Categoria')['Importo'].sum().reset_index()
        
        if not spese_per_cat.empty: # Aggiungiamo un controllo per evitare errori se non ci sono spese
            fig = px.pie(spese_per_cat, values='Importo', names='Categoria', 
                         title=f'Distribuzione Spese {mese_scelto}',
                         hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nessuna spesa per il mese selezionato per generare il grafico.")
        # --- FINE MODIFICA GRAFICO A TORTA ---

    with tab3:
        st.write("Cancellazione:")
        indice = st.selectbox("Quale voce eliminare?", options=df_filtrato.index,
                             format_func=lambda x: f"{df.loc[x, 'Descrizione']} (€{df.loc[x, 'Importo']})")
        
        if st.button("Elimina voce selezionata"):
            df_residuo = df.drop(indice)
            
            if not df_residuo.empty:
                df_residuo['Data'] = pd.to_datetime(df_residuo['Data'], dayfirst=True).dt.strftime('%d/%m/%Y')
            
            conn.update(spreadsheet=st.secrets["connections"]["gsheets"]["spreadsheet"], data=df_residuo)
            st.warning("Voce eliminata!")
            st.rerun()
else:
    st.info("Inizia aggiungendo la prima spesa!")
