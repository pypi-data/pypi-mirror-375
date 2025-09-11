# -*- coding: utf-8 -*-
from typing import Optional, List, Union, Literal
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, model_validator


AllowedFileType = Literal["xlsx", "xls"]
ExportMode = Literal["single_file", "per_sheet"]


class PdfExportConfig(BaseModel):
    """PDF conversion configuration class"""

    # 타입 강화: Path, Literal 사용
    folder_path: Path = Field(..., description="Folder path")
    filename: str = Field(..., description="File name (with extension)")
    filter: Optional[Union[str, List[str], int, List[int]]] = Field(
        default=None,
        description="Sheet name filter (None='all', str/int=single sheet, List[str/int]=multiple sheets)",
    )
    export_mode: ExportMode = Field(
        default="per_sheet",
        description="Export mode: 'per_sheet' for separate files, 'single_file' for one file with multiple pages"
    )
    pdf_filename: Optional[str] = Field(
        default=None,
        description="PDF filename (without extension) for single_file mode. If None, uses Excel filename"
    )

    # ---- Field validators (v2) ----
    @field_validator("folder_path")
    @classmethod
    def _validate_folder_path(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Folder does not exist: {v}")
        if not v.is_dir():
            raise ValueError(f"Path is not a directory: {v}")
        return v.resolve()

    @field_validator("filename")
    @classmethod
    def _validate_filename(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Filename is empty")
        return v
    
    @field_validator("pdf_filename")
    @classmethod
    def _validate_pdf_filename(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                return None
            # Remove extension if provided
            if v.lower().endswith('.pdf'):
                v = v[:-4]
        return v

    @field_validator("filter")
    @classmethod
    def _normalize_filter(cls, v: Optional[Union[str, List[str], int, List[int]]]):
        if v is None:
            return None
        if isinstance(v, int):
            return str(v)  # 숫자를 문자열로 변환
        if isinstance(v, str):
            v = v.strip()
            return v or None
        if isinstance(v, list):
            cleaned = []
            for item in v:
                if isinstance(item, str):
                    cleaned_str = item.strip()
                    if cleaned_str:
                        cleaned.append(cleaned_str)
                elif isinstance(item, int):
                    cleaned.append(str(item))  # 숫자를 문자열로 변환
            return cleaned or None
        raise ValueError("filter must be None, str, int, List[str], or List[int]")

    # ---- Model-level validator (필드 간 관계 검증) ----
    @model_validator(mode="after")
    def _cross_validate(self):
        # filename의 확장자가 지원되는 파일 타입인지 확인
        ext = Path(self.filename).suffix.lower().lstrip(".")
        if ext not in ["xlsx", "xls"]:
            raise ValueError(
                f"Unsupported file extension: {ext}. Only 'xlsx' and 'xls' are supported."
            )
        return self

    # ---- Convenience properties ----
    @property
    def filepath(self) -> Path:
        """Return full file path"""
        return (self.folder_path / self.filename).resolve()

    @property
    def filename_without_ext(self) -> str:
        """Return filename without extension"""
        return Path(self.filename).stem
    
    @property
    def filetype(self) -> AllowedFileType:
        """Extract file type from filename extension"""
        ext = Path(self.filename).suffix.lower().lstrip(".")
        return ext  # type: ignore

    def validate_file_exists(self) -> None:
        """Check if the target file exists"""
        if not self.filepath.exists():
            raise FileNotFoundError(f"File not found: {self.filepath}")


