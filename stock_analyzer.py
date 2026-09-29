import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests

# Configurazione Pagina
st.set_page_config(page_title="App N. 2 - Stock Analyzer & Fair Value", layout="wide")

st.title("🔎 App N. 2: Stock Analyzer & Fair Value Engine")
st.markdown("Analisi fondamentale, stima del Fair Value e salute finanziaria delle aziende (Alternative a InvestingPro).")

# Sidebar - Selezione Titolo
st.sidebar.header("🎯 Selezione Azienda")
ticker_symbol = st.sidebar.text_input("Inserisci Ticker (es. RACE, NKE, DUOL, ZTS, AAPL, MSFT):", value="RACE").upper().strip()

@st.cache_data(ttl=3600)
def load_stock_data(symbol):
    try:
        # Creazione di una sessione con User-Agent per evitare blocchi da Yahoo Finance su Cloud
        session = requests.Session()
        session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        
        t = yf.Ticker(symbol, session=session)
        info = t.info if t.info else {}
        financials = t.financials if t.financials is not None else pd.DataFrame()
        cashflow = t.cashflow if t.cashflow is not None else pd.DataFrame()
        balance = t.balance_sheet if t.balance_sheet is not None else pd.DataFrame()
        return info, financials, cashflow, balance
    except Exception as e:
        return {}, pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

