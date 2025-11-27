
***

# NiceGUI 컴포넌트 기반 보일러플레이트 (로그인 및 사용자 관리 포함)

컴포넌트 기반 최신 NiceGUI 애플리케이션 보일러플레이트로, 인증, 사용자 관리, 반응형 사이드바, 모듈러 구조를 갖췄습니다. 빠른 의존성 관리를 위해 `uv` 패키지 매니저를 사용하고, OAuth 통합과 로컬 데이터베이스 지원, 포괄적인 서비스 계층을 포함합니다.

***

## 🛠️ 설치 및 실행

### 필수 조건
- Python 3.11 이상
- [UV 패키지 매니저](https://github.com/astral-sh/uv)

### 빠른 시작

1. **레포지토리 복제**
   ```bash
   git clone <your-repo-url>
   cd nicegui-base-main
   ```

2. **UV로 의존성 설치**
   ```bash
   uv sync
   ```

3. **애플리케이션 구성**
   
   첫 실행 시 기본 `config.json` 파일이 생성되며, 다음과 같이 업데이트하세요:
   
   ```json
   {
     "appName": "Your App Name",
     "appVersion": "1.0.0",
     "appPort": 3000,
     "google_oauth": {
       "client_id": "your-google-client-id",
       "client_secret": "your-google-client-secret",
       "redirect_uri": "http://localhost:3000/auth"
     }
   }
   ```

4. **애플리케이션 실행**
   ```bash
   # 인증 활성화 (추천)
   uv run python main.py
   ```

5. **기본 관리자 계정**
   - 사용자명: `admin`
   - 비밀번호: `admin`
   - ⚠️ 최초 로그인 후 반드시 기본 관리자 비밀번호를 변경하세요!

***

## 🔐 Google OAuth 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속  
   - 새 프로젝트 생성 또는 기존 프로젝트 선택

2. Google+ API 활성화  
   - "APIs & Services" > "Library"에서 "Google+ API" 검색 및 활성화

3. OAuth 2.0 클라이언트 ID 생성  
   - "Credentials" > "Create Credentials" > "OAuth 2.0 Client IDs" 선택  
   - "Web application" 유형 선택  
   - 승인된 리디렉션 URI 추가:  
     - `http://localhost:3000/auth` (개발용)  
     - `https://yourdomain.com/auth` (배포용)

4. `config.json`에 클라이언트 ID, 시크릿 및 리디렉션 URI 설정  
   ```json
   {
     "google_oauth": {
       "client_id": "your-actual-client-id.googleusercontent.com",
       "client_secret": "your-actual-client-secret",
       "redirect_uri": "http://localhost:3000/auth"
     }
   }
   ```

***

## 🧑‍💻 네이버 API 활용 데이터 분석 (예시 3개)

트렌드 검색 컴포넌트 UI

블로그 트렌드 검색: 네이버 블로그의 최신 트렌드를 분석하는 카드
지역 트렌드 검색: 지역별 업체 및 장소를 분석하는 카드
데이터랩 트렌드: 키워드별 검색량 추이를 분석하는 카드

각 카드는 반응형이며 클릭 시 관련 페이지로 이동합니다.


이들은 각기 Python HTTP 클라이언트 라이브러리를 활용합니다.

***
