import httpx
import os
from typing import Dict, List, Optional
import logging
from pathlib import Path
from dotenv import load_dotenv

# 상위 디렉토리의 .env 파일 로드
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

class NaverAPIService:
    def __init__(self):
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        self.base_headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
    
    async def search_blog(
        self, 
        query: str, 
        display: int = 20, 
        sort: str = 'sim'
    ) -> Dict:
        """블로그 검색
        
        Args:
            query: 검색어
            display: 결과 수 (1-100)
            sort: 정렬 방식 ('sim' 또는 'date')
        
        Returns:
            검색 결과 딕셔너리
        """
        url = 'https://openapi.naver.com/v1/search/blog'
        params = {
            'query': query,
            'display': display,
            'sort': sort
        }
        
        logger.info(f"블로그 검색 시작 - 검색어: '{query}'")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, 
                    headers=self.base_headers, 
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"✅ 블로그 검색 성공 | 검색어: '{query}' | 결과: {len(data.get('items', []))}건")
                return data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 블로그 API 오류 | 상태: {e.response.status_code} | {e}")
            raise Exception(f"검색 실패: {e.response.status_code}")
        except Exception as e:
            logger.error(f"❌ 블로그 검색 오류 | {str(e)}")
            raise
    
    async def search_local(
        self,
        query: str,
        display: int = 5,
        sort: str = 'random'
    ) -> Dict:
        """지역 검색
        
        Args:
            query: 검색어
            display: 결과 수 (1-5)
            sort: 정렬 방식 ('random' 또는 'comment')
        
        Returns:
            검색 결과 딕셔너리
        """
        url = 'https://openapi.naver.com/v1/search/local.json'
        params = {
            'query': query,
            'display': display,
            'sort': sort
        }
        
        logger.info(f"지역 검색 시작 - 검색어: '{query}'")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.base_headers,
                    params=params
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"✅ 지역 검색 성공 | 검색어: '{query}' | 결과: {len(data.get('items', []))}건")
                return data
                
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 지역 API 오류 | 상태: {e.response.status_code}")
            raise Exception(f"검색 실패: {e.response.status_code}")
        except Exception as e:
            logger.error(f"❌ 지역 검색 오류 | {str(e)}")
            raise
    
    async def search_datalab(
        self,
        start_date: str,
        end_date: str,
        time_unit: str,
        keyword_groups: List[Dict],
        device: Optional[str] = None,
        gender: Optional[str] = None,
        ages: Optional[List[str]] = None
    ) -> Dict:
        """데이터랩 트렌드 검색"""
        url = 'https://openapi.naver.com/v1/datalab/search'
        
        # 날짜 포맷 변환 (YYYY-MM-DD -> YYYY-MM-DD 유지)
        request_body = {
            'startDate': start_date,
            'endDate': end_date,
            'timeUnit': time_unit,
            'keywordGroups': keyword_groups
        }
        
        # 선택적 파라미터 추가
        if device:
            request_body['device'] = device
        if gender:
            request_body['gender'] = gender
        if ages:
            request_body['ages'] = ages
        
        logger.info(f"데이터랩 분석 | 그룹: {len(keyword_groups)}, 연령: {ages}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={
                        **self.base_headers,
                        'Content-Type': 'application/json'
                    },
                    json=request_body
                )
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"✅ 데이터랩 성공 | 결과: {len(data.get('results', []))}개")
                return data
                
        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.text else {}
            error_msg = error_data.get('errorMessage', str(e))
            logger.error(f"❌ 데이터랩 오류 | {e.response.status_code} | {error_msg}")
            raise Exception(f"분석 실패: {error_msg}")
        except Exception as e:
            logger.error(f"❌ 데이터랩 오류 | {str(e)}")
            raise

# 싱글톤 인스턴스
naver_api = NaverAPIService()
