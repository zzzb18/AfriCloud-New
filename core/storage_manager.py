"""云存储管理器"""
import streamlit as st
import pandas as pd
import os
import json
import hashlib
import mimetypes
import base64
import io
import time
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import zipfile
import shutil
from pathlib import Path
import requests
from PIL import Image
import re
import numpy as np
from collections import Counter
import jieba
import jieba.analyse
import matplotlib.pyplot as plt
import seaborn as sns
import contextlib

# 尝试导入tools.generate_report（可选）
try:
    from tools.generate_report import SmartAnalysisGenerator
    SMART_REPORT_AVAILABLE = True
except ImportError:
    SMART_REPORT_AVAILABLE = False

from config.settings import INDUSTRY_KEYWORDS, INDUSTRY_ENGLISH_MAPPING
from utils.dependencies import (
    PDF_AVAILABLE, OCR_AVAILABLE, ML_AVAILABLE, 
    TRANSFORMERS_AVAILABLE, OPENAI_AVAILABLE,
    TESSERACT_AVAILABLE
)

# 导入PDF支持库
if PDF_AVAILABLE:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        fitz = None
else:
    fitz = None

# 导入OCR支持库 - 仅使用Tesseract OCR
if TESSERACT_AVAILABLE:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        pytesseract = None
        Image = None
else:
    pytesseract = None
    Image = None

