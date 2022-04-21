ECHO OFF
ECHO ============================================================
ECHO Starting Django Project
ECHO DONT execute this if you are using docker. This script will start django on windows without django.
ECHO ============================================================

SET PYTHON_EXECUTABLE=notfound
@REM LOOP through the list of python commands  to find the correct one by execute the --version of the command and set it to the variable PYTHON_EXECUTABLE of the one which does not throw an error
FOR %%P IN ("py -3.10", "python3.10", "py -3.9", "python3.9", "python3", "py" "python") DO (
    %%~P --version
    IF NOT ERRORLEVEL 1 (
        SET PYTHON_EXECUTABLE=%%~P
        echo Python command found: %%~P
        GOTO :start_django_project
    )
)

IF PYTHON_EXECUTABLE=notfound (
    echo Python command not found. Please install python 3.9 or higher and make sure the command to execute it is 'py -3.9'
    PAUSE
    EXIT
)

:start_django_project

@REM Check if we have a venv
@REM If we do, activate it
@REM If we don't, create it


IF NOT EXIST venv\Scripts\activate.bat (
    ECHO Creating venv ... This may take a while
    %PYTHON_EXECUTABLE% -m venv venv
)

@REM Install requirements if they are not already installed
@REM If they are, skip this step

IF NOT EXIST venv\req_installed  (
    ECHO Installing requirements
	"venv\Scripts\pip" install -r requirements.txt
    COPY NUL venv\req_installed
) ELSE (
    ECHO Requirements already installed
)

@REM Start Django

if EXIST .\web\manage.py (
    ECHO Making migrations
	"venv\Scripts\python" .\web\manage.py makemigrations

    ECHO Running migrations
	"venv\Scripts\python" .\web\manage.py migrate app
	"venv\Scripts\python" .\web\manage.py migrate

    ECHO Loading fixtures

    @REM LOOP through all fixtures in the fixtures folder in a for loop and load them one by one
    for %%f in (app\fixtures\*.*) do (
        ECHO Loading fixture %%f
        "venv\Scripts\python" .\web\manage.py loaddata %%f
    )

    IF NOT EXIST venv\user_created (
        ECHO ----------------------------------------------------------------------------------------------------
        ECHO ----------------------------------------------------------------------------------------------------
        ECHO Please create and admin user and password, you will need to use this to signin to the admin panel
        ECHO Please do not use a real password this is a development environment.
        ECHO Create an admin user

        COPY NUL venv\user_created
        "venv\Scripts\python" .\web\manage.py createsuperuser
    ) ELSE (
        ECHO Super User already created
    )

    ECHO Collecting static files
    "venv\Scripts\python" .\web\manage.py collectstatic --noinput

    ECHO Running server
    start "" /d iexplore.exe "http://localhost:8000"
	"venv\Scripts\python" .\web\manage.py runserver
)

PAUSE