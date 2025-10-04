@echo off
echo 🇹🇭 Thai Energy RAG System - Automated Setup
echo ==========================================
echo Installing required packages...

pip install sentence-transformers scikit-learn gradio pandas numpy
if %errorlevel% neq 0 (
    echo Trying with python -m pip...
    python -m pip install sentence-transformers scikit-learn gradio pandas numpy
)

echo.
echo 🚀 Starting Thai Energy RAG System...
echo Using complete dataset with 309 documents
echo.

python thai_energy_complete_rag.py

pause