class CloudStorageManager:
    def __init__(self):
        # 云部署配置
        import os
        self.is_cloud_deployment = os.getenv('STREAMLIT_SERVER_PORT') is not None

        if self.is_cloud_deployment:
            # 云部署：使用持久化存储
            self.storage_dir = Path("/tmp/cloud_storage")
            self.cache_dir = Path("/tmp/local_cache")
            self.ai_analysis_dir = Path("/tmp/ai_analysis")
        else:
            # 本地部署：使用当前目录
            self.storage_dir = Path("cloud_storage")
            self.cache_dir = Path("local_cache")
            self.ai_analysis_dir = Path("ai_analysis")

        # 创建目录
        self.storage_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.ai_analysis_dir.mkdir(exist_ok=True)

        # 将路径转换为字符串，确保在Windows上正常工作
        self.db_path = str(self.storage_dir / "storage.db")
        self.init_database()

        # 初始化AI功能
        self.init_ai_models()

        # 天气缓存
        self.latest_weather: Optional[Dict[str, Any]] = None
        # 遥感缓存
        self.latest_remote_sensing: Optional[Dict[str, Any]] = None

    def init_database(self):
        """初始化数据库"""
        try:
            # 确保数据库目录存在（双重保险）
            db_path_obj = Path(self.db_path)
            db_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 文件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER,
                    file_type TEXT,
                    folder_id INTEGER,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checksum TEXT,
                    is_cached BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (folder_id) REFERENCES folders (id)
                )
            ''')

            # 文件夹表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS folders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    folder_name TEXT NOT NULL,
                    parent_folder_id INTEGER,
                    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_folder_id) REFERENCES folders (id)
                )
            ''')

            # 上传进度表（用于断点续传）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS upload_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    total_size INTEGER,
                    uploaded_size INTEGER,
                    chunk_size INTEGER,
                    checksum TEXT,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # AI分析结果表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id INTEGER,
                    analysis_type TEXT,
                    industry_category TEXT,
                    extracted_text TEXT,
                    key_phrases TEXT,
                    summary TEXT,
                    confidence_score REAL,
                    method TEXT,
                    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (file_id) REFERENCES files (id)
                )
            ''')

            # 迁移：若旧表无 method 列则补充
            try:
                cursor.execute("PRAGMA table_info(ai_analysis)")
                cols = [row[1] for row in cursor.fetchall()]
                if 'method' not in cols:
                    cursor.execute('ALTER TABLE ai_analysis ADD COLUMN method TEXT')
                # 添加ocr_content字段用于存储完整的OCR内容
                if 'ocr_content' not in cols:
                    cursor.execute('ALTER TABLE ai_analysis ADD COLUMN ocr_content TEXT')
            except Exception:
                pass

            # 行业分类表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS industry_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name TEXT UNIQUE,
                    keywords TEXT,
                    description TEXT,
                    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            import os
            error_msg = f"数据库初始化失败: {str(e)}\n数据库路径: {self.db_path}\n目录存在: {os.path.exists(db_path_obj.parent)}"
            print(f"[ERROR] {error_msg}")
            raise RuntimeError(error_msg) from e
        except Exception as e:
            import os
            error_msg = f"数据库初始化时发生未知错误: {str(e)}\n数据库路径: {self.db_path}"
            print(f"[ERROR] {error_msg}")
            raise RuntimeError(error_msg) from e

    def init_ai_models(self):
        """初始化AI模型"""
        # 初始化行业分类关键词（Agribusiness细分，补充非洲常见作物/要素）
        self.industry_keywords = {
            "种植业": ["作物", "玉米", "小米", "高粱", "水稻", "木薯", "山药", "红薯", "花生", "芝麻", "葵花籽", "棉花",
                       "可可", "咖啡", "茶叶", "香蕉", "芒果", "菠萝", "蔬菜", "果园", "产量", "单产", "公顷", "亩",
                       "播种", "收获", "灌溉", "病虫害", "除草", "密度"],
            "畜牧业": ["生猪", "牛羊", "家禽", "奶牛", "出栏", "存栏", "饲料", "日龄", "增重", "料肉比", "免疫", "兽药",
                       "疫病", "繁育", "犊牛", "屠宰"],
            "农资与土壤": ["肥料", "氮肥", "磷肥", "钾肥", "配方施肥", "有机质", "pH", "土壤盐分", "微量元素", "保水",
                           "覆盖", "深松", "秸秆还田"],
            "农业金融": ["采购", "成本", "贷款", "保单", "保险", "赔付", "保费", "授信", "现金流", "应收", "应付",
                         "利润", "毛利率", "价格", "期货"],
            "供应链与仓储": ["冷链", "仓储", "物流", "运输", "库容", "损耗", "周转", "交付", "订单", "批次", "追溯"],
            "气候与遥感": ["降雨", "降水", "温度", "积温", "蒸散", "干旱", "NDVI", "EVI", "卫星", "遥感", "气象站",
                           "辐射", "沙漠蝗虫", "草地贪夜蛾"],
            "农业物联网": ["传感器", "湿度", "含水率", "EC", "阈值", "阀门", "泵站", "滴灌", "喷灌", "自动化", "报警"]
        }

        # 初始化DeepSeek API密钥（从环境变量或Streamlit secrets获取）
        import os
        self.deepseek_api_key = ''
        # 优先从环境变量读取
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY', '')
        # 如果环境变量没有，尝试从Streamlit secrets读取
        if not self.deepseek_api_key:
            try:
                if hasattr(st, 'secrets') and st.secrets:
                    self.deepseek_api_key = st.secrets.get('DEEPSEEK_API_KEY', '')
            except Exception as e:
                # 如果读取secrets失败，记录但不中断初始化
                pass
        # 清理密钥（去除可能的空格）
        if self.deepseek_api_key:
            self.deepseek_api_key = self.deepseek_api_key.strip()
        self.deepseek_api_url = "https://api.deepseek.com/v1/chat/completions"
        self.deepseek_model = "deepseek-chat"  # 或 "deepseek-coder" 用于代码生成
        # 注意：如果使用DeepSeek-V3，模型名称应为 "deepseek-chat"

        # 初始化OCR - 仅使用Tesseract OCR（轻量级，无需加载模型）
        self.ocr_available = TESSERACT_AVAILABLE
        self.ocr_load_failed = False
        
        if TESSERACT_AVAILABLE:
            print(f"[DEBUG] ✅ OCR初始化 - 使用Tesseract OCR（轻量级，内存占用约50-100MB，无需加载模型）")
        else:
            import platform
            system = platform.system()
            print(f"[DEBUG] ⚠️ OCR初始化 - Tesseract不可用")
            if system == "Windows":
                print(f"[DEBUG] 💡 Windows安装说明:")
                print(f"[DEBUG]    1. 下载安装: https://github.com/UB-Mannheim/tesseract/wiki")
                print(f"[DEBUG]    2. 安装时选择中文语言包")
                print(f"[DEBUG]    3. 添加到系统PATH")
                print(f"[DEBUG]    4. 详细说明: INSTALL_TESSERACT_WINDOWS.md")
            elif system == "Linux":
                print(f"[DEBUG] 💡 Linux安装: sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim")
            elif system == "Darwin":  # macOS
                print(f"[DEBUG] 💡 macOS安装: brew install tesseract")
            print(f"[DEBUG] 💡 Python依赖: pip install pytesseract Pillow")

        # 初始化文本分类模型
        self.text_classifier = None
        if TRANSFORMERS_AVAILABLE:
            try:
                # 使用中文BERT模型进行文本分类
                self.text_classifier = pipeline(
                    "text-classification",
                    model="bert-base-chinese",
                    tokenizer="bert-base-chinese"
                )
                st.success("✅ BERT text classification model loaded successfully")
            except Exception as e:
                # Downgrade to info to avoid noisy toast; rules/ML will fallback
                pass  # 静默失败，使用回退方案
        # else:
        #     st.info("ℹ️ Transformers library not installed, using machine learning classification")

        # 初始化摘要生成模型
        self.summarizer = None
        if TRANSFORMERS_AVAILABLE:
            try:
                # 使用T5模型进行摘要生成
                self.summarizer = pipeline(
                    "summarization",
                    model="t5-small",
                    tokenizer="t5-small"
                )
                st.success("✅ T5 summarization model loaded successfully")
            except Exception as e:
                # 静默失败，使用智能规则
                pass
        # else:
        #     st.info("ℹ️ Using smart summarization algorithm")

        # 初始化机器学习分类器
        self.ml_classifier = None
        self.ml_trained = False
        if ML_AVAILABLE:
            try:
                # 使用朴素贝叶斯分类器
                self.ml_classifier = Pipeline([
                    ('tfidf', TfidfVectorizer(max_features=1000, stop_words=None)),
                    ('classifier', MultinomialNB())
                ])
                # 自动初始化预训练分类器
                if self.init_pretrained_classifier():
                    # 成功时静默，避免过多提示
                    pass
                # else:
                #     st.info("Pre-trained ML classifier unavailable, using keyword matching")
            except Exception as e:
                # 静默失败，使用关键词匹配
                pass
        # else:
        #     st.info("ℹ️ 使用关键词匹配分类")

        # 初始化默认行业分类
        self.init_default_categories()

    def fetch_weather_summary(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """从 Open-Meteo 获取未来7天的气象摘要（无需API密钥）"""
        try:
            url = (
                "https://api.open-meteo.com/v1/forecast"
                f"?latitude={latitude}&longitude={longitude}"
                "&hourly=temperature_2m,precipitation"
                "&daily=precipitation_sum,temperature_2m_max,temperature_2m_min"
                "&forecast_days=7&timezone=auto"
            )
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            daily = data.get("daily", {})
            result = {
                "location": {"lat": latitude, "lon": longitude},
                "precipitation_sum": daily.get("precipitation_sum", []),
                "tmax": daily.get("temperature_2m_max", []),
                "tmin": daily.get("temperature_2m_min", []),
                "dates": daily.get("time", [])
            }
            # 简要统计
            try:
                total_rain = float(sum(x for x in result["precipitation_sum"] if isinstance(x, (int, float))))
            except Exception:
                total_rain = 0.0
            result["summary"] = {
                "7d_total_rain_mm": round(total_rain, 1),
                "avg_tmax": round(sum(result["tmax"]) / max(1, len(result["tmax"])), 1) if result["tmax"] else None,
                "avg_tmin": round(sum(result["tmin"]) / max(1, len(result["tmin"])), 1) if result["tmin"] else None,
            }
            self.latest_weather = result
            return {"success": True, "weather": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def compute_remote_sensing_stub(self, latitude: float, longitude: float, days: int = 30) -> Dict[str, Any]:
        """遥感指数占位：生成近days天的NDVI/EVI简易时序（无需外部服务）。"""
        try:
            import math
            base_date = datetime.now()
            dates = [(base_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days - 1, -1, -1)]
            ndvi = []
            evi = []
            for i in range(days):
                # 生成平滑的波动数据，范围做物理合理约束
                v = 0.5 + 0.3 * math.sin(i / 6.0) + 0.1 * math.sin(i / 2.5)
                ndvi.append(round(max(0.0, min(0.9, v)), 3))
                e = 0.4 + 0.25 * math.sin(i / 7.0 + 0.5)
                evi.append(round(max(0.0, min(0.8, e)), 3))
            summary = {
                "ndvi_avg": round(sum(ndvi) / len(ndvi), 3) if ndvi else None,
                "evi_avg": round(sum(evi) / len(evi), 3) if evi else None,
                "ndvi_last": ndvi[-1] if ndvi else None,
                "evi_last": evi[-1] if evi else None,
            }
            result = {
                "location": {"lat": latitude, "lon": longitude},
                "dates": dates,
                "ndvi": ndvi,
                "evi": evi,
                "summary": summary,
            }
            self.latest_remote_sensing = result
            return {"success": True, "remote_sensing": result}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def extract_agri_structured_fields(self, text: str) -> Dict[str, Any]:
        """农业报表模板抽取（规则版占位）：作物、面积、日期、施肥/灌溉/用药/单产等。"""
        if not text:
            return {}
        import re
        fields: Dict[str, Any] = {}
        try:
            # 作物
            m = re.search(r'(作物|品种|作物名称)[：:，]\s*([\u4e00-\u9fffA-Za-z0-9]+)', text)
            if m: fields['作物'] = m.group(2)
            # 面积（亩/公顷/ha）
            m = re.search(r'(面积|播种面积|收获面积)[：:，]\s*([\d,.]+)\s*(亩|公顷|ha)', text)
            if m: fields['面积'] = f"{m.group(2)} {m.group(3)}"
            # 日期（简单识别 年-月-日 或 年/月/日 或 中文）
            m = re.search(r'(日期|时间|记录时间)[：:，]\s*(\d{4}[-年/]\d{1,2}[-月/]\d{1,2})', text)
            if m: fields['日期'] = m.group(2)
            # 施肥
            m = re.search(r'(施肥|肥料|配方施肥)[：:，]?\s*([\u4e00-\u9fffA-Za-z0-9]+)?\s*([\d,.]+)\s*(kg|公斤|斤)', text)
            if m: fields['施肥'] = f"{(m.group(2) or '').strip()} {m.group(3)} {m.group(4)}".strip()
            # 灌溉
            m = re.search(r'(灌溉|浇水)[：:，]?\s*([\d,.]+)\s*(mm|立方|m3|方)', text)
            if m: fields['灌溉'] = f"{m.group(2)} {m.group(3)}"
            # 用药
            m = re.search(r'(农药|用药|防治)[：:，]?\s*([\u4e00-\u9fffA-Za-z0-9]+)\s*([\d,.]+)\s*(ml|毫升|L|升|kg|克|g)',
                          text)
            if m: fields['用药'] = f"{m.group(2)} {m.group(3)} {m.group(4)}"
            # 单产/产量
            m = re.search(r'(单产|亩产)[：:，]\s*([\d,.]+)\s*(斤/亩|公斤/亩|kg/ha|t/ha)', text)
            if m: fields['单产'] = f"{m.group(2)} {m.group(3)}"
            m = re.search(r'(总产|产量)[：:，]\s*([\d,.]+)\s*(kg|吨|t)', text)
            if m: fields['产量'] = f"{m.group(2)} {m.group(3)}"
        except Exception:
            pass
        return fields

    def init_default_categories(self):
        """初始化默认行业分类"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for category, keywords in self.industry_keywords.items():
            cursor.execute('''
                INSERT OR IGNORE INTO industry_categories (category_name, keywords, description)
                VALUES (?, ?, ?)
            ''', (category, json.dumps(keywords, ensure_ascii=False), f"{category}相关文档"))

        conn.commit()
        conn.close()

    def _to_english_category(self, category: str) -> str:
        """将分类名称转换为英文（统一存储格式）"""
        mapping = {
            "种植业": "Planting",
            "畜牧业": "Livestock",
            "农资与土壤": "Inputs-Soil",
            "农业金融": "Agri-Finance",
            "供应链与仓储": "SupplyChain-Storage",
            "气候与遥感": "Climate-RemoteSensing",
            "农业物联网": "Agri-IoT",
            "未分类": "Unclassified",  # 添加未分类的映射
        }
        # 如果不在映射表中，检查是否已经是英文分类名称
        if category in mapping:
            return mapping[category]
        # 如果已经是英文分类名称，直接返回
        english_categories = ["Planting", "Livestock", "Inputs-Soil", "Agri-Finance", 
                            "SupplyChain-Storage", "Climate-RemoteSensing", "Agri-IoT", "Unclassified"]
        if category in english_categories:
            return category
        # 否则返回Unclassified作为默认值
        return "Unclassified"
    
    def _extract_classification_from_ai_response(self, ai_response: str, extracted_text: str) -> Optional[Dict[str, Any]]:
        """从DeepSeek AI响应中提取行业分类，只返回与工业视图匹配的标签"""
        try:
            import re
            
            # 定义有效的分类标签（与工业视图一致）
            valid_categories = ["Planting", "Livestock", "Inputs-Soil", "Agri-Finance", 
                              "SupplyChain-Storage", "Climate-RemoteSensing", "Agri-IoT", "Unclassified"]
            
            # 首先尝试使用正则表达式直接提取明确的分类声明
            pattern = r'(?:Industry\s*(?:Classification|Category)?\s*:?\s*|分类\s*:?\s*)([A-Za-z-]+)'
            match = re.search(pattern, ai_response, re.IGNORECASE)
            if match:
                category_name = match.group(1).strip()
                # 标准化分类名称
                category_mapping = {
                    "planting": "Planting",
                    "livestock": "Livestock",
                    "inputs-soil": "Inputs-Soil",
                    "inputsoil": "Inputs-Soil",
                    "agri-finance": "Agri-Finance",
                    "agrifinance": "Agri-Finance",
                    "supplychain-storage": "SupplyChain-Storage",
                    "supplychainstorage": "SupplyChain-Storage",
                    "climate-remotesensing": "Climate-RemoteSensing",
                    "climateremotesensing": "Climate-RemoteSensing",
                    "agri-iot": "Agri-IoT",
                    "agriiot": "Agri-IoT",
                    "unclassified": "Unclassified"
                }
                normalized_category = category_mapping.get(category_name.lower())
                if normalized_category and normalized_category in valid_categories:
                    print(f"[DEBUG] _extract_classification_from_ai_response: 从AI响应中直接提取分类: {normalized_category}")
                    return {
                        "category": normalized_category,
                        "confidence": 0.8,
                        "method": "AI Response Direct Extraction"
                    }
            
            # 如果无法直接提取，使用关键词匹配（使用与classify_industry相同的关键词）
            combined_text = (ai_response + " " + extracted_text).lower()
            category_scores = {}
            
            for category, keywords in self.industry_keywords.items():
                score = 0
                for keyword in keywords:
                    count = combined_text.count(keyword.lower())
                    if count > 0:
                        score += count
                category_scores[category] = score
            
            # 找到得分最高的分类
            if category_scores and max(category_scores.values()) > 0:
                best_category = max(category_scores, key=category_scores.get)
                max_score = category_scores[best_category]
                
                # 计算置信度
                total_keywords = len(self.industry_keywords[best_category])
                confidence = min(max_score / (total_keywords * 1.5), 1.0)
                
                # 如果置信度低于阈值，直接返回Unclassified
                if confidence < 0.1:
                    print(f"[DEBUG] _extract_classification_from_ai_response: 置信度太低 ({confidence:.2f})，返回Unclassified")
                    return {"category": "Unclassified", "confidence": 0.0, "method": "AI Response (Low Confidence)"}
                
                # 转换为英文分类名称
                eng_category = self._to_english_category(best_category)
                
                print(f"[DEBUG] _extract_classification_from_ai_response: 从AI响应中关键词匹配分类: {eng_category}, 置信度: {confidence:.2f}")
                return {
                    "category": eng_category,
                    "confidence": confidence,
                    "method": "AI Response Keyword Matching"
                }
            else:
                print(f"[DEBUG] _extract_classification_from_ai_response: 无法从AI响应中提取分类，返回Unclassified")
                return {"category": "Unclassified", "confidence": 0.0, "method": "AI Response (No Match)"}
                
        except Exception as e:
            print(f"[DEBUG] _extract_classification_from_ai_response: 错误: {str(e)}")
            return {"category": "Unclassified", "confidence": 0.0, "method": "AI Response (Error)"}

    def generate_smart_report(self, file_id: int) -> Dict[str, Any]:
        """生成智能报告和图表"""
        try:
            # 获取文件信息
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT file_path, file_type, filename FROM files WHERE id = ?', (file_id,))
            result = cursor.fetchone()
            conn.close()

            if not result:
                return {"success": False, "error": "文件不存在"}

            file_path, file_type, filename = result

            # 提取文本内容
            text = self.extract_text_from_file(file_id)
            if not text:
                return {"success": False, "error": "无法提取文本内容"}

            # 分析文档结构
            analysis = self.analyze_document_structure(text)
            analysis["full_text"] = text

            # 提取数据点
            data_points = self.extract_data_points(text)

            # 生成图表
            charts = self.generate_charts(data_points)

            # 生成报告
            report = self.create_smart_report(analysis, charts, filename)

            return {
                "success": True,
                "analysis": analysis,
                "data_points": data_points,
                "charts": charts,
                "report": report
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def call_deepseek_api(self, messages: List[Dict[str, str]], max_tokens: int = 2000, temperature: float = 0.7) -> Optional[str]:
        """调用DeepSeek API进行对话"""
        if not self.deepseek_api_key:
            return None
        
        # 清理API密钥（去除可能的空格和换行符）
        api_key = self.deepseek_api_key.strip()
        if not api_key:
            st.error("DeepSeek API key is empty, please check configuration")
            return None
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": self.deepseek_model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }
            
            # 调试信息（仅在开发时显示）
            if st.session_state.get('debug_mode', False):
                st.write(f"API URL: {self.deepseek_api_url}")
                st.write(f"Model: {self.deepseek_model}")
                st.write(f"API Key (前10位): {api_key[:10]}...")
            
            response = requests.post(
                self.deepseek_api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    choice = result['choices'][0]
                    content = choice['message']['content']
                    
                    # 检查响应是否完整
                    finish_reason = choice.get('finish_reason', '')
                    if finish_reason == 'length':
                        # 响应因达到max_tokens限制而被截断
                        st.warning("⚠️ AI response was truncated due to token limit. Consider increasing max_tokens or asking a more specific question.")
                        # 仍然返回内容，但添加提示
                        return content + "\n\n[Note: Response may be incomplete due to token limit]"
                    elif finish_reason == 'stop':
                        # 正常完成
                        return content
                    else:
                        # 其他情况，仍然返回内容
                        return content
                else:
                    st.warning(f"API response format abnormal: {result}")
                    return None
            elif response.status_code == 401:
                error_msg = "DeepSeek API authentication failed"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = f"Authentication failed: {error_data['error'].get('message', 'Invalid API key')}"
                except:
                    error_msg = f"Authentication failed: {response.text}"
                st.error(error_msg)
                st.info("💡 Please check:\n1. Is the API key correct (in .secrets.toml)?\n2. Is the API key valid and not expired?\n3. Is the key format correct (should start with sk-)?")
                return None
            else:
                error_msg = f"DeepSeek API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = f"{error_msg} - {error_data['error'].get('message', response.text)}"
                except:
                    error_msg = f"{error_msg} - {response.text}"
                st.error(error_msg)
                return None
                
        except requests.exceptions.Timeout:
            st.error("DeepSeek API request timeout, please check network connection")
            return None
        except requests.exceptions.ConnectionError:
            st.error("Unable to connect to DeepSeek API, please check network connection")
            return None
        except Exception as e:
            st.error(f"Failed to call DeepSeek API: {str(e)}")
            return None

    def generate_ai_report(self, file_id: int, user_question) -> Dict[str, Any]:
        """使用DeepSeek AI生成智能报告和回答用户问题
        
        处理逻辑：
        1. 文档类（.txt, .docx等）：直接读取文档内容，结合用户问题提问
        2. 图片或PDF：先用Tesseract OCR进行提取，然后结合用户问题发给deepseek
        3. Excel或xlsx：保留原来的分析程序
        """
        try:
            if not self.deepseek_api_key:
                return {"success": False, "error": "未配置DeepSeek API密钥，请在环境变量或Streamlit secrets中设置DEEPSEEK_API_KEY"}
            
            start_time = time.time()
            # 获取文件信息
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT file_path, file_type, filename FROM files WHERE id = ?', (file_id,))
            result = cursor.fetchone()
            conn.close()

            if not result:
                return {"success": False, "error": "文件不存在"}

            file_path, file_type, filename = result
            print(f"[DEBUG] generate_ai_report: 开始处理 - file_id: {file_id}, file_type: {file_type}, filename: {filename}")

            # 提取文件内容
            file_content = ""
            df = None
            
            # ========== 逻辑1: Excel/CSV文件 - 保留原来的分析程序 ==========
            if filename.endswith(('.xlsx', '.xls', '.csv')):
                print(f"[DEBUG] generate_ai_report: 检测到Excel/CSV文件，使用原有分析程序")
                df = self.extract_excel_csv(file_id)
                if df is not None:
                    # 将DataFrame转换为文本描述
                    file_content = f"文件类型: Excel/CSV\n"
                    file_content += f"文件名: {filename}\n"
                    file_content += f"数据形状: {df.shape[0]}行 x {df.shape[1]}列\n"
                    file_content += f"列名: {', '.join(df.columns.tolist())}\n\n"
                    file_content += f"数据预览（前10行）:\n{df.head(10).to_string()}\n\n"
                    file_content += f"数据统计信息:\n{df.describe().to_string()}\n\n"
                    # 如果数据量不大，包含完整数据
                    if len(df) <= 100:
                        file_content += f"完整数据:\n{df.to_string()}\n"
                    print(f"[DEBUG] generate_ai_report: Excel/CSV数据提取完成，内容长度: {len(file_content)}")
                else:
                    return {"success": False, "error": "无法读取Excel/CSV文件，请确保文件格式正确"}
            
            # ========== 逻辑2: 图片或PDF文件 - 优先使用数据库中的OCR内容 ==========
            elif file_type == 'image' or (file_type == 'application' and filename.endswith('.pdf')):
                print(f"[DEBUG] generate_ai_report: 检测到图片或PDF文件，优先使用数据库中的OCR内容")
                
                # 先尝试从数据库读取OCR内容
                conn_ocr = sqlite3.connect(self.db_path)
                cursor_ocr = conn_ocr.cursor()
                cursor_ocr.execute('''
                    SELECT ocr_content FROM ai_analysis 
                    WHERE file_id = ? AND ocr_content IS NOT NULL AND ocr_content != ''
                    ORDER BY analysis_time DESC LIMIT 1
                ''', (file_id,))
                ocr_result = cursor_ocr.fetchone()
                conn_ocr.close()
                
                if ocr_result and ocr_result[0]:
                    # 使用数据库中的OCR内容
                    ocr_text = ocr_result[0]
                    print(f"[DEBUG] generate_ai_report: ✅ 从数据库读取OCR内容，长度: {len(ocr_text)}")
                    file_content = f"File Type: {'Image' if file_type == 'image' else 'PDF'}\n"
                    file_content += f"Filename: {filename}\n\n"
                    file_content += f"OCR Recognized Text:\n{ocr_text}"
                    st.info("✅ 使用已保存的OCR内容（无需重新识别）")
                elif OCR_AVAILABLE and TESSERACT_AVAILABLE:
                    # 数据库中没有OCR内容，执行OCR提取
                    print(f"[DEBUG] generate_ai_report: 数据库中没有OCR内容，开始执行OCR提取")
                
                    try:
                        # 延迟加载OCR模型
                        if not self._load_ocr_model():
                            print(f"[DEBUG] generate_ai_report: OCR模型加载失败，跳过OCR提取")
                            file_content = f"File Type: {'Image' if file_type == 'image' else 'PDF'}\n"
                            file_content += f"Filename: {filename}\n"
                            file_content += f"Note: OCR model loading failed, unable to extract text from file."
                            st.warning("⚠️ OCR model loading failed, skipping OCR extraction")
                        else:
                            # 对于PDF文件，需要先转换为图片
                            ocr_file_path = file_path
                            is_pdf = filename.endswith('.pdf')
                            temp_images = []
                            
                            if is_pdf and PDF_AVAILABLE and fitz is not None:
                                print(f"[DEBUG] generate_ai_report: PDF文件，先转换为图片...")
                                try:
                                    doc = fitz.open(file_path)
                                    all_ocr_text = []
                                    
                                    # 限制PDF页数，避免内存溢出
                                    max_pages = min(len(doc), 10)  # 最多处理10页
                                    if len(doc) > max_pages:
                                        print(f"[DEBUG] generate_ai_report: PDF有{len(doc)}页，只处理前{max_pages}页以节省内存")
                                        st.info(f"📄 PDF has {len(doc)} pages, processing first {max_pages} pages to save memory")
                                    
                                    with st.spinner("🔍 Converting PDF to images and recognizing text..."):
                                        for page_num in range(max_pages):
                                            try:
                                                page = doc[page_num]
                                                # 降低缩放比例以节省内存（从2倍降到1.5倍）
                                                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                                                img_data = pix.tobytes("png")
                                                
                                                # 检查图片大小，如果太大则跳过
                                                img_size_mb = len(img_data) / (1024 * 1024)
                                                if img_size_mb > 10:  # 如果单页图片超过10MB，跳过
                                                    print(f"[DEBUG] generate_ai_report: PDF第{page_num + 1}页图片过大({img_size_mb:.2f}MB)，跳过")
                                                    continue
                                                
                                                # 保存临时图片
                                                import tempfile
                                                import os
                                                temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                                                temp_img.write(img_data)
                                                temp_img.close()
                                                temp_images.append(temp_img.name)
                                                
                                                # 对每页进行OCR
                                                print(f"[DEBUG] generate_ai_report: 处理PDF第 {page_num + 1} 页...")
                                                try:
                                                    page_results = self._ocr_readtext(temp_img.name)
                                                    
                                                    if page_results and len(page_results) > 0:
                                                        page_text = ' '.join([result[1] for result in page_results])
                                                        all_ocr_text.append(f"Page {page_num + 1}:\n{page_text}")
                                                except MemoryError as e:
                                                    print(f"[DEBUG] generate_ai_report: PDF第{page_num + 1}页OCR内存不足: {str(e)}")
                                                    st.warning(f"⚠️ Page {page_num + 1} OCR failed due to insufficient memory")
                                                    break  # 内存不足时停止处理
                                                except Exception as e:
                                                    print(f"[DEBUG] generate_ai_report: PDF第{page_num + 1}页OCR失败: {str(e)}")
                                                    # 继续处理下一页
                                                    continue
                                            except MemoryError as e:
                                                print(f"[DEBUG] generate_ai_report: PDF第{page_num + 1}页处理内存不足: {str(e)}")
                                                st.warning(f"⚠️ Page {page_num + 1} processing failed due to insufficient memory")
                                                break
                                            except Exception as e:
                                                print(f"[DEBUG] generate_ai_report: PDF第{page_num + 1}页处理失败: {str(e)}")
                                                continue
                                    
                                    doc.close()
                                    
                                    # 清理临时图片
                                    for temp_img_path in temp_images:
                                        try:
                                            os.unlink(temp_img_path)
                                        except:
                                            pass
                                    
                                    if all_ocr_text:
                                        ocr_text = '\n\n'.join(all_ocr_text)
                                        print(f"[DEBUG] generate_ai_report: ✅ PDF OCR识别成功，共 {len(all_ocr_text)} 页，文字长度: {len(ocr_text)}")
                                        file_content = f"File Type: PDF\n"
                                        file_content += f"Filename: {filename}\n\n"
                                        file_content += f"OCR Recognized Text:\n{ocr_text}"
                                        st.success(f"✅ PDF OCR recognition successful, recognized {len(all_ocr_text)} pages")
                                    else:
                                        print(f"[DEBUG] generate_ai_report: ⚠️ PDF OCR未识别到文字")
                                        file_content = f"File Type: PDF\n"
                                        file_content += f"Filename: {filename}\n"
                                        file_content += f"Note: No text content recognized in PDF, may be a scanned PDF or unclear text."
                                        st.warning("⚠️ PDF OCR did not recognize any text content")
                                        
                                except Exception as pdf_error:
                                    print(f"[DEBUG] generate_ai_report: PDF处理失败: {str(pdf_error)}")
                                    # 清理临时图片
                                    for temp_img_path in temp_images:
                                        try:
                                            import os
                                            os.unlink(temp_img_path)
                                        except:
                                            pass
                                    raise pdf_error
                            else:
                                # 图片文件直接OCR
                                print(f"[DEBUG] generate_ai_report: 开始OCR识别图片: {file_path}")
                                
                                # 检查图片大小和尺寸，如果太大则缩放
                                try:
                                    from PIL import Image
                                    img = Image.open(file_path)
                                    img_width, img_height = img.size
                                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                                    
                                    print(f"[DEBUG] generate_ai_report: 图片尺寸: {img_width}x{img_height}, 文件大小: {file_size_mb:.2f}MB")
                                    
                                    # 如果图片太大，进行缩放
                                    max_dimension = 2000  # 最大尺寸2000像素
                                    max_file_size_mb = 5  # 最大文件大小5MB
                                    
                                    if img_width > max_dimension or img_height > max_dimension or file_size_mb > max_file_size_mb:
                                        print(f"[DEBUG] generate_ai_report: 图片过大，进行缩放...")
                                        st.info(f"📷 Image is large ({img_width}x{img_height}, {file_size_mb:.1f}MB), resizing for OCR...")
                                        
                                        # 计算缩放比例
                                        scale = min(max_dimension / img_width, max_dimension / img_height)
                                        new_width = int(img_width * scale)
                                        new_height = int(img_height * scale)
                                        
                                        # 缩放图片
                                        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                                        
                                        # 保存到临时文件
                                        import tempfile
                                        temp_img_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                                        temp_img_path.close()
                                        img_resized.save(temp_img_path.name, 'PNG')
                                        
                                        ocr_file_path = temp_img_path.name
                                        temp_images.append(ocr_file_path)
                                        print(f"[DEBUG] generate_ai_report: 图片已缩放至: {new_width}x{new_height}")
                                    else:
                                        ocr_file_path = file_path
                                except Exception as e:
                                    print(f"[DEBUG] generate_ai_report: 图片检查失败: {str(e)}，使用原始文件")
                                    ocr_file_path = file_path
                                
                                try:
                                    with st.spinner("🔍 Recognizing text in image..."):
                                        results = self._ocr_readtext(ocr_file_path)
                                    print(f"[DEBUG] generate_ai_report: OCR识别完成，结果数量: {len(results) if results else 0}")
                                except MemoryError as e:
                                    print(f"[DEBUG] generate_ai_report: OCR识别内存不足: {str(e)}")
                                    st.error("❌ OCR recognition failed: Insufficient memory. The image may be too large.")
                                    file_content = f"File Type: Image\n"
                                    file_content += f"Filename: {filename}\n"
                                    file_content += f"Note: OCR recognition failed due to insufficient memory. Please try with a smaller image or disable OCR."
                                    raise  # 重新抛出异常以便外层处理
                                except Exception as e:
                                    print(f"[DEBUG] generate_ai_report: OCR识别失败: {str(e)}")
                                    raise  # 重新抛出异常以便外层处理
                                
                                if results and len(results) > 0:
                                    ocr_text = ' '.join([result[1] for result in results])
                                    print(f"[DEBUG] generate_ai_report: ✅ OCR识别成功，文字长度: {len(ocr_text)}")
                                    print(f"[DEBUG] generate_ai_report: OCR文字预览: {ocr_text[:200]}...")
                                    
                                    file_content = f"File Type: Image\n"
                                    file_content += f"Filename: {filename}\n\n"
                                    file_content += f"OCR Recognized Text:\n{ocr_text}"
                                    
                                    st.success(f"✅ OCR recognition successful, recognized {len(results)} text regions")
                                else:
                                    print(f"[DEBUG] generate_ai_report: ⚠️ OCR未识别到文字")
                                    file_content = f"File Type: Image\n"
                                    file_content += f"Filename: {filename}\n"
                                    file_content += f"Note: No text content recognized in image, may be a pure image or unclear text."
                                    st.warning("⚠️ OCR did not recognize any text content")
                            
                    except Exception as e:
                        print(f"[DEBUG] generate_ai_report: ❌ OCR识别失败: {str(e)}")
                        import traceback
                        print(f"[DEBUG] generate_ai_report: 错误堆栈:\n{traceback.format_exc()}")
                        file_content = f"File Type: {'Image' if file_type == 'image' else 'PDF'}\n"
                        file_content += f"Filename: {filename}\n"
                        file_content += f"Note: OCR recognition failed ({str(e)}), unable to extract text from file."
                        st.error(f"❌ OCR recognition failed: {str(e)}")
                else:
                    print(f"[DEBUG] generate_ai_report: OCR不可用")
                    file_content = f"File Type: {'Image' if file_type == 'image' else 'PDF'}\n"
                    file_content += f"Filename: {filename}\n"
                    file_content += f"Note: OCR feature unavailable, unable to recognize text in file. Please install Tesseract OCR. See INSTALL_TESSERACT.md for details."
                    st.warning("⚠️ OCR feature unavailable. Please install Tesseract OCR. See INSTALL_TESSERACT.md for details.")
            
            # ========== 逻辑3: 文档类文件 - 直接读取文档内容 ==========
            else:
                print(f"[DEBUG] generate_ai_report: 检测到文档类文件，直接读取内容")
                file_content = self.extract_text_from_file(file_id)
                print(f"[DEBUG] generate_ai_report: 文档内容提取完成，长度: {len(file_content) if file_content else 0}")
                
                if not file_content or file_content.startswith("(No extractable text"):
                    print(f"[DEBUG] generate_ai_report: ⚠️ 无法提取文档内容")
                    file_content = f"文件类型: {file_type}\n"
                    file_content += f"文件名: {filename}\n"
                    file_content += f"注意: 无法直接提取此文件类型的文本内容，请尝试预览或下载文件查看。\n"
            
            # 验证文件内容
            if not file_content:
                print(f"[DEBUG] generate_ai_report: ❌ 最终无法获取文件内容")
                return {"success": False, "error": "无法提取文件内容，请确保文件格式支持"}
            
            print(f"[DEBUG] generate_ai_report: ✅ 文件内容提取完成，内容长度: {len(file_content)}")

            # 构建提示词
            system_prompt = """You are a professional data analysis assistant. Please answer the user's questions based on the content of the uploaded file.
If the file is Excel or CSV data, please provide detailed data analysis, statistical information, and insights.
If the file is a document, please answer questions based on the document content.
Please answer in English, be accurate, detailed, and well-organized."""

            # 限制内容长度避免超出token限制
            file_content_limited = file_content[:8000]
            user_prompt = f"""File content:
{file_content_limited}

User question: {user_question}

Please answer the user's question based on the above file content."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # 调用DeepSeek API - 增加max_tokens以确保完整响应
            with st.spinner("🤔 DeepSeek AI is analyzing the file and generating response..."):
                ai_response = self.call_deepseek_api(messages, max_tokens=4000, temperature=0.7)
            
            generation_time = time.time() - start_time

            if ai_response:
                st.success(f"✅ AI analysis completed, took {generation_time:.2f} seconds")
                
                # Display AI response
                st.markdown("#### 🤖 AI Analysis Results")
                st.markdown(ai_response)
                
                # 如果是数据文件，还可以生成可视化
                if df is not None and len(df) > 0:
                    with st.expander("📊 Data Visualization (Optional)"):
                        try:
                            plt.close('all')
                            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
                            
                            # 数值列的分布
                            numeric_cols = df.select_dtypes(include=[np.number]).columns
                            if len(numeric_cols) > 0:
                                col = numeric_cols[0]
                                axes[0, 0].hist(df[col].dropna(), bins=20, alpha=0.7, color='#667eea')
                                axes[0, 0].set_title(f'{col} 分布')
                                axes[0, 0].set_xlabel(col)
                                axes[0, 0].set_ylabel('频数')
                            
                            # 相关性热力图（如果有多个数值列）
                            if len(numeric_cols) > 1:
                                corr_matrix = df[numeric_cols].corr()
                                im = axes[0, 1].imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
                                axes[0, 1].set_xticks(range(len(corr_matrix.columns)))
                                axes[0, 1].set_yticks(range(len(corr_matrix.columns)))
                                axes[0, 1].set_xticklabels(corr_matrix.columns, rotation=45)
                                axes[0, 1].set_yticklabels(corr_matrix.columns)
                                axes[0, 1].set_title('相关性矩阵')
                                plt.colorbar(im, ax=axes[0, 1])
                            
                            # 分类列的计数
                            categorical_cols = df.select_dtypes(include=['object']).columns
                            if len(categorical_cols) > 0:
                                col = categorical_cols[0]
                                value_counts = df[col].value_counts().head(10)
                                axes[1, 0].bar(range(len(value_counts)), value_counts.values, color='#764ba2')
                                axes[1, 0].set_xticks(range(len(value_counts)))
                                axes[1, 0].set_xticklabels(value_counts.index, rotation=45, ha='right')
                                axes[1, 0].set_title(f'{col} 计数')
                                axes[1, 0].set_ylabel('数量')
                            
                            # 散点图（如果有两个数值列）
                            if len(numeric_cols) >= 2:
                                axes[1, 1].scatter(df[numeric_cols[0]], df[numeric_cols[1]], alpha=0.6, color='#667eea')
                                axes[1, 1].set_xlabel(numeric_cols[0])
                                axes[1, 1].set_ylabel(numeric_cols[1])
                                axes[1, 1].set_title(f'{numeric_cols[0]} vs {numeric_cols[1]}')
                            
                            plt.tight_layout()
                            st.pyplot(fig)
                        except Exception as e:
                            st.warning(f"Error generating visualization: {str(e)}")

                return {
                    "success": True,
                    "response": ai_response,
                    "generation_time": generation_time
                }
            else:
                return {"success": False, "error": "DeepSeek API call failed, please check API key and network connection"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}



    def analyze_document_structure(self, text: str) -> Dict[str, Any]:
        """分析文档结构，识别农业领域文档类型与要素"""
        analysis = {
            "document_type": "未知",
            "data_types": [],
            "key_metrics": [],
            "time_periods": [],
            "categories": [],
            "confidence": 0.0
        }

        # 识别农业文档类型
        if any(k in text for k in ["单产", "亩产", "t/ha", "kg/ha", "播种面积", "收获面积", "产量"]):
            analysis["document_type"] = "种植业生产报告"
            analysis["data_types"].extend(["面积", "产量", "单产", "趋势"])
        elif any(k in text for k in ["出栏", "存栏", "增重", "日增重", "料肉比", "免疫"]):
            analysis["document_type"] = "畜牧业生产报告"
            analysis["data_types"].extend(["头数", "重量", "转换率", "免疫"])
        elif any(k in text for k in ["降雨", "降水", "mm", "积温", "干旱", "NDVI", "遥感"]):
            analysis["document_type"] = "气候与遥感监测"
            analysis["data_types"].extend(["降雨", "温度", "指数", "时间序列"])
        elif any(k in text for k in ["成本", "采购", "价格", "保险", "赔付", "利润", "毛利率"]):
            analysis["document_type"] = "农业财务/供应链报告"
            analysis["data_types"].extend(["金额", "比率", "对比", "价格趋势"])

        # 提取关键指标
        import re
        # 查找数字模式（支持带单位）
        numbers = re.findall(r'[\d,]+\.?\d*\s*(?:t/ha|kg/ha|kg|t|吨|公斤|元/斤|元/吨|mm)?', text)
        analysis["key_metrics"] = numbers[:10]  # 取前10个数字

        # 查找时间模式
        time_patterns = re.findall(r'\d{4}年|\d{1,2}月|\d{1,2}日|Q[1-4]', text)
        analysis["time_periods"] = list(set(time_patterns))

        # 查找分类信息
        category_patterns = re.findall(r'[A-Za-z\u4e00-\u9fff]+[：:]\s*[\d,]+', text)
        analysis["categories"] = category_patterns[:5]

        # 计算置信度（农业场景稍微提高关键指标权重）
        confidence = min(len(analysis["key_metrics"]) * 0.12 +
                         len(analysis["time_periods"]) * 0.18 +
                         len(analysis["categories"]) * 0.1, 1.0)
        analysis["confidence"] = confidence

        return analysis

    def extract_data_points(self, text: str) -> List[Dict[str, Any]]:
        """提取数据点用于生成图表（增强农业单位识别）"""
        data_points = []

        import re

        # 提取数值和标签
        patterns = [
            r'([A-Za-z\u4e00-\u9fff]+)[：:]\s*([\d,]+\.?\d*)\s*(t/ha|kg/ha|kg|t|吨|公斤|mm|%)?',
            r'([A-Za-z\u4e00-\u9fff]+)\s*([\d,]+\.?\d*)\s*(%)',
            r'([A-Za-z\u4e00-\u9fff]+)\s*为\s*([\d,]+\.?\d*)\s*(t/ha|kg/ha|kg|t|吨|公斤|mm|%)?'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 3:
                    label, value, unit = match
                else:
                    label, value = match
                    unit = None
                try:
                    # 清理数值
                    clean_value = float(value.replace(',', ''))
                    if clean_value > 0:  # 只保留正数
                        data_points.append({
                            "label": label.strip(),
                            "value": clean_value,
                            "type": unit or "数值"
                        })
                except ValueError:
                    continue

        # 去重并排序
        seen = set()
        unique_points = []
        for point in data_points:
            key = point["label"]
            if key not in seen:
                seen.add(key)
                unique_points.append(point)

        # 按数值排序
        unique_points.sort(key=lambda x: x["value"], reverse=True)

        return unique_points[:10]  # 返回前10个数据点

    def generate_charts(self, data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成图表数据"""
        charts = []

        if not data_points:
            return charts

        # 生成柱状图数据
        if len(data_points) >= 2:
            bar_chart = {
                "type": "bar",
                "title": "数据对比柱状图",
                "data": {
                    "labels": [point["label"] for point in data_points[:8]],
                    "values": [point["value"] for point in data_points[:8]]
                }
            }
            charts.append(bar_chart)

        # 生成饼图数据（前5个）
        if len(data_points) >= 3:
            pie_data = data_points[:5]
            total = sum(point["value"] for point in pie_data)
            pie_chart = {
                "type": "pie",
                "title": "数据分布饼图",
                "data": {
                    "labels": [point["label"] for point in pie_data],
                    "values": [point["value"] for point in pie_data],
                    "percentages": [round(point["value"] / total * 100, 1) for point in pie_data]
                }
            }
            charts.append(pie_chart)

        # 生成趋势图（如果有时间数据）
        if len(data_points) >= 4:
            line_chart = {
                "type": "line",
                "title": "数据趋势图",
                "data": {
                    "labels": [point["label"] for point in data_points[:6]],
                    "values": [point["value"] for point in data_points[:6]]
                }
            }
            charts.append(line_chart)

        return charts

    def create_smart_report(self, analysis: Dict, charts: List[Dict], filename: str) -> str:
        """生成智能报告（加入农业洞察与KPI）"""
        report = f"# 📊 Agribusiness Smart Analysis Report\n\n"
        report += f"**File name**: {filename}\n\n"
        report += f"**Document type**: {analysis['document_type']}\n\n"
        report += f"**Confidence**: {analysis['confidence']:.1%}\n\n"

        # 农业KPI（从全文智能提取）
        agrikpis = self.compute_agribusiness_kpis(analysis.get('full_text', '')) if isinstance(analysis, dict) else {}
        if agrikpis:
            report += "## 🌾 Agribusiness KPIs\n\n"
            for k, v in agrikpis.items():
                report += f"- {k}: {v}\n"
            report += "\n"

        # 天气摘要（如果已获取）
        if getattr(self, 'latest_weather', None):
            ws = self.latest_weather.get('summary', {})
            report += "## ☁️ Climate summary (next 7 days)\n\n"
            if ws:
                if ws.get('7d_total_rain_mm') is not None:
                    report += f"- Total rainfall: {ws['7d_total_rain_mm']} mm\n"
                if ws.get('avg_tmax') is not None:
                    report += f"- Avg Tmax: {ws['avg_tmax']} °C\n"
                if ws.get('avg_tmin') is not None:
                    report += f"- Avg Tmin: {ws['avg_tmin']} °C\n"
            report += "\n"

        # 遥感摘要（如果已获取）
        if getattr(self, 'latest_remote_sensing', None):
            rs = self.latest_remote_sensing.get('summary', {})
            report += "## 🛰️ Remote sensing summary\n\n"
            if rs:
                if rs.get('ndvi_avg') is not None:
                    report += f"- NDVI average: {rs['ndvi_avg']}\n"
                if rs.get('evi_avg') is not None:
                    report += f"- EVI average: {rs['evi_avg']}\n"
                if rs.get('ndvi_last') is not None:
                    report += f"- Latest NDVI: {rs['ndvi_last']}\n"
                if rs.get('evi_last') is not None:
                    report += f"- Latest EVI: {rs['evi_last']}\n"
            report += "\n"

        # 模板抽取结果
        structured = self.extract_agri_structured_fields(analysis.get('full_text', '')) if isinstance(analysis,
                                                                                                      dict) else {}
        if structured:
            report += "## 🗂️ Structured fields (template extraction)\n\n"
            for k, v in structured.items():
                report += f"- {k}: {v}\n"
            report += "\n"

        # Key metrics
        if analysis['key_metrics']:
            report += "## 🔢 Key metrics\n\n"
            for i, metric in enumerate(analysis['key_metrics'][:5], 1):
                report += f"{i}. {metric}\n"
            report += "\n"

        # Time periods
        if analysis['time_periods']:
            report += "## 📅 Time periods\n\n"
            report += f"Detected time info: {', '.join(analysis['time_periods'])}\n\n"

        # Categories
        if analysis['categories']:
            report += "## 📋 Categories\n\n"
            for category in analysis['categories']:
                report += f"- {category}\n"
            report += "\n"

        # Visualization notes
        if charts:
            report += "## 📈 Data visualization\n\n"
            for chart in charts:
                report += f"### {chart['title']}\n\n"
                if chart['type'] == 'bar':
                    report += "Bar chart shows value comparison across categories to spot highs and lows.\n\n"
                elif chart['type'] == 'pie':
                    report += "Pie chart shows proportion distribution for intuitive share comparison.\n\n"
                elif chart['type'] == 'line':
                    report += "Line chart shows temporal trends to identify growth or decline patterns.\n\n"

        # Suggestions
        report += "## 💡 Suggestions\n\n"
        if analysis['document_type'] in ["种植业生产报告", "畜牧业生产报告"]:
            report += "- Track trends of key KPIs (yield, rainfall, FCR).\n"
            report += "- Compare fields/lots or herds to find outliers.\n"
            report += "- Plan interventions (fertigation, pest control) based on thresholds.\n"
        elif analysis['document_type'] in ["农业财务/供应链报告"]:
            report += "- Monitor margins and price trends.\n"
            report += "- Optimize cost structure and inventory turnover.\n"
            report += "- Manage risk with insurance/hedging where applicable.\n"
        else:
            report += "- Keep data updated regularly.\n"
            report += "- Focus on KPI trends and anomalies.\n"
            report += "- Apply data-driven decisions.\n"

        return report

    def compute_agribusiness_kpis(self, text: str) -> Dict[str, Any]:
        """基于规则快速提取农业常见KPI（轻量占位，可后续换模型）"""
        if not text:
            return {}
        import re
        kpis: Dict[str, Any] = {}
        try:
            # 单产（支持 kg/ha, t/ha, 亩产）
            m = re.search(r'(单产|亩产)[:：]?\s*([\d,.]+)\s*(kg/ha|t/ha|公斤/亩|斤/亩|吨/公顷)?', text)
            if m:
                kpis['单产'] = f"{m.group(2)} {m.group(3) or ''}".strip()

            # 面积（亩、公顷）
            m = re.search(r'(播种面积|收获面积|面积)[:：]?\s*([\d,.]+)\s*(亩|公顷|ha)', text)
            if m:
                kpis['面积'] = f"{m.group(2)} {m.group(3)}"

            # 降雨量（mm）
            m = re.search(r'(降雨|降水|累计降雨|累计降水)[:：]?\s*([\d,.]+)\s*mm', text)
            if m:
                kpis['累计降雨'] = f"{m.group(2)} mm"

            # 成本与利润
            m = re.search(r'(总成本|成本)[:：]?\s*([\d,.]+)', text)
            if m:
                kpis['成本'] = m.group(2)
            m = re.search(r'(利润|毛利|毛利率)[:：]?\s*([\d,.]+)\s*(%)?', text)
            if m:
                kpis['利润/毛利'] = f"{m.group(2)}{m.group(3) or ''}"

            # 畜牧关键指标
            m = re.search(r'(出栏|存栏)[:：]?\s*([\d,.]+)\s*(头|只)?', text)
            if m:
                kpis[m.group(1)] = f"{m.group(2)} {m.group(3) or ''}".strip()
            m = re.search(r'(料肉比|FCR)[:：]?\s*([\d,.]+)', text)
            if m:
                kpis['料肉比'] = m.group(2)

            # 遥感指数
            m = re.search(r'(NDVI|EVI)[:：]?\s*([\d,.]+)', text)
            if m:
                kpis[m.group(1)] = m.group(2)
        except Exception:
            pass
        return kpis

    def calculate_checksum(self, file_path: str) -> str:
        """计算文件校验和"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_file_type(self, filename: str) -> str:
        """获取文件类型"""
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            return mime_type.split('/')[0]
        return 'unknown'

    def upload_file(self, uploaded_file, folder_id: Optional[int] = None) -> Dict[str, Any]:
        """上传文件"""
        try:
            # 生成唯一文件名
            timestamp = int(time.time())
            filename = f"{timestamp}_{uploaded_file.name}"
            file_path = self.storage_dir / filename

            # 保存文件
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 计算文件信息
            file_size = file_path.stat().st_size
            checksum = self.calculate_checksum(str(file_path))
            file_type = self.get_file_type(uploaded_file.name)

            # 保存到数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO files (filename, file_path, file_size, file_type, folder_id, checksum)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (uploaded_file.name, str(file_path), file_size, file_type, folder_id, checksum))
            conn.commit()
            conn.close()

            return {
                "success": True,
                "filename": uploaded_file.name,
                "file_size": file_size,
                "file_type": file_type
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_files(self, folder_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取文件列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if folder_id is None:
            # Query files with folder_id IS NULL
            cursor.execute('''
                SELECT id, filename, file_size, file_type, upload_time, is_cached
                FROM files WHERE folder_id IS NULL
                ORDER BY upload_time DESC
            ''')
            print(f"[DEBUG] get_files: Querying files with folder_id IS NULL")
        else:
            cursor.execute('''
                SELECT id, filename, file_size, file_type, upload_time, is_cached
                FROM files WHERE folder_id = ?
                ORDER BY upload_time DESC
            ''', (folder_id,))

        files = []
        for row in cursor.fetchall():
            files.append({
                "id": row[0],
                "filename": row[1],
                "file_size": row[2],
                "file_type": row[3],
                "upload_time": row[4],
                "is_cached": bool(row[5])
            })

        print(f"[DEBUG] get_files: folder_id={folder_id}, found {len(files)} files")
        if files:
            print(f"[DEBUG] get_files: First file - ID: {files[0]['id']}, Name: {files[0]['filename']}, Type: {files[0]['file_type']}")

        conn.close()
        return files
    
    def get_file_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        """通过文件ID获取文件信息（不依赖文件夹）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, filename, file_size, file_type, upload_time, is_cached, folder_id, file_path
                FROM files WHERE id = ?
            ''', (file_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                print(f"[DEBUG] get_file_by_id: Found file - ID: {result[0]}, Name: {result[1]}, Path: {result[7]}")
                return {
                    "id": result[0],
                    "filename": result[1],
                    "file_size": result[2],
                    "file_type": result[3],
                    "upload_time": result[4],
                    "is_cached": bool(result[5]),
                    "folder_id": result[6],
                    "file_path": result[7]
                }
            else:
                print(f"[DEBUG] get_file_by_id: File not found - ID: {file_id}")
            return None
        except Exception as e:
            print(f"[DEBUG] get_file_by_id 错误: {str(e)}")
            import traceback
            print(f"[DEBUG] get_file_by_id 错误堆栈:\n{traceback.format_exc()}")
            return None

    def create_folder(self, folder_name: str, parent_folder_id: Optional[int] = None) -> Dict[str, Any]:
        """创建文件夹"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO folders (folder_name, parent_folder_id)
                VALUES (?, ?)
            ''', (folder_name, parent_folder_id))
            conn.commit()
            folder_id = cursor.lastrowid
            conn.close()

            return {"success": True, "folder_id": folder_id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_files(self, query: str, file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """搜索文件"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if file_type:
            cursor.execute('''
                SELECT id, filename, file_size, file_type, upload_time, is_cached
                FROM files 
                WHERE filename LIKE ? AND file_type = ?
                ORDER BY upload_time DESC
            ''', (f"%{query}%", file_type))
        else:
            cursor.execute('''
                SELECT id, filename, file_size, file_type, upload_time, is_cached
                FROM files 
                WHERE filename LIKE ?
                ORDER BY upload_time DESC
            ''', (f"%{query}%",))

        files = []
        for row in cursor.fetchall():
            files.append({
                "id": row[0],
                "filename": row[1],
                "file_size": row[2],
                "file_type": row[3],
                "upload_time": row[4],
                "is_cached": bool(row[5])
            })

        conn.close()
        return files

    def preview_file(self, file_id: int) -> Optional[bytes]:
        """预览文件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT file_path, file_type FROM files WHERE id = ?', (file_id,))
            result = cursor.fetchone()
            conn.close()

            if not result:
                print(f"[DEBUG] preview_file: File not found in database - ID: {file_id}")
                return None

            file_path, file_type = result
            print(f"[DEBUG] preview_file: Attempting to read file - ID: {file_id}, Path: {file_path}")

            try:
                import os
                if not os.path.exists(file_path):
                    print(f"[DEBUG] preview_file: File path does not exist - {file_path}")
                    return None
                
                with open(file_path, 'rb') as f:
                    data = f.read()
                    print(f"[DEBUG] preview_file: Successfully read {len(data)} bytes from file")
                    return data
            except Exception as e:
                print(f"[DEBUG] preview_file: Error reading file - {str(e)}")
                import traceback
                print(f"[DEBUG] preview_file: Error stack:\n{traceback.format_exc()}")
                return None
        except Exception as e:
            print(f"[DEBUG] preview_file: Database error - {str(e)}")
            import traceback
            print(f"[DEBUG] preview_file: Error stack:\n{traceback.format_exc()}")
            return None

    def cache_file(self, file_id: int) -> bool:
        """缓存文件到本地"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT file_path, filename FROM files WHERE id = ?', (file_id,))
            result = cursor.fetchone()

            if result:
                file_path, filename = result
                cache_path = self.cache_dir / filename
                shutil.copy2(file_path, cache_path)

                # 更新数据库
                cursor.execute('UPDATE files SET is_cached = TRUE WHERE id = ?', (file_id,))
                conn.commit()
                conn.close()
                return True
        except:
            pass
        return False

    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f}{size_names[i]}"

    def get_file_icon(self, file_type: str) -> str:
        """获取文件类型图标"""
        icons = {
            'image': '🖼️',
            'application': '📄',
            'text': '📝',
            'video': '🎥',
            'audio': '🎵',
            'unknown': '📁'
        }
        return icons.get(file_type, '📁')

    def upload_file_with_resume(self, uploaded_file, folder_id: Optional[int] = None, chunk_size: int = 1024 * 1024) -> \
    Dict[str, Any]:
        """带断点续传的文件上传"""
        try:
            filename = uploaded_file.name
            file_size = len(uploaded_file.getbuffer())

            # 检查是否有未完成的上传
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, uploaded_size, checksum FROM upload_progress 
                WHERE filename = ? AND total_size = ?
                ORDER BY upload_time DESC LIMIT 1
            ''', (filename, file_size))

            progress_record = cursor.fetchone()

            if progress_record:
                # 断点续传
                progress_id, uploaded_size, stored_checksum = progress_record
                st.info(f"🔄 Resumable upload found, continue from {uploaded_size} bytes...")
            else:
                # 新上传
                uploaded_size = 0
                progress_id = None
                stored_checksum = None

            # 分块上传
            uploaded_file.seek(uploaded_size)
            current_size = uploaded_size

            progress_bar = st.progress(uploaded_size / file_size)
            status_text = st.empty()

            while current_size < file_size:
                chunk = uploaded_file.read(min(chunk_size, file_size - current_size))
                if not chunk:
                    break

                # 这里应该将chunk发送到服务器
                # 为了演示，我们直接写入本地文件
                temp_file_path = self.storage_dir / f"temp_{filename}"
                with open(temp_file_path, "ab") as f:
                    f.write(chunk)

                current_size += len(chunk)
                progress = current_size / file_size
                progress_bar.progress(progress)
                status_text.text(f"Uploading: {current_size}/{file_size} bytes ({progress * 100:.1f}%)")

                # 更新进度到数据库
                if progress_id:
                    cursor.execute('''
                        UPDATE upload_progress 
                        SET uploaded_size = ? 
                        WHERE id = ?
                    ''', (current_size, progress_id))
                else:
                    cursor.execute('''
                        INSERT INTO upload_progress (filename, total_size, uploaded_size, chunk_size, checksum)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (filename, file_size, current_size, chunk_size, stored_checksum))
                    progress_id = cursor.lastrowid

                conn.commit()

                # 模拟网络延迟
                time.sleep(0.1)

            # 上传完成，移动文件到最终位置
            final_file_path = self.storage_dir / f"{int(time.time())}_{filename}"
            shutil.move(str(temp_file_path), str(final_file_path))

            # 计算校验和
            checksum = self.calculate_checksum(str(final_file_path))
            file_type = self.get_file_type(filename)

            # 保存文件信息到数据库
            file_path_str = str(final_file_path)
            print(f"[DEBUG] upload_file_with_resume: Saving to database - filename: {filename}, file_path: {file_path_str}, file_size: {file_size}, file_type: {file_type}, folder_id: {folder_id}")
            
            cursor.execute('''
                INSERT INTO files (filename, file_path, file_size, file_type, folder_id, checksum)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filename, file_path_str, file_size, file_type, folder_id, checksum))
            
            file_id = cursor.lastrowid
            print(f"[DEBUG] upload_file_with_resume: File saved to database - file_id: {file_id}, filename: {filename}, folder_id: {folder_id}, file_path: {file_path_str}")
            
            # Verify the file was saved correctly
            cursor.execute('SELECT file_path FROM files WHERE id = ?', (file_id,))
            saved_path = cursor.fetchone()
            if saved_path:
                print(f"[DEBUG] upload_file_with_resume: Verified saved file_path: {saved_path[0]}")
            else:
                print(f"[DEBUG] upload_file_with_resume: WARNING - Could not verify saved file_path!")

            # 删除进度记录
            if progress_id:
                cursor.execute('DELETE FROM upload_progress WHERE id = ?', (progress_id,))

            conn.commit()
            conn.close()

            progress_bar.empty()
            status_text.empty()

            return {
                "success": True,
                "filename": filename,
                "file_size": file_size,
                "file_type": file_type,
                "checksum": checksum,
                "file_id": file_id,
                "folder_id": folder_id
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_upload_progress(self) -> List[Dict[str, Any]]:
        """获取上传进度列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT filename, total_size, uploaded_size, upload_time
            FROM upload_progress
            ORDER BY upload_time DESC
        ''')

        progress_list = []
        for row in cursor.fetchall():
            filename, total_size, uploaded_size, upload_time = row
            progress_list.append({
                "filename": filename,
                "total_size": total_size,
                "uploaded_size": uploaded_size,
                "progress": uploaded_size / total_size if total_size > 0 else 0,
                "upload_time": upload_time
            })

        conn.close()
        return progress_list

    def resume_upload(self, filename: str) -> Dict[str, Any]:
        """恢复上传"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, total_size, uploaded_size, chunk_size, checksum
            FROM upload_progress 
            WHERE filename = ?
            ORDER BY upload_time DESC LIMIT 1
        ''', (filename,))

        result = cursor.fetchone()
        if result:
            progress_id, total_size, uploaded_size, chunk_size, checksum = result
            return {
                "success": True,
                "progress_id": progress_id,
                "total_size": total_size,
                "uploaded_size": uploaded_size,
                "chunk_size": chunk_size,
                "checksum": checksum
            }
        else:
            return {"success": False, "error": "未找到上传进度记录"}

    def cancel_upload(self, filename: str) -> bool:
        """取消上传"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM upload_progress WHERE filename = ?', (filename,))
            conn.commit()
            conn.close()
            return True
        except:
            return False

    # ==================== AI功能方法 ====================
    def extract_excel_csv(self, file_id: int):
        """
        通过file_id读取Excel(.xlsx, .xls)或CSV文件，返回Pandas DataFrame
        非支持类型/读取失败时返回None，并显示Streamlit提示
        """
        # 1. 从数据库查询文件信息
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # 查询文件路径、类型、文件名（与数据库表结构对应）
            cursor.execute(
                'SELECT file_path, file_type, filename FROM files WHERE id = ?',
                (file_id,)
            )
            result = cursor.fetchone()
            if not result:
                st.error("File not found in database (invalid file ID).")
                return None  # 文件不存在，返回None

            file_path, file_type, filename = result
            filename = filename.lower()  # 统一转为小写，避免大小写判断问题

            # 2. 校验文件类型（仅支持Excel和CSV）
            if filename.endswith(('.xlsx', '.xls')):
                # 3. 读取Excel文件
                try:
                    df = pd.read_excel(file_path)
                    if df.empty:
                        st.warning("The Excel file is empty.")
                        return None
                    return df
                except FileNotFoundError:
                    st.error(f"Excel file not found at path: {file_path}")
                except pd.errors.EmptyDataError:
                    st.error("Excel file contains no valid data.")
                except pd.errors.ParserError:
                    st.error("Failed to parse Excel file (may be corrupted).")
                except Exception as e:
                    st.error(f"Error reading Excel file: {str(e)}")

            elif filename.endswith('.csv'):
                # 3. 读取CSV文件
                try:
                    # 尝试常用编码，避免中文乱码导致读取失败
                    df = pd.read_csv(file_path, encoding='utf-8')
                except UnicodeDecodeError:
                    # 编码错误时尝试gbk（适合中文环境）
                    try:
                        df = pd.read_csv(file_path, encoding='gbk')
                    except Exception as e:
                        st.error(f"CSV file encoding error: {str(e)}")
                        return None
                except FileNotFoundError:
                    st.error(f"CSV file not found at path: {file_path}")
                    return None
                except pd.errors.EmptyDataError:
                    st.error("CSV file contains no valid data.")
                    return None
                except pd.errors.ParserError:
                    st.error("Failed to parse CSV file (may be corrupted).")
                    return None
                except Exception as e:
                    st.error(f"Error reading CSV file: {str(e)}")
                    return None

                if df.empty:
                    st.warning("The CSV file is empty.")
                    return None
                return df

            else:
                # 非Excel/CSV类型，返回None（将由extract_text_from_file处理）
                return None

        except sqlite3.Error as db_err:
            st.error(f"Database error: {str(db_err)} (failed to get file info)")
            return None
        finally:
            # 确保数据库连接关闭
            if conn:
                conn.close()
        return None

    def extract_text_from_file(self, file_id: int) -> str:
        """从文件中提取文本内容"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT file_path, file_type, filename FROM files WHERE id = ?', (file_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return ""

        file_path, file_type, filename = result
        extracted_text = ""

        try:
            if file_type == 'text' or filename.endswith('.txt'):
                # 文本文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()

            elif file_type == 'application' and filename.endswith('.pdf'):
                # PDF文件
                if PDF_AVAILABLE and fitz is not None:
                    try:
                        doc = fitz.open(file_path)
                        for page in doc:
                            extracted_text += page.get_text()
                        doc.close()
                    except Exception as e:
                        st.warning(f"PDF reading failed: {str(e)}")
                # 若不可用则保持为空，后续给出友好占位

            elif file_type == 'application' and filename.endswith(('.xlsx', '.xls')):
                # Excel文件
                try:
                    df = pd.read_excel(file_path)
                    # 确保DataFrame不为空
                    if not df.empty:
                        # 安全地转换为字符串，避免numpy.str_错误
                        try:
                            extracted_text = df.to_string()
                        except Exception as str_error:
                            # 如果to_string失败，尝试其他方法
                            extracted_text = str(df.values.tolist())
                    else:
                        extracted_text = "Excel file is empty"
                except Exception as e:
                    st.warning(f"Excel reading failed: {str(e)}")
                    extracted_text = ""

            elif filename.endswith('.csv'):
                # CSV文件
                try:
                    df = pd.read_csv(file_path)
                    if not df.empty:
                        try:
                            extracted_text = df.to_string()
                        except Exception:
                            extracted_text = str(df.values.tolist())
                    else:
                        extracted_text = "CSV file is empty"
                except Exception as e:
                    st.warning(f"CSV reading failed: {str(e)}")
                    extracted_text = ""

            elif filename.endswith('.docx'):
                # DOCX（可选处理）
                try:
                    import docx  # type: ignore
                    doc = docx.Document(file_path)
                    paras = [p.text for p in doc.paragraphs if p.text]
                    extracted_text = "\n".join(paras)
                except Exception:
                    # 未安装或解析失败则忽略
                    pass

            elif file_type == 'image':
                # 图片文件 - OCR识别
                print(f"[DEBUG] 开始处理图片文件: {filename}")
                print(f"[DEBUG] 文件路径: {file_path}")
                print(f"[DEBUG] OCR状态 - OCR_AVAILABLE: {OCR_AVAILABLE}, TESSERACT: {TESSERACT_AVAILABLE}")
                
                if OCR_AVAILABLE and TESSERACT_AVAILABLE:
                    # 延迟加载OCR模型
                    if not self._load_ocr_model():
                        print("[DEBUG] OCR模型加载失败，跳过OCR提取")
                        extracted_text = ""
                    else:
                        # OCR模型已加载，进行识别
                        print(f"[DEBUG] OCR模型已加载，开始识别图片: {file_path}")
                        try:
                            print("[DEBUG] 调用 _ocr_readtext()...")
                            results = self._ocr_readtext(file_path)
                            print(f"[DEBUG] OCR识别完成，返回结果数量: {len(results) if results else 0}")
                            
                            if results and len(results) > 0:
                                print(f"[DEBUG] OCR识别结果详情:")
                                for i, result in enumerate(results):
                                    print(f"  [{i+1}] 位置: {result[0]}, 文字: {result[1]}, 置信度: {result[2]:.2f}")
                                
                                extracted_text = ' '.join([result[1] for result in results])
                                if extracted_text.strip():
                                    print(f"[DEBUG] ✅ OCR识别成功，提取的文字: {extracted_text[:100]}...")
                                    st.success(f"✅ OCR recognition successful, recognized {len(results)} text regions")
                                else:
                                    extracted_text = ""  # OCR没有识别到文字
                                    print("[DEBUG] ⚠️ OCR识别结果为空字符串")
                                    st.warning("⚠️ OCR did not recognize any text content")
                            else:
                                extracted_text = ""  # OCR没有识别到文字
                                print("[DEBUG] ⚠️ OCR未识别到任何文字（results为空）")
                                st.warning("⚠️ OCR未识别到文字内容")
                        except Exception as e:
                            print(f"[DEBUG] ❌ OCR识别过程出错: {str(e)}")
                            print(f"[DEBUG] 错误类型: {type(e).__name__}")
                            import traceback
                            print(f"[DEBUG] 错误堆栈:\n{traceback.format_exc()}")
                            st.warning(f"OCR recognition failed: {str(e)}")
                            extracted_text = ""
                else:
                    # OCR不可用，提示用户
                    print(f"[DEBUG] OCR不可用 - OCR_AVAILABLE: {OCR_AVAILABLE}, TESSERACT: {TESSERACT_AVAILABLE}")
                    if not OCR_AVAILABLE or not TESSERACT_AVAILABLE:
                        st.warning("⚠️ OCR feature unavailable. Please install Tesseract OCR. See INSTALL_TESSERACT.md for details.")
                    extracted_text = ""

        except Exception as e:
            st.error(f"Text extraction failed: {str(e)}")

        # 兜底：仍无法提取文本时，返回占位文本，避免AI流程直接失败
        if not extracted_text:
            extracted_text = f"(No extractable text from file: {filename}. Try preview/download.)"

        return extracted_text

    def classify_industry(self, text: str) -> Dict[str, Any]:
        """使用真正的AI对文档进行行业分类，返回与工业视图匹配的标签"""
        if not text:
            return {"category": "Unclassified", "confidence": 0.0, "keywords": []}

        # 方法1: 使用BERT模型分类（如果可用）
        if self.text_classifier and len(text) > 10:
            try:
                # 截取文本前512个字符（BERT限制）
                text_sample = text[:512]
                result = self.text_classifier(text_sample)

                # 将BERT结果映射到我们的行业分类
                bert_label = result[0]['label']
                bert_confidence = result[0]['score']

                # 简单的标签映射（可以根据需要扩展）
                label_mapping = {
                    'LABEL_0': '种植业',
                    'LABEL_1': '畜牧业',
                    'LABEL_2': '农资与土壤',
                    'LABEL_3': '农业金融',
                    'LABEL_4': '供应链与仓储',
                    'LABEL_5': '气候与遥感',
                    'LABEL_6': '农业物联网'
                }

                mapped_category = label_mapping.get(bert_label, 'Unclassified')
                # 转换为英文分类名称
                eng_category = self._to_english_category(mapped_category)

                if eng_category != 'Unclassified':
                    return {
                        "category": eng_category,
                        "confidence": bert_confidence,
                        "keywords": self._extract_keywords_from_text(text),
                        "method": "BERT"
                    }
            except Exception as e:
                # Suppress noisy toast; fallback methods will be tried below
                pass

        # 方法2: 使用机器学习分类器（如果可用且已训练）
        if self.ml_classifier and self.ml_trained and len(text) > 20:
            try:
                X = [text]
                y_pred = self.ml_classifier.predict(X)
                y_proba = self.ml_classifier.predict_proba(X)

                categories = list(self.industry_keywords.keys())
                predicted_category = categories[y_pred[0]]
                confidence = y_proba[0].max()
                
                # 如果置信度低于阈值，直接返回Unclassified
                if confidence < 0.1:
                    print(f"[DEBUG] classify_industry (ML): 置信度太低 ({confidence:.2f})，返回Unclassified")
                    return {"category": "Unclassified", "confidence": 0.0, "keywords": [], "method": "ML"}

                # 转换为英文分类名称
                eng_category = self._to_english_category(predicted_category)
                return {
                    "category": eng_category,
                    "confidence": confidence,
                    "keywords": self._extract_keywords_from_text(text),
                    "method": "ML"
                }
            except Exception as e:
                # Suppress noisy toast; fallback to rules
                pass

        # 方法3: 智能关键词匹配（改进版）
        words = jieba.lcut(text)
        category_scores = {}
        matched_keywords = {}

        for category, keywords in self.industry_keywords.items():
            score = 0
            matched = []

            # 基础关键词匹配
            for keyword in keywords:
                if keyword in text:
                    score += 1
                    matched.append(keyword)

            # 同义词和相似词匹配
            synonyms = self._get_synonyms(category)
            for synonym in synonyms:
                if synonym in text:
                    score += 0.5
                    matched.append(synonym)

            # 词频权重
            for keyword in keywords:
                count = text.count(keyword)
                if count > 1:
                    score += count * 0.2

            category_scores[category] = score
            matched_keywords[category] = matched

        if category_scores and max(category_scores.values()) > 0:
            best_category = max(category_scores, key=category_scores.get)
            max_score = category_scores[best_category]

            # 改进的置信度计算
            total_keywords = len(self.industry_keywords[best_category])
            confidence = min(max_score / (total_keywords * 1.5), 1.0)

            # 降低置信度阈值（从0.1降到0.05），允许更多文件被分类
            if confidence < 0.1:
                print(f"[DEBUG] classify_industry: 置信度太低 ({confidence:.2f})，返回Unclassified")
                return {"category": "Unclassified", "confidence": 0.0, "keywords": [], "method": "关键词匹配"}

            # 转换为英文分类名称
            eng_category = self._to_english_category(best_category)
            return {
                "category": eng_category,
                "confidence": confidence,
                "keywords": matched_keywords[best_category],
                "method": "智能关键词匹配"
            }

        return {"category": "Unclassified", "confidence": 0.0, "keywords": [], "method": "无匹配"}

    def _get_synonyms(self, category: str) -> List[str]:
        """获取行业分类的同义词"""
        synonyms_map = {
            "种植业": ["种植", "耕作", "育秧", "移栽", "密植", "病虫害", "施肥", "灌溉", "田间管理", "玉米", "高粱",
                       "小米", "木薯", "花生", "芝麻", "棉花", "可可", "咖啡"],
            "畜牧业": ["养殖", "饲喂", "免疫", "防疫", "繁育", "断奶", "出栏", "存栏", "增重"],
            "农资与土壤": ["配方施肥", "土壤改良", "施用量", "有机肥", "微量元素", "土壤养分"],
            "农业金融": ["贴现", "授信", "保费", "赔付", "承保", "风控", "保单"],
            "供应链与仓储": ["冷链运输", "损耗率", "批次追溯", "库容", "周转率", "分拣"],
            "气候与遥感": ["降雨", "气温", "积温", "干旱指数", "NDVI", "EVI", "遥感", "沙漠蝗虫", "草地贪夜蛾"],
            "农业物联网": ["含水率", "EC", "滴灌", "喷灌", "阀门", "阈值", "报警"]
        }
        return synonyms_map.get(category, [])

    def init_pretrained_classifier(self):
        """初始化预训练的分类器"""
        if not self.ml_classifier:
            return False

        try:
            # 使用预定义的关键词作为特征进行训练
            X_train = []
            y_train = []

            # 为每个行业类别创建训练样本
            for category, keywords in self.industry_keywords.items():
                # 为每个关键词创建训练样本
                for keyword in keywords:
                    # 创建包含关键词的样本文本
                    sample_text = f"这是一个关于{keyword}的文档，涉及{category}领域的内容。"
                    X_train.append(sample_text)
                    y_train.append(category)

                # 添加同义词样本
                synonyms = self._get_synonyms(category)
                for synonym in synonyms:
                    sample_text = f"这是一个关于{synonym}的文档，涉及{category}领域的内容。"
                    X_train.append(sample_text)
                    y_train.append(category)

            # 训练分类器
            if len(X_train) > 0:
                self.ml_classifier.fit(X_train, y_train)
                self.ml_trained = True
                return True
            else:
                return False

        except Exception as e:
            st.error(f"Failed to initialize pre-trained classifier: {str(e)}")
            return False

    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        try:
            # 使用jieba的TF-IDF提取关键词
            keywords = jieba.analyse.extract_tags(text, topK=10, withWeight=False)
            return keywords
        except:
            # 简单的关键词提取
            words = jieba.lcut(text)
            word_count = Counter(words)
            stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也',
                          '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
            filtered_words = {word: count for word, count in word_count.items()
                              if len(word) > 1 and word not in stop_words and count > 1}
            return list(dict(sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:10]).keys())

    def extract_key_phrases(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键短语"""
        if not text:
            return []

        try:
            # 使用jieba的TF-IDF提取关键词
            keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
            return keywords
        except:
            # 简单的关键词提取
            words = jieba.lcut(text)
            word_count = Counter(words)
            # 过滤掉单字符和常见停用词
            stop_words = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也',
                          '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}
            filtered_words = {word: count for word, count in word_count.items()
                              if len(word) > 1 and word not in stop_words and count > 1}
            return list(dict(sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:top_k]).keys())

    def generate_summary(self, text: str, max_length: int = 200) -> str:
        """Generate document summary (model first, fallback to rules)."""
        if not text:
            return "Unable to generate summary"

        # 方法1: 使用T5模型生成摘要（如果可用）
        if self.summarizer and len(text) > 50:
            try:
                # 截取文本前1024个字符（T5限制）
                text_sample = text[:1024]
                summary_result = self.summarizer(
                    text_sample,
                    max_length=min(max_length, 150),
                    min_length=30,
                    do_sample=False
                )

                if summary_result and len(summary_result) > 0:
                    ai_summary = summary_result[0]['summary_text']
                    return f"🤖 AI Summary: {ai_summary}"
            except Exception as e:
                st.warning(f"T5 summarization failed: {str(e)}")

        # 方法2: 使用OpenAI GPT（如果可用）
        if OPENAI_AVAILABLE and len(text) > 100:
            try:
                # 这里需要OpenAI API密钥
                # 暂时跳过，因为需要API密钥
                pass
            except Exception as e:
                st.warning(f"OpenAI summarization failed: {str(e)}")

        # 方法3: 智能句子选择（改进的规则方法）
        try:
            # 使用更智能的句子选择
            sentences = re.split(r'[。！？.!?]', text)
            sentences = [s.strip() for s in sentences if s.strip() and len(s) > 10]

            if len(sentences) <= 2:
                return text[:max_length] + "..." if len(text) > max_length else text

            # 选择最重要的句子（基于长度和关键词）
            scored_sentences = []
            for i, sentence in enumerate(sentences):
                score = len(sentence)  # 基础分数：句子长度

                # 关键词加分
                important_words = ['重要', '关键', '主要', '核心', '总结', '结论', '结果', '发现']
                for word in important_words:
                    if word in sentence:
                        score += 20

                # 位置加分（开头和结尾的句子更重要）
                if i < 2 or i >= len(sentences) - 2:
                    score += 10

                scored_sentences.append((score, sentence))

            # 选择得分最高的2-3个句子
            scored_sentences.sort(reverse=True)
            selected_sentences = [s[1] for s in scored_sentences[:3]]

            summary = '。'.join(selected_sentences)
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."

            return f"📝 Smart summary: {summary}"
        except:
            # 方法4: 简单截取（最后备用）
            return text[:max_length] + "..." if len(text) > max_length else text

    def _load_ocr_model(self):
        """检查OCR是否可用（Tesseract无需加载模型）"""
        # 检查是否禁用OCR
        import os
        if os.getenv('DISABLE_OCR', '').lower() in ('1', 'true', 'yes'):
            print("[DEBUG] OCR已通过环境变量禁用")
            self.ocr_load_failed = True
            return False
        
        if self.ocr_load_failed:
            print("[DEBUG] OCR之前检查失败，跳过重试")
            return False
        
        if not OCR_AVAILABLE or not TESSERACT_AVAILABLE:
            print("[DEBUG] Tesseract OCR不可用")
            return False
        
        # Tesseract不需要加载模型，直接可用
        print("[DEBUG] ✅ Tesseract OCR可用（无需加载模型，轻量级）")
        return True
    
    def _ocr_readtext(self, image_path: str):
        """OCR识别接口 - 使用Tesseract OCR"""
        if not self._load_ocr_model():
            return []
        
        try:
            # 使用Tesseract OCR
            import pytesseract
            from PIL import Image
            
            # 读取图片
            img = Image.open(image_path)
            
            # 检测语言
            import os
            lang = 'chi_sim+eng' if os.getenv('ENABLE_CHINESE_OCR', '').lower() in ('1', 'true', 'yes') else 'eng'
            
            # 识别文字
            text = pytesseract.image_to_string(img, lang=lang)
            
            # 转换为统一格式: [(bbox, text, confidence)]
            # Tesseract只返回文字，没有坐标信息，bbox设为None，confidence设为1.0
            if text.strip():
                return [(None, text.strip(), 1.0)]
            return []
        except Exception as e:
            print(f"[DEBUG] Tesseract OCR识别失败: {str(e)}")
            import traceback
            print(f"[DEBUG] 错误堆栈:\n{traceback.format_exc()}")
            return []
    
    def extract_ocr_content(self, file_id: int) -> Optional[str]:
        """提取图片或PDF的OCR内容（用于保存到数据库）"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT file_path, file_type, filename FROM files WHERE id = ?', (file_id,))
            result = cursor.fetchone()
            conn.close()

            if not result:
                return None

            file_path, file_type, filename = result
            
            # 只处理图片和PDF文件
            if file_type != 'image' and not (file_type == 'application' and filename.endswith('.pdf')):
                return None

            ocr_content = None

            # 延迟加载OCR模型
            if not self._load_ocr_model():
                print("[DEBUG] extract_ocr_content: OCR模型加载失败，跳过OCR提取")
                return None

            # 对于PDF文件，需要转换为图片后OCR
            if filename.endswith('.pdf') and PDF_AVAILABLE and fitz is not None:
                try:
                    doc = fitz.open(file_path)
                    all_ocr_text = []
                    
                    # 限制PDF页数，避免内存溢出
                    max_pages = min(len(doc), 10)  # 最多处理10页
                    if len(doc) > max_pages:
                        print(f"[DEBUG] PDF有{len(doc)}页，只处理前{max_pages}页以节省内存")
                    
                    for page_num in range(max_pages):
                        page = doc[page_num]
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                        img_data = pix.tobytes("png")
                        
                        import tempfile
                        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                        temp_img.write(img_data)
                        temp_img.close()
                        
                        try:
                            page_results = self._ocr_readtext(temp_img.name)
                            if page_results and len(page_results) > 0:
                                page_text = ' '.join([result[1] for result in page_results])
                                all_ocr_text.append(f"Page {page_num + 1}:\n{page_text}")
                        finally:
                            try:
                                os.unlink(temp_img.name)
                            except:
                                pass
                    
                    doc.close()
                    
                    if all_ocr_text:
                        ocr_content = '\n\n'.join(all_ocr_text)
                except Exception as e:
                    print(f"[DEBUG] extract_ocr_content: PDF OCR失败: {str(e)}")
            
            # 对于图片文件，直接OCR
            elif file_type == 'image':
                try:
                    # 检查图片大小和尺寸，如果太大则缩放
                    from PIL import Image
                    img = Image.open(file_path)
                    img_width, img_height = img.size
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    
                    print(f"[DEBUG] extract_ocr_content: 图片尺寸: {img_width}x{img_height}, 文件大小: {file_size_mb:.2f}MB")
                    
                    # 如果图片太大，进行缩放
                    max_dimension = 2000  # 最大尺寸2000像素
                    max_file_size_mb = 5  # 最大文件大小5MB
                    
                    ocr_file_path = file_path
                    temp_img_path = None
                    
                    if img_width > max_dimension or img_height > max_dimension or file_size_mb > max_file_size_mb:
                        print(f"[DEBUG] extract_ocr_content: 图片过大，进行缩放...")
                        
                        # 计算缩放比例
                        scale = min(max_dimension / img_width, max_dimension / img_height)
                        new_width = int(img_width * scale)
                        new_height = int(img_height * scale)
                        
                        # 缩放图片
                        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # 保存到临时文件
                        import tempfile
                        temp_img_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                        temp_img_path.close()
                        img_resized.save(temp_img_path.name, 'PNG')
                        
                        ocr_file_path = temp_img_path.name
                        print(f"[DEBUG] extract_ocr_content: 图片已缩放至: {new_width}x{new_height}")
                    
                    try:
                        results = self._ocr_readtext(ocr_file_path)
                        if results and len(results) > 0:
                            ocr_content = ' '.join([result[1] for result in results])
                    except MemoryError as e:
                        print(f"[DEBUG] extract_ocr_content: 图片OCR内存不足: {str(e)}")
                        ocr_content = None
                    finally:
                        # 清理临时文件
                        if temp_img_path and os.path.exists(temp_img_path.name):
                            try:
                                os.unlink(temp_img_path.name)
                            except:
                                pass
                except MemoryError as e:
                    print(f"[DEBUG] extract_ocr_content: 图片处理内存不足: {str(e)}")
                    ocr_content = None
                except Exception as e:
                    print(f"[DEBUG] extract_ocr_content: 图片OCR失败: {str(e)}")
                    ocr_content = None
            
            return ocr_content
        except Exception as e:
            print(f"[DEBUG] extract_ocr_content: 错误: {str(e)}")
            return None

    def analyze_file_with_ai(self, file_id: int) -> Dict[str, Any]:
        """使用DeepSeek AI分析文件"""
        try:
            # 提取文本
            extracted_text = self.extract_text_from_file(file_id)

            if not extracted_text:
                return {"success": False, "error": "无法提取文件文本内容"}
            
            # 对于图片和PDF文件，提取并保存OCR内容
            ocr_content = None
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT file_type, filename FROM files WHERE id = ?', (file_id,))
            file_info = cursor.fetchone()
            conn.close()
            
            if file_info:
                file_type, filename = file_info
                if file_type == 'image' or (file_type == 'application' and filename.endswith('.pdf')):
                    ocr_content = self.extract_ocr_content(file_id)
                    print(f"[DEBUG] analyze_file_with_ai: OCR内容提取完成，长度: {len(ocr_content) if ocr_content else 0}")

            # 如果配置了DeepSeek API，使用AI分析
            if self.deepseek_api_key:
                # 构建分析提示词 - 明确要求返回行业分类
                system_prompt = """You are a professional document analysis assistant. Please analyze the user's uploaded file and provide the following information in a structured format:
