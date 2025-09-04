@echo off
REM Ativar ambiente virtual e executar o app

echo ===========================================
echo 🚀 Iniciando Gerador de QR Code...
echo ===========================================

REM Ativa o ambiente virtual
call venv\Scripts\activate

REM Instala dependências (se necessário)
pip install -r requirements.txt

REM Executa o programa
python gerador_qrcode.py

REM Mantém a janela aberta depois de rodar
pause
