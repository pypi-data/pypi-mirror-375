@echo off

:: 1. ����ɹ�������
echo ����ɹ�������...
if exist dist (
    rmdir /s /q dist
)
mkdir dist 2>nul

:: 2. �Զ������汾����ȡ�°汾��
echo �Զ������汾��...
for /f "delims=" %%v in ('python bump_version.py') do set "NEW_VERSION=%%v"
echo �汾�Ѹ���Ϊ: %NEW_VERSION%

:: 3. ������
echo �����°汾...
hatch build

:: 4. ����Git�ύ��Ϣ��֧�ֿ�ѡ������
echo ׼���ύ����...
:: Ĭ���ύ��Ϣ
set "COMMIT_MSG=idl����- %NEW_VERSION%"

:: �ؼ��޸�����"%~1"�������ո��������������ƴ�Ӱ汾��
if not "%~1"=="" (
    set "COMMIT_MSG=%NEW_VERSION% - %~1"
)

git add .
git commit -m "%COMMIT_MSG%"
git push

:: 5. �ϴ���PyPI
echo �ϴ���PyPI...
twine upload dist/*

echo ������ɣ�
echo �ύ��Ϣ: %COMMIT_MSG%
