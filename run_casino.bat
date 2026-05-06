@echo off
setlocal

where py >nul 2>nul
if %errorlevel%==0 (
    py -m pip install -r requirements.txt
    py main.py
    goto :end
)

where python >nul 2>nul
if %errorlevel%==0 (
    python -m pip install -r requirements.txt
    python main.py
    goto :end
)

where python3 >nul 2>nul
if %errorlevel%==0 (
    python3 -m pip install -r requirements.txt
    python3 main.py
    goto :end
)

echo Python nao foi encontrado no PATH.
echo Instale o Python 3 e rode: pip install -r requirements.txt
pause

:end
endlocal
