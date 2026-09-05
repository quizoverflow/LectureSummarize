import os
from faster_whisper import WhisperModel

class Transcriber:
    def __init__(self,mode):
        """
        Whisper 모델 초기화
        :param model_size: 사용할 모델 크기 ('tiny', 'base', 'small', 'medium', 'large-v3')
        한국어는 'small' 이상을 권장하나, 속도 우선시 'base' 사용 가능
        :param device: 'cuda' (GPU 사용) 또는 'cpu'
        :param compute_type: 메모리 절약을 위한 연산 타입 ('float16', 'int8' 등)
        """
        print(f"[{mode['model']}] Whisper 모델을 불러오는 중... (Device: {mode['device']})")
        self.model = WhisperModel(mode["model"], device=mode["device"], compute_type=mode["compute_type"])

    def transcribe_slides(self, video_path: str, slides_data: list, language: str = "ko") -> list:
        """
        강의 영상의 특정 슬라이드 시간 구간별로 음성을 인식하여 자막 텍스트를 추출합니다.
        
        :param video_path: 강의 mp4 파일 경로
        :param slides_data: video_analyzer에서 전달받은 슬라이드 정보 리스트
        :param language: 인식할 언어 코드 (기본 'ko')
        :return: 자막 정보(text)가 추가된 slides_data
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"영상 파일을 찾을 수 없습니다: {video_path}")

        print(f"[{video_path}] 전체 음성 인식 및 슬라이드 구간별 텍스트 매핑 시작...")

        # 1. 영상 전체의 음성을 한 번에 트랜스크립션하여 연산 속도 최적화
        # (구간별로 모델을 반복 호출하는 것보다 전체를 한 번에 돌리는 것이 훨씬 빠릅니다)
        segments, info = self.model.transcribe(
            video_path,
            language=language,
            beam_size=5,
            vad_filter=True  # 묵음 구간을 제외하여 환각(Hallucination) 현상 방지
        )

        print(f"언어 감지: {info.language} (확률: {info.language_probability:.2f})")

        # 세그먼트 생성기를 리스트로 전환
        all_segments = list(segments)

        # 2. 추출된 자막 세그먼트들을 슬라이드 구간별로 매핑
        cnt = 0
        last_step = 0
        for slide in slides_data:
            s_start = slide["start_time"]
            s_end = slide["end_time"]
            
            slide_texts = []
            
            for seg in all_segments:
                # 자막 세그먼트의 중간 지점이 슬라이드 시간 범위 내에 속하는지 확인
                seg_mid = (seg.start + seg.end) / 2
                if s_start <= seg_mid < s_end:
                    slide_texts.append(seg.text.strip())
            
            # 구간 내 자막들을 하나의 문단으로 병합
            full_text = " ".join(slide_texts)
            slide["script"] = full_text if full_text else "(해당 구간에 음성 자막이 없습니다.)"

            cnt += 1
            progress = int( ((cnt+1) / len(slides_data)) * 100)
            step = int(progress // 10)
            if step > last_step:
                percent = step * 10
                blocks = "█" * step
                print(f"진행률: {percent:3d}% |{blocks:<10}|")
                last_step = step

            print(f"Slide {slide['slide_idx']} ({s_start:.1f}초~{s_end:.1f}초) 자막 추출 완료")
            # print(f"   내용: {slide['script'][:60]}..." if len(slide['script']) > 60 else f"   내용: {slide['script']}")

        print("\n✅ 모든 슬라이드 구간의 자막 추출이 완료되었습니다.")
        return slides_data