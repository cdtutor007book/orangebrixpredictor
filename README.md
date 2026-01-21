# 제주 성산의 감귤 당도 예측기 

기상정보와 햇빛을 받은 시간에 따라 달라지는 감귤의 당도를 예측하는 앱입니다.
2015년~2025년 약 10년의 최저기온, 평균기온, 최고기온, 가조시간(직사광선을 받은시간), 강수량, 일교차, 당도 데이터를 분석하였고
이중 당도 데이터와 상관관계가 높은 변수들을 뽑아 선형회귀로 학습을 시켜보았습니다. 
선형회귀와 다항선형회귀 중 다항선형회귀가 성능이 더 좋아서 다항선형회귀로 만든 모델을 사용해 당도예측앱을 제작하였습니다. 
학습에 사용한 데이터는 아래의 링크에서 참조하였습니다. 

1. 기상정보 : https://data.kma.go.kr/data/grnd/selectAsosRltmList.do?pgmNo=36
2. 감귤의 당도정보 : https://fruit.nihhs.go.kr/main/qlityInfo_frutQlity.do?frtgrdCode=citrus

    

### 이 앱을 사용하기 위해서는 아래의 라이브러리가 필요합니다. 

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
