% prepara el repositorio para su despliegue.
release: sh -c 'python manage.py migrate --noinput'
release: sh -c 'pip install -U pip setuptools wheel'
release: sh -c 'pip install -U spacy'
release: sh -c 'python -m spacy download es_core_news_lg'
% especifica el comando para lanzar MIDAS
web: sh -c 'cd MIDAS && gunicorn MIDAS.wsgi --log-file -'
