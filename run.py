import os
from dotenv import load_dotenv
import pyqvrpro
import datetime
from flask import Flask, send_from_directory, request

load_dotenv()
def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['RECORDING_DIR'] = os.environ.get("RECORDING_DIR") if os.environ.get("RECORDING_DIR") is not None else os.path.join(root_dir(), 'recording')
app.config['QVRPRO_USER'] = os.environ.get("QVRPRO_USER")
app.config['QVRPRO_PW'] = os.environ.get("QVRPRO_PW")
app.config['QVRPRO_HOST'] = os.environ.get("QVRPRO_HOST") 
app.config['QVRPRO_PROTOCOL'] = os.environ.get('QVRPRO_PROTOCOL')
app.config['QVRPRO_PORT'] = os.environ.get('QVRPRO_PORT') if os.environ.get("QVRPRO_PORT") is not None else 443
app.config['VERIFY_SSL'] = False if os.environ.get("VERIFY_SSL") == '0' else True

def get_camera_guid(client):
    camera_guid = os.environ.get("CAMERA_GUID")
    if camera_guid == '':
        app.logger("Getting new camera guid")
        cameras = client.list_cameras()
        camera_guid = cameras["datas"][0]["guid"]
        app.logger.info(f"channel_guid: {camera_guid}")
    app.logger.info('Camera GUID: ', camera_guid)
    return camera_guid

def get_now_timestamp():
    now = datetime.datetime.now()
    return int(now.timestamp() * 1000)
    
def get_offset_timestamp(offset):
    now = datetime.datetime.now()
    timestamp = now + datetime.timedelta(seconds=offset)
    return int(timestamp.timestamp() * 1000)

@app.route('/get_recording', methods=["GET"])
def get_recording():
    pre_period_param = request.args.get("pre_period", default="", type=int)
    post_period_param = request.args.get("post_period", default="", type=int)
    offset_param = request.args.get("offset", default="", type=int)
    pre_period = pre_period_param * 1000 if pre_period_param != "" else 10000
    post_period = post_period_param * 1000 if post_period_param != "" else 1000
    offset = offset_param if offset_param != "" else 0
    
    client = pyqvrpro.Client(app.config['QVRPRO_USER'], app.config['QVRPRO_PW'], app.config['QVRPRO_HOST'], app.config['QVRPRO_PROTOCOL'], app.config['QVRPRO_PORT'], verify_SSL=app.config['VERIFY_SSL'])
    camera_guid = get_camera_guid(client)
    timestamp = get_offset_timestamp(offset)

    app.logger.info({
        'request_time': datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
        'timestamp': timestamp,
        'pre_period': pre_period,
        'post_period': post_period,
        'offset': offset
    })

    response = client.get_recording(timestamp=timestamp, camera_guid=camera_guid, channel_id=0, pre_period=pre_period, post_period=post_period)

    if response.headers['content-type'] == 'application/json':
        # Means error
        app.logger.error({
            'error_response': response.json(),
            'timestamp': timestamp,
            'pre_period': pre_period,
            'post_period': post_period,
            'offset': offset
        })
        return response.json(), 404, {'Content-Type': 'application/json'}

    if response.headers['content-type'] == 'video/mp4':
        return response.content, 200, {'Content-Type': 'video/mp4'}
    
    return "Invalid Response"

@app.route('/generate_qvr_recording', methods=["GET"])
def generate_qvr_recording():
    client = pyqvrpro.Client(app.config['QVRPRO_USER'], app.config['QVRPRO_PW'], app.config['QVRPRO_HOST'], app.config['QVRPRO_PROTOCOL'], app.config['QVRPRO_PORT'], verify_SSL=app.config['VERIFY_SSL'])
    camera_guid = get_camera_guid(client)

    timestamp_string = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f'{timestamp_string}.mp4'
    filepath = os.path.join(app.config['RECORDING_DIR'], filename)
    timestamp = get_now_timestamp()
    
    recording =  client.get_recording(timestamp=timestamp, camera_guid=camera_guid, channel_id=0 )

    recording_path = client.get_recording_path(recording, filepath)

    response = {'full_path': recording_path, 'filename': filename}
    return response, 200, {'Content-Type': 'application/json'}

@app.route('/get_recording/<path:filename>', methods=["GET"])
def get_recording_file(filename):
    return send_from_directory(app.config['RECORDING_DIR'], filename)

@app.route('/delete_recordings/<path:filename>', methods=["GET", "POST"])
def delete_recording(filename):
    app.logger.info(f"Trying to delete file: {os.path.join(app.config['RECORDING_DIR'], filename)}")
    if os.path.exists(os.path.join(app.config['RECORDING_DIR'], filename)):
        os.remove(os.path.join(app.config['RECORDING_DIR'], filename))
        app.logger.info(f"Deleted: {os.path.join(app.config['RECORDING_DIR'], filename)}")
        return "OK"
    else:
        app.logger.error("Error deleting file!")
        return "ERROR"

@app.route('/health_check', methods=["GET"])
def get_health_check():
    health_check_res = {"status": "healthy"}
    return health_check_res, 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
   app.run(debug = True)