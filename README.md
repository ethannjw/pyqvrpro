#QVR Pro API Client

Basic client for interfacing with QVR Pro API.

## Exposed API
 - /generate_qvr_recording
 - /get_recording
 - /get_recording/:filename
 - /delete_recording/:filename

## Install requirements
`pip install -r requirements.txt`

## Run the file
`python run.py`


## Building the docker image
`docker build --tag pyqvrpro .`

