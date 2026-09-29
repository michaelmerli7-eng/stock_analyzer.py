import pandas as pd
import streamlit as st


@st.cache_data
def load_data(ticker_symbol):
  # Stooq richiede un suffisso, ad esempio '.US' per le azioni americane (es. AAPL.US)
  url = f'https://stooq.com/q/d/l/?s={ticker_symbol}&i=d'
  try:
    df = pd.read_csv(url)
    if df.empty or 'Close' not in df.columns:
      return None

    # Pulizia e formattazione del dataset
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)

    # Conversione in numerico per sicurezza
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
      if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df
  except Exception as e:
    st.error(f"Errore nel recupero dei dati: {e}")
    return None


# Interfaccia Streamlit
st.title("Analisi Finanziaria (Sorgente: Stooq)")

# Input utente (ricordati di specificare il mercato, es. AAPL.US, TSLA.US, MSFT.US)
ticker = st.text_input(
    "Inserisci il Ticker (es. AAPL.US per Apple):", value="AAPL.US"
)

data = load_data(ticker)

if data is not None and not data.empty:
  st.success(f"Dati caricati con successo per {ticker}!")
  st.line_chart(data["Close"])
  st.dataframe(data.tail())
else:
  st.warning(
      "Impossibile trovare dati per questo simbolo. Verifica che il ticker sia"
      " corretto (es. AAPL.US)."
  )
