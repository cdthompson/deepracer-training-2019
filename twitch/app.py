import datetime
from flask import abort, Flask, render_template, request, send_from_directory
from flask_bootstrap import Bootstrap
import json
import os.path
import sys
import threading
import time
from worker import log_worker

# Paths
image_path='images'
cache_path='cache'
log_prefix='logs'

# Session information
job_id=''
model_name = ''
session_name = ''
track_name = ''

# The main flask app
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
Bootstrap(app)

@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    response.cache_control.max_age = 0
    return response

@app.route('/')
def get_metrics():
    try:
      with open('images/summary.json', 'r') as f:
        metrics = json.load(f)
        duration = time.time() - metrics['session_start']
    except Exception as e:
      print("Exception {} trying to load metrics file".format(type(e)))
      print(e)
      metrics = {} 
      duration = 0

    return render_template('index.html', 
                           metrics=metrics,
                           duration=duration,
                           model=model_name,
                           session=session_name,
                           training_image=os.path.join(image_path,'training.png'),
                           track_image=os.path.join(image_path,'%s.svg' % track_name))

@app.route('/images/<path:path>')
def serve_images(path):
  return send_from_directory('images', path)

if __name__ == '__main__':
    if len(sys.argv) < 5:
        raise Exception("Usage: python3 %s <job id> <model name> <session name> <track>" % (sys.argv[0]))
    job_id = sys.argv[1]
    model_name = sys.argv[2]
    session_name = sys.argv[3]
    track_name = sys.argv[4]
    log_path = os.path.join(log_prefix, job_id)
    os.makedirs(log_path, exist_ok=True)
    # start the background worker
    thread = threading.Thread(target=log_worker, 
                              args=(job_id, log_path, image_path))
    thread.start()

    # remove any old summary metrics
    #os.remove('images/summary.json')

    # start the web app
    app.run(host='0.0.0.0')
