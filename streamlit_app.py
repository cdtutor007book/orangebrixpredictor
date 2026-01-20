import streamlit as st
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

st.title("🍊 제주 성산의 감귤 당도 예측기")
st.write("슬라이더로 기후 데이터를 조정하면 실시간으로 당도를 예측합니다.")

# 레이아웃: 왼쪽 입력(좁게), 오른쪽 출력(넓게)
left_col, right_col = st.columns([1, 2])

# 콜백: 어느 슬라이더가 마지막으로 변경됐는지 기록하고
# 두 값의 차이가 18을 넘으면 반대쪽 값을 조정하여 범위를 리셋
def _on_min_change():
	st.session_state._last_changed = 'min'
	# max가 min보다 18초과면 max를 min+18로 조정
	if st.session_state.get('max_temp', st.session_state.min_temp) - st.session_state['min_temp'] > 18:
		st.session_state['max_temp'] = st.session_state['min_temp'] + 18
		# 평균도 범위 내로 유지
		if st.session_state.get('avg_temp', st.session_state['min_temp']) < st.session_state['min_temp']:
			st.session_state['avg_temp'] = st.session_state['min_temp']
		if st.session_state.get('avg_temp', st.session_state['min_temp']) > st.session_state['max_temp']:
			st.session_state['avg_temp'] = st.session_state['max_temp']

def _on_max_change():
	st.session_state._last_changed = 'max'
	# min이 max보다 18초과면 min을 max-18로 조정
	if st.session_state['max_temp'] - st.session_state.get('min_temp', st.session_state['max_temp']) > 18:
		st.session_state['min_temp'] = st.session_state['max_temp'] - 18
		if st.session_state.get('avg_temp', st.session_state['min_temp']) < st.session_state['min_temp']:
			st.session_state['avg_temp'] = st.session_state['min_temp']
		if st.session_state.get('avg_temp', st.session_state['min_temp']) > st.session_state['max_temp']:
			st.session_state['avg_temp'] = st.session_state['max_temp']

with left_col:
	st.header("입력")
	# 세션 상태에 기본값 설정
	if "min_temp" not in st.session_state:
		st.session_state.min_temp = 26.30
	if "max_temp" not in st.session_state:
		st.session_state.max_temp = 31.60
	if "avg_temp" not in st.session_state:
		st.session_state.avg_temp = 28.60
	if "sun_hours" not in st.session_state:
		st.session_state.sun_hours = 13.80

	# 슬라이더 순서: 평균기온 → 최고기온 → 최저기온 → 가조시간 (피처 순서와 동일)
	# 전체 허용 범위: -5 ~ 36
	avg_temp = st.slider("평균기온 (℃)", min_value=-5.0, max_value=36.0, value=min(max(st.session_state.avg_temp, -5.0), 36.0), step=0.1, key="avg_temp")
	# 최고기온은 최저기온보다 작을 수 없음; 전체 최대 36
	max_temp = st.slider("최고기온 (℃)", min_value=-5.0, max_value=36.0, value=min(max(st.session_state.max_temp, -5.0), 36.0), step=0.1, key="max_temp", on_change=_on_max_change)
	# 최저기온은 최고기온과의 차이가 18 이하
	min_temp = st.slider("최저기온 (℃)", min_value=-5.0, max_value=36.0, value=max(min(st.session_state.min_temp, 36.0), -5.0), step=0.1, key="min_temp", on_change=_on_min_change)
	sun_hours = st.slider("가조시간 (시간)", min_value=0.0, max_value=15.0, value=min(max(st.session_state.sun_hours, 0.0), 15.0), step=0.1, key="sun_hours")

with right_col:
	st.header("예측 결과")

	# 모델 로드
	model_path = Path("brix_model.joblib")
	model = None
	if model_path.exists():
		try:
			model = joblib.load(model_path)
		except Exception as e:
			st.error(f"모델 로드 실패: {e}")
	else:
		st.warning("루트에 `brix_model.joblib` 파일이 없습니다. 업로드하거나 경로를 확인하세요.")

	# 세션 상태 초기화
	if "history" not in st.session_state:
		st.session_state.history = []

	# 실시간 예측 및 히스토리 추가
	if model is not None:
		try:
			# 안전한 값 보장: 최저 <= 평균 <= 최고
			if max_temp < min_temp:
				max_temp = min_temp
			if avg_temp < min_temp:
				avg_temp = min_temp
			if avg_temp > max_temp:
				avg_temp = max_temp
			# (주의) 슬라이더 위젯이 이미 `st.session_state`를 업데이트하므로
			# 여기서 다시 쓰지 않습니다. 직접 덮어쓰면 Streamlit에서 오류가 발생합니다.
			# 모델이 feature names를 기대할 수 있으므로 DataFrame으로 전달
			X_df = pd.DataFrame([[avg_temp, max_temp, min_temp, sun_hours]], columns=["평균기온", "최고기온", "최저기온", "가조시간"])
			y_pred = model.predict(X_df)
			prediction_value = float(y_pred[0])
			st.metric("예측값 (당도)", f"{prediction_value:.3f}")

			entry = {
				"평균기온": round(float(avg_temp), 1),
				"최고기온": round(float(max_temp), 1),
				"최저기온": round(float(min_temp), 1),
				"가조시간": round(float(sun_hours), 1),
				"예측값": round(prediction_value, 3),
			}

			if not st.session_state.history or st.session_state.history[-1] != entry:
				st.session_state.history.append(entry)

		except Exception as e:
			st.error(f"예측 중 오류 발생: {e}")

	else:
		st.info("모델을 로드하면 슬라이더 조작 시 실시간 예측이 표시됩니다.")

	# 히스토리 표시
	if st.session_state.history:
		st.subheader("📋 예측 히스토리")
		import pandas as pd

		df = pd.DataFrame(st.session_state.history)
		# 인덱스 컬럼 제거하여 가로 스크롤 최소화
		st.dataframe(df.reset_index(drop=True), width='stretch')

		if st.button("히스토리 초기화"):
			st.session_state.history = []
			st.experimental_rerun()

	st.caption("모델은 Colab에서 생성된 `brix_model.joblib`입니다. 입력 전처리가 필요한 경우 모델에 맞게 값을 변환하세요.")

