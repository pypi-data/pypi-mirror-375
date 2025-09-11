# pyright: reportMissingModuleSource=false
import os
import re
import time
from typing import List, Union, Optional, Dict, Any

import pythoncom

from .config import PdfExportConfig

try:
    import win32com.client as win32  # type: ignore
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False


def process_file_to_pdf(config: PdfExportConfig) -> Dict[str, Any]:
    """
    파일을 PDF로 변환하는 메인 함수
    
    Args:
        config (PdfExportConfig): PDF 변환 설정 객체
    
    Returns:
        Dict[str, Any]: 처리 결과와 메타데이터를 포함한 딕셔너리
            - success: bool - 처리 성공 여부
            - files: List[str] - 생성된 PDF 파일들의 경로 리스트
            - warnings: List[str] - 경고 메시지들
            - sheet_count: int - 처리된 시트 수
            - merge_method: str - 병합에 사용된 방법 (pypdf, fallback, none)
    """
    # 파일 존재 여부 확인
    config.validate_file_exists()
    
    if config.filetype in ['xlsx', 'xls']:
        return excel_to_pdf(config)
    else:
        raise ValueError(f"Unsupported file type: {config.filetype}")


def excel_to_pdf(config: PdfExportConfig) -> Dict[str, Any]:
    """
    엑셀 파일의 각 시트를 PDF로 변환
    
    Args:
        config (PdfExportConfig): PDF 변환 설정 객체
    
    Returns:
        Dict[str, Any]: 처리 결과와 메타데이터를 포함한 딕셔너리
    """
    if not WIN32_AVAILABLE:
        raise ImportError("pywin32 is required. Please install it with: pip install pywin32")
    
    created_pdfs = []
    pythoncom.CoInitialize()
    warnings = []
    excel_app = None
    workbook = None
    merge_method = "none"
    
    try:
        # Excel 애플리케이션 시작
        excel_app = win32.Dispatch("Excel.Application")
        excel_app.Visible = False  # 백그라운드에서 실행
        excel_app.DisplayAlerts = False  # 경고 메시지 비활성화
        
        # 엑셀 파일 열기
        workbook = excel_app.Workbooks.Open(os.path.abspath(config.filepath))
        
        # 시트 필터링
        worksheets_to_process = []
        if config.filter is None or (isinstance(config.filter, str) and config.filter.lower() == "전체"):
            # 전체 시트 처리
            worksheets_to_process = list(workbook.Worksheets)
        else:
            # 특정 시트만 처리
            if isinstance(config.filter, str):
                target_sheet_names = [config.filter]
            else:
                target_sheet_names = config.filter
            
            
            for sheet_name in target_sheet_names:
                try:
                    # 숫자인 경우 인덱스로 처리 (1-based)
                    if isinstance(sheet_name, int) or (isinstance(sheet_name, str) and sheet_name.isdigit()):
                        sheet_index = int(sheet_name)
                        if 1 <= sheet_index <= workbook.Worksheets.Count:
                            worksheet = workbook.Worksheets(sheet_index)
                            worksheets_to_process.append(worksheet)
                        else:
                            raise ValueError(f"Sheet index {sheet_index} is out of range.")
                    else:
                        # 문자열인 경우 시트명으로 처리
                        worksheet = workbook.Worksheets(sheet_name)
                        worksheets_to_process.append(worksheet)
                except Exception as e:
                    error_msg = f"Sheet '{sheet_name}' not found: {str(e)}"
                    raise ValueError(error_msg)
        
        if config.export_mode == "single_file":
            # single_file 모드: 개별 PDF 생성 후 병합하여 하나의 파일로 만들기
            pdf_filename = config.pdf_filename or config.filename_without_ext
            pdf_path = os.path.join(config.folder_path, f"{pdf_filename}.pdf")
            
            
            # 개별 PDF 파일들을 생성
            temp_pdfs = []
            for i, worksheet in enumerate(worksheets_to_process):
                sheet_name = worksheet.Name
                temp_pdf_filename = f"temp_{i}_{sanitize_filename(sheet_name)}.pdf"
                temp_pdf_path = os.path.join(config.folder_path, temp_pdf_filename)
                
                worksheet.Select()
                worksheet.ExportAsFixedFormat(
                    Type=0,  # xlTypePDF
                    Filename=os.path.abspath(temp_pdf_path)
                )
                temp_pdfs.append(temp_pdf_path)
            
            # PDF 병합 시도 (여러 라이브러리 시도)
            merge_success = False
            
            # pypdf 시도 (최신)
            if not merge_success:
                try:
                    import pypdf
                    
                    merger = pypdf.PdfWriter()
                    for temp_pdf in temp_pdfs:
                        reader = pypdf.PdfReader(temp_pdf)
                        for page in reader.pages:
                            merger.add_page(page)
                    
                    with open(pdf_path, 'wb') as output_file:
                        merger.write(output_file)
                    
                    merge_success = True
                    merge_method = "pypdf"
                    
                except ImportError:
                    pass
                except Exception as e:
                    pass
            
            # 병합 실패 시 첫 번째 파일만 사용
            if not merge_success:
                warnings.append("PDF merge failed, using only the first sheet")
                if not temp_pdfs:
                    raise Exception("No temporary PDF files were generated")
                import shutil
                shutil.move(temp_pdfs[0], pdf_path)
                merge_method = "fallback"
            
            # 임시 파일들 정리
            for temp_pdf in temp_pdfs:
                try:
                    if os.path.exists(temp_pdf):  # 첫 번째 파일이 이동되었을 수 있으므로 확인
                        os.remove(temp_pdf)
                except Exception as e:
                    pass
            
            created_pdfs.append(pdf_path)
            
        else:
            merge_method = "per_sheet"
            # per_sheet 모드: 각 시트별로 개별 PDF 파일 생성
            for worksheet in worksheets_to_process:
                sheet_name = worksheet.Name
                
                # PDF 파일명 생성 (시트명 사용)
                safe_sheet_name = sanitize_filename(sheet_name)
                pdf_filename = f"{safe_sheet_name}.pdf"
                pdf_path = os.path.join(config.folder_path, pdf_filename)
                
                
                # 해당 시트를 활성 시트로 설정
                worksheet.Select()
                
                worksheet.ExportAsFixedFormat(
                    Type=0,  # xlTypePDF
                    Filename=os.path.abspath(pdf_path)
                )
                
                created_pdfs.append(pdf_path)
        
        # 결과 반환
        return {
            "success": True,
            "files": created_pdfs,
            "warnings": warnings,
            "sheet_count": len(worksheets_to_process),
            "merge_method": merge_method
        }
        
    except Exception as e:
        raise Exception(f"Error processing Excel file: {str(e)}")
    
    finally:
        # Excel 애플리케이션 정리
        try:
            if workbook:
                workbook.Close(SaveChanges=False)
            if excel_app:
                excel_app.Quit()
        except:
            pass

        # ✅ COM 해제
        pythoncom.CoUninitialize()


def sanitize_filename(filename):
    """
    파일명에서 사용할 수 없는 문자들을 제거/대체
    
    Args:
        filename (str): 원본 파일명
    
    Returns:
        str: 정제된 파일명
    """
    # Windows에서 사용할 수 없는 문자들 제거/대체
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # 연속된 공백을 하나로 줄이고 앞뒤 공백 제거
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # 빈 문자열이면 기본값 사용
    if not sanitized:
        sanitized = "Sheet"
    
    return sanitized
    