import pickle
import numpy as np 
import pandas as pd
model_pkl = open('MLP.pkl', 'rb')
saved_model = pickle.load(model_pkl)
#Add recipe information
recipe =""
y_pred= saved_model.predict(np.array(recipe))
y_pred= y_pred>0.5
result=y_pred[0]
if result[0]==False:
    print("it's easy")
else: print("it's hard")