if ticker_symbol:
    with st.spinner(f"Caricamento dati per {ticker_symbol}..."):
        info, financials, cashflow, balance = load_stock_data(ticker_symbol)

    if not info or ('shortName' not in info and 'longName' not in info and 'currentPrice' not in info and 'regularMarketPrice' not in info):
        st.error(f"Impossibile recuperare i dati per il ticker '{ticker_symbol}'. Prova a verificare il ticker su Yahoo Finance (es. 'RACE' per Ferrari a New York o 'RACE.MI' per Milano).")
    else:
        # Intestazione Azienda
        company_name = info.get('longName', info.get('shortName', ticker_symbol))
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        currency = info.get('currency', 'USD')
        
        col_header1, col_header2 = st.columns([3, 1])
        with col_header1:
            st.header(f"{company_name} ({ticker_symbol})")
            st.caption(f"Settore: **{sector}** | Industria: **{industry}** | Valuta: **{currency}**")
        with col_header2:
            st.metric(label="Prezzo Attuale", value=f"{current_price:,.2f} {currency}" if current_price else "N/A")

        st.divider()

        # Tabs principali
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Dashboard & Health Score", 
            "💎 Stima Fair Value", 
            "📈 Trend di Bilancio", 
            "⚔️ Confronto Competitor"
        ])

        # ==========================================
        # TAB 1: HEALTH SCORE & METRICHE CHIAVE
        # ==========================================
        with tab1:
            st.subheader("🏥 Punteggio di Salute Finanziaria (Health Score)")
            
            score = 0
            checks = []

            # 1. Redditività (ROE)
            roe = info.get('returnOnEquity', 0) or 0
            if roe > 0.15:
                score += 25
                checks.append("✅ **ROE Elevato (> 15%)**: Ottimo utilizzo del capitale proprio.")
            elif roe > 0.08:
                score += 15
                checks.append("⚠️ **ROE Medio (8% - 15%)**: Redditività nella media.")
            else:
                checks.append("❌ **ROE Basso (< 8%)**: Bassa redditività del capitale.")

            # 2. Margine Netto
            profit_margin = info.get('profitMargins', 0) or 0
            if profit_margin > 0.15:
                score += 25
                checks.append("✅ **Margine Netto Elevato (> 15%)**: Forte potere di prezzo e redditività.")
            elif profit_margin > 0.05:
                score += 15
                checks.append("⚠️️ **Margine Netto Basso (5% - 15%)**: Margini accettabili.")
            else:
                checks.append("❌ **Margine Netto Ridotto (< 5%)**: A rischio in caso di aumento dei costi.")

            # 3. Indebitamento (Debt to Equity)
            debt_to_equity = (info.get('debtToEquity', 100) or 100) / 100
            if debt_to_equity < 0.8:
                score += 25
                checks.append("✅ **Debito Sostenibile (D/E < 0.8)**: Solida struttura patrimoniale.")
            elif debt_to_equity < 1.5:
                score += 15
                checks.append("⚠️ **Debito Moderato (D/E 0.8 - 1.5)**: Livello di debito sotto controllo.")
            else:
                checks.append("❌ **Debito Elevato (D/E > 1.5)**: Elevata leva finanziaria.")

            # 4. Solvibilità di Breve Periodo (Current Ratio)
            current_ratio = info.get('currentRatio', 0) or 0
            if current_ratio > 1.5:
                score += 25
                checks.append("✅ **Ottima Liquidità (Current Ratio > 1.5)**: Copertura eccellente dei debiti a breve.")
            elif current_ratio >= 1.0:
                score += 15
                checks.append("⚠️ **Liquidità Sufficiente (Current Ratio 1.0 - 1.5)**: Copertura sufficiente.")
            else:
                checks.append("❌ **Liquidità Rischiosa (Current Ratio < 1.0)**: Possibili tensioni di cassa.")

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
            
            pe = info.get('trailingPE', None)
            fwd_pe = info.get('forwardPE', None)
            ps = info.get('priceToSalesTrailing12Months', None)
            pb = info.get('priceToBook', None)
            div_yield = info.get('dividendYield', 0) or 0

            m1.metric("P/E (Trailing)", f"{pe:.2f}" if pe else "N/A")
            m2.metric("P/E (Forward)", f"{fwd_pe:.2f}" if fwd_pe else "N/A")
            m3.metric("P/S (Price/Sales)", f"{ps:.2f}" if ps else "N/A")
            m4.metric("P/B (Price/Book)", f"{pb:.2f}" if pb else "N/A")
            m5.metric("Dividend Yield", f"{div_yield * 100:.2f}%" if div_yield else "N/A")

        # ==========================================
        # TAB 2: VALUTAZIONE FAIR VALUE
        # ==========================================
        with tab2:
            st.subheader("💎 Modelli di Stima del Fair Value")
            st.write("Confronto tra prezzo di mercato attuale e il valore intrinseco stimato con diversi modelli matematici.")

            eps = info.get('trailingEps', 0) or 0
            bvps = info.get('bookValue', 0) or 0
            fcf = info.get('freeCashflow', 0) or 0
            shares = info.get('sharesOutstanding', 1) or 1

            graham_value = np.sqrt(22.5 * max(0, eps) * max(0, bvps)) if (eps > 0 and bvps > 0) else None

            col_dcf1, col_dcf2 = st.columns(2)
            with col_dcf1:
                growth_rate = st.slider("Tasso di Crescita FCF Annuo Atteso (%)", 0.0, 30.0, 8.0, 0.5) / 100
                discount_rate = st.slider("Tasso di Sconto / WACC (%)", 5.0, 15.0, 9.0, 0.5) / 100

            fcf_per_share = (fcf / shares) if (fcf and shares) else (eps * 0.8)
            future_fcf = [fcf_per_share * ((1 + growth_rate) ** i) for i in range(1, 6)]
            discounted_fcf = [f / ((1 + discount_rate) ** i) for i, f in enumerate(future_fcf, start=1)]
            
            terminal_value = (future_fcf[-1] * 1.02) / (discount_rate - 0.02) if discount_rate > 0.02 else 0
            discounted_terminal_value = terminal_value / ((1 + discount_rate) ** 5)
            
            dcf_fair_value = sum(discounted_fcf) + discounted_terminal_value if fcf_per_share > 0 else None

            st.divider()
            v1, v2, v3 = st.columns(3)
            
            v1.metric("Prezzo Attuale", f"{current_price:,.2f} {currency}" if current_price else "N/A")
            v2.metric("Fair Value (DCF)", f"{dcf_fair_value:,.2f} {currency}" if dcf_fair_value else "N/A",
                      delta=f"{((dcf_fair_value - current_price) / current_price)*100:.1f}%" if (dcf_fair_value and current_price) else None)
            v3.metric("Valore di Graham", f"{graham_value:,.2f} {currency}" if graham_value else "N/A",
                      delta=f"{((graham_value - current_price) / current_price)*100:.1f}%" if (graham_value and current_price) else None)

            target_mean = info.get('targetMeanPrice', None)
            if target_mean:
                st.info(f"🎯 **Target Price Medio degli Analisti Wall Street:** {target_mean:,.2f} {currency} (Potenziale: {((target_mean - current_price)/current_price)*100:+.1f}%)")

        # ==========================================
        # TAB 3: TREND DI BILANCIO
        # ==========================================
        with tab3:
            st.subheader("📈 Andamento Storico di Bilancio")
            
            if financials is not None and not financials.empty:
                rev_key = [k for k in financials.index if 'Total Revenue' in k or 'Revenue' in k]
                net_key = [k for k in financials.index if 'Net Income' in k]

                if rev_key and net_key:
                    years = [str(col.year) for col in financials.columns]
                    revenues = financials.loc[rev_key[0]].values / 1e6
                    net_incomes = financials.loc[net_key[0]].values / 1e6

                    df_chart = pd.DataFrame({
                        'Anno': years,
                        'Ricavi (€/M)': revenues,
                        'Utile Netto (€/M)': net_incomes
                    }).iloc[::-1]

                    fig = px.bar(df_chart, x='Anno', y=['Ricavi (€/M)', 'Utile Netto (€/M)'],
                                 barmode='group', title=f"Ricavi e Utili di {ticker_symbol} (Milioni {currency})",
                                 color_discrete_sequence=['#1f77b4', '#2ca02c'])
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Dati dettagliati sui ricavi non disponibili.")
            else:
                st.info("Rendiconto finanziario non disponibile per questo titolo.")

        # ==========================================
        # TAB 4: CONFRONTO COMPETITOR
        # ==========================================
        with tab4:
            st.subheader("⚔️ Confronto Diretto con Competitor")
            peers_input = st.text_input("Inserisci altri Ticker da confrontare (separati da comma):", value="NKE, RACE, AAPL")
            
            if peers_input:
                peer_list = [p.strip().upper() for p in peers_input.split(",") if p.strip()]
                if ticker_symbol not in peer_list:
                    peer_list.insert(0, ticker_symbol)

                peer_data = []
                for p in peer_list:
                    try:
                        session_p = requests.Session()
                        session_p.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                        p_ticker = yf.Ticker(p, session=session_p)
                        p_info = p_ticker.info if p_ticker.info else {}
                        
                        if p_info and ('shortName' in p_info or 'longName' in p_info or 'currentPrice' in p_info):
                            peer_data.append({
                                'Ticker': p,
                                'Nome': p_info.get('longName', p_info.get('shortName', p)),
                                'Prezzo': p_info.get('currentPrice', p_info.get('regularMarketPrice', 0)),
                                'P/E (Trailing)': p_info.get('trailingPE', None),
                                'P/S': p_info.get('priceToSalesTrailing12Months', None),
                                'ROE (%)': (p_info.get('returnOnEquity', 0) or 0) * 100,
                                'Margine Netto (%)': (p_info.get('profitMargins', 0) or 0) * 100,
                                'Market Cap (Mld)': (p_info.get('marketCap', 0) or 0) / 1e9
                            })
                    except Exception:
                        continue
                
                if peer_data:
                    df_peers = pd.DataFrame(peer_data)
                    st.dataframe(df_peers.style.highlight_max(subset=['ROE (%)', 'Margine Netto (%)'], color='#d4edda')
                                                .highlight_min(subset=['P/E (Trailing)', 'P/S'], color='#d4edda'),
                                 use_container_width=True)
