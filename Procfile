% prepara el repositorio para su despliegue.
release: sh -c 'python manage.py migrate --noinput; pip install -U pip setuptools wheel; pip install -U spacy'
% especifica el comando para lanzar MIDAS
web: sh -c 'python -m spacy download es_core_news_sm'
web: sh -c 'cd MIDAS && gunicorn MIDAS.wsgi --log-file -'