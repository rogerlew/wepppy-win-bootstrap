echo downloading %1 %2
wget.exe -rv -nH --cut-dirs=5 -p --directory-prefix=%2 --header="raw: True"  https://wepp.cloud/weppcloud/runs/%1/cfg/browse/ 