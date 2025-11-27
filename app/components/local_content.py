from nicegui import ui
from services.naver_api import naver_api
import re

def content():
    def clean_html(text: str) -> str:
        """HTML 태그 제거"""
        return re.sub(r'</?b>|&gt;', lambda m: ' > ' if m.group() == '&gt;' else '', text)
    
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
            data = await naver_api.search_local(
                query=query,
                display=int(display_select.value),
                sort=sort_select.value
            )
            
            # 결과 표시
            results_container.clear()
            with results_container:
                if not data.get('items'):
                    ui.label(f"'{query}' 검색 결과가 없습니다.").classes('text-orange-500')
                    return
                
                # 결과 헤더
                with ui.row().classes('w-full items-center justify-between mb-4'):
                    ui.label(f"'{query}' 검색 결과").classes('text-xl font-bold text-green-700')
                    ui.badge(f"{data.get('total', 0):,}개").classes('bg-green-500 text-white')
                
                # 검색 결과 카드
                for idx, item in enumerate(data['items'], 1):
                    with ui.card().classes('w-full mb-3 hover:shadow-lg transition-shadow'):
                        with ui.row().classes('w-full items-start justify-between gap-4'):
                            with ui.column().classes('flex-grow'):
                                # 제목과 카테고리
                                with ui.row().classes('items-center gap-2 mb-1'):
                                    title = clean_html(item['title'])
                                    if item.get('link'):
                                        ui.link(title, item['link'], new_tab=True).classes('text-lg font-semibold text-gray-800 hover:text-green-600')
                                    else:
                                        ui.label(title).classes('text-lg font-semibold text-gray-800')
                                    
                                    ui.badge(str(idx)).classes('bg-gray-300 text-gray-800')
                                
                                # 카테고리
                                category = item['category'].replace('&gt;', ' > ')
                                with ui.row().classes('items-center gap-1 mb-2'):
                                    ui.icon('sell', size='sm').classes('text-green-600')
                                    ui.label(category).classes('text-sm text-gray-600')
                                
                                # 설명
                                if item.get('description'):
                                    ui.label(item['description']).classes('text-sm text-gray-600 mb-2')
                                
                                # 주소
                                address = item.get('roadAddress') or item.get('address', '')
                                if address:
                                    with ui.row().classes('items-center gap-1 mb-1'):
                                        ui.icon('location_on', size='sm').classes('text-red-500')
                                        ui.label(address).classes('text-sm text-gray-700')
                                
                                # 전화번호
                                if item.get('telephone'):
                                    with ui.row().classes('items-center gap-1 mb-2'):
                                        ui.icon('phone', size='sm').classes('text-blue-500')
                                        ui.link(item['telephone'], f"tel:{item['telephone']}").classes('text-sm text-blue-600 hover:underline')
                                
                                # 지도 보기 버튼
                                if item.get('mapx') and item.get('mapy'):
                                    map_url = f"https://map.naver.com/v5/search/{title}?c={item['mapx']},{item['mapy']},15,0,0,0,dh"
                                    ui.button('지도 보기', on_click=lambda url=map_url: ui.open(url, new_tab=True)) \
                                        .props('outline color=green size=sm icon=map')
            
            ui.notify(f'검색 완료: {len(data["items"])}건', type='positive')
            
        except Exception as e:
            results_container.clear()
            with results_container:
                ui.label(f'검색 실패: {str(e)}').classes('text-red-500')
            ui.notify(f'검색 중 오류 발생: {str(e)}', type='negative')
    
    # UI 구성
    with ui.column().classes('w-full max-w-4xl mx-auto p-4'):
        # 헤더
        ui.label('Trendis 지역 트렌드 검색').classes('text-3xl font-bold text-green-700 text-center mb-2')
        ui.label('지역별 업체 및 장소의 인기 트렌드를 분석하세요').classes('text-gray-500 text-center mb-8')
        
        # 검색 폼
        with ui.card().classes('w-full p-6 mb-4'):
            with ui.row().classes('w-full gap-2 mb-4'):
                search_input = ui.input(
                    placeholder='지역 검색어를 입력하세요 (예: 강남 맛집, 홍대 카페)'
                ).classes('flex-grow').props('outlined')
                
                ui.button('검색', on_click=handle_search).props('color=green size=lg')
            
            # 옵션
            with ui.row().classes('w-full gap-4'):
                with ui.column().classes('flex-1'):
                    ui.label('결과 수(최대 5건)').classes('text-sm')
                    display_select = ui.select(
                        options=[5, 4, 3],
                        value=5
                    ).classes('w-full')
                
                with ui.column().classes('flex-1'):
                    ui.label('정렬 기준').classes('text-sm')
                    sort_select = ui.select(
                        options={'random': '정확도순', 'comment': '리뷰 많은순'},
                        value='random'
                    ).classes('w-full')
        
        # 검색 결과 영역
        results_container = ui.column().classes('w-full')
        with results_container:
            ui.label('지역 검색어를 입력하여 업체 및 장소의 트렌드를 확인해보세요.').classes('text-gray-500 text-center p-4')
