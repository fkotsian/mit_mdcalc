import numpy as np
import pickle

def unreliability(X):
    # Load trained alternative risk model
    f = open('./model_rlrvi/pyyh.pkl','rb')
    pyyh = pickle.load(f)
    f.close()

    # Load trained logistic regression model
    f = open('./model_rlrvi/lr_model.pkl','rb')
    lr = pickle.load(f)
    f.close()

    yh = lr.predict_proba(X)[:,1]

    yp = []
    for jj in range(len(yh)):
	    yidx = np.argwhere(yh[jj] >= edges)
	    yidx = yidx[-1]
	    yp[jj] = pyyh[yidx]


    return np.abs(yh-yp)
