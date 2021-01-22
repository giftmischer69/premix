echo off

goto(){
# Linux code here
uname -o
conda deactivate
conda env remove -n premix
echo "remove the current directory for a full uninstallation"
}

goto $@
exit

:(){
rem Windows script here
echo %OS%
call conda deactivate
conda env remove -n premix
echo "remove the current directory for a full uninstallation"
exit