


insatll modules:

python -m pip install pip-tools

pip-compile requirements.in   
pip install -r requirements.txt

How to comit to code destined for dev:


- run: 
pre-commit run --all-files

- if failed:

pytest -q --maxfail=1  
tox 
isort .  
black .


