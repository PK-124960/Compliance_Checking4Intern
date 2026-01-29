"""
OCR Service for Document Processing
Supports DeepSeek-OCR 2 and PyMuPDF fallback
"""

import os
import fitz  # PyMuPDF
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OCRResult:
    """Result from OCR processing"""
    success: bool
    text: str
    pages: int
    words: int
    method: str  # "deepseek-ocr2" or "pymupdf"
    confidence: float
    tables: List[dict] = None
    error: str = None
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "text_preview": self.text[:500] + "..." if len(self.text) > 500 else self.text,
            "pages": self.pages,
            "words": self.words,
            "method": self.method,
            "confidence": self.confidence,
            "tables_count": len(self.tables) if self.tables else 0,
            "error": self.error
        }


class OCRService:
    """
    OCR Service with DeepSeek-OCR 2 support
    
    DeepSeek-OCR 2 Features:
    - 91.09% accuracy on OmniDocBench v1.5
    - Visual Causal Flow architecture
    - Better table and formula extraction
    - Reduced R-order Edit Distance (0.057)
    """
    
    def __init__(self, deepseek_api_url: str = None):
        self.deepseek_api_url = deepseek_api_url or os.getenv("DEEPSEEK_OCR_URL")
        self.use_deepseek = self.deepseek_api_url is not None
    
    def extract_text(self, pdf_path: str, use_deepseek: bool = None) -> OCRResult:
        """
        Extract text from PDF using best available method
        
        Priority:
        1. DeepSeek-OCR 2 (if available and use_deepseek=True)
        2. PyMuPDF (fallback)
        """
        use_deepseek = use_deepseek if use_deepseek is not None else self.use_deepseek
        
        if use_deepseek and self.deepseek_api_url:
            result = self._extract_with_deepseek(pdf_path)
            if result.success:
                return result
            # Fall back to PyMuPDF if DeepSeek fails
        
        return self._extract_with_pymupdf(pdf_path)
    
    def _extract_with_deepseek(self, pdf_path: str) -> OCRResult:
        """Extract text using DeepSeek-OCR 2 API"""
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.deepseek_api_url}/ocr",
                    files=files,
                    timeout=120
                )
                response.raise_for_status()
                data = response.json()
                
                return OCRResult(
                    success=True,
                    text=data.get("text", ""),
                    pages=data.get("pages", 0),
                    words=len(data.get("text", "").split()),
                    method="deepseek-ocr2",
                    confidence=data.get("confidence", 0.91),
                    tables=data.get("tables", [])
                )
        except Exception as e:
            return OCRResult(
                success=False,
                text="",
                pages=0,
                words=0,
                method="deepseek-ocr2",
                confidence=0,
                error=str(e)
            )
    
    def _extract_with_pymupdf(self, pdf_path: str) -> OCRResult:
        """Extract text using PyMuPDF (fallback)"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            tables = []
            
            for page_num, page in enumerate(doc):
                # Extract text
                page_text = page.get_text()
                text += page_text + "\n"
                
                # Try to detect tables (simple heuristic)
                blocks = page.get_text("dict")["blocks"]
                for block in blocks:
                    if block.get("type") == 0:  # Text block
                        lines = block.get("lines", [])
                        if len(lines) >= 3:
                            # Potential table if multiple aligned lines
                            spans_per_line = [len(line.get("spans", [])) for line in lines]
                            if all(s > 2 for s in spans_per_line):
                                tables.append({
                                    "page": page_num + 1,
                                    "type": "detected_table",
                                    "rows": len(lines)
                                })
            
            pages = len(doc)
            doc.close()
            
            return OCRResult(
                success=True,
                text=text,
                pages=pages,
                words=len(text.split()),
                method="pymupdf",
                confidence=0.85,  # Lower than DeepSeek
                tables=tables
            )
        except Exception as e:
            return OCRResult(
                success=False,
                text="",
                pages=0,
                words=0,
                method="pymupdf",
                confidence=0,
                error=str(e)
            )
    
    def compare_methods(self, pdf_path: str) -> Dict[str, OCRResult]:
        """Compare both OCR methods on the same document"""
        results = {}
        
        # PyMuPDF
        results["pymupdf"] = self._extract_with_pymupdf(pdf_path)
        
        # DeepSeek-OCR 2 (if available)
        if self.use_deepseek:
            results["deepseek-ocr2"] = self._extract_with_deepseek(pdf_path)
        
        return results


# Global OCR service instance
ocr_service = OCRService()
