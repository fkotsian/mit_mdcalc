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
   calc_name = 'as'
   deploy_path = '/calc-as'
   return render_template('index.html', calc_name=calc_name, deploy_path=deploy_path)

@app.route('/as',methods = ['POST'])
def result_as():
   if request.method == 'POST':
      result = request.form
      keys = ['tFlow','pressure','area','chf_baseline','mi_baseline','pvd_baseline','wall_abnormality','hyperlipidemia_baseline','ckd_baseline','thickness','diameter_mm']
      arr = []
      print("INPUTS")
      for k in keys:
          val = request.form.get(k, None)

          # translate frontend radio button "value"s into 0/1
          if val == 'true':
              val = 1
          elif val == 'false':
              val = 0

          # translate sinus diameter into mm, if needed
          if k == "diameter_mm" and request.form.get("diameter_metric", None) == "cm":
             val = float(val) * FACTOR_CM_TO_MM

          if k == "diameter_mm":
             print("DIAMETER is: ")
             print(val, request.form.get("diameter_metric"))

          print(k, request.form.get(k, None), float(val))
          arr.append(float(val))

      model_inputs = np.array([arr])
      res = model_as(model_inputs)
      res = [r[0] for r in res]  # account for numpy returning each value as an array
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
      # dummy inputs - if needed
      #       res = (0.5549738219895288,
      #  0.7225130890052356,
      #  0.44502617801047123,
      #  0.5287958115183246,
      #  0.5104895104895105,
      #  0.6293706293706294,
      #  0.539512561556879,
      #  0.7074213028500234,
      #  0.4311168850455077,
      #  0.5120883312499264,
      #  0.49258244842160626,
      #  0.6114624324191157,
      #  0.5704350824221787,
      #  0.7376048751604478,
      #  0.45893547097543475,
      #  0.5455032917867227,
      #  0.5283965725574148,
      #  0.6472788263221431)

if __name__ == '__main__':
   app.run(host=os.environ.get("HOST", "0.0.0.0"), port=os.environ.get("PORT", 80))
