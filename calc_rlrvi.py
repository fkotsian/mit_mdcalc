import os
import sys
import random
import logging
import numpy as np
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from flask import Flask, render_template, request, jsonify
from model_as.lr_model_cal import get_model_output as model_as
from model_rlrvi.lr_model import get_model_output as model_rlrvi
from model_rlrvi.unreliability import unreliability

app = Flask(__name__)

FACTOR_LBS_TO_KG = float(2.205)
FACTOR_CM_TO_MM = float(10)

@app.route('/',methods = ['GET'])
def index():
   app.logger.error('Loading main calculator page')
   calc_name = 'rlrvi'
   deploy_path = '/calc-rlrvi'
   return render_template('index.html', calc_name=calc_name, deploy_path=deploy_path)

@app.route('/rlrvi',methods = ['POST'])
def result_rlrvi():
   if request.method == 'POST':
      result = request.form
      keys = [
         'age',
         'pulse',
         'systolic',
         'creatinine',
         'killip',
         'cardiac_arrest',
         'enzymes',
         'st_deviation',
         'weight_kg',
         'renal_insufficiency',
         'rlrvi_chf',
         'rlrvi_pad',
         'warfarin',
         'use_betablocker',
         'use_statin',
         'use_diuretic',
         'use_insulin',
         'use_iv_inotropic',
         'use_iv_betablocker',
         # helper param: 'weight_metric'
      ]
      arr = []
      print("INPUTS")
      for k in keys:
          val = request.form.get(k, None)
          print(k, request.form.get(k, None), val and float(val))

          # allow for nonrequired inputs
          if val is None or val == "":
             arr.append(np.nan)
             continue
          else:
             val = float(val)

          # translate weight from lbs, if needed
          if k == "weight_kg" and request.form.get("weight_metric", None) == "lb":
             val = float(val) / FACTOR_LBS_TO_KG

          if k == "weight_kg":
             print("WEIGHT is: ")
             print(val, request.form.get("weight_metric"))

          arr.append(val)

      model_inputs = np.array([arr])
      print(arr)
      print(model_inputs)
      res = model_rlrvi(model_inputs)
      res = [r[0] for r in res]  # account for numpy returning each value as an array
      risk_score, lci, uci, unreliability = res
      print("RESULTS")
      print(risk_score)
      print(lci)
      print(uci)
      print(unreliability)

      return jsonify({
         "": ("Percentage", "95% Confidence Interval"),
         "Mortality within 6 Months": (risk_score, lci, uci),
         "Using a previously developed unreliability metric, the AUC for similar patients is": (unreliability, None, None),
      })

if __name__ == '__main__':
   app.run(host=os.environ.get("HOST", "0.0.0.0"), port=os.environ.get("PORT", 80))
