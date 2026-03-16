@echo off
title BUILD - WHATSAPP BOT LOCAL

echo ============================================
echo        GERANDO EXECUTÁVEL DO BOT
echo ============================================

REM Ativar ambiente virtual (primeiro procura .venv e depois venv)
if exist .venv (
    echo Ativando ambiente virtual .venv...
    call .venv\Scripts\activate
) else if exist venv (
    echo Ativando ambiente virtual venv...
    call venv\Scripts\activate
) else (
    echo [ERRO] Nenhum ambiente virtual "venv" ou ".venv" encontrado!
    pause
    exit /b
)

echo.
echo Instalando dependencias...
pip install -r requirements.txt --quiet

echo.
echo Limpando builds anteriores...
if exist build (
    echo Removendo pasta build...
    rmdir /s /q build
)
if exist dist (
    echo Removendo pasta dist...
    rmdir /s /q dist
)

if exist app\whatsapp_profile (
    echo Removendo perfil sensivel - app\whatsapp_profile...
    rmdir /s /q app\whatsapp_profile
)
if exist whatsapp_profile (
    echo Removendo perfil sensivel - whatsapp_profile...
    rmdir /s /q whatsapp_profile
)

REM Caso queira regenerar a .spec, descomente a linha abaixo:
REM if exist WhatsAppBotLocal.spec del WhatsAppBotLocal.spec

echo.
echo Gerando executavel a partir da SPEC...
pyinstaller --noconfirm WhatsAppBotLocal.spec

echo.
echo ============================================
echo BUILD FINALIZADO!
echo Arquivo gerado: dist\WhatsAppBotLocal.exe
echo ============================================

if not defined SKIP_PAUSE pause
