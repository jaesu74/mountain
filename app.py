"""
예제 프로젝트: 산악지역 부동산 등기 및 중계 통합 플랫폼 백엔드 서비스
수정 내용:
  - Step 2: 로깅 시스템 도입 (Python logging 모듈 사용)
  - Step 3: 에러 핸들링 강화 (try-except, Flask errorhandler 적용)
  - Step 4: 보안 관련 추가 설정 (CORS, Rate Limiting)
  
필요한 패키지 설치:
  pip install flask requests python-dotenv flask-cors flask-limiter
"""

# 1. 라이브러리 및 환경 변수 로드
import os
from flask import Flask, request, jsonify
import requests
import logging
from dotenv import load_dotenv
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# 환경 변수 로드 (.env 파일에서 API 키 등 관리)
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # 환경 변수에 저장된 구글 API 키

# 2. Flask 애플리케이션 초기화
app = Flask(__name__)

# 4-1. CORS 설정: 프론트엔드와 백엔드가 다른 도메인/포트에 있을 경우를 대비
CORS(app)

# 4-2. Rate Limiting 설정: IP 당 일정 시간 내 요청 제한 (예: 10회/분)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# 2. 로깅 시스템 설정 (Step 2)
logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR)
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # 로그 파일에 기록
        logging.StreamHandler()            # 콘솔에도 출력
    ]
)

# 3-1. 구글 지도 API 호출 함수 (실제 API 호출 및 에러 핸들링 적용)
def get_map_info(latitude, longitude):
    """
    구글 지오코딩 API를 호출하여 위도/경도를 기반으로 주소 정보를 조회하고,
    Static Maps API를 통해 지도 이미지 URL을 생성하는 함수.
    """
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"latlng": f"{latitude},{longitude}", "key": GOOGLE_API_KEY}
    
    try:
        response = requests.get(geocode_url, params=params, timeout=5)
        geocode_data = response.json()
        logging.info("Google Geocoding API 호출 성공: %s", geocode_data)
    except Exception as e:
        logging.error("Google Geocoding API 호출 실패: %s", e)
        geocode_data = {"status": "ERROR"}
    
    if geocode_data.get("status") == "OK" and geocode_data.get("results"):
        result = geocode_data["results"][0]
        # address_components 또는 formatted_address 사용
        address = result.get("formatted_address", "주소 정보 없음")
        location_type = result.get("geometry", {}).get("location_type", "N/A")
    else:
        address = "주소 정보를 찾을 수 없음"
        location_type = ""
    
    map_image_url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"center={latitude},{longitude}&zoom=15&size=600x300&key={GOOGLE_API_KEY}"
    )
    
    return {
        "address": address,
        "formatted_address": address,
        "location_type": location_type,
        "map_image_url": map_image_url
    }

# 3-2. 한국 산림청 API 호출 함수 (모의 함수, 에러 핸들링 적용)
def get_forest_data(latitude, longitude):
    """
    산림청 또는 공공데이터 포털의 산림/산악 지역 데이터를 조회하는 함수.
    실제 API 연동 전까지 모의 데이터를 반환.
    """
    try:
        data = {
            "is_mountain_area": True,
            "region_name": "강원도 산림지역",
            "boundary_coordinates": [
                {"lat": latitude + 0.001, "lon": longitude + 0.001},
                {"lat": latitude + 0.002, "lon": longitude + 0.001},
                {"lat": latitude + 0.002, "lon": longitude + 0.002},
                {"lat": latitude + 0.001, "lon": longitude + 0.002}
            ]
        }
        logging.info("산림청 API 호출 성공: %s", data)
        return data
    except Exception as e:
        logging.error("산림청 API 호출 실패: %s", e)
        return {"is_mountain_area": False, "region_name": "", "boundary_coordinates": []}

# 3-3. 법원 등기소 API 호출 함수 (모의 함수, 에러 핸들링 적용)
def get_property_data(region_name):
    """
    법원 등기소 또는 민간 부동산 API를 통해 부동산 등기 및 소유자 정보를 조회하는 함수.
    실제 연동 전까지 모의 데이터를 반환.
    """
    try:
        data = {
            "owner": "홍길동",
            "registration_number": "1234-5678-9012",
            "management": None
        }
        logging.info("법원 등기소 API 호출 성공: %s", data)
        return data
    except Exception as e:
        logging.error("법원 등기소 API 호출 실패: %s", e)
        return {"owner": "", "registration_number": "", "management": None}

# 5. Flask API 엔드포인트 구현 (Rate Limiting 적용 및 에러 핸들링 강화)
@app.route('/api/getRegionInfo', methods=['GET'])
@limiter.limit("10 per minute")  # 각 IP 당 1분에 10회 요청 제한
def get_region_info():
    """
    위도와 경도를 GET 파라미터로 받아, 각 API 함수의 결과를 종합하여 JSON 응답을 반환.
    """
    try:
        # 요청 파라미터 추출 (Step 5-1)
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        if latitude is None or longitude is None:
            return jsonify({"error": "latitude와 longitude 파라미터가 필요합니다."}), 400
        
        # 각 API 호출 (Step 5-2 ~ 5-4)
        map_info = get_map_info(latitude, longitude)
        forest_data = get_forest_data(latitude, longitude)
        property_data = get_property_data(forest_data.get("region_name", ""))
        
        # 결과 종합 (Step 5-5)
        result = {
            "map_info": map_info,
            "forest_data": forest_data,
            "property_data": property_data
        }
        return jsonify(result)
    except Exception as e:
        logging.error("get_region_info 엔드포인트 에러: %s", e)
        return jsonify({"error": "서버 에러 발생"}), 500

# 3-4. 에러 핸들러: 서버 내부 에러 발생 시 처리 (Step 3)
@app.errorhandler(500)
def internal_error(error):
    logging.error("내부 서버 에러: %s", error)
    return jsonify({"error": "내부 서버 에러 발생"}), 500

# 6. Flask 애플리케이션 실행 (개발용)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