1. File type and main content overview
2. Industry classification: Please classify this document into ONE of these categories:
   - Planting (crop cultivation, agriculture, farming)
   - Livestock (animal husbandry, cattle, poultry)
   - Inputs-Soil (fertilizer, soil testing, agricultural inputs)
   - Agri-Finance (agricultural finance, insurance, credit)
   - SupplyChain-Storage (supply chain, logistics, warehouse)
   - Climate-RemoteSensing (climate, weather, remote sensing, NDVI, EVI)
   - Agri-IoT (IoT sensors, irrigation, smart agriculture)
   If none of these categories fit, respond with "Unclassified"
3. Key information extraction
4. File summary (within 200 words)

IMPORTANT: Please clearly state the industry classification in your response, for example: "Industry Classification: Planting" or "Industry: Livestock"

Please answer in English, with clear and organized format."""

                # 限制长度避免超出token限制（增加到8000以提供更多上下文）
                extracted_text_limited = extracted_text[:8000]
                user_prompt = f"""Please analyze the following file content:

{extracted_text_limited}

Please provide detailed analysis results, and clearly state the Industry Classification. Make sure to provide a complete and comprehensive analysis."""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]

                # 调用DeepSeek API - 增加max_tokens以确保完整响应
                ai_analysis = self.call_deepseek_api(messages, max_tokens=4000, temperature=0.7)
                
                if ai_analysis:
                    # 解析AI返回的分析结果
                    # 首先尝试从AI响应中提取行业分类
                    classification = self._extract_classification_from_ai_response(ai_analysis, extracted_text)
                    
                    # 如果无法从AI响应中提取，使用本地分类方法
                    if not classification or classification.get('category') == 'Unclassified' or classification.get('category') == '未分类':
                        print(f"[DEBUG] analyze_file_with_ai: 无法从AI响应中提取分类，使用本地分类方法")
                        classification = self.classify_industry(extracted_text)
                    
                    if isinstance(classification, dict) and 'category' in classification:
                        classification['category'] = self._to_english_category(classification['category'])
                        print(f"[DEBUG] analyze_file_with_ai: 最终分类结果: {classification['category']}, 置信度: {classification.get('confidence', 0)}")

                    # 提取关键短语（作为备用）
                    key_phrases = self.extract_key_phrases(extracted_text)

                    # 使用AI生成的摘要，如果没有则使用本地生成
                    summary = ai_analysis[:200] if ai_analysis else self.generate_summary(extracted_text)
                    
                    # 保存分析结果到数据库
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()

                    cursor.execute('''
                        INSERT INTO ai_analysis (file_id, analysis_type, industry_category, extracted_text, key_phrases, summary, confidence_score, method, ocr_content)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (file_id, "full_analysis", classification["category"],
                          extracted_text[:1000], json.dumps(key_phrases, ensure_ascii=False),
                          summary, classification["confidence"], "DeepSeek AI", ocr_content))

                    conn.commit()
                    conn.close()

                    return {
                        "success": True,
                        "extracted_text": extracted_text,
                        "classification": classification,
                        "key_phrases": key_phrases,
                        "summary": summary,
                        "ai_analysis": ai_analysis
                    }
                else:
                    # DeepSeek API调用失败，回退到本地分析
                    st.warning("DeepSeek API call failed, using local analysis method")
            
            # 回退到本地分析方法
            classification = self.classify_industry(extracted_text)
            if isinstance(classification, dict) and 'category' in classification:
                classification['category'] = self._to_english_category(classification['category'])

            key_phrases = self.extract_key_phrases(extracted_text)
            summary = self.generate_summary(extracted_text)

            # 保存分析结果到数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO ai_analysis (file_id, analysis_type, industry_category, extracted_text, key_phrases, summary, confidence_score, method, ocr_content)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (file_id, "full_analysis", classification["category"],
                  extracted_text[:1000], json.dumps(key_phrases, ensure_ascii=False),
                  summary, classification["confidence"], "Local Analysis", ocr_content))

            conn.commit()
            conn.close()

            return {
                "success": True,
                "extracted_text": extracted_text,
                "classification": classification,
                "key_phrases": key_phrases,
                "summary": summary
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_ai_analysis(self, file_id: int) -> Optional[Dict[str, Any]]:
        """获取文件的AI分析结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT analysis_type, industry_category, extracted_text, key_phrases, summary, confidence_score, method, analysis_time
            FROM ai_analysis WHERE file_id = ? ORDER BY analysis_time DESC LIMIT 1
        ''', (file_id,))
        result = cursor.fetchone()
        conn.close()

        if result:
            analysis_type, industry_category, extracted_text, key_phrases, summary, confidence_score, method, analysis_time = result
            return {
                "analysis_type": analysis_type,
                "industry_category": industry_category,
                "extracted_text": extracted_text,
                "key_phrases": json.loads(key_phrases) if key_phrases else [],
                "summary": summary,
                "confidence_score": confidence_score,
                "method": method or "Unknown",
                "analysis_time": analysis_time
            }
        return None

    def create_industry_folder(self, category: str) -> int:
        """为行业分类创建文件夹"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 检查文件夹是否已存在（英文命名）
        eng_category = self._to_english_category(category)
        cursor.execute('SELECT id FROM folders WHERE folder_name = ?', (f"AI_{eng_category}",))
        result = cursor.fetchone()

        if result:
            folder_id = result[0]
        else:
            cursor.execute('''
                INSERT INTO folders (folder_name, parent_folder_id)
                VALUES (?, ?)
            ''', (f"AI_{eng_category}", None))
            folder_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return folder_id

    def move_file_to_industry_folder(self, file_id: int, category: str) -> Dict[str, Any]:
        """将文件移动到行业分类文件夹
        
        Returns:
            Dict包含success和folder_id（如果成功）
        """
        try:
            # 先检查文件是否存在
            file_info = self.get_file_by_id(file_id)
            if not file_info:
                print(f"[DEBUG] move_file_to_industry_folder: 文件不存在 - file_id: {file_id}")
                return {"success": False, "error": "文件不存在"}
            
            print(f"[DEBUG] move_file_to_industry_folder: 开始移动文件 - file_id: {file_id}, category: {category}")
            
            # 创建或获取分类文件夹
            folder_id = self.create_industry_folder(category)
            print(f"[DEBUG] move_file_to_industry_folder: 文件夹ID: {folder_id}")

            # 更新文件的folder_id
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE files SET folder_id = ? WHERE id = ?', (folder_id, file_id))
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            
            if affected_rows > 0:
                print(f"[DEBUG] move_file_to_industry_folder: ✅ 文件移动成功 - file_id: {file_id}, folder_id: {folder_id}")
                return {"success": True, "folder_id": folder_id, "category": category}
            else:
                print(f"[DEBUG] move_file_to_industry_folder: ⚠️ 未更新任何行 - file_id: {file_id}")
                return {"success": False, "error": "文件移动失败，未更新任何记录"}
        except Exception as e:
            print(f"[DEBUG] move_file_to_industry_folder: ❌ 错误: {str(e)}")
            import traceback
            print(f"[DEBUG] move_file_to_industry_folder: 错误堆栈:\n{traceback.format_exc()}")
            return {"success": False, "error": f"文件移动失败: {str(e)}"}

    # ==================== 基础文件管理功能 ====================

    def rename_file(self, file_id: int, new_filename: str) -> Dict[str, Any]:
        """重命名文件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查新文件名是否已存在
            cursor.execute('SELECT id FROM files WHERE filename = ? AND id != ?', (new_filename, file_id))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "error": "文件名已存在"}

            # 更新文件名
            cursor.execute('UPDATE files SET filename = ? WHERE id = ?', (new_filename, file_id))
            conn.commit()
            conn.close()

            return {"success": True, "new_filename": new_filename}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_file(self, file_id: int) -> Dict[str, Any]:
        """删除文件"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 获取文件路径
            cursor.execute('SELECT file_path FROM files WHERE id = ?', (file_id,))
            result = cursor.fetchone()

            if result:
                file_path = result[0]

                # 删除物理文件
                if os.path.exists(file_path):
                    os.remove(file_path)

                # 删除数据库记录
                cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))

                # 删除AI分析记录
                cursor.execute('DELETE FROM ai_analysis WHERE file_id = ?', (file_id,))

                conn.commit()
                conn.close()

                return {"success": True}
            else:
                conn.close()
                return {"success": False, "error": "文件不存在"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def rename_folder(self, folder_id: int, new_folder_name: str) -> Dict[str, Any]:
        """重命名文件夹"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查新文件夹名是否已存在
            cursor.execute('SELECT id FROM folders WHERE folder_name = ? AND id != ?', (new_folder_name, folder_id))
            if cursor.fetchone():
                conn.close()
                return {"success": False, "error": "文件夹名已存在"}

            # 更新文件夹名
            cursor.execute('UPDATE folders SET folder_name = ? WHERE id = ?', (new_folder_name, folder_id))
            conn.commit()
            conn.close()

            return {"success": True, "new_folder_name": new_folder_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_folder(self, folder_id: int) -> Dict[str, Any]:
        """删除文件夹"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 检查文件夹是否为空
            cursor.execute('SELECT COUNT(*) FROM files WHERE folder_id = ?', (folder_id,))
            file_count = cursor.fetchone()[0]

            if file_count > 0:
                conn.close()
                return {"success": False, "error": f"文件夹不为空，包含 {file_count} 个文件"}

            # 检查是否有子文件夹
            cursor.execute('SELECT COUNT(*) FROM folders WHERE parent_folder_id = ?', (folder_id,))
            subfolder_count = cursor.fetchone()[0]

            if subfolder_count > 0:
                conn.close()
                return {"success": False, "error": f"文件夹包含 {subfolder_count} 个子文件夹"}

            # 删除文件夹
            cursor.execute('DELETE FROM folders WHERE id = ?', (folder_id,))
            conn.commit()
            conn.close()

            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_folders(self, parent_folder_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取文件夹列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if parent_folder_id is None:
            cursor.execute('''
                SELECT id, folder_name, created_time, 
                       (SELECT COUNT(*) FROM files WHERE folder_id = folders.id) as file_count
                FROM folders 
                WHERE parent_folder_id IS NULL
                ORDER BY created_time DESC
            ''')
        else:
            cursor.execute('''
                SELECT id, folder_name, created_time,
                       (SELECT COUNT(*) FROM files WHERE folder_id = folders.id) as file_count
                FROM folders 
                WHERE parent_folder_id = ?
                ORDER BY created_time DESC
            ''', (parent_folder_id,))

        folders = []
        for row in cursor.fetchall():
            folders.append({
                "id": row[0],
                "folder_name": row[1],
                "created_time": row[2],
                "file_count": row[3]
            })

        conn.close()
        return folders

    def sync_cached_files(self) -> Dict[str, Any]:
        """同步缓存文件到云端"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 获取所有已缓存的文件
            cursor.execute('''
                SELECT id, filename, file_path, last_modified
                FROM files 
                WHERE is_cached = TRUE
            ''')

            cached_files = cursor.fetchall()
            synced_count = 0

            for file_id, filename, file_path, last_modified in cached_files:
                # 检查文件是否仍然存在
                if os.path.exists(file_path):
                    # 更新最后修改时间
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute('''
                        UPDATE files 
                        SET last_modified = ? 
                        WHERE id = ?
                    ''', (current_time, file_id))
                    synced_count += 1

            conn.commit()
            conn.close()

            return {
                "success": True,
                "synced_count": synced_count,
                "message": f"成功同步 {synced_count} 个缓存文件"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# 初始化云存储管理器
