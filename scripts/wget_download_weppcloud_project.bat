echo downloading %1 %2
wget.exe -O- -v https://wepp.cloud/weppcloud/runs/%1/cfg/export/prep_details/?no_retrieve
wget.exe -rv -nH --cut-dirs=5 -p --directory-prefix=%2 --header="raw: True"  https://wepp.cloud/weppcloud/runs/%1/cfg/browse/ 