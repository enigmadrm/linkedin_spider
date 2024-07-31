@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/company/the-operators-guild/posts/?feedView=all" ^
 --json="operators-guild/operators-guild" ^
 --store="vs_TdFjgB3U89Tn2J8d93nFNXzj"