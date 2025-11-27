from nicegui import ui
from services.naver_api import naver_api
import re

def content():
    search_results = []
    
    def clean_html(text: str) -> str:
        """HTML 태그 제거"""
        return re.sub(r'</?b>', '', text)
    
    def format_date(date_str: str) -> str:
        """날짜 포맷 (20250919 -> 2025-09-19)"""
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    
    async def handle_search():
        query = search_input.value.strip()
        if not query:
            ui.notify('검색어를 입력해주세요', type='warning')
            return
        
        # 로딩 표시
        results_container.clear()
        with results_container:
            ui.spinner(size='lg')
            ui.label('검색 중입니다...').classes('text-gray-500 mt-4')
        
        try:
            # API 호출
            data = await naver_api.search_blog(
                query=query,
                display=int(display_select.value),
                sort=sort_select.value
            )
            
            # 결과 표시
            results_container.clear()
            with results_container:
                if not data.get('items'):
                    ui.label(f"'{query}' 검색 결과가 없습니다.").classes('text-warning')
                    return
                
                # 결과 헤더
                with ui.row().classes('w-full items-center justify-between mb-4'):
                    ui.label(f"'{query}' 검색 결과").classes('text-xl font-bold')
                    ui.badge(f"{data.get('total', 0):,}개").classes('bg-gray-500')
                
                # 검색 결과 카드
                for idx, item in enumerate(data['items'], 1):
                    with ui.card().classes('w-full mb-3 hover:shadow-lg transition-shadow'):
                        with ui.row().classes('w-full items-start justify-between'):
                            with ui.column().classes('flex-grow'):
                                # 제목
                                title = clean_html(item['title'])
                                ui.link(title, item['link'], new_tab=True).classes('text-lg font-semibold text-gray-800 hover:text-blue-600')
                                
                                # 설명
                                description = clean_html(item['description'])
                                ui.label(description).classes('text-sm text-gray-600 mt-2')
                                
                                # 메타 정보
                                with ui.row().classes('mt-2 gap-4'):
                                    ui.label(f"👤 {item['bloggername']}").classes('text-xs text-gray-500')
                                    ui.label(f"📅 {format_date(item['postdate'])}").classes('text-xs text-gray-500')
                            
                            # 순번 배지
                            # ui.badge(str(idx)).classes('bg-gray-200 text-white-700')
                            ui.badge(str(idx)).classes('bg-blue-100 text-blue-50')

            ui.notify(f'검색 완료: {len(data["items"])}건', type='positive')
            
        except Exception as e:
            results_container.clear()
            with results_container:
                ui.label(f'검색 실패: {str(e)}').classes('text-red-500')
            ui.notify(f'검색 중 오류 발생: {str(e)}', type='negative')
    
    # UI 구성
    with ui.column().classes('w-full max-w-4xl mx-auto p-4'):
        # 헤더
        ui.label('Trendis 블로그 트렌드 검색').classes('text-3xl font-bold text-center mb-2')
        ui.label('네이버 블로그의 최신 트렌드를 분석하세요').classes('text-gray-500 text-center mb-8')
        
        # 검색 폼
        with ui.card().classes('w-full p-6 mb-4'):
            with ui.row().classes('w-full gap-2 mb-4'):
                search_input = ui.input(
                    placeholder='검색어를 입력하세요 (예: 인공지능, K-POP)'
                ).classes('flex-grow').props('outlined')
                
                ui.button('검색', on_click=handle_search).props('color=primary size=lg')
            
            # 옵션
            with ui.row().classes('w-full gap-4'):
                with ui.column().classes('flex-1'):
                    ui.label('결과 수').classes('text-sm')
                    display_select = ui.select(
                        options=[10, 20, 50, 100],
                        value=20
                    ).classes('w-full')
                
                with ui.column().classes('flex-1'):
                    ui.label('정렬 기준').classes('text-sm')
                    sort_select = ui.select(
                        options={'sim': '정확도순', 'date': '최신순'},
                        value='sim'
                    ).classes('w-full')
        
        # 검색 결과 영역
        results_container = ui.column().classes('w-full')
        with results_container:
            ui.label('검색어를 입력하여 네이버 블로그의 최신 트렌드를 분석해보세요.').classes('text-gray-500 text-center p-4')
