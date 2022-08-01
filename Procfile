% prepara el repositorio para su despliegue.
release: sh -c 'cd MIDAS && python manage.py migrate --noinput'
% especifica el comando para lanzar MIDAS
web: sh -c 'cd MIDAS && gunicorn MIDAS.wsgi --log-file -'