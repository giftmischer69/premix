echo off

goto(){
# Linux code here
conda activate premix
python run.py
conda deactivate
}

goto $@
exit

:(){
rem Windows script here
call conda activate premix
python run.py
call conda deactivate
exit