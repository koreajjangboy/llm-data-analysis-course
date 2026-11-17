@echo off
:: 가상환경 활성화
call ..\.venv\Scripts\activate

:: 전체 파이프라인 진입점 실행
python run_pipeline.py

:: 실행 완료 후 터미널이 바로 닫히지 않도록 대기
pause