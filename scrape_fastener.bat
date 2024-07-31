@echo off

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scrape_linkedin.py ^
 --profile="%CD%\\profiles\\rebekah" ^
 --openai ^
 --url="https://www.linkedin.com/company/fastener-io/posts/?feedView=all" ^
 --json="fastener/fastener" ^
 --store="vs_GbjaYs1jGl98CoGckYSyQlcH"