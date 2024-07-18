import streamlit as st
import json
import os
from datetime import datetime
import time

# 사용자 데이터 파일 경로
USER_DATA_DIR = "user_data"

# 디렉토리가 없으면 생성
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)

# 사용자 데이터 파일 경로 생성 함수
def get_user_data_file(user_id):
    return os.path.join(USER_DATA_DIR, f"{user_id}_data.json")

# 사용자 데이터 로드 및 저장 함수
def load_user_data(user_id):
    user_data_file = get_user_data_file(user_id)
    try:
        if os.path.exists(user_data_file):
            with open(user_data_file, 'r') as file:
                user_data = json.load(file)
        else:
            user_data = None
    except (FileNotFoundError, json.decoder.JSONDecodeError, TypeError):
        user_data = None
    return user_data

def save_user_data(user_id, user_data):
    user_data_file = get_user_data_file(user_id)
    try:
        with open(user_data_file, 'w') as file:
            json.dump(user_data, file, indent=4, default=str)
    except Exception as e:
        st.error(f"데이터 저장 중 오류 발생: {str(e)}")

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'page' not in st.session_state:
    st.session_state.page = "홈페이지"

# 로그인 처리 함수
def login(user_id, password):
    user_data = load_user_data(user_id)
    if user_data and user_data.get('profile', {}).get('password') == password:
        st.session_state.logged_in = True
        st.session_state.user_id = user_id
        st.session_state.page = "목표 설정"
        st.success(f"{user_id}님, 환영합니다!")
        st.experimental_rerun()  # 로그인 후 페이지를 새로고침
    else:
        st.error("잘못된 사용자 ID 또는 비밀번호입니다.")

# 로그아웃 처리 함수
def logout():
    if st.session_state.logged_in:
        confirm_logout = st.button("로그아웃 하시겠습니까?")
        if confirm_logout:
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.page = "홈페이지"
            st.success("로그아웃되었습니다.")
            st.experimental_rerun()  # 로그아웃 후 페이지를 새로고침
    else:
        st.warning("로그인 상태가 아닙니다.")

# 회원가입 처리 함수
def register(user_id, password):
    user_data = load_user_data(user_id)
    if user_data is None:
        user_data = {'profile': {'password': password}, 'tasks': {}, 'completed_tasks': [], 'goal': None, 'points': 0}
        save_user_data(user_id, user_data)
        st.success(f"{user_id}님, 회원가입이 완료되었습니다. 이제 로그인하세요.")
    else:
        st.error("이미 존재하는 사용자 ID입니다.")

# 목표 설정 함수
def set_goal(user_id, goal_text):
    user_data = load_user_data(user_id)
    if user_data:
        user_data['goal'] = goal_text
        save_user_data(user_id, user_data)
        st.success(f"목표를 설정했습니다: {goal_text}")
        st.session_state.goal_set = True
        time.sleep(2)
        st.experimental_rerun()  # 목표 설정 후 페이지를 새로고침

# 임무 추가 함수
def add_task(user_id, task_name, hardcore):
    user_data = load_user_data(user_id)
    if user_data and task_name not in user_data['tasks']:
        user_data['tasks'][task_name] = {'completed': False, 'hardcore': hardcore}
        save_user_data(user_id, user_data)
        st.success(f"{task_name} 임무가 추가되었습니다.")
    else:
        st.warning(f"{task_name} 이미 추가된 임무입니다.")

# 임무 완료 처리 함수
def complete_task(user_id, task_name):
    user_data = load_user_data(user_id)
    if user_data and task_name in user_data['tasks']:
        if not user_data['tasks'][task_name]['completed']:
            user_data['tasks'][task_name]['completed'] = True
            completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_data['completed_tasks'].append({'name': task_name, 'time': completion_time})
            if user_data['tasks'][task_name].get('hardcore', False):
                points = 5
            else:
                points = 3  # 수정된 포인트
            user_data['points'] += points  # 기존 포인트에 추가
            save_user_data(user_id, user_data)
            st.success(f"{task_name} 임무를 완료했습니다! (+{points} 포인트)")
            st.experimental_rerun()  # 완료 후 페이지를 새로고침
        else:
            st.warning("이미 완료된 임무입니다.")
    else:
        st.error(f"{task_name} 임무를 찾을 수 없습니다.")

# 목표 달성 게이지 계산 함수
def calculate_progress(user_id):
    user_data = load_user_data(user_id)
    if user_data:
        total_completed_tasks = sum(
            5 if user_data['tasks'][task].get('hardcore', False) and user_data['tasks'][task]['completed'] else 3
            if user_data['tasks'][task]['completed'] else 0
            for task in user_data['tasks']
        )
        return min(total_completed_tasks / 50, 1.0)
    return 0

