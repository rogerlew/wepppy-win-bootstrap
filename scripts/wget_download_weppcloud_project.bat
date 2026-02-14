@echo off
echo downloading %1 %2

REM Read JWT token from %USERPROFILE%\.weppcloud_jwt if it exists
set "JWT="
if exist "%USERPROFILE%\.weppcloud_jwt" (
    set /p JWT=<"%USERPROFILE%\.weppcloud_jwt"
)

if defined JWT (
    echo using JWT authentication
    wget.exe -O- -v https://wepp.cloud/weppcloud/runs/%1/cfg/export/prep_details/?no_retrieve --header="Authorization: Bearer %JWT%"
    wget.exe -rv -nH --cut-dirs=5 -p --directory-prefix=%2 --header="raw: True" --header="Authorization: Bearer %JWT%" https://wepp.cloud/weppcloud/runs/%1/cfg/browse/
) else (
    echo no JWT token found at %USERPROFILE%\.weppcloud_jwt
    echo downloading without authentication
    wget.exe -O- -v https://wepp.cloud/weppcloud/runs/%1/cfg/export/prep_details/?no_retrieve
    wget.exe -rv -nH --cut-dirs=5 -p --directory-prefix=%2 --header="raw: True" https://wepp.cloud/weppcloud/runs/%1/cfg/browse/
)
