@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/in/max-jurasic-24815832/recent-activity/all" ^
 --json="tehama-wireless/max-jurasic" ^
 --store="vs_kTKOK5gV1q9fixjGXT1He01v"