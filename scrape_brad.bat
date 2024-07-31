@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/in/brad-murray-95692953/recent-activity/all/" ^
 --json="tehama-wireless/brad-murray" ^
 --store="vs_kTKOK5gV1q9fixjGXT1He01v"