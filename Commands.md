 .\.venv\Scripts\Activate.ps1 ; 
 
 python main.py --stage 1
 python main.py --stage 2

 python -m unittest discover -s tests -v
