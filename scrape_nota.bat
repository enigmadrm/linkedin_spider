@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py --url="https://www.linkedin.com/company/heynota/posts/?feedView=all" --excel