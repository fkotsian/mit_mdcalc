import numpy as np
import os
import random

from flask import Flask, render_template, request, jsonify
from model_as.lr_model_cal import get_model_output as model_as
from model_rlrvi.lr_model import get_model_output as model_rlrvi
from model_rlrvi.unreliability import unreliability

app = Flask(__name__)

FACTOR_LBS_TO_KG = float(2.205)

@app.route('/',methods = ['GET'])
def index():
   calc_name = os.environ.get("CALC_NAME", "as")
   return render_template('index.html', calc_name=calc_name)

@app.route('/as',methods = ['POST'])
def result_as():
   if request.method == 'POST':
      result = request.form
      keys = ['tFlow','pressure','area','chf_baseline','mi_baseline','pvd_baseline','wall_abnormality','hyperlipidemia_baseline','ckd_baseline','thickness','diameter']
      arr = []
      print("INPUTS")
      for k in keys:
          val = request.form.get(k, None)

          # translate frontend radio button "value"s into 0/1
          if val == 'true':
              val = 1
          elif val == 'false':
              val = 0

          print(k, request.form.get(k, None), float(val))
          arr.append(float(val))
      model_inputs = np.array([arr])
      res = model_as(model_inputs)
      r3yr_combined = (res[0], res[6], res[12])
      r5yr_combined = (res[1], res[7], res[13])
      r3yr_mortality = (res[2], res[8], res[14])
      r5yr_mortality = (res[3], res[9], res[15])
      r3yr_valve_replacement = (res[4], res[10], res[16])
      r5yr_valve_replacement = (res[5], res[11], res[17])

      return jsonify({
         "": ("Percentage", "95% Confidence Interval"),
         #"All-cause mortality or aortic valve replacement (3yrs)": r3yr_combined,
         #"All-cause mortality or aortic valve replacement (5yrs)": r5yr_combined,
         "Mortality within 3 Years": r3yr_mortality,
         "Mortality within 5 Years": r5yr_mortality,
         #"All-cause mortality without an aortic valve replacement (3yrs)": r3yr_valve_replacement,
         #"All-cause mortality without an aortic valve replacement (5yrs)": r5yr_valve_replacement,
      })

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
          if val is None:
             arr.append(np.nan)
             continue

          # translate weight from lbs, if needed
          if k == "weight_kg" and request.form.get("weight_metric", None) == "lb":
             val = float(val) / FACTOR_LBS_TO_KG

          if k == "weight_kg":
             print("WEIGHT!!! METRIC!!!!")
             print(val, request.form.get("weight_metric"))

          arr.append(float(val))

      model_inputs = np.array([arr])
      print(arr)
      print(model_inputs)
      risk_score, lci, uci, unreliability = model_rlrvi(model_inputs)
      print("RESULTS")
      print(risk_score)
      print(lci)
      print(uci)
      print(unreliability)

      return jsonify({
         "": ("Value", "Lower 95% CI", "Upper 95% CI"),
         "Risk Score": (risk_score[0], lci, uci),
         "This patient is from a subgroup in which the model AUC is": (unreliability[0], None, None),
      })

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=80)
