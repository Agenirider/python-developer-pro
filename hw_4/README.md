### Pull docker image from docker hub
docker pull redis


### Run docker container
docker run -d -p 6379:6379 -t redis


### Install redis library - requirements.txt
pip install -r requirements.txt


### Start tests
- python.exe -m unittest -v test.py
- python -m unittest discover -s tests/integration