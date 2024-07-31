@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/company/tehama-wireless/posts/?feedView=all" ^
 --json="tehama-wireless/tehama-wireless" ^
 --store="vs_kTKOK5gV1q9fixjGXT1He01v"