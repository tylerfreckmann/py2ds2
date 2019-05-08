from sklearn.externals import joblib
import pandas as pd

ml_pipe = joblib.load('/pymodels/hmeq2/ml_pipe.pickle')

def score(LOAN, MORTDUE, VALUE, REASON, JOB, YOJ, DEROG, DELINQ, CLAGE, NINQ, CLNO, DEBTINC):
    'Output: EM_EVENTPROBABILITY'
    data = pd.DataFrame([{'LOAN': LOAN, 'MORTDUE': MORTDUE, 'VALUE': VALUE, 'REASON': REASON, 'JOB': JOB, 'YOJ': YOJ, 'DEROG': DEROG, 'DELINQ': DELINQ, 'CLAGE': CLAGE, 'NINQ': NINQ, 'CLNO': CLNO, 'DEBTINC': DEBTINC}])
    _, EM_EVENTPROBABILITY = ml_pipe.predict_proba(data)[0]
    return float(EM_EVENTPROBABILITY)
