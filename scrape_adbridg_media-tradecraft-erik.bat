@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/in/erikrequidan/recent-activity/all/" ^
 --json="adbridg/media-tradecraft-erik-requidan" ^
 --store="vs_amL7Z6KxhCGTMsNChvDCJ1Ln"