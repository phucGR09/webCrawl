@echo off
REM Simple crawler runner

if "%1"=="" goto usage

REM Activate venv
call venv\Scripts\activate.bat

REM Run command
if "%1"=="crawl" (
    if "%2"=="" (
        REM Run all crawlers
        for /d %%d in (src\crawl\*) do (
            if exist "%%d\crawler.py" python "%%d\crawler.py"
        )
    ) else (
        REM Run specific crawler
        python src\crawl\%2\crawler.py
    )
    goto end
)

if "%1"=="merge" (
    python src\merge_data.py
    goto end
)

:usage
echo Usage:
echo   run.bat crawl [name]  - Run crawler(s)
echo   run.bat merge         - Merge data
goto end

:end
