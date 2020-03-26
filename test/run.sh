echo  =================================================================
echo  ====================installing sonar scanner=====================
echo  =================================================================
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-3.3.0.1492-linux.zip
unzip sonar-scanner-cli-3.3.0.1492-linux.zip
rm sonar-scanner-cli-3.3.0.1492-linux.zip
chmod +x sonar-scanner-3.3.0.1492-linux/bin/sonar-scanner
echo "PATH=$PATH:sonar-scanner-3.3.0.1492-linux/bin" >> ~/.bashrc
. ~/.bashrc
echo  =================================================================
echo EXECUTING PYTEST...
echo  =================================================================
pytest --junitxml=pytest-report.xml
echo  =================================================================
echo EXECUTING COVERAGE...
echo  =================================================================
coverage run main_test.py
coverage xml -i
echo  =================================================================
echo EXECUTING SONAR SCANNER
echo  =================================================================
sonar-scanner