import numpy as np
import pickle

def get_model_output(X_test):
# Rows of X_test are patients
# Columns of X_test:
# 0: Age in years
# 1: Pulse rate in bpm
# 2: Systolic blood pressure in mmHg
# 3: Initial creatinine in mg/dL
# 4: Killip class (1 = No CHF, 2 = Rales, 3 = Pulmonary edema, 4 = Cardiogenic shock)
# 5: Cardiac arrest on presentation (1 = Yes, 2 = No)
# 6: Initial positive cardiac enzymes, including CK, CK-MB, and troponin (1 = Positive, 2 = Negative)
# 7: ST segment deviation (1 = Yes, 2 = No)
# 8: Admission weight in kg
# 9: History of renal insufficiency (1 = Yes, 2 = No)
# 10: History of congestive heart failure (CHF) (1 = Yes, 2 = No)
# 11: History of peripheral arterial disease (1 = Yes, 2 = No)
# 12: Chronic warfarin use (1 = Yes, 2 = No)
# 13: Oral beta blocker use, pre-hospital acute or within first 24 hours at hospital (1 = Yes, 2 = No)
# 14: Statin use, pre-hospital acute or within first 24 hours at hospital (1 = Yes, 2 = No)
# 15: Diuretic use, pre-hospital acute or within first 24 hours at hospital (1 = Yes, 2 = No)
# 16: Insulin use, pre-hospital acute or within first 24 hours at hospital (1 = Yes, 2 = No)
# 17: IV inotropic agent use, pre-hospital acute or within first 24 hours at hospital (1 = Yes, 2 = No)
# 18: IV beta blocker use, pre-hospital acute or within first 24 hours at hospital (1 = Yes, 2 = No)

    # Load normalization factors for X_test
    # The logistic regression model requires that the input features are between 0 and 1, inclusive
    f = open('./model_rlrvi/norm_fact.pkl','rb')
    nf = pickle.load(f)
    f.close()

	# Normalize X_test
    for i in range(X_test.shape[1]):
        X_test[:,i] = (X_test[:,i]-nf[i,1])/nf[i,0]

	# Load multivariate normal distribution parameters
    f = open('./model_rlrvi/mvn_mu.pkl','rb')
    mu = pickle.load(f)
    f.close()
    f = open('./model_rlrvi/mvn_s.pkl','rb')
    s = pickle.load(f)
    f.close()

	# Impute missing data
    idx = []
    for i in range(X_test.shape[0]):
        a = np.argwhere(np.isnan(X_test[i,:]))
        idx.extend(a.reshape((1,a.shape[0])))

    s_inv = np.linalg.inv(s)

    if len(idx) > 0:
        X = np.zeros((X_test.shape[0],X_test.shape[1]))

        for i in range(X_test.shape[0]):
            A               = s_inv[idx[i],:]
            A               = A[:,idx[i]]
            C               = np.setdiff1d(range(X_test.shape[1]),idx[i])
            c2              = s_inv[idx[i],:]
            B				= -1*np.matmul(c2[:,C],np.transpose(X_test[i,C])-mu[C,0])
            X[i,C]          = X_test[i,C]
            X[i,idx[i]]     = np.linalg.solve(A,B)
            X[i,idx[i]]     = X[i,idx[i]]+np.transpose(mu[idx[i]])
    else:
        X = np.copy(X_test)

    # Load trained logistic regression model
    f = open('./model_rlrvi/lr_model.pkl','rb')
    lr = pickle.load(f)
    f.close()

    yh = lr.predict_proba(X)[:,1]

    # Load calibration data
    # Combined outcome at 3 years
    f = open('./model_rlrvi/cal.pkl','rb')
    e,r,ci = pickle.load(f)
    e = e[0,:]
    f.close()

    # Find bin for model output and convert to risk score with confidence intervals
    d = np.digitize(yh,e[0,:],False)

    if d < 0.5:
        d = 0
    elif d >= len(e):
        d = len(e)-1

    yr = r[d]
    lci = ci[d,0]
    uci = ci[d,1]

    # Load trained alternative risk model
    f = open('./model_rlrvi/pyyh.pkl','rb')
    pyyh = pickle.load(f)
    pyyh = pyyh['pyyh']
    f.close()

    edges = np.linspace(0,1,1000)

    yp = np.zeros((len(yh),))
    for jj in range(len(yh)):
        yidx = np.argwhere(yh[jj] >= edges)
        yidx = yidx[-1]
        yp[jj] = pyyh[0,yidx[0]]

    # Unreliability score
    u = np.abs(yh-yp)

    f = open('./model_rlrvi/u_cal.pkl','rb')
    al,cl,_ = pickle.load(f)
    al = al[0]
    cl = cl[0]
    f.close()

    ud = np.digitize(u,cl,False)

    if ud < 0.5:
        ud = 1

    # Return risk scorei, confidence intervals, and unreliability score
    return (yr,lci,uci,al[ud-1])
