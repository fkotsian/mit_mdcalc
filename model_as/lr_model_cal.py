import numpy as np
import pickle

# Tested with NumPy version 1.16.2

def load_from_pkl(pkl):
    f = open(pkl, 'rb')
    e, r, ci = pickle.load(f)
    e = e[0]
    r = list(r.flat)
    f.close()
    return (e,r,ci)


def get_model_output(X_test):
    # Rows of X_test are patients
    # Columns of X_test:
    # 0: Peak flow velocity in m/s
    # 1: Mean pressure gradient across aortic valve in mmHg
    # 2: Aortic valve area in cm^2
    # 3: Congestive heart failure (CHF) at baseline (0 = No, 1 = Yes)
    # 4: Myocardial infarction (MI) at baseline (0 = No, 1 = Yes)
    # 5: Peripheral vascular disease (PVD) at baseline (0 = No, 1 = Yes)
    # 6: Left ventricular segmental wall motion abnormality (0 = No, 1 = Yes)
    # 7: Hyperlipidemia at baseline (0 = No, 1 = Yes)
    # 8: Chronic kidney disease (CKD) at baseline (0 = No, 1 = Yes)
    # 9: Posterior wall thickness (mm)
    # 10: Aortic sinus diameter (mm)

    # Logistic regression model inputs (after preprocessing of X_test; code below does the preprocessing):
    # 0: Transvalvular flow rate (binarized)
    # 1: Mean pressure gradient across aortic valve (binarized)
    # 2: Aortic valve area (binarized)
    # 3: Congestive heart failure (CHF) at baseline (0 = No, 1 = Yes)
    # 4: MI or PVD or abnormal wall motion
    # 5: Hyperlipidemia at baseline (0 = No, 1 = Yes)
    # 6: Chronic kidney disease (CKD) at baseline (0 = No, 1 = Yes)
    # 7: Posterior wall thickness (normalized)
    # 8: EL2 (normalized)

    # Compute energy loss coefficient from aortic valve area, transvalvular flow rate, and aortic sinus diameter
    ELCO_n = np.multiply(X_test[:,2],np.pi*np.square(X_test[:,10]/20))
    ELCO_d = np.pi*np.square(X_test[:,10]/20)-X_test[:,2]
    ELCO = np.divide(ELCO_n,ELCO_d)
    EL2 = np.square(np.divide(X_test[:,0],50*ELCO))

	# Compute transvalvular flow rate from peak velocity, mean gradient, and aortic valve area
    Q1 = X_test[:,1]+np.sqrt(X_test[:,1]*X_test[:,1]+32*X_test[:,1]*X_test[:,0]*X_test[:,0])
    Q2 = Q1/(16*X_test[:,0])
    Q3 = Q2*100
    Q = Q3*X_test[:,2]

    # Binarize aortic valve area (1 if <= 1 cm^2)
    AVA_b = X_test[:,2] <= 1
    # Binarize mean gradient (1 if >= 40 mmHg)
    MG_b = X_test[:,1] >= 40
    # Binarize flow rate (1 if <= 210 mL/s)
    Q_b = X_test[:,0] <= 210

    # Load trained logistic regression model
    f = open('./model_as/lr_model.pkl','rb')
    lr = pickle.load(f)
    f.close()

    # Load normalization factors for X_test
    # The logistic regression model requires that the input features are between 0 and 1, inclusive
    f = open('./model_as/norm_fact.pkl','rb')
    nf = pickle.load(f)
    f.close()

    # Build input to logistic regression model
    X = np.zeros((X_test.shape[0],9))
    X[:,0] = np.copy(Q_b)
    X[:,1] = np.copy(MG_b)
    X[:,2] = np.copy(AVA_b)
    X[:,3] = np.copy(X_test[:,3])
    X[:,4] = np.bitwise_or(np.bitwise_or(X_test[:,4].astype(np.int64),X_test[:,5].astype(np.int64)),X_test[:,6].astype(np.int64))
    X[:,5] = np.copy(X_test[:,7])
    X[:,6] = np.copy(X_test[:,8])
    X[:,7] = (np.copy(X_test[:,9])-nf[0,0])/nf[0,1]
    X[:,8] = (np.copy(EL2)-nf[1,0])/nf[1,1]

    yh = lr.predict_proba(X)[:,1]

	# Calibrate model for 3-year mortality
    b_3 = 0.4262
    me_3 = 0.0668
    yh_cal_3 = yh*b_3
    yh_lci_3 = yh*(b_3-me_3)
    yh_uci_3 = yh*(b_3+me_3)

	# Calibrate model for 5-year mortality
    b_5 = 0.5288
    me_5 = 0.0702
    yh_cal_5 = yh*b_5
    yh_lci_5 = yh*(b_5-me_5)
    yh_uci_5 = yh*(b_5+me_5)

    # Return risk scores and confidence intervals by metric
    ret = (yh_cal_3,yh_cal_5,yh_cal_3,yh_cal_5,yh_cal_3,yh_cal_5,\
	       yh_lci_3,yh_lci_5,yh_lci_3,yh_lci_5,yh_lci_3,yh_lci_5, \
	       yh_uci_3,yh_uci_5,yh_uci_3,yh_uci_5,yh_uci_3,yh_uci_5)

    from pprint import pprint
    pprint("RET")
    pprint(len(ret))
    pprint(ret)

    return ret
