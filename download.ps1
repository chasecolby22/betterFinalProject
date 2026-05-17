
git pull
mv ./stockfish ../
mv ../stockfish ./
rm -rf ./.venv 
rm -rf ./__pycache__ 
python -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install pygame-ce
python main.py



echo "done"