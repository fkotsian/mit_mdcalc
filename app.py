from flask import Flask, render_template, request, jsonify
import numpy as np
from lr_model import get_model_output

app = Flask(__name__)

@app.route('/',methods = ['GET'])
def index():
   return render_template('index.html')

@app.route('/',methods = ['POST'])
def result():
   if request.method == 'POST':
      result = request.form
      keys = ['tFlow','pressure','area','yes_no3','yes_no4','yes_no5','yes_no6','yes_no7','yes_no8','thickness','diameter']
      arr = []
      print("YES3")
      from pprint import pprint
      pprint(request.form)
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
      res = get_model_output(model_inputs)
      res = [el for el in res]
      yh_syn = res[0]
      print(arr)
      print("YH SYN")
      print(yh_syn)
      print(type(yh_syn))
      return jsonify({
         "result": arr,
         "yh_syn": yh_syn,
      })
      # return render_template("indexFilled.html",result = arr, ans = yh_syn)

if __name__ == '__main__':
   app.run(host="0.0.0.0", port=80)
