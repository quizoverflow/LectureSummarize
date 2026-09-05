import cv2
import os
import numpy as np
from skimage.metrics import structural_similarity as ssim

class VideoAnalyzer:
    def __init__(self, video_path: str, output_dir: str = "output/slides"):
        """
        비디오 분석기 초기화
        :param video_path: 분석할 mp4 영상 경로
        :param output_dir: 추출된 슬라이드 이미지를 저장할 경로
        """
        self.video_path = video_path
        self.output_dir = output_dir
        
        # 출력 디렉토리가 없으면 생성
        os.makedirs(self.output_dir, exist_ok=True)

    def _preprocess_frame(self, frame):
        """
        SSIM 비교 속도를 높이기 위해 프레임을 흑백으로 변환하고 크기를 줄입니다.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 연산 속도 향상을 위해 640x360 해상도로 리사이즈
        resized = cv2.resize(gray, (640, 360))
        return resized

    def analyze(self, ssim_threshold: float = 0.85, sample_rate: float = 1.0, min_slide_duration: float = 2.0):
        """
        영상을 분석하여 슬라이드 변경 지점을 찾고 이미지를 추출합니다.
        
        :param ssim_threshold: 이 수치보다 유사도가 낮아지면 슬라이드가 넘어간 것으로 간주 (기본 0.85)
        :param sample_rate: 1초당 검사할 프레임 수 (1.0이면 1초에 1번 검사)
        :param min_slide_duration: 슬라이드가 최소한 유지되어야 하는 시간(초). 애니메이션 효과 등으로 인한 중복 캡처 방지 (기본 2초)
        :return: 각 슬라이드의 정보가 담긴 딕셔너리 리스트
        """
        cap = cv2.VideoCapture(self.video_path)
        
        if not cap.isOpened():
            raise Exception("비디오 파일을 열 수 없습니다.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_duration = total_frames / fps
        
        # 1초에 sample_rate 만큼만 건너뛰면서 검사하여 속도 최적화
        frame_skip = int(fps / sample_rate)
        
        slides_info = []
        slide_count = 0
        start_time = 0.0
        
        # 첫 프레임 읽기
        ret, frame = cap.read()
        if not ret:
            return slides_info

        # 이전 프레임 정보 초기화
        prev_gray = self._preprocess_frame(frame)
        prev_high_res = frame.copy() # 원본 화질 유지를 위해 백업
        prev_time = 0.0
        
        frame_idx = frame_skip

        print(f"총 영상 길이: {video_duration:.2f}초. (슬라이드 추출 중...)")

        while True:
            # 지정된 프레임 위치로 이동
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                break
                
            curr_time = frame_idx / fps
            curr_gray = self._preprocess_frame(frame)
            
            # 이전 프레임과 현재 프레임의 구조적 유사도(SSIM) 측정
            score, _ = ssim(prev_gray, curr_gray, full=True)
            
            # 유사도가 임계치보다 낮고, 최소 유지 시간을 넘겼다면 "슬라이드 전환"으로 판단
            if score < ssim_threshold and (curr_time - start_time) >= min_slide_duration:
                # print(f"슬라이드 전환 감지 ({prev_time:.2f}초 -> {curr_time:.2f}초) SSIM: {score:.3f}")
                
                # 저장할 파일명 지정
                img_filename = f"slide_{slide_count:03d}.png"
                img_path = os.path.join(self.output_dir, img_filename)
                
                # 직전 프레임(필기가 모두 완료된 상태)을 원본 고화질로 저장
                cv2.imwrite(img_path, prev_high_res)
                
                # 슬라이드 정보 기록
                slides_info.append({
                    "slide_idx": slide_count,
                    "start_time": start_time,    # 해당 슬라이드가 시작된 시간
                    "end_time": prev_time,       # 해당 슬라이드가 넘어간 시간 (자막 추출용)
                    "image_path": img_path       # 캡처된 이미지 경로
                })
                
                # 다음 슬라이드를 위해 변수 갱신
                slide_count += 1
                start_time = curr_time
                
            # 교수님이 필기 중일 때는 SSIM이 높게 유지되므로,
            # 계속해서 최신 프레임을 prev_high_res에 덮어씌우며 업데이트 합니다.
            # 이렇게 하면 전환되기 "직전"의 가장 필기가 많은 화면이 저장됩니다.
            prev_gray = curr_gray
            prev_high_res = frame.copy()
            prev_time = curr_time
            
            frame_idx += frame_skip

            # 10% 단위로 진행률 출력
            if frame_idx % (frame_skip * 60) == 0: 
                percent = (curr_time / video_duration) * 100
                blocks = "█" * int((percent // 10))
                print(f"진행률: {percent:.1f}% |{blocks:<10}|")

        # 영상이 끝난 후 마지막 슬라이드 저장
        img_filename = f"slide_{slide_count:03d}.png"
        img_path = os.path.join(self.output_dir, img_filename)
        cv2.imwrite(img_path, prev_high_res)
        
        slides_info.append({
            "slide_idx": slide_count,
            "start_time": start_time,
            "end_time": video_duration,
            "image_path": img_path
        })
        print(f"분석 완료 총 {len(slides_info)}장의 슬라이드가 추출되었습니다.")
        
        cap.release()
        return slides_info