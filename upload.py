from ftplib import FTP
import os

# FTP 서버 정보 (인피니티프리에서 제공하는 FTP 정보 사용)
FTP_SERVER = "ftp.yourdomain.com"  # 예: InfinityFree FTP 서버 주소
FTP_USER = "your_ftp_username"
FTP_PASS = "your_ftp_password"

# 업로드할 로컬 디렉터리와 원격 디렉터리 설정 (보통 htdocs 폴더)
LOCAL_DIR = r"C:\path\to\your\website_files"
REMOTE_DIR = "htdocs"  # 인피니티프리에서 웹사이트 파일이 위치할 디렉터리

def upload_files(ftp, local_dir, remote_dir):
    # 원격 디렉터리로 이동
    ftp.cwd(remote_dir)
    
    # 로컬 디렉터리의 모든 파일을 업로드
    for filename in os.listdir(local_dir):
        local_path = os.path.join(local_dir, filename)
        if os.path.isfile(local_path):
            with open(local_path, 'rb') as f:
                print(f"Uploading {filename}...")
                ftp.storbinary(f"STOR {filename}", f)
        # 폴더인 경우, 재귀적으로 업로드 가능 (필요 시 추가 구현)
            
def main():
    # FTP 서버 연결 및 로그인
    ftp = FTP(FTP_SERVER)
    ftp.login(FTP_USER, FTP_PASS)
    print("Connected to FTP server.")
    
    # 파일 업로드 실행
    upload_files(ftp, LOCAL_DIR, REMOTE_DIR)
    
    # 연결 종료
    ftp.quit()
    print("Upload complete and connection closed.")

if __name__ == '__main__':
    main()
