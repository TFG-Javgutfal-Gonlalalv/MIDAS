% prepara el repositorio para su despliegue.
release: sh -c 'python manage.py migrate --noinput'
release: sh -c 'python manage.py syncdb'
% especifica el comando para lanzar MIDAS
web: sh -c 'cd MIDAS && gunicorn MIDAS.wsgi --log-file -'