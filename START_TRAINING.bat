@echo off
echo INSTALLING REQUIREMENTS...
pip install -r requirements.txt

echo.
echo LOGIN TO HUGGINGFACE...
huggingface-cli login

echo.
echo STARTING PEALLM TRAINING...
python execute_peallm_now.py

pause
