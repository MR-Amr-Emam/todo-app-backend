# todo-app-backend

this is backend part of todo app
the porject is made with django, it is json api endpoints
the project mainly consists of two apps authentication app and notes app, authentication app set JWT in cookies, and
the notes app manage notes, reminders and goals instance in sqlite database

### demo
https://mramremam.pythonanywhere.com

## how to run app

### development mode
* clone repository
* download dependencies with "pip install requiremnts.txt" in base directory
* run "python manage.py runserver" in base directory

### production mode
* clone repository
* downolad dependencies as before
* download uwsgi for wsgi server
* download Nginx to work as proxy server for uwsgi server and to deploy static files see [documentation](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html)

### Note
if you are on windows like me, uwsgi runs on linux only, so install cygwin which is linux simulator and install uwsgi in it's bash and make virutal environment in it's bash also because it the virtual environment that is created in windows bash(power shell) can't be recognised from uwsgi that is installed in cygwin shell as the venv will be installed like it is in windows (Scripts folder(which is in windows) not bin folder(which is on linux)) that take for me too long time to figure that.
recap: to install uwsgi on windows first install cygwin then open the cygwin shell and install uwsgi then create virtualenv in cygwin shell also and download all dependencies with "pip install requirements.txt)

### another Note
make all configurations needed in settings.py file for host name , cors and cookies

### third Note :)
because frontend is on a domain (todo-app-frontend-demo.vercel.app) and backend on other domain(mramremam.pythonanywhere.com) I have had to make cookies samesite to "None" to allow cross origins and to remove csrf middleware because it is impossible to use csrf with two different domains as access to backend domain cookies from frontend domain in browser is impossible.
  
