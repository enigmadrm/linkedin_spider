@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/in/joshuabrandau/recent-activity/all/" ^
 --json="nota/josh-brandau" ^
 --store="vs_zpVIl8WJPL7RwuNeyGOjVmAt"