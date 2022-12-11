import os
import pyqvrpro
import datetime
from flask import Flask, send_from_directory

app = Flask(__name__, static_folder="./recording")
app.config['CAMERAUSER'] = os.environ.get("QVRPRO_USER")
app.config['PASSWORD'] = os.environ.get("QVRPRO_PW")
app.config['HOST'] = os.environ.get('QVRPRO_HOST')
app.config['PROTOCOL'] = os.environ.get('QVRPRO_PROTOCOL')
app.config['PORT'] = os.environ.get('QVRPRO_PORT')
app.config['VERIFY_SSL'] = False

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))


@app.route('/get_qvr_recording', methods=["GET"])
def get_qvr_recording():
    client = pyqvrpro.Client(os.environ.get("QVRPRO_USER"), os.environ.get("QVRPRO_PW"), os.environ.get('QVRPRO_HOST'), os.environ.get('QVRPRO_PROTOCOL'), os.environ.get('QVRPRO_PORT'), verify_SSL=False)
    cameras = client.list_cameras()
    camera_guid = cameras["datas"][0]["guid"]
    print(f"channel_guid: {camera_guid}")

    timestamp_string = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filepath = f'./recording/{timestamp_string}.mp4'

    recording_path = client.get_recording_path(client.get_recording(camera_guid=camera_guid, channel_id=0), filepath)

    return recording_path

@app.route('/get_recording/<path:path>', methods=["GET"])
def get_recording_file(path):
    return send_from_directory('recording', path)


if __name__ == '__main__':
   app.run(debug = True)