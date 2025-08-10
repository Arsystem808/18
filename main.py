import os, sys
CURR=os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURR); sys.path.append(os.path.join(CURR,'src'))
import streamlit as st
from src.common.config import get_config
from src.signals.signal_engine import build_signal

st.set_page_config(page_title='US Stocks — AI Signals (main.py)', layout='wide')
cfg=get_config()

st.title('US Stocks — AI Signals')
st.caption('3 тикера • 3 года истории • кэш данных. Формат: BUY / SHORT / CLOSE / WAIT + уровни.')

tickers=st.text_input('Tickers (comma-separated)', value=','.join(cfg.tickers)).upper()
tickers_list=[t.strip() for t in tickers.split(',') if t.strip()]

colA,colB=st.columns([1,3])
with colA:
    selected=st.selectbox('Выберите тикер', tickers_list, index=0 if tickers_list else None)
    if st.button('Сгенерировать сигнал'):
        if selected:
            sig=build_signal(selected,'1d')
            st.session_state['latest_signal']=sig

sig=st.session_state.get('latest_signal')
with colB:
    if sig:
        st.subheader(f"Сигнал для {sig['symbol']}")
        c1,c2,c3,c4=st.columns(4)
        c1.metric('Entry', sig['entry'])
        c2.metric('TP1', sig['tp'][0])
        c3.metric('TP2', sig['tp'][1])
        c4.metric('SL', sig['sl'])
        st.write(f"**Действие:** {sig['action']}  |  **Уверенность:** {sig['confidence']:.2f}")
        st.write(sig['rationale_text'])
    else:
        st.info('Выберите тикер и нажмите «Сгенерировать сигнал».')
