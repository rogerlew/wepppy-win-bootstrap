@echo off
echo downloading %1 %2

REM Read JWT token from %USERPROFILE%\.weppcloud_jwt if it exists
set "JWT="
if exist "%USERPROFILE%\.weppcloud_jwt" (
    set /p JWT=<"%USERPROFILE%\.weppcloud_jwt"
)

if defined JWT (
    echo using JWT authentication
    wget.exe https://wepp.cloud/weppcloud/runs/%1/cfg/aria2c.spec --output-document=%1_aria2c.spec --max-redirect=0 --header="Authorization: Bearer %JWT%"
    aria2c -j 10 --allow-overwrite true -d %2 --header="Authorization: Bearer %JWT%" --input-file=%1_aria2c.spec
) else (
    echo no JWT token found at %USERPROFILE%\.weppcloud_jwt
    echo downloading without authentication
    wget.exe https://wepp.cloud/weppcloud/runs/%1/cfg/aria2c.spec --output-document=%1_aria2c.spec --max-redirect=0
    aria2c -j 10 --allow-overwrite true -d %2 --input-file=%1_aria2c.spec
)
