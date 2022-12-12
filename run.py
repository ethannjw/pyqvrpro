import os
from dotenv import load_dotenv
import pyqvrpro
import datetime
from flask import Flask, send_from_directory

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

def get_10_sec_ago():
    now = datetime.datetime.now()
    sec10ago = now - datetime.timedelta(seconds=10)
    return int(sec10ago.timestamp() * 1000)
    
@app.route('/get_recording', methods=["GET"])
def get_recording():
    client = pyqvrpro.Client(app.config['QVRPRO_USER'], app.config['QVRPRO_PW'], app.config['QVRPRO_HOST'], app.config['QVRPRO_PROTOCOL'], app.config['QVRPRO_PORT'], verify_SSL=app.config['VERIFY_SSL'])
    camera_guid = get_camera_guid(client)
    timestamp = get_10_sec_ago()
    response =  client.get_recording(timestamp=timestamp, camera_guid=camera_guid, channel_id=0 )
    return response, 200, {'Content-Type': 'video/mp4'}

@app.route('/generate_qvr_recording', methods=["GET"])
def generate_qvr_recording():
    client = pyqvrpro.Client(app.config['QVRPRO_USER'], app.config['QVRPRO_PW'], app.config['QVRPRO_HOST'], app.config['QVRPRO_PROTOCOL'], app.config['QVRPRO_PORT'], verify_SSL=app.config['VERIFY_SSL'])
    camera_guid = get_camera_guid(client)

    timestamp_string = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f'{timestamp_string}.mp4'
    filepath = os.path.join(app.config['RECORDING_DIR'], filename)
    timestamp = get_10_sec_ago()
    
    recording =  client.get_recording(timestamp=timestamp, camera_guid=camera_guid, channel_id=0 )

    recording_path = client.get_recording_path(recording, filepath)

    response = {'full_path': recording_path, 'filename': filename}
    return response, 200, {'Content-Type': 'application/json'}

@app.route('/get_recording/<path:filename>', methods=["GET"])
def get_recording_file(filename):
    response =  send_from_directory(app.config['RECORDING_DIR'], filename)

    @response.call_on_close
    def on_close():
        app.logger.info(f"Trying to delete file: {os.path.join(app.config['RECORDING_DIR'], filename)}")
        if os.path.exists(os.path.join(app.config['RECORDING_DIR'], filename)):
            os.remove(os.path.join(app.config['RECORDING_DIR'], filename))
            app.logger.info(f"Deleted: {os.path.join(app.config['RECORDING_DIR'], filename)}")
        else:
            app.logger.error("Error deleting file!")
    
    return response

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


if __name__ == '__main__':
   app.run(debug = True)