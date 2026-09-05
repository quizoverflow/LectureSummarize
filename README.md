# Lecture Summarizer (강의 영상 자동 정리 프로그램)

강의 영상을 분석하여 **교수님의 필기가 완료된 슬라이드 캡처 화면**과 **해당 구간의 음성을 한글 자막**으로 변환하여, 한눈에 보기 편한 **PDF 요약본**으로 자동 생성해 주는 파이썬 프로그램

추후 생성형 AI 모델과 연동하여 핵심만 추출하는 기능도 추가 예정 

---

## 📌 주요 기능

- **슬라이드 전환 자동 감지**: Structural Similarity Index (SSIM) 알고리즘을 사용하여 단순 필기와 실제 슬라이드 전환을 구별
- **필기 완벽 캡처**: 슬라이드가 넘어가기 직전, 교수님의 필기가 모두 반영된 상태의 화면을 고화질로 저장
- **음성 자막 자동 추출**: faster-whisper 모델을 활용하여 각 슬라이드 구간에 해당하는 강의 음성을 한글 자막 변환
- **PDF 문서 자동 생성**: PyMuPDF를 활용해 슬라이드 이미지와 한글 자막이 한 페이지씩 담기게 생성
---

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
