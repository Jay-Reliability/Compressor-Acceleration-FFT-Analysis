# 1. 로컬 저장소 초기화 (main 브랜치 기준)
git init -b main
# 2. 캐시 및 파이썬 컴파일 임시 파일 무시 설정 (.gitignore 작성)
# (이 폴더에 .gitignore 파일을 생성하여 __pycache__/ 등을 적어두시면 더욱 좋습니다)
# 3. 배포할 소스 코드 및 가속도 데이터 CSV 파일 추가
git add streamlit_app.py requirements.txt README.md run_dashboard.py Compressor_Acceleration_Analysis.html TVN6_0124_1822_50deg_Time.csv
# 4. 첫 번째 커밋 기록 생성
git commit -m "Deploy Compressor Acceleration Analysis to Streamlit"
# 5. 복사해 둔 GitHub 원격 주소 연결
git remote add origin https://github.com/사용자이름/compressor-analysis.git
# 6. GitHub 원격 브랜치로 코드 업로드
git push -u origin main
