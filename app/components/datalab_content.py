from nicegui import ui
from services.naver_api import naver_api
from datetime import datetime, timedelta

def content():
    keyword_groups = []
    
    def add_keyword_group():
        if len(keyword_groups) >= 5:
            ui.notify('최대 5개 그룹까지만 추가할 수 있습니다', type='warning')
            return
        
        with keyword_container:
            group_idx = len(keyword_groups)
            
            with ui.card().classes('w-full p-4 mb-3 bg-gray-50') as group_card:
                ui.label(f'키워드 그룹 {group_idx + 1}').classes('font-bold mb-2')
                
                group_name = ui.input('그룹 이름').classes('w-full mb-2').props('outlined dense')
                keywords_input = ui.input('키워드 (쉼표로 구분, 예: 한글,korean)').classes('w-full').props('outlined dense')
                
                keyword_groups.append({
                    'card': group_card,
                    'name': group_name,
                    'keywords': keywords_input
                })
    
    def remove_keyword_group():
        if len(keyword_groups) <= 1:
            ui.notify('최소 1개의 그룹이 필요합니다', type='warning')
            return
        
        group = keyword_groups.pop()
        group['card'].delete()
    
    async def handle_search():
        # 유효성 검사
        if not start_date.value or not end_date.value:
            ui.notify('시작/종료 날짜를 선택해주세요', type='warning')
            return
        
        # 키워드 그룹 구성
        groups = []
        for group in keyword_groups:
            name = group['name'].value.strip()
            keywords_str = group['keywords'].value.strip()
            
            if not name or not keywords_str:
                ui.notify('모든 그룹의 이름과 키워드를 입력해주세요', type='warning')
                return
            
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
            if not keywords:
                ui.notify('키워드를 입력해주세요', type='warning')
                return
            
            groups.append({
                'groupName': name,
                'keywords': keywords
            })
        
        # 로딩 표시
        results_container.clear()
        with results_container:
            ui.spinner(size='lg')
            ui.label('데이터 분석 중입니다...').classes('text-gray-500 mt-4')
        
        try:
            # 날짜 포맷 변환 (YYYY-MM-DD -> YYYY-MM-DD 그대로 유지)
            start = start_date.value
            end = end_date.value
            
            # 연령대 처리
            selected_ages = [age for age, checkbox in age_checkboxes.items() if checkbox.value]
            
            # API 호출
            data = await naver_api.search_datalab(
                start_date=start,
                end_date=end,
                time_unit=time_unit_select.value,
                keyword_groups=groups,
                device=device_select.value if device_select.value != 'all' else None,
                gender=gender_select.value if gender_select.value != 'all' else None,
                ages=selected_ages if selected_ages else None
            )
            
            # 결과 표시
            results_container.clear()
            with results_container:
                if not data.get('results'):
                    ui.label('분석 결과가 없습니다.').classes('text-orange-500')
                    return
                
                with ui.card().classes('w-full p-6'):
                    with ui.row().classes('items-center gap-2 mb-4'):
                        ui.icon('analytics', size='lg').classes('text-purple-600')
                        ui.label('트렌드 분석 결과').classes('text-2xl font-bold')
                    
                    colors = ['blue', 'green', 'red', 'orange', 'purple']
                    
                    for idx, result in enumerate(data['results']):
                        color = colors[idx % len(colors)]
                        
                        with ui.expansion(result['title'], icon='trending_up').classes('w-full mb-3') as expansion:
                            expansion.classes(f'bg-{color}-50')
                            
                            # 키워드 표시
                            with ui.row().classes('gap-2 mb-3'):
                                ui.label('키워드:').classes('font-semibold')
                                for keyword in result['keywords']:
                                    ui.badge(keyword).classes(f'bg-{color}-500 text-white')
                            
                            # 데이터 테이블
                            columns = [
                                {'name': 'period', 'label': '날짜', 'field': 'period', 'align': 'left'},
                                {'name': 'ratio', 'label': '검색 비율', 'field': 'ratio', 'align': 'left'}
                            ]
                            
                            rows = result['data']
                            
                            ui.table(columns=columns, rows=rows, row_key='period').classes('w-full')
                            
                            # 프로그레스 바로 시각화
                            ui.label('검색 추이').classes('font-semibold mt-4 mb-2')
                            for item in result['data'][:10]:  # 최근 10개만 표시
                                with ui.row().classes('w-full items-center gap-2 mb-1'):
                                    ui.label(item['period']).classes('text-xs text-gray-600 w-24')
                                    ui.linear_progress(item['ratio'] / 100).classes(f'flex-grow').props(f'color={color}')
                                    ui.label(str(item['ratio'])).classes('text-xs text-gray-700 w-12 text-right')
            
            ui.notify(f'분석 완료: {len(data["results"])}개 그룹', type='positive')
            
        except Exception as e:
            results_container.clear()
            with results_container:
                ui.label(f'분석 실패: {str(e)}').classes('text-red-500')
            ui.notify(f'분석 중 오류 발생: {str(e)}', type='negative')
    
    # UI 구성
    with ui.column().classes('w-full max-w-5xl mx-auto p-4'):
        # 헤더
        ui.label('Trendis 데이터랩 트렌드 분석').classes('text-3xl font-bold text-purple-700 text-center mb-2')
        ui.label('키워드별 검색량 추이를 시각화하여 트렌드를 분석하세요').classes('text-gray-500 text-center mb-8')
        
        # 검색 폼
        with ui.card().classes('w-full p-6 mb-4'):
            # 날짜 선택
            with ui.row().classes('w-full gap-4 mb-4'):
                with ui.column().classes('flex-1'):
                    ui.label('시작 날짜 (2016-01-01 이후)').classes('text-sm mb-1')
                    start_date = ui.date(value=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')).props('outlined')
                
                with ui.column().classes('flex-1'):
                    ui.label('종료 날짜').classes('text-sm mb-1')
                    end_date = ui.date(value=datetime.now().strftime('%Y-%m-%d')).props('outlined')
            
            # 옵션
            with ui.row().classes('w-full gap-4 mb-4'):
                with ui.column().classes('flex-1'):
                    ui.label('시간 단위').classes('text-sm mb-1')
                    time_unit_select = ui.select(
                        options={'date': '일간', 'week': '주간', 'month': '월간'},
                        value='month'
                    ).classes('w-full')
                
                with ui.column().classes('flex-1'):
                    ui.label('기기').classes('text-sm mb-1')
                    device_select = ui.select(
                        options={'all': '전체', 'pc': 'PC', 'mo': '모바일'},
                        value='all'
                    ).classes('w-full')
                
                with ui.column().classes('flex-1'):
                    ui.label('성별').classes('text-sm mb-1')
                    gender_select = ui.select(
                        options={'all': '전체', 'm': '남성', 'f': '여성'},
                        value='all'
                    ).classes('w-full')
            
            # 연령대 선택
            ui.label('연령대 (선택 안 함 = 전체)').classes('font-bold mb-2')
            age_checkboxes = {}
            age_options = {
                '1': '0~12세',
                '2': '13~18세',
                '3': '19~24세',
                '4': '25~29세',
                '5': '30~34세',
                '6': '35~39세',
                '7': '40~44세',
                '8': '45~49세',
                '9': '50~54세',
                '10': '55~59세',
                '11': '60세 이상'
            }
            
            with ui.grid(columns=3).classes('w-full gap-2 mb-4'):
                for age_code, age_label in age_options.items():
                    age_checkboxes[age_code] = ui.checkbox(age_label)
            
            # 키워드 그룹
            ui.label('키워드 그룹 (최대 5개)').classes('font-bold mb-2')
            keyword_container = ui.column().classes('w-full mb-4')
            
            # 버튼
            with ui.row().classes('gap-2 mb-4'):
                ui.button('키워드 그룹 추가', on_click=add_keyword_group).props('outline color=purple icon=add')
                ui.button('그룹 제거', on_click=remove_keyword_group).props('outline color=red icon=remove')
            
            ui.button('트렌드 분석 시작', on_click=handle_search).props('color=purple size=lg icon=analytics').classes('w-full')
        
        # 결과 영역
        results_container = ui.column().classes('w-full')
    
    # 초기 그룹 1개 추가
    add_keyword_group()
