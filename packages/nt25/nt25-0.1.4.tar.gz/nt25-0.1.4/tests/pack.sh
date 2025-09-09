#!env bash
uvx pyinstaller \
  --hidden-import=matplotlib \
  --hidden-import=openpyxl \
  --hidden-import=pandas \
  --hidden-import=scikit-learn \
  --hidden-import=sympy \
  ./src/nt25/main.py
