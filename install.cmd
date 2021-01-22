echo off

goto(){
# Linux code here
uname -o
conda env create -f env.yaml
conda activate premix
conda install -c conda-forge sox
conda deactivate
chmod +x premix.cmd
}

goto $@
exit

:(){
rem Windows script here
echo %OS%
conda env create -f env.yaml
rem call conda activate premix
exit