"""
OCR管理器 - 支持多种OCR引擎，自动选择最适合的方案
根据服务器内存情况自动选择OCR引擎
"""

import os
import gc
from typing import Optional, List, Tuple, Dict
from enum import Enum

class OCREngine(Enum):
    """OCR引擎类型"""
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"
    PADDLEOCR = "paddleocr"
    DISABLED = "disabled"

class OCRManager:
    """OCR管理器 - 统一管理多种OCR引擎"""
    
    def __init__(self):
        self.current_engine: Optional[OCREngine] = None
        self.easyocr_reader = None
        self.paddleocr_reader = None
        self.tesseract_available = False
        
        # 内存使用标记
        self.memory_check_enabled = True
        self.max_memory_mb = 1500  # 默认最大内存限制（MB）
        
        # 初始化可用引擎
        self._detect_available_engines()
        
        # 根据环境变量选择引擎
        self._select_engine()
    
    def _detect_available_engines(self):
        """检测可用的OCR引擎"""
        # 检测EasyOCR
        try:
            import easyocr
            self.easyocr_available = True
        except ImportError:
            self.easyocr_available = False
        
        # 检测Tesseract
        try:
            import pytesseract
            from PIL import Image
            # 测试Tesseract是否可用
            try:
                pytesseract.get_tesseract_version()
                self.tesseract_available = True
            except:
                self.tesseract_available = False
        except ImportError:
            self.tesseract_available = False
        
        # 检测PaddleOCR
        try:
            from paddleocr import PaddleOCR
            self.paddleocr_available = True
        except ImportError:
            self.paddleocr_available = False
    
    def _select_engine(self):
        """根据环境变量和可用性选择OCR引擎"""
        # 检查是否禁用OCR
        if os.getenv('DISABLE_OCR', '').lower() in ('1', 'true', 'yes'):
            self.current_engine = OCREngine.DISABLED
            print("[DEBUG] OCR已通过环境变量禁用")
            return
        
        # 检查指定的OCR引擎
        preferred_engine = os.getenv('OCR_ENGINE', '').lower()
        
        if preferred_engine == 'tesseract' and self.tesseract_available:
            self.current_engine = OCREngine.TESSERACT
            print("[DEBUG] 使用Tesseract OCR引擎")
        elif preferred_engine == 'paddleocr' and self.paddleocr_available:
            self.current_engine = OCREngine.PADDLEOCR
            print("[DEBUG] 使用PaddleOCR引擎")
        elif preferred_engine == 'easyocr' and self.easyocr_available:
            self.current_engine = OCREngine.EASYOCR
            print("[DEBUG] 使用EasyOCR引擎")
        elif self.tesseract_available:
            # 默认优先使用Tesseract（最轻量）
            self.current_engine = OCREngine.TESSERACT
            print("[DEBUG] 自动选择Tesseract OCR引擎（最轻量）")
        elif self.paddleocr_available:
            self.current_engine = OCREngine.PADDLEOCR
            print("[DEBUG] 自动选择PaddleOCR引擎")
        elif self.easyocr_available:
            self.current_engine = OCREngine.EASYOCR
            print("[DEBUG] 自动选择EasyOCR引擎")
        else:
            self.current_engine = OCREngine.DISABLED
            print("[DEBUG] 没有可用的OCR引擎")
    
    def get_memory_usage(self) -> float:
        """获取当前进程内存使用量（MB）"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def check_memory(self) -> bool:
        """检查内存是否足够"""
        if not self.memory_check_enabled:
            return True
        
        current_memory = self.get_memory_usage()
        if current_memory > self.max_memory_mb:
            print(f"[DEBUG] 内存使用过高 ({current_memory:.1f}MB > {self.max_memory_mb}MB)，建议先释放内存")
            return False
        return True
    
    def load_easyocr(self, languages: List[str] = None) -> bool:
        """加载EasyOCR模型"""
        if self.easyocr_reader is not None:
            return True
        
        if not self.easyocr_available:
            return False
        
        try:
            import easyocr
            
            if languages is None:
                # 默认只加载英文（更轻量）
                enable_chinese = os.getenv('ENABLE_CHINESE_OCR', '').lower() in ('1', 'true', 'yes')
                languages = ['ch_sim', 'en'] if enable_chinese else ['en']
            
            print(f"[DEBUG] 加载EasyOCR模型，语言: {languages}")
            
            # 检查内存
            if not self.check_memory():
                print("[DEBUG] 内存不足，无法加载EasyOCR模型")
                return False
            
            self.easyocr_reader = easyocr.Reader(languages, gpu=False)
            print("[DEBUG] ✅ EasyOCR模型加载成功")
            return True
        except MemoryError as e:
            print(f"[DEBUG] ❌ EasyOCR模型加载失败 - 内存不足: {str(e)}")
            return False
        except Exception as e:
            print(f"[DEBUG] ❌ EasyOCR模型加载失败: {str(e)}")
            return False
    
    def load_paddleocr(self) -> bool:
        """加载PaddleOCR模型"""
        if self.paddleocr_reader is not None:
            return True
        
        if not self.paddleocr_available:
            return False
        
        try:
            from paddleocr import PaddleOCR
            
            print("[DEBUG] 加载PaddleOCR模型...")
            
            # 检查内存
            if not self.check_memory():
                print("[DEBUG] 内存不足，无法加载PaddleOCR模型")
                return False
            
            # 使用轻量版配置
            self.paddleocr_reader = PaddleOCR(
                use_angle_cls=True,
                lang='ch' if os.getenv('ENABLE_CHINESE_OCR', '').lower() in ('1', 'true', 'yes') else 'en',
                use_gpu=False,
                show_log=False
            )
            print("[DEBUG] ✅ PaddleOCR模型加载成功")
            return True
        except MemoryError as e:
            print(f"[DEBUG] ❌ PaddleOCR模型加载失败 - 内存不足: {str(e)}")
            return False
        except Exception as e:
            print(f"[DEBUG] ❌ PaddleOCR模型加载失败: {str(e)}")
            return False
    
    def unload_models(self):
        """卸载所有OCR模型，释放内存"""
        if self.easyocr_reader is not None:
            del self.easyocr_reader
            self.easyocr_reader = None
            print("[DEBUG] EasyOCR模型已卸载")
        
        if self.paddleocr_reader is not None:
            del self.paddleocr_reader
            self.paddleocr_reader = None
            print("[DEBUG] PaddleOCR模型已卸载")
        
        # 强制垃圾回收
        gc.collect()
        print("[DEBUG] 内存已释放")
    
    def readtext_easyocr(self, image_path: str) -> List[Tuple]:
        """使用EasyOCR识别文字"""
        if not self.load_easyocr():
            return []
        
        try:
            results = self.easyocr_reader.readtext(image_path)
            return results
        except Exception as e:
            print(f"[DEBUG] EasyOCR识别失败: {str(e)}")
            return []
    
    def readtext_tesseract(self, image_path: str) -> List[Tuple]:
        """使用Tesseract识别文字"""
        if not self.tesseract_available:
            return []
        
        try:
            import pytesseract
            from PIL import Image
            
            # 读取图片
            img = Image.open(image_path)
            
            # 识别文字
            text = pytesseract.image_to_string(img, lang='chi_sim+eng' if os.getenv('ENABLE_CHINESE_OCR', '').lower() in ('1', 'true', 'yes') else 'eng')
            
            # 转换为EasyOCR格式的返回结果
            # Tesseract只返回文字，没有坐标信息
            if text.strip():
                return [(None, text.strip(), None)]  # (bbox, text, confidence)
            return []
        except Exception as e:
            print(f"[DEBUG] Tesseract识别失败: {str(e)}")
            return []
    
    def readtext_paddleocr(self, image_path: str) -> List[Tuple]:
        """使用PaddleOCR识别文字"""
        if not self.load_paddleocr():
            return []
        
        try:
            results = self.paddleocr_reader.ocr(image_path, cls=True)
            
            # 转换为EasyOCR格式
            formatted_results = []
            if results and results[0]:
                for line in results[0]:
                    if line:
                        bbox, (text, confidence) = line
                        formatted_results.append((bbox, text, confidence))
            
            return formatted_results
        except Exception as e:
            print(f"[DEBUG] PaddleOCR识别失败: {str(e)}")
            return []
    
    def readtext(self, image_path: str) -> List[Tuple]:
        """统一的OCR识别接口，自动选择引擎"""
        if self.current_engine == OCREngine.DISABLED:
            print("[DEBUG] OCR已禁用")
            return []
        
        if self.current_engine == OCREngine.TESSERACT:
            return self.readtext_tesseract(image_path)
        elif self.current_engine == OCREngine.PADDLEOCR:
            return self.readtext_paddleocr(image_path)
        elif self.current_engine == OCREngine.EASYOCR:
            return self.readtext_easyocr(image_path)
        else:
            print("[DEBUG] 没有可用的OCR引擎")
            return []
    
    def is_available(self) -> bool:
        """检查OCR是否可用"""
        return self.current_engine != OCREngine.DISABLED
    
    def get_engine_name(self) -> str:
        """获取当前使用的OCR引擎名称"""
        if self.current_engine:
            return self.current_engine.value
        return "none"
