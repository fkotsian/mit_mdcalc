def unreliability(X):
    # Load trained alternative risk model
    f = open('./pyyh.pkl','rb')
    pyyh = pickle.load(f)
    f.close()

    for jj in range(len(yh)):
	    yidx = np.argwhere(yh[jj] >= edges)
	    yidx = yidx[-1]
	    yp[jj] = pyyh[yidx]

    # Load trained logistic regression model
    f = open('./lr_model.pkl','rb')
    lr = pickle.load(f)
    f.close()

    yh = lr.predict_proba(X)[:,1]

    return np.abs(yh-yp)