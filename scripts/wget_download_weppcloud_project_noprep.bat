@echo off
python "%~dp0download_with_aria2c.py" %*
exit /b %errorlevel%
