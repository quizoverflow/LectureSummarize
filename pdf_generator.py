import fitz  # PyMuPDF
import os
import urllib.request

class PDFGenerator:
    def __init__(self, output_dir: str = "output/pdf"):
        """
        PDF 생성기 초기화
        :param output_dir: 최종 PDF 파일이 저장될 디렉토리
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.font_path = self._get_korean_font_path()

    def _get_korean_font_path(self) -> str:
        """
        한글 폰트 경로를 찾거나 다운로드합니다.
        """
        # 1. OS별 기본 한글 폰트 경로 확인
        candidate_fonts = [
            "C:/Windows/Fonts/malgun.ttf",  # Windows 맑은 고딕
            "/System/Library/Fonts/Supplemental/AppleGothic.ttf",  # macOS AppleGothic
            "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"  # Linux 나눔고딕
        ]

        for font in candidate_fonts:
            if os.path.exists(font):
                return font

        # 2. 시스템 폰트가 없는 경우 실행 폴더에 나눔고딕 다운로드
        fallback_font = "NanumGothic.ttf"
        if not os.path.exists(fallback_font):
            print("한글 폰트를 찾을 수 없어 나눔고딕을 다운로드합니다...")
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            urllib.request.urlretrieve(url, fallback_font)

        return fallback_font

    def generate(self, slides_data: list, output_filename: str = "lecture_summary.pdf") -> str:
        """
        슬라이드 이미지와 자막 데이터를 받아 PDF 파일을 생성합니다.

        :param slides_data: image_path, script 정보가 담긴 리스트
        :param output_filename: 생성될 PDF 파일명
        :return: 생성된 PDF 파일 경로
        """
        pdf_path = os.path.join(self.output_dir, output_filename)
        doc = fitz.open()

        # A4 크기 설정 (포트레이트: 595 x 842 pt)
        page_width, page_height = 595, 842
        margin = 40

        cnt = 0
        last_step = 0
        for slide in slides_data:
            page = doc.new_page(width=page_width, height=page_height)
            
            # --- 1. 상단 타이틀 영역 ---
            title_text = f"Slide {slide['slide_idx'] + 1} ({slide['start_time']:.1f}s ~ {slide['end_time']:.1f}s)"
            page.insert_text(
                fitz.Point(margin, margin + 10),
                title_text,
                fontsize=14,
                fontfile=self.font_path,
                fontname="ko_font",
                color=(0.2, 0.2, 0.2)
            )

            # --- 2. 슬라이드 이미지 영역 ---
            img_path = slide["image_path"]
            if os.path.exists(img_path):
                # 이미지 크기 및 비율 계산
                pix = fitz.Pixmap(img_path)
                img_w, img_h = pix.width, pix.height
                
                # 가로 폭을 페이지 너비(마진 제외)에 맞추고 높이는 비율 유지
                target_w = page_width - (margin * 2)
                target_h = target_w * (img_h / img_w)
                
                img_rect = fitz.Rect(margin, margin + 25, margin + target_w, margin + 25 + target_h)
                page.insert_image(img_rect, filename=img_path)
                image_bottom = margin + 25 + target_h
            else:
                image_bottom = margin + 100

            # --- 3. 구분선 추가 ---
            line_y = image_bottom + 15
            page.draw_line(
                fitz.Point(margin, line_y),
                fitz.Point(page_width - margin, line_y),
                color=(0.8, 0.8, 0.8),
                width=1
            )

            # --- 4. 자막(스크립트) 영역 ---
            script_y = line_y + 20
            script_rect = fitz.Rect(margin, script_y, page_width - margin, page_height - margin)
            
            script_text = slide.get("script", "(자막 정보 없음)")
            
            # 텍스트 상자로 감싸서 영역 내 자동 줄바꿈 처리
            page.insert_textbox(
                script_rect,
                script_text,
                fontsize=11,
                fontfile=self.font_path,
                fontname="ko_font",
                color=(0.1, 0.1, 0.1),
                align=0  # 좌측 정렬
            )
            cnt += 1
            progress = int( ((cnt+1) / len(slides_data)) * 100)
            step = int(progress // 10)
            if step > last_step:
                percent = step * 10
                blocks = "█" * step
                print(f"진행률: {percent:3d}% |{blocks:<10}|")
                last_step = step


        doc.save(pdf_path)
        doc.close()

        return pdf_path