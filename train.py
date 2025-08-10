import os, joblib, numpy as np, pandas as pd
from lightgbm import LGBMClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score
from src.common.config import get_config
from src.data.data_hub import load_history_yf
from src.features.feature_engine import build_features, make_labels

MODEL_DIR='artifacts'; os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH=os.path.join(MODEL_DIR,'lgbm_direction.pkl')
FEATURE_COLS=['open','high','low','close','volume','ret1','atr14','mom10','pivot','r1','s1','r2','s2','dist_pivot','dist_r1','dist_s1']

def train():
    cfg=get_config(); frames=[]
    for sym in cfg.tickers:
        df=load_history_yf(sym, period_years=cfg.data_lookback_years, interval='1d')
        feats=build_features(df); feats['symbol']=sym; feats['label']=make_labels(feats,1); frames.append(feats)
    data=pd.concat(frames).dropna(); X=data[FEATURE_COLS]; y=data['label']
    tscv=TimeSeriesSplit(n_splits=3); best_auc=-1; best=None
    for seed in [7,13]:
        m=LGBMClassifier(n_estimators=400,learning_rate=0.04,subsample=0.9,colsample_bytree=0.8,random_state=seed)
        oof=np.zeros(len(X))
        for tr,va in tscv.split(X):
            m.fit(X.iloc[tr], y.iloc[tr]); oof[va]=m.predict_proba(X.iloc[va])[:,1]
        auc=roc_auc_score(y,oof); print(f'Seed {seed}: OOF AUC={auc:.4f}')
        if auc>best_auc: best_auc=auc; best=m
    joblib.dump({'model':best,'features':FEATURE_COLS}, MODEL_PATH)
    print(f'Saved model to {MODEL_PATH} (AUC={best_auc:.4f})')

if __name__=='__main__':
    train()