# 목표 달성 여부 체크 함수
def check_goal_completion(user_id):
    if st.session_state.get('logged_in', False):
        progress_percent = calculate_progress(user_id) * 100
        if progress_percent >= 100:
            st.balloons()
            st.success("축하합니다! 모든 목표를 달성하셨습니다!")
            st.markdown("---")  # 이펙트를 구분하기 위한 줄 추가
            st.session_state.goal_completed = True
    else:
        st.error("로그인이 필요합니다.")

# 임시 목표 설정 확인 함수
def show_temporary_goal_set(user_id):
    if not st.session_state.get('goal_set', False):
        st.session_state.goal_set = False
    if not st.session_state.get('goal_completed', False):
        st.session_state.goal_completed = False

    user_data = load_user_data(user_id)
    if user_data:
        current_goal = user_data.get('goal', None)

        if not st.session_state.goal_set and not st.session_state.goal_completed:
            if current_goal:
                st.markdown(f"<h2>현재 설정된 목표:</h2> <h1>{current_goal}</h1>", unsafe_allow_html=True)
                progress = calculate_progress(user_id)
                st.progress(progress)
                check_goal_completion(user_id)
            else:
                show_set_goal_form(user_id)
        else:
            show_set_goal_form(user_id)

# 목표 설정 폼 표시 함수
def show_set_goal_form(user_id):
    st.title("목표 설정")
    
    # 사용자 데이터 로드
    user_data = load_user_data(user_id)
    if user_data:
        current_goal = user_data.get('goal', None)
        current_points = user_data.get('points', 0)
        
        # 목표 표시
        st.markdown(f"<h1>{current_goal or '목표가 없습니다.'}</h1>", unsafe_allow_html=True)
        
        # 목표 포인트 게이지 표시
        st.markdown(f"현재 목표 포인트: **{current_points}**")
        st.progress(current_points / 50)  # 최대 포인트가 50일 때의 게이지
        
        if not current_goal:
            new_goal = st.text_input("새로운 목표를 입력하세요:")
            set_goal_button_key = "set_goal_button"  # 목표 설정 버튼에 고유한 키 부여
            if st.button("목표 설정하기", key=set_goal_button_key):
                set_goal(user_id, new_goal)

# 완료된 임무 페이지 표시 함수
def show_completed_tasks_page(user_id):
    st.title("완료된 임무")
    user_data = load_user_data(user_id)
    
    if user_data:
        completed_tasks = user_data['completed_tasks']
        if completed_tasks:
            for task in completed_tasks:
                task_name = task['name']
                completion_time = task['time']
                if user_data['tasks'][task_name].get('hardcore', False):
                    st.markdown(f"<span style='color:red;'>**{task_name}** (Hardcore) - 완료 시간: {completion_time}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{task_name}** - 완료 시간: {completion_time}")
        else:
            st.info("아직 완료된 임무가 없습니다.")
    else:
        st.error("사용자 데이터를 찾을 수 없습니다.")

# 임무 추가 페이지 표시 함수
def show_add_task_page(user_id):
    st.title("임무 추가")
    task_name = st.text_input("임무 이름:")
    hardcore = st.checkbox("하드코어 모드 (포인트 5점)")
    add_task_button_key = "add_task_button"  # 임무 추가 버튼에 고유한 키 부여
    if st.button("임무 추가", key=add_task_button_key):
        add_task(user_id, task_name, hardcore)
        st.experimental_rerun()  # 임무 추가 후 페이지를 새로고침

# 임무 현황 페이지 표시 함수
def show_task_status_page(user_id):
    st.title("임무 현황")
    user_data = load_user_data(user_id)
    if user_data:
        tasks_to_show = [task for task in user_data['tasks'] if not user_data['tasks'][task]['completed']]

        for task in tasks_to_show:
            col1, col2 = st.columns([4, 1])
            with col1:
                if user_data['tasks'][task].get('hardcore', False):
                    st.markdown(f"<span style='color:red;'>**{task}** (Hardcore)</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{task}**", unsafe_allow_html=True)
            with col2:
                complete_button_key = f"complete_button_{task}"  # 임무 완료 버튼에 고유한 키 부여
                if st.button("완료", key=complete_button_key):
                    complete_task(user_id, task)
                    st.experimental_rerun()  # 임무 완료 후 페이지를 새로고침

