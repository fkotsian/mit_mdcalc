import lr_model
import numpy as np

x = np.array([72.3559206020000,86,193,1.40000000000000,np.nan,np.nan,np.nan,2,1,2,2,2,2,1,1,2,2,2,2]).reshape((1,19))

print(lr_model.get_model_output(x))
