import os
import sys
from pathlib import Path
from .config import PdfExportConfig
from .file_to_pdf import process_file_to_pdf

def main():
    """Main function demonstrating pydantic-based PDF conversion"""
    
    # Sample file configuration
    folder_path = "C:\\src\\PdfExport\\FileExample\\TMA-F-1173-1\\"
    filename = "TMA-F COA_1.xlsx"
    # filename = "TMA-F COA_1 (原料).xlsx"
        
    # Example 1: per_sheet 모드 (기본값)
    # try:
    #     print("\n=== Example 1: per_sheet 모드 ===")
    #     config = PdfExportConfig(
    #         folder_path=folder_path,
    #         filename=filename,
    #         export_mode="per_sheet"
    #     )
        
    #     print(f"Config created successfully:")
    #     print(f"  - Folder: {config.folder_path}")
    #     print(f"  - File: {config.filename}")
    #     print(f"  - Type: {config.filetype}")
    #     print(f"  - Filter: {config.filter}")
    #     print(f"  - Export mode: {config.export_mode}")
        
    #     result = process_file_to_pdf(config)
    #     if result["success"]:
    #         print(f"[OK] Generated {len(result['files'])} PDF files from {result['sheet_count']} sheets:")
    #         for pdf_file in result['files']:
    #             print(f"  - {os.path.basename(pdf_file)}")
    #         if result['warnings']:
    #             print("Warnings:")
    #             for warning in result['warnings']:
    #                 print(f"  [WARNING] {warning}")
    #     else:
    #         print(f"[ERROR] Failed to generate PDF files")
            
    # except Exception as e:
    #     print(f"[ERROR] Error: {e}")
    
    # Example 2: single_file 모드
    try:
        print("\n=== Example 2: single_file 모드 (기본 파일명) ===")
        config = PdfExportConfig(
            folder_path=folder_path,
            filename=filename,
            export_mode="single_file",
            pdf_filename="test_report"
        )
        
        print(f"Config created successfully:")
        print(f"  - Export mode: {config.export_mode}")
        print(f"  - PDF filename: {config.pdf_filename or config.filename_without_ext}")
        
        result = process_file_to_pdf(config)
        if result["success"]:
            print(f"[OK] Generated {len(result['files'])} PDF files from {result['sheet_count']} sheets:")
            for pdf_file in result['files']:
                print(f"  - {os.path.basename(pdf_file)}")
            if result['warnings']:
                print("Warnings:")
                for warning in result['warnings']:
                    print(f"  [WARNING] {warning}")
        else:
            print(f"[ERROR] Failed to generate PDF files")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()