# 초기화 기능 구현 함수
def reset_user_data(user_id):
    st.title("초기화")
    confirm_reset = st.button("초기화")
    if confirm_reset:
        user_data_file = get_user_data_file(user_id)
        try:
            if os.path.exists(user_data_file):
                # 사용자 데이터 파일을 읽어옴
                with open(user_data_file, 'r') as file:
                    user_data = json.load(file)
                
                # 목표와 목표 포인트 초기화
                if user_data.get('goal'):
                    user_data['goal'] = None
                user_data['points'] = 0
                
                # 완료된 임무 초기화
                user_data['completed_tasks'] = []
                
                # 사용자 데이터 파일 다시 저장
                with open(user_data_file, 'w') as file:
                    json.dump(user_data, file, indent=4, default=str)
                
                st.success("목표, 목표 포인트 및 완료된 임무가 초기화되었습니다.")
                time.sleep(5)  # 5초 동안 메시지 표시
                st.experimental_rerun()  # 페이지 새로고침
            else:
                st.warning("초기화할 데이터가 없습니다.")
        except Exception as e:
            st.error(f"초기화 중 오류가 발생했습니다: {str(e)}")

# 규칙 페이지 표시 함수
def show_rules_page():
    st.title("규칙 (How to do)")
    rules = """
    1. 이 사이트는 여러 분들의 목표를 달성시켜주기 위한 페이지입니다. 목표를 설정하고 임무를 지정하세요! 목표 포인트는 50점을 이루면 게이지가 달성되고 일반 임무는 완료 시 목표 포인트 3점, 하드코어 임무는 완료 시 목표 포인트 5점을 획득합니다!
    2. 임무는 임무 추가 페이지에서 추가 가능하고 임무 현황 페이지에서 임무 확인 및 임무 완료를 할 수 있습니다. 완료된 페이지는 안봐도 아시죠^^~?
    3. 초기화 버튼을 누르면 목표와 목표포인트, 그리고 임무들이 다 초기화 됩니다. 신중히 선택하세요!
    """
    st.markdown(rules)

# 홈페이지 표시 함수
def show_home_page():
    st.title("홈페이지")
    if st.session_state.logged_in:
        st.warning("이미 로그인 상태입니다.")
    else:
        if st.button("로그인"):
            st.session_state.page = "로그인"
        if st.button("회원가입"):
            st.session_state.page = "회원가입"

# 로그인 페이지 표시 함수
def show_login_page():
    st.title("로그인")
    user_id = st.text_input("사용자 ID 입력:")
    password = st.text_input("비밀번호 입력:", type='password')

    login_button_key = "login_button"  # 로그인 버튼에 고유한 키 부여
    if st.button("로그인", key=login_button_key):
        login(user_id, password)

# 회원가입 페이지 표시 함수
def show_register_page():
    st.title("회원가입")
    new_user_id = st.text_input("새로운 사용자 ID 입력:")
    new_password = st.text_input("새로운 비밀번호 입력:", type='password')

    register_button_key = "register_button"  # 회원가입 버튼에 고유한 키 부여
    if st.button("회원가입", key=register_button_key):
        register(new_user_id, new_password)

# 메인 함수
def main():
    st.sidebar.title("메뉴")
    menu = ["목표 설정", "임무 추가", "임무 현황", "완료된 임무", "규칙 (How to do)", "초기화", "로그아웃"]
    choice = st.sidebar.radio("메뉴", menu)

    if choice == "목표 설정":
        if st.session_state.logged_in:
            show_temporary_goal_set(st.session_state.user_id)
        else:
            st.error("로그인이 필요합니다.")
    elif choice == "임무 추가":
        if st.session_state.logged_in:
            show_add_task_page(st.session_state.user_id)
        else:
            st.error("로그인이 필요합니다.")
    elif choice == "임무 현황":
        if st.session_state.logged_in:
            show_task_status_page(st.session_state.user_id)
        else:
            st.error("로그인이 필요합니다.")
    elif choice == "완료된 임무":
        if st.session_state.logged_in:
            show_completed_tasks_page(st.session_state.user_id)
        else:
            st.error("로그인이 필요합니다.")
    elif choice == "초기화":
        if st.session_state.logged_in:
            reset_user_data(st.session_state.user_id)
        else:
            st.warning("로그인 상태가 아닙니다.")
    elif choice == "로그아웃":
        if st.session_state.logged_in:
            logout()
        else:
            st.warning("로그인 상태가 아닙니다.")
    elif choice == "규칙 (How to do)":
        show_rules_page()
    
    st.sidebar.markdown("---")
    if not st.session_state.logged_in:
        if st.button("로그인"):
            st.session_state.page = "로그인"
        if st.button("회원가입"):
            st.session_state.page = "회원가입"

    if st.session_state.page == "로그인":
        show_login_page()
    elif st.session_state.page == "회원가입":
        show_register_page()

if __name__ == "__main__":
    main()
