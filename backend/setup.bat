@echo off
setlocal

cd /d %~dp0

python -m venv venv
call venv\Scripts\activate

pip install -r requirements.txt

if not exist ..\.env (
  copy ..\.env.example ..\.env
)

echo Create databases:
echo   createdb hireus
echo   createdb hireus_test
echo Then update ..\.env with your DB password.

alembic upgrade head

echo Setup complete. Run: uvicorn app.main:app --reload
endlocal
