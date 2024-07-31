@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
--url="https://www.linkedin.com/feed/" ^
--start=1 ^
--excel ^
--username="casey.woo@gmail.com" ^
--password="Millvalley!2345" ^
--profile="%CD%\\profiles\\casey" ^
--limit=10 ^
--headless=0

pause
