
### 외장 그래픽 카드 사용시 그래픽카드 모드 사용 권장
엔비디아 그래픽카드만 글카모드 사용가능
cpu 모드 0번 사용시 30분 강의 기준 약 200초 내외 소요 (컴퓨터 환경에 상이)


### 필요 패키지

pip install opencv-python

pip install numpy

pip install scikit-image

pip install faster-whisper

pip install pymupdf

### 기타
최초 실행시 아래와 같은 경고문구가 뜰 수 있지만 이는 Whisper 모델을 다운 받는 과정에서 뜨는 메세지입니다
[small] Whisper 모델을 불러오는 중... (Device: cpu)
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
UserWarning: `huggingface_hub` cache-system uses symlinks by default to efficiently store duplicated files but your machine does not support them in ~~

약 600MB 크기입니다.
