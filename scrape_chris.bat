@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/in/chriswargo/recent-activity/all/" ^
 --json="fastener/chris-wargo" ^
 --store="vs_GbjaYs1jGl98CoGckYSyQlcH"