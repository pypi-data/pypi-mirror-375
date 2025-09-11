"""
Debug version of MCP server for PDF Export with extensive logging.
"""

import logging
import asyncio
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List

import pythoncom
from mcp.server.fastmcp import FastMCP
import concurrent.futures
import traceback
import sys
import os
import io

# Stdin/Stdout의 인코딩을 UTF-8로 강제하여 한글 깨짐을 방지합니다.
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Import from current package
from . import PdfExportConfig, process_file_to_pdf as pdf_export_func

# Set up detailed logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,  # 콘솔 로그를 stderr 대신 stdout으로 보냅니다.
    force=True,         # 다른 라이브러리의 설정을 무시하고 이 설정을 강제합니다.
    # 로그 형식을 지정하면 더 보기 좋습니다.
    format='[PY Server] %(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = FastMCP(name="PDF-Export-Debug")

# Create a dedicated executor for PDF operations
_pdf_executor = concurrent.futures.ThreadPoolExecutor(
    max_workers=1, thread_name_prefix="PDFConversion"
)


def _run_pdf_conversion_sync(
    folder_path: str,
    filename: str,
    filter_value: Optional[Any] = None,
    export_mode: str = "per_sheet",
    pdf_filename: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Debug version with extensive logging and built-in PDF processing.
    """
    logger.info(f"Starting PDF conversion: {filename}")

    pythoncom.CoInitialize()
    try:
        config = PdfExportConfig(
            folder_path=Path(folder_path),
            filename=filename,
            filter=filter_value,
            export_mode=export_mode,
            pdf_filename=pdf_filename
        )
        
        config.validate_file_exists()
        
        import time
        time.sleep(0.5)
        
        pdf_result = pdf_export_func(config)
        
        logger.info(f"Generated {len(pdf_result['files'])} PDF files")
        if pdf_result['warnings']:
            logger.warning(f"Warnings: {pdf_result['warnings']}")
        result_dict = {
            "success": pdf_result["success"],
            "message": f"Successfully converted {filename} to PDF",
            "generated_files": [Path(pdf_file).name for pdf_file in pdf_result["files"]],
            "file_count": len(pdf_result["files"]),
            "output_folder": folder_path,
            "sheet_count": pdf_result["sheet_count"],
            "merge_method": pdf_result["merge_method"],
            "warnings": pdf_result["warnings"]
        }
        return result_dict

    except Exception as e:
        logger.error(f"PDF conversion failed: {str(e)}")
        logger.debug(traceback.format_exc())

        result_dict = {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "message": f"Failed to convert {filename} to PDF"
        }
        
        return result_dict
    
    finally:
        pythoncom.CoUninitialize()


def _process_pdf_result(result: Dict[str, Any]) -> str:
    """
    Process PDF conversion result and format response message.

    Args:
        result: PDF conversion result dictionary

    Returns:
        Formatted response message
    """
    try:
        if result.get("success"):
            message = f"[OK] {result.get('message', 'PDF conversion completed')}\n"
            message += f"Generated {result.get('file_count', 0)} PDF files from {result.get('sheet_count', 0)} sheets:\n"
            
            for filename in result.get("generated_files", []):
                message += f"  - {filename}\n"
            
            if result.get("merge_method"):
                message += f"Merge method: {result.get('merge_method')}\n"
            
            if result.get("warnings"):
                message += f"Warnings:\n"
                for warning in result.get("warnings", []):
                    message += f"  - {warning}\n"
                
            return message
        else:
            error_msg = f"[ERROR] {result.get('message', 'PDF conversion failed')}\n"
            error_msg += f"Error: {result.get('error', 'Unknown error')}"
            return error_msg

    except Exception as e:
        logger.error(f"Error processing PDF result: {e}")
        logger.debug(traceback.format_exc())
        return f"[ERROR] Error processing result: {str(e)}"


@mcp.tool()
async def process_file_to_pdf(
    folder_path: str,
    filename: str,
    filter_value: Optional[Any] = None,
    export_mode: str = "per_sheet",
    pdf_filename: Optional[str] = None,
) -> str:
    """
    Convert Excel file to PDF format with debug logging.
    
    Args:
        folder_path: Path to the folder containing the Excel file
        filename: Name of the Excel file (with extension)
        filter_value: Sheet name filter (null=all sheets, string=single sheet, array=multiple sheets)
        export_mode: Export mode ('per_sheet' for separate files, 'single_file' for one file with multiple pages)
        pdf_filename: PDF filename (without extension) for single_file mode. If None, uses Excel filename
    
    Returns:
        Formatted result message
    """
    logger.info(f"MCP tool called: process_file_to_pdf for {filename}")

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _pdf_executor,
            _run_pdf_conversion_sync,
            folder_path,
            filename,
            filter_value,
            export_mode,
            pdf_filename,
        )
        
        # Process and format the result
        formatted_result = _process_pdf_result(result)
        return formatted_result

    except Exception as e:
        logger.error(f"MCP tool failed: process_file_to_pdf - {str(e)}")
        logger.debug(traceback.format_exc())
        
        return f"[ERROR] PDF conversion failed: {str(e)}"


@mcp.tool()
async def list_excel_sheets(
    folder_path: str,
    filename: str,
    filetype: str,
) -> str:
    """
    List all sheets in an Excel file.
    
    Args:
        folder_path: Path to the folder containing the Excel file
        filename: Name of the Excel file (with extension)  
        filetype: Excel file type ('xlsx' or 'xls')
    
    Returns:
        List of sheet names or error message
    """
    logger.info(f"MCP tool called: list_excel_sheets for {filename}")

    try:
        from pathlib import Path
        
        # Check if file exists
        file_path = Path(folder_path) / filename
        if not file_path.exists():
            return f"[ERROR] File not found: {file_path}"
        
        # Import Excel library
        try:
            import win32com.client as win32
        except ImportError:
            return "[ERROR] pywin32 library not available. Cannot read Excel sheets."
        
        # Open Excel file and get sheet names
        excel_app = None
        workbook = None
        sheet_names = []
        
        try:
            excel_app = win32.Dispatch("Excel.Application")
            excel_app.Visible = False
            excel_app.DisplayAlerts = False
            
            workbook = excel_app.Workbooks.Open(str(file_path.absolute()))
            
            for worksheet in workbook.Worksheets:
                sheet_names.append(worksheet.Name)
                
            message = f"[OK] Found {len(sheet_names)} sheets in {filename}:\n"
            for i, sheet_name in enumerate(sheet_names, 1):
                message += f"  {i}. {sheet_name}\n"
                
            return message
            
        finally:
            if workbook:
                workbook.Close(SaveChanges=False)
            if excel_app:
                excel_app.Quit()
        
    except Exception as e:
        logger.error(f"MCP tool failed: list_excel_sheets - {str(e)}")
        logger.debug(traceback.format_exc())
        
        return f"[ERROR] Failed to list Excel sheets: {str(e)}"


@mcp.tool()
async def health_check() -> str:
    """Simple health check for PDF export server."""
    return "[OK] PDF Export Debug server is running and healthy"


@mcp.tool()
async def validate_file(
    folder_path: str,
    filename: str,
) -> str:
    """
    Validate if an Excel file exists and can be processed.
    
    Args:
        folder_path: Path to the folder containing the Excel file
        filename: Name of the Excel file (with extension)
    
    Returns:
        Validation result message
    """
    logger.info(f"MCP tool called: validate_file for {filename}")

    try:
        # Create config to validate
        config = PdfExportConfig(
            folder_path=Path(folder_path),
            filename=filename,
            filter=None
        )
        
        # Check if file exists
        config.validate_file_exists()
        
        # Get file info
        file_path = config.filepath
        file_size = file_path.stat().st_size
        
        message = f"[OK] File validation successful\n"
        message += f"File: {filename}\n"
        message += f"Path: {file_path}\n"
        message += f"Size: {file_size:,} bytes\n"
        message += f"Type: {config.filetype}\n"
        message += f"Status: Ready for PDF conversion"
        
        return message
        
    except Exception as e:
        logger.error(f"MCP tool failed: validate_file - {str(e)}")
        logger.debug(traceback.format_exc())
        
        return f"[ERROR] File validation failed: {str(e)}"


def main():
    logger.info("Starting PDF Export Debug MCP Server...")
    logger.info("Available tools:")
    logger.info("  - process_file_to_pdf: Convert Excel files to PDF")
    logger.info("  - list_excel_sheets: List all sheets in an Excel file")
    logger.info("  - validate_file: Validate if file exists and can be processed")
    logger.info("  - health_check: Server health check")

    mcp.run()

if __name__ == "__main__":
    main()