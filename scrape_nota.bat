@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/company/heynota/posts/?feedView=all" ^
 --json="nota/nota" ^
 --store="vs_zpVIl8WJPL7RwuNeyGOjVmAt"