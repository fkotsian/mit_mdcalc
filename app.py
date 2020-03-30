from flask import Flask, render_template, request, jsonify
import numpy as np
from model_as.lr_model_cal import get_model_output as model_as
from model_rlrvi.lr_model import get_model_output as model_rlrvi
from model_rlrvi.unreliability import unreliability
import random

app = Flask(__name__)

@app.route('/',methods = ['GET'])
def index():
   return render_template('index.html')

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
         "Combined outcome (3yrs)": r3yr_combined,
         "Combined outcome (5yrs)": r5yr_combined,
         "Mortality (3yrs)": r3yr_mortality,
         "Mortality (5yrs)": r5yr_mortality,
         "Mortality with no intervention (3yrs)": r3yr_valve_replacement,
         "Mortality with no intervention (5yrs)": r5yr_valve_replacement,
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
         'weight',
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
      ]
      arr = []
      print("INPUTS")
      for k in keys:
          val = request.form.get(k, None)
          print(k, request.form.get(k, None), float(val))
          arr.append(float(val))

      model_inputs = np.array([arr])
      rlrvi_prediction = model_rlrvi(model_inputs)
      risk_score = unreliability(model_inputs)

      return jsonify({
         "RLRVI": rlrvi_prediction,
         "Raw Score": (risk_score, None, None),
      })

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=80)
