echo downloading %1 %2
wget.exe https://wepp.cloud/weppcloud/runs/%1/cfg/aria2c.spec --output-document=%1_aria2c.spec --max-redirect=0 

aria2c -j 10 --allow-overwrite true -d %2 --input-file=%1_aria2c.spec