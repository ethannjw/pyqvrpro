# QVR Pro API Client

Dockerised Flask API wrapper for the qvr pro recorder. WIP

## Exposed API
 - /generate_qvr_recording
 - /get_recording
   - Gets the recordings directly with offset (sec) pre_period (sec) post_period (sec) params TBA
 - /get_recording/:filename
 - /delete_recording/:filename
 - /health_check

## Use a virtual env
`python -m venv venv`
`cd venv/Scripts`
`activate`

## Install requirements
`pip install -r requirements.txt`

## Run the file
`python run.py`

## Building the docker image
To build the image, simply run the command at root
`docker build --tag pyqvrpro .`


