@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py --url="https://www.linkedin.com/in/mollyanawalt/recent-activity/all/" --excel


python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/in/mollyanawalt/recent-activity/all/" ^
 --json="operators-guild/molly-gunderson" ^
 --store="vs_TdFjgB3U89Tn2J8d93nFNXzj"