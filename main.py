from video_analyzer import *
from transcriber import *
from pdf_generator import *
from pathlib import Path
from tool import *
import time

script_path = Path(__file__).resolve()
input_folder = str(script_path.parent / "input")
mp4_files = [str(file) for file in Path(input_folder).rglob("*.mp4")]
mode_config = [
    # cpu
    {"model":"tiny","device":"cpu","compute_type":"int8"},
    {"model":"base","device":"cpu","compute_type":"int8"},
    {"model":"small","device":"cpu","compute_type":"int8"},
    {"model":"medium","device":"cpu","compute_type":"int8"},
    # gpu
    {"model":"base","device":"cuda","compute_type":"float16"},
    {"model":"small","device":"cuda","compute_type":"float16"},
    {"model":"medium","device":"cuda","compute_type":"float16"},
]

def main():
    tp = TerminalPrinter()
    tp.clear()
    tp.title("Lecture Analyzer 1.0")
    tp.out("요약할 mp4 파일은 아래와 같습니다")
    if len(mp4_files) <= 5 :
        for file in mp4_files:
            print(Path(file).name)
    else:
        ilist = [0,1,-2,-1]
        for idx in ilist:
            print(Path(mp4_files[idx]).name)

    tp.out(f"총 {len(mp4_files)} 개")
    tp.wout("진행하시겠습니까? [y/n]")
    yn = input()

    if yn == "y":
        tp.clear()
        tp.out("모드 선택 : cpu 모드 (0~3) gPU 모드 (4~6)")
        tp.out("숫자가 클 수록 인식 성능 향상, 속도는 저하")
        mode_idx = int(input())
        mode = mode_config[mode_idx]

        start = time.time()
        for video_path in mp4_files:
            name = Path(video_path).name

            tp.out(f"{name} 분석중")
            video_start = time.time()
            videoAnalyzer = VideoAnalyzer(video_path)
            # 슬라이드 추출
            slides_info = videoAnalyzer.analyze()

            duration = time.time() - video_start
            total = time.time() - start
            print(f"[분석시간] {duration:.1f} 초 [총 시간] {total:.1f}")

            print(f"{name} 음성 분석 시작")
            voice_start = time.time()

            transcriber = Transcriber(mode)
            slides_data = transcriber.transcribe_slides(video_path,slides_info,language="ko")
            duration = time.time() - voice_start
            total = time.time() - start
            print(f"{name} 음성 분석 완료  [분석시간] {duration:.1f} 초 [총 시간] {total:.1f}")

            print(f"{name}.pdf 구성중")
            pdf_start = time.time()

            pdf_gen = PDFGenerator()
            pdf_gen.generate(slides_data,output_filename=f"{name}.pdf")

            duration = time.time() - pdf_start
            total = time.time() - start

            tp.out(f"{name} 완료")

if __name__ == "__main__":
    main()