% prepara el repositorio para su despliegue.
release: sh -c 'python manage.py makemigrations; python manage.py migrate --noinput; pip install -U pip setuptools wheel; pip install -U spacy'
% especifica el comando para lanzar MIDAS
web: sh -c 'cd MIDAS && gunicorn MIDAS.wsgi --log-file -'