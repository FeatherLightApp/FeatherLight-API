Template for creating containerized ariadne applications with docker-compose

Usage

git clone https://github.com/seanaye/ariadne_template

cd ariadne_template

docker-compose -f ./docker-compose.yml up

Optional setup pylint for use with VSCode

python3 -m venv env

source env/bin/activate

pip install -r requirements.txt


