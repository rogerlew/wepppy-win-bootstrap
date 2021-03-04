echo downloading %1 %2
wget -O- -v https://wepp.cloud/weppcloud/runs/%1/cfg/export/arcmap/?no_retrieve
wget -O- -v https://wepp.cloud/weppcloud/runs/%1/cfg/export/prep_details/?no_retrieve
wget -rv -nH --cut-dirs=5 --directory-prefix=%1 --header="raw: True"  https://wepp.cloud/weppcloud/runs/%1/cfg/browse/ %2