goto(){
# Linux code here
uname -o
conda env create -f env.yaml
conda activate premix
}

goto $@
exit

:(){
rem Windows script here
echo %OS%
conda env create -f env.yaml
call conda activate premix
exit