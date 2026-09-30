from datetime import datetime
from curl_cffi import requests
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf

# Configurazione Pagina
st.set_page_config(
    page_title="App N. 2 - Stock Analyzer & Fair Value", layout="wide"
)

st.title("🔎 App N. 2: Stock Analyzer & Fair Value Engine")
st.markdown(
    "Analisi fondamentale, stima del Fair Value, trend finanziari e notizie in"
    " tempo reale."
)

# Sidebar - Selezione Titolo
st.sidebar.header("🎯 Selezione Azienda")
ticker_symbol = (
    st.sidebar.text_input(
        "Inserisci Ticker (es. RACE, NKE, DUOL, ZTS, AAPL, MSFT):", value="RACE"
    )
    .upper()
    .strip()
)


@st.cache_data(ttl=3600)
def load_stock_data(symbol):
  try:
    session = requests.Session(impersonate="chrome")
    t = yf.Ticker(symbol, session=session)
    info = t.info if t.info else {}
    financials = t.financials if t.financials is not None else pd.DataFrame()
    cashflow = t.cashflow if t.cashflow is not None else pd.DataFrame()
    balance = (
        t.balance_sheet if t.balance_sheet is not None else pd.DataFrame()
    )
    history = t.history(period="max") if t else pd.DataFrame()
    news = t.news if hasattr(t, "news") and t.news else []
    return info, financials, cashflow, balance, history, news
  except Exception as e:
    return (
        {},
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        pd.DataFrame(),
        [],
    )


if ticker_symbol:
  with st.spinner(f"Caricamento dati e notizie per {ticker_symbol}..."):
    info, financials, cashflow, balance, history, news = load_stock_data(
        ticker_symbol
    )

  if not info or (
      "shortName" not in info
      and "longName" not in info
      and "currentPrice" not in info
      and "regularMarketPrice" not in info
  ):
    st.error(
        f"Impossibile recuperare i dati per il ticker '{ticker_symbol}'."
        " Verifica che sia corretto su Yahoo Finance."
    )
  else:
    # Intestazione Azienda
    company_name = info.get("longName", info.get("shortName", ticker_symbol))
    sector = info.get("sector", "N/A")
    industry = info.get("industry", "N/A")
    current_price = info.get(
        "currentPrice", info.get("regularMarketPrice", 0)
    )
    currency = info.get("currency", "USD")

    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
      st.header(f"{company_name} ({ticker_symbol})")
      st.caption(
          f"Settore: **{sector}** | Industria: **{industry}** | Valuta:"
          f" **{currency}**"
      )
    with col_header2:
      st.metric(
          label="Prezzo Attuale",
          value=(
              f"{current_price:,.2f} {currency}" if current_price else "N/A"
          ),
      )

    st.divider()

    # Tabs principali (Aggiunta la Tab delle Notizie)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard & Health Score",
        "💎 Stima Fair Value",
        "📈 Trend di Bilancio & Prezzo",
        "⚔️ Confronto Competitor",
        "📰 Ultime Notizie",
    ])

    # ==========================================
    # TAB 1: HEALTH SCORE & METRICHE CHIAVE
    # ==========================================
    with tab1:
      st.subheader("🏥 Punteggio di Salute Finanziaria (Health Score)")

      score = 0
      checks = []

      roe = info.get("returnOnEquity", 0) or 0
      if roe > 0.15:
        score += 25
        checks.append(
            "✅ **ROE Elevato (> 15%)**: Ottimo utilizzo del capitale proprio."
        )
      elif roe > 0.08:
        score += 15
        checks.append("⚠️ **ROE Medio (8% - 15%)**: Redditività nella media.")
      else:
        checks.append("❌ **ROE Basso (< 8%)**: Bassa redditività del capitale.")

      profit_margin = info.get("profitMargins", 0) or 0
      if profit_margin > 0.15:
        score += 25
        checks.append(
            "✅ **Margine Netto Elevato (> 15%)**: Forte potere di prezzo e"
            " redditività."
        )
      elif profit_margin > 0.05:
        score += 15
        checks.append("⚠️ **Margine Netto Basso (5% - 15%)**: Margini accettabili.")
      else:
        checks.append(
            "❌ **Margine Netto Ridotto (< 5%)**: A rischio in caso di aumento"
            " dei costi."
        )

      debt_to_equity = (info.get("debtToEquity", 100) or 100) / 100
      if debt_to_equity < 0.8:
        score += 25
        checks.append(
            "✅ **Debito Sostenibile (D/E < 0.8)**: Solida struttura"
            " patrimoniale."
        )
      elif debt_to_equity < 1.5:
        score += 15
        checks.append(
            "⚠️ **Debito Moderato (D/E 0.8 - 1.5)**: Livello di debito sotto"
            " controllo."
        )
      else:
        checks.append(
            "❌ **Debito Elevato (D/E > 1.5)**: Elevata leva finanziaria."
        )

      current_ratio = info.get("currentRatio", 0) or 0
      if current_ratio > 1.5:
        score += 25
        checks.append(
            "✅ **Ottima Liquidità (Current Ratio > 1.5)**: Copertura"
            " eccellente dei debiti a breve."
        )
      elif current_ratio >= 1.0:
        score += 15
        checks.append(
            "⚠️ **Liquidità Sufficiente (Current Ratio 1.0 - 1.5)**: Copertura"
            " sufficiente."
        )
      else:
        checks.append(
            "❌ **Liquidità Rischiosa (Current Ratio < 1.0)**: Possibili"
            " tensioni di cassa."
        )

      col_s1, col_s2 = st.columns([1, 2])
      with col_s1:
        st.metric(label="Health Score complessivo", value=f"{score} / 100")
        if score >= 75:
          st.success("🟢 **Azienda Molto Solida**")
        elif score >= 50:
          st.warning("🟡 **Azienda Moderatamente Stabile**")
        else:
          st.error("🔴 **Azienda con Profilo Finanziario Debole**")

      with col_s2:
        st.write("**Dettaglio Indicatori:**")
        for check in checks:
          st.markdown(check)

      st.divider()

      st.subheader("📌 Multipli e Indicatori Fondamentali")
      m1, m2, m3, m4, m5 = st.columns(5)

      pe = info.get("trailingPE", None)
      fwd_pe = info.get("forwardPE", None)
      ps = info.get("priceToSalesTrailing12Months", None)
      pb = info.get("priceToBook", None)
      div_yield = info.get("dividendYield", 0) or 0

      m1.metric("P/E (Trailing)", f"{pe:.2f}" if pe else "N/A")
      m2.metric("P/E (Forward)", f"{fwd_pe:.2f}" if fwd_pe else "N/A")
      m3.metric("P/S (Price/Sales)", f"{ps:.2f}" if ps else "N/A")
      m4.metric("P/B (Price/Book)", f"{pb:.2f}" if pb else "N/A")
      m5.metric(
          "Dividend Yield", f"{div_yield * 100:.2f}%" if div_yield else "N/A"
      )

    # ==========================================
    # TAB 2: VALUTAZIONE FAIR VALUE
    # ==========================================
    with tab2:
      st.subheader("💎 Modelli di Stima del Fair Value")
      st.write(
          "Confronto tra prezzo di mercato attuale e il valore intrinseco"
          " stimato con diversi modelli matematici."
      )

      eps = info.get("trailingEps", 0) or 0
      bvps = info.get("bookValue", 0) or 0
      fcf = info.get("freeCashflow", 0) or 0
      shares = info.get("sharesOutstanding", 1) or 1

      graham_value = (
          np.sqrt(22.5 * max(0, eps) * max(0, bvps))
          if (eps > 0 and bvps > 0)
          else None
      )

      col_dcf1, col_dcf2 = st.columns(2)
      with col_dcf1:
        growth_rate = (
            st.slider(
                "Tasso di Crescita FCF Annuo Atteso (%)", 0.0, 30.0, 8.0, 0.5
            )
            / 100
        )
        discount_rate = (
            st.slider("Tasso di Sconto / WACC (%)", 5.0, 15.0, 9.0, 0.5) / 100
        )

      fcf_per_share = (fcf / shares) if (fcf and shares) else (eps * 0.8)
      future_fcf = [
          fcf_per_share * ((1 + growth_rate) ** i) for i in range(1, 6)
      ]
      discounted_fcf = [
          f / ((1 + discount_rate) ** i) for i, f in enumerate(future_fcf, start=1)
      ]

      terminal_value = (
          (future_fcf[-1] * 1.02) / (discount_rate - 0.02)
          if discount_rate > 0.02
          else 0
      )
      discounted_terminal_value = terminal_value / ((1 + discount_rate) ** 5)

      dcf_fair_value = (
          sum(discounted_fcf) + discounted_terminal_value
          if fcf_per_share > 0
          else None
      )

      st.divider()
      v1, v2, v3 = st.columns(3)

      v1.metric(
          "Prezzo Azione Attuale",
          f"{current_price:,.2f} {currency}" if current_price else "N/A",
      )
      v2.metric(
          "Fair Value (DCF)",
          f"{dcf_fair_value:,.2f} {currency}" if dcf_fair_value else "N/A",
          delta=(
              f"{((dcf_fair_value - current_price) / current_price)*100:.1f}%"
              if (dcf_fair_value and current_price)
              else None
          ),
      )
      v3.metric(
          "Valore di Graham",
          f"{graham_value:,.2f} {currency}" if graham_value else "N/A",
          delta=(
              f"{((graham_value - current_price) / current_price)*100:.1f}%"
              if (graham_value and current_price)
              else None
          ),
      )

      target_mean = info.get("targetMeanPrice", None)
      if target_mean:
        st.info(
            f"🎯 **Target Price Medio degli Analisti Wall Street:**"
            f" {target_mean:,.2f} {currency} (Potenziale:"
            f" {((target_mean - current_price)/current_price)*100:+.1f}%)"
        )

    # ==========================================
    # TAB 3: TREND DI BILANCIO & PREZZO (FILTRI + UTILE)
    # ==========================================
    with tab3:
      st.subheader("📈 Trend Storico: Prezzo, Fatturato e Utile Netto")

      if (
          financials is not None
          and not financials.empty
          and not history.empty
      ):
        col_ctrl1, col_ctrl2 = st.columns([3, 1])
        with col_ctrl1:
          timeframe = st.radio(
              "Seleziona Periodo Prezzo:",
              ["3 Mesi", "1 Anno", "5 Anni", "10 Anni", "20 Anni", "Max"],
              horizontal=True,
              index=2,
          )
        with col_ctrl2:
          show_net_income = st.checkbox(
              "Mostra Utile Netto", value=True, key="net_income_chk"
          )

        hist_filtered = history.copy()
        if hist_filtered.index.tz is not None:
          hist_filtered.index = hist_filtered.index.tz_localize(None)

        now = pd.Timestamp.now()
        if timeframe == "3 Mesi":
          hist_filtered = hist_filtered[
              hist_filtered.index >= (now - pd.DateOffset(months=3))
          ]
        elif timeframe == "1 Anno":
          hist_filtered = hist_filtered[
              hist_filtered.index >= (now - pd.DateOffset(years=1))
          ]
        elif timeframe == "5 Anni":
          hist_filtered = hist_filtered[
              hist_filtered.index >= (now - pd.DateOffset(years=5))
          ]
        elif timeframe == "10 Anni":
          hist_filtered = hist_filtered[
              hist_filtered.index >= (now - pd.DateOffset(years=10))
          ]
        elif timeframe == "20 Anni":
          hist_filtered = hist_filtered[
              hist_filtered.index >= (now - pd.DateOffset(years=20))
          ]

        rev_key = [
            k
            for k in financials.index
            if "Total Revenue" in k or "Revenue" in k
        ]
        net_key = [
            k
            for k in financials.index
            if "Net Income" in k and "Common" not in k
        ]
        if not net_key:
          net_key = [k for k in financials.index if "Net Income" in k]

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        if "Close" in hist_filtered.columns:
          fig.add_trace(
              go.Scatter(
                  x=hist_filtered.index,
                  y=hist_filtered["Close"],
                  name="Prezzo Azione",
                  line=dict(color="#1f77b4", width=2),
              ),
              secondary_y=True,
          )

        if rev_key:
          rev_dates = financials.columns
          rev_values = financials.loc[rev_key[0]].values / 1e6
          fig.add_trace(
              go.Bar(
                  x=rev_dates,
                  y=rev_values,
                  name=f"Fatturato ({currency} Mln)",
                  marker_color="#2ca02c",
                  opacity=0.6,
              ),
              secondary_y=False,
          )

        if show_net_income and net_key:
          net_dates = financials.columns
          net_values = financials.loc[net_key[0]].values / 1e6
          fig.add_trace(
              go.Bar(
                  x=net_dates,
                  y=net_values,
                  name=f"Utile Netto ({currency} Mln)",
                  marker_color="#ff7f0e",
                  opacity=0.7,
              ),
              secondary_y=False,
          )

        fig.update_layout(
            title=f"Analisi di {ticker_symbol} - Periodo: {timeframe}",
            xaxis_title="Data",
            hovermode="x unified",
            barmode="group",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        fig.update_yaxes(
            title_text=f"<b>Valori di Bilancio</b> ({currency} Mln)",
            secondary_y=False,
        )
        fig.update_yaxes(
            title_text=f"<b>Prezzo Azione</b> ({currency})", secondary_y=True
        )

        st.plotly_chart(fig, use_container_width=True)
      else:
        st.info("Dati storici o di bilancio insufficienti per il grafico.")

    # ==========================================
    # TAB 4: CONFRONTO COMPETITOR
    # ==========================================
    with tab4:
      st.subheader("⚔️ Confronto Diretto con Competitor")
      peers_input = st.text_input(
          "Inserisci altri Ticker da confrontare (separati da virgola):",
          value="NKE, RACE, AAPL",
      )

      if peers_input:
        peer_list = [p.strip().upper() for p in peers_input.split(",") if p.strip()]
        if ticker_symbol not in peer_list:
          peer_list.insert(0, ticker_symbol)

        peer_data = []
        for p in peer_list:
          try:
            session_p = requests.Session(impersonate="chrome")
            p_ticker = yf.Ticker(p, session=session_p)
            p_info = p_ticker.info if p_ticker.info else {}

            if p_info and (
                "shortName" in p_info
                or "longName" in p_info
                or "currentPrice" in p_info
            ):
              peer_data.append({
                  "Ticker": p,
                  "Nome": p_info.get("longName", p_info.get("shortName", p)),
                  "Prezzo": p_info.get(
                      "currentPrice", p_info.get("regularMarketPrice", 0)
                  ),
                  "P/E (Trailing)": p_info.get("trailingPE", None),
                  "P/S": p_info.get("priceToSalesTrailing12Months", None),
                  "ROE (%)": (p_info.get("returnOnEquity", 0) or 0) * 100,
                  "Margine Netto (%)": (p_info.get("profitMargins", 0) or 0)
                  * 100,
                  "Market Cap (Mld)": (p_info.get("marketCap", 0) or 0) / 1e9,
              })
          except Exception:
            continue

        if peer_data:
          df_peers = pd.DataFrame(peer_data)
          st.dataframe(
              df_peers.style.highlight_max(
                  subset=["ROE (%)", "Margine Netto (%)"], color="#d4edda"
              ).highlight_min(
                  subset=["P/E (Trailing)", "P/S"], color="#d4edda"
              ),
              use_container_width=True,
          )

    # ==========================================
    # TAB 5: ULTIME NOTIZIE
    # ==========================================
   st.subheader("📰 Ultime Notizie")

try:
  news_list = ticker.news
  if not news_list:
    st.info("Nessuna notizia recente trovata per questo titolo.")
  else:
    for item in news_list:
      # Gestione della struttura dati (diretta o annidata in 'content')
      content = (
          item.get("content", {})
          if isinstance(item.get("content"), dict)
          else {}
      )

      # Estrazione del titolo con fallback multipli
      title = (
          item.get("title")
          or content.get("title")
          or item.get("headline")
          or "Titolo non disponibile"
      )

      # Estrazione della fonte/editore con fallback multipli
      publisher = (
          item.get("publisher")
          or content.get("provider", {}).get("displayName")
          or content.get("publisher")
          or "Fonte sconosciuta"
      )

      # Estrazione del link dell'articolo con fallback multipli
      link = (
          item.get("link")
          or item.get("clickThroughUrl", {}).get("url")
          or content.get("clickThroughUrl", {}).get("url")
          or content.get("canonicalUrl", {}).get("url")
          or "#"
      )

      # Rendering dell'interfaccia in Streamlit
      with st.container():
        st.markdown(f"**[{title}]({link})**")
        st.caption(f"Fonte: {publisher}")
        st.divider()

except Exception as e:
  st.error(f"Errore nel recupero delle notizie: {e}")
