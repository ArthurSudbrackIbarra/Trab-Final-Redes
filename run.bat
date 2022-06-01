@echo off

:: start python "src/main.py src/config/config-1.txt 9200"
:: start python "src/main.py src/config/config-2.txt 9000"
:: start python "src/main.py src/config/config-3.txt 9100"

cd src/
python main.py