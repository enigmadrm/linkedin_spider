@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/in/jim-orton-835175/recent-activity/all/" ^
 --json="tehama-wireless/jim-orton" ^
 --store="vs_kTKOK5gV1q9fixjGXT1He01v"