$ErrorActionPreference = "Stop"
Push-Location .\backend
python -m pip install -r .\requirements.txt
python -m pytest .\tests -q
Pop-Location
