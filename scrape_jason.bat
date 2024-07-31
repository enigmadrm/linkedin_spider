@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/in/jasongreene/recent-activity/all/" ^
 --json="fastener/jason-greene" ^
 --store="vs_GbjaYs1jGl98CoGckYSyQlcH"