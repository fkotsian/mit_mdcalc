import sys
# enable path to python3 packages
sys.path.insert(0,'/var/www/html/rleweb/cb/mit_mdcalc')
sys.path.insert(0,'/usr/local/lib64/python3.6')

# set calculator type
import os
os.environ['CALC_NAME'] = 'rlrvi'
os.environ['DEPLOY_PATH'] = '/cb/calc-rlrvi'
from app import app as application
