import streamlit as st
from datetime import date
from planner_agent import run_planner

# 페이지 설정
st.set_page_config(page_title="AI 멀티 학습 플래너", page_icon="📚", layout="wide")

st.title("📚 AI 멀티 과목 스마트 학습 플래너")
st.caption("여러 과목을 동시에 입력하고, 하루 공부 시간을 효율적으로 배분하는 맞춤형 플래너입니다.")

# 세션 상태 초기화 (결과 저장용)
if "planner_result" not in st.session_state:
    st.session_state.planner_result = None

# 사이드바 - 학습 기본 정보 설정
st.sidebar.header("🛠️ 나의 학습 정보 설정")

# 1. 여러 과목 동시 관리 기능 UI
st.sidebar.subheader("🎯 학습 과목 추가")
if "subjects_list" not in st.session_state:
    st.session_state.subjects_list = ["정보처리기사", "영어 회화"]

# 새로운 과목을 입력받아 리스트에 추가하는 UI
new_sub = st.sidebar.text_input("➕ 새 과목 입력:", placeholder="예: 파이썬, 수학, SQL 등")
if st.sidebar.button("과목 추가"):
    if new_sub.strip() and new_sub not in st.session_state.subjects_list:
        st.session_state.subjects_list.append(new_sub.strip())
        st.rerun()

# 등록된 과목 리스트 보여주기 및 삭제 기능
st.sidebar.write("**현재 등록된 과목 목록:**")
subjects_to_remove = []
for sub in st.session_state.subjects_list:
    col1, col2 = st.sidebar.columns([4, 1])
    col1.write(f"- {sub}")
    if col2.button("❌", key=f"del_{sub}"):
        subjects_to_remove.append(sub)

if subjects_to_remove:
    for sub in subjects_to_remove:
        st.session_state.subjects_list.remove(sub)
    st.rerun()

st.sidebar.markdown("---")

# 시험 날짜 및 총 공부 가능 시간
exam_date = st.sidebar.date_input("📅 최종 시험/목표 날짜", min_value=date.today(), value=date(2026, 12, 31))
study_hours = st.sidebar.slider("⏳ 총 하루 공부 시간 (시간)", min_value=0.5, max_value=16.0, value=4.0, step=0.5)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "💡 **사용 팁:**\n"
    "- 과목을 여러 개 추가하면 AI가 전체 공부 시간 내에서 과목별 중요도나 학습량에 따라 시간을 배분해 줍니다.\n"
    "- '수학에 70%, 영어에 30% 비중을 줘서 계획 짜줘'처럼 요청 사항에 구체적인 비율을 적으셔도 좋습니다."
)

# 메인 화면 - 유저 프롬프트 입력
st.subheader("🤖 무엇을 도와드릴까요?")
joined_subjects = ", ".join(st.session_state.subjects_list)
st.info(f"📋 선택된 과목: **{joined_subjects if joined_subjects else '선택된 과목 없음'}**")

user_input = st.text_area(
    "요청 사항을 입력하세요:", 
    placeholder="예) 직장인이라 주중에는 가볍게 개념 위주로, 주말에 집중해서 공부할 수 있는 과목별 시간 분배 및 4주 완성 계획표 짜줘."
)

if st.button("🚀 에이전트 가동하기", use_container_width=True):
    if not st.session_state.subjects_list:
        st.error("최소 한 개 이상의 과목을 등록해 주세요!")
    elif not user_input.strip():
        st.warning("요청 사항을 입력해주세요!")
    else:
        with st.spinner("AI 에이전트들이 과목별 밸런스를 맞춰 계획을 짜고 있습니다..."):
            try:
                # planner_agent.py의 run_planner 호출
                result = run_planner(
                    user_input=user_input,
                    subject=joined_subjects,
                    exam_date=exam_date.strftime("%Y-%m-%d"),
                    study_hours=study_hours
                )
                st.session_state.planner_result = result
                st.success("🤖 플래너 구성 완료!")
            except Exception as e:
                st.error(f"실행 중 오류가 발생했습니다: {e}")

# 결과 출력 및 다운로드 기능
if st.session_state.planner_result:
    st.markdown("---")
    
    # 2. 다운로드 버튼 구현 (결과가 있을 때만 활성화)
    st.download_button(
        label="📥 생성된 학습 계획을 TXT 파일로 다운로드",
        data=st.session_state.planner_result,
        file_name=f"AI_Study_Plan_{date.today().strftime('%Y%m%d')}.txt",
        mime="text/plain",
        use_container_width=True
    )
    
    st.markdown(st.session_state.planner_result)
