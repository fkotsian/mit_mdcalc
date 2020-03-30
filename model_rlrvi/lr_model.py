import numpy as np
import pickle

def get_model_output(X_test):
# Rows of X_test are patients
# Columns of X_test:
# 0:  Age in years
# 1:  Pulse rate in bpm
# 2:  Systolic blood pressure in mmHg
# 3:  Initial creatinine in mg/dL
# 4:  Killip class (1 = No CHF, 2 = Rales, 3 = Pulmonary edema, 4 = Cardiogenic shock)
# 5:  Cardiac arrest on presentation (1 = Yes, 2 = No)
# 6:  Initial positive cardiac enzymes, including CK, CK-MB, and troponin (1 = Positive, 2 = Negative)
# 7:  ST segment deviation (1 = Yes, 2 = No)
# 8:  Admission weight in kg
# 9:  History of renal insufficiency (1 = Yes, 2 = No)
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
    norm_fact = pickle.load(f)
    f.close()

    # Normalize X_test
    for i in range(X_test.shape[1]):
	    X_test[:,i] = (X_test[:,i]-norm_fact[i,1])/norm_fact[i,0]

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
	    idx.extend([np.argwhere(np.isnan(X_test[i,:]))])

    s_inv = np.linalg.inv(s)

    print("S INV")
    print(s_inv)

    print("X TEST")
    print(X_test)
    print(X_test.shape[0], X_test.shape[1])
    print("IDX")
    print(idx)
    print(idx[0], idx[0])

    X = np.zeros((X_test.shape[0],X_test.shape[1]))

    for i in range(X_test.shape[0]):
	    A               = s_inv[idx[i],idx[i]]
	    C               = np.setdiff1d(range(X_test.shape[1]),idx[i])
	    B				= -1*np.matmul(s_inv[idx[i],C],np.transpose(X_test[i,C])-mu[C])
	    X[i,C]          = X_test[i,C]
	    print("SOLVING")
	    print(i)
	    print(A)
	    print(B)
	    X[i,idx[i]]     = np.linalg.solve(A,B)
	    X[i,idx[i]]     = X[i,idx[i]]+np.transpose(mu[idx[i]])

    # Load trained logistic regression model
    f = open('./model_rlrvi/lr_model.pkl','rb')
    lr = pickle.load(f)
    f.close()

    yh = lr.predict_proba(X_test)[:,1]

    # Load calibration data
    # Combined outcome at 3 years
    f = open('./model_rlrvi/cal.pkl')
    e,r,ci = pickle.load(f)
    f.close()

    # Find bin for model output and convert to risk score with confidence intervals
    d = np.digitize(yh,e,False)

    if d < 0.5:
	    d = 0
    elif d >= len(e):
	    d = len(e)-1

    yr = r[d]
    lci = ci[d,0]
    uci = ci[d,1]

    # Return risk score and confidence intervals
    return (yr,lci,uci)
