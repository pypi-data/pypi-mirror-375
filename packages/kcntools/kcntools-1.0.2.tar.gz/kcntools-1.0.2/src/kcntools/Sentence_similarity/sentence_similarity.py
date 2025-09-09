#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
句子相似度计算系统
级联流程：预处理与标准化 -> 快速检查 -> 子串过滤 -> 专名通道 -> 长短文本处理 -> 优化LCS -> 语义相似 -> LLM裁决
"""

import re
import json
import numpy as np
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict, field
import jieba
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from .entity_extractor import EntityExtractor, EntityInfo
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import pandas as pd
import os
import gensim.downloader as api
import logging
import time
from statistics import mean
# 机器学习评估指标完整导入
from sklearn.metrics import (
    accuracy_score,           # 准确率
    precision_score,          # 精确率
    recall_score,             # 召回率
    f1_score,                 # F1分数
    precision_recall_fscore_support,  # 多类别的精确率、召回率、F1
    confusion_matrix,         # 混淆矩阵
    cohen_kappa_score         # Kappa系数（可选，用于一致性检验）
)

logging.basicConfig(level=logging.INFO)

# 导入常量定义
from .constants import (
    ProcessingStage,
    SimilarityResult,
    EntityType,
    ExcelColumns,
    LogMessages,
    ThresholdConstants,
    DefaultValues,
    FilePatterns,
    get_stage_display_name,
    get_result_display_name,
    get_entity_type_name,
    get_excel_column_name
)
from opencc import OpenCC   
from bs4 import BeautifulSoup
import unicodedata
from glob import glob



@dataclass
class TextPairInfo:
    """文本对的基本信息，在入口函数中统一计算，避免重复判断"""
    is_short1: bool
    is_short2: bool
    is_short_pair: bool  # 短-短文本对
    is_long_short: bool  # 长-短文本对
    is_long_pair: bool   # 长-长文本对
    enable_entity_extraction: bool  # 是否启用实体抽取
    
    @classmethod
    def create(cls, text1: str, text2: str, preprocessor) -> 'TextPairInfo':
        """根据两个文本创建文本对信息 - 使用基于token的短文本判断"""
        is_short1 = preprocessor.is_short_text(text1)
        is_short2 = preprocessor.is_short_text(text2)
        is_short_pair = is_short1 and is_short2
        is_long_short = (is_short1 and not is_short2) or (not is_short1 and is_short2)
        is_long_pair = not is_short1 and not is_short2
        enable_entity_extraction = is_short_pair  # 只在短-短文本对中启用实体抽取
        
        return cls(
            is_short1=is_short1,
            is_short2=is_short2,
            is_short_pair=is_short_pair,
            is_long_short=is_long_short,
            is_long_pair=is_long_pair,
            enable_entity_extraction=enable_entity_extraction
        )


@dataclass
class StageScore:
    """单个阶段的分数信息"""
    stage_name: str
    score: float = 0.0
    confidence: float = 0.0
    result: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False


@dataclass
class ExplainabilityData:
    """可解释性数据结构 - 包含所有阶段的分数信息"""
    input_text1: str
    input_text2: str
    normalized_text1: str = ""
    normalized_text2: str = ""
    final_result: str = ""
    final_confidence: float = 0.0
    final_stage: str = ""
    stage_scores: Dict[str, StageScore] = field(default_factory=lambda: {
        ProcessingStage.PREPROCESSING.value: StageScore(ProcessingStage.PREPROCESSING.value),
        ProcessingStage.QUICK_CHECK.value: StageScore(ProcessingStage.QUICK_CHECK.value),
        ProcessingStage.SUBSTRING_FILTER.value: StageScore(ProcessingStage.SUBSTRING_FILTER.value),
        ProcessingStage.ENTITY_CHANNEL.value: StageScore(ProcessingStage.ENTITY_CHANNEL.value),
        ProcessingStage.LONG_SHORT_SEMANTIC.value: StageScore(ProcessingStage.LONG_SHORT_SEMANTIC.value),
        ProcessingStage.OPTIMIZED_LCS.value: StageScore(ProcessingStage.OPTIMIZED_LCS.value),
        ProcessingStage.SEMANTIC_SIMILARITY.value: StageScore(ProcessingStage.SEMANTIC_SIMILARITY.value),
        ProcessingStage.LLM_DECISION.value: StageScore(ProcessingStage.LLM_DECISION.value)
    })
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def update_stage_score(self, stage: ProcessingStage, score: float = 0.0, confidence: float = 0.0,
                          result: SimilarityResult = None, details: Dict[str, Any] = None, processed: bool = True):
        """更新指定阶段的分数信息"""
        stage_key = stage.value
        if stage_key in self.stage_scores:
            self.stage_scores[stage_key].score = score
            self.stage_scores[stage_key].confidence = confidence
            # 处理result可能是枚举对象或字符串的情况
            if result is None:
                self.stage_scores[stage_key].result = ""
            elif isinstance(result, str):
                self.stage_scores[stage_key].result = result
            else:
                # 假设是枚举对象
                self.stage_scores[stage_key].result = result.value if hasattr(result, 'value') else str(result)
            self.stage_scores[stage_key].processed = processed
            if details:
                self.stage_scores[stage_key].details.update(details)
    
    def get_all_scores(self) -> Dict[str, Dict[str, Any]]:
        """获取所有阶段的分数信息"""
        return {
            stage_name: {
                "score": stage_score.score,
                "confidence": stage_score.confidence,
                "result": stage_score.result,
                "processed": stage_score.processed,
                "details": stage_score.details
            }
            for stage_name, stage_score in self.stage_scores.items()
        }


class TextPreprocessor:
    """文本预处理与标准化"""
    
    def __init__(self,
                 remove_continue_space=True,      # 去除空格
                 remove_suspension=True,          # 转换省略号
                 remove_sentiment_character=True, # 去除表情符号
                 to_simple=True,                  # 转化为简体中文
                 unicode_normalize=True,          # unicode标准化
                 remove_html_label=False,         # 去除html标签(在句子相似度中通常不需要)
                 remove_md_label=False,           # 去除markdown标签(在句子相似度中通常不需要)
                 remove_stop_words=True           # 去除停用词
                 ):
        self.entity_extractor = EntityExtractor(use_spacy=True)
        
        # TextCleaner的配置参数
        self.remove_continue_space = remove_continue_space
        self._remove_suspension = remove_suspension
        self._remove_sentiment_character = remove_sentiment_character
        self._unicode_normalize = unicode_normalize
        self._to_simple = to_simple
        self._remove_html_label = remove_html_label
        self._remove_stop_words = remove_stop_words
        self._remove_md_label = remove_md_label
        self._stop_words = []  # 停用词列表
        
        # 加载停用词
        if self._remove_stop_words:
            self._stop_words = self.load_stop_words()
        
        # 尝试导入OpenCC用于繁简转换
        if self._to_simple:
            try:
                if OpenCC is not None:
                    self.opencc_converter = OpenCC('t2s')
                    self.has_opencc = True
                else:
                    print(LogMessages.OPENCC_NOT_INSTALLED.value)
                    self.opencc_converter = None
                    self.has_opencc = False
            except Exception as e:
                logging.error(LogMessages.OPENCC_INIT_FAILED.value.format(error=e))
                self.opencc_converter = None
                self.has_opencc = False
        else:
            self.has_opencc = False
        
        # 导入BeautifulSoup用于HTML/Markdown标签清理
        if self._remove_html_label or self._remove_md_label:
            if BeautifulSoup is None:
                logging.warning(LogMessages.BEAUTIFULSOUP_NOT_INSTALLED.value)
                self.has_beautifulsoup = False
            else:
                self.has_beautifulsoup = True
        else:
            self.has_beautifulsoup = False
    
    def clean_and_normalize(self, text: str) -> str:
        """清洗与规范化文本"""
        return self.clean_single_text_common(text)
    
    def clean_single_text_common(self, text: str) -> str:
        """基础文本清洗"""
        if not text:
            return text
            
        if self.remove_continue_space:
            text = self.remove_space(text)
        if self._remove_suspension:
            text = self.remove_suspension(text)
        if self._remove_sentiment_character:
            text = self.remove_sentiment_character(text)
        if self._to_simple:
            text = self.to_simple(text)
        if self._unicode_normalize:
            text = self.to_unicode_normalize(text)
        if self._remove_html_label:
            text = self.remove_html_label(text)
        if self._remove_md_label:
            text = self.remove_md_label(text)
        return text
    
    def clean_single_text_with_stopwords(self, text: str) -> str:
        """完整文本清洗包含停用词处理"""
        if not text:
            return text
            
        # 先进行基础清洗
        text = self.clean_single_text_common(text)
        
        # 去除停用词
        if self._remove_stop_words:
            text = self.remove_stop_words(words_list=jieba.lcut(text), with_space=False)
        
        return text
    
    def remove_space(self, text: str) -> str:
        """去掉文本中的连续空格"""
        return re.sub(r'\s+', ' ', text)
    
    def remove_suspension(self, text: str) -> str:
        """转换省略号为句号"""
        return text.replace('...', '。')
    
    def remove_sentiment_character(self, sentence: str) -> str:
        """去除表情符号"""
        pattern = re.compile("[^\u4e00-\u9fa5^,^.^!^，^。^?^？^！^a-z^A-Z^0-9\s]")  # 只保留中英文、数字和符号，去掉其他东西
        line = re.sub(pattern, '', sentence)  # 把文本中匹配到的字符替换成空字符
        new_sentence = re.sub(r'\s+', ' ', line)
        return new_sentence
    
    def to_simple(self, sentence: str) -> str:
        """繁体转为简体"""
        if self.has_opencc and self.opencc_converter:
            try:
                return self.opencc_converter.convert(sentence)
            except Exception as e:
                print(LogMessages.TRADITIONAL_TO_SIMPLIFIED_FAILED.value.format(error=e))
                return sentence
        return sentence
    
    def to_unicode_normalize(self, text: str) -> str:
        """Unicode标准化"""
        try:
            # Unicode NFC正规化
            text = unicodedata.normalize('NFC', text)
            
            # 全角转半角
            text = ''.join([unicodedata.normalize('NFKC', char)
                           if unicodedata.name(char, '').startswith('FULLWIDTH')
                           else char for char in text])
            return text
        except Exception as e:
            print(LogMessages.UNICODE_NORMALIZE_FAILED.value.format(error=e))
            return text
    
    def remove_html_label(self, text: str) -> str:
        """去除HTML标签"""
        if not self.has_beautifulsoup:
            return text
        try:
            soup = BeautifulSoup(text, 'html.parser')
            return soup.get_text()
        except Exception as e:
            print(LogMessages.HTML_CLEAN_FAILED.value.format(error=e))
            return text
    
    def remove_md_label(self, text: str) -> str:
        """去除Markdown标签"""
        if not self.has_beautifulsoup:
            return text
        try:
            # 简单的Markdown标签清理
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **粗体**
            text = re.sub(r'\*(.*?)\*', r'\1', text)      # *斜体*
            text = re.sub(r'`(.*?)`', r'\1', text)        # `代码`
            text = re.sub(r'#+ ', '', text)               # # 标题
            text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # [链接](url)
            return text
        except Exception as e:
            print(LogMessages.MARKDOWN_CLEAN_FAILED.value.format(error=e))
            return text
    
    def remove_stop_words(self, words_list, with_space=False):
        """去除停用词"""
        words = [w for w in words_list if w not in self._stop_words]  # 去除文本中的停用词
        new_text = ''
        if with_space:
            new_text = ' '.join(words)
        else:
            new_text = ''.join(words)
        return self.remove_space(new_text)
    
    def load_stop_words(self):
        """加载停用词"""
        try:
            # 获取当前脚本所在目录（Sentence_similarity 目录）
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 关键修正：用 os.path.join 拼接路径，自动加分隔符
            stop_word_pattern = os.path.join(current_dir, FilePatterns.STOPWORDS_PATTERN)
            
            # 查找停用词文件
            stop_word_filepath_list = glob(stop_word_pattern)
            
            if not stop_word_filepath_list:
                logging.warning(LogMessages.STOPWORDS_FILE_NOT_FOUND.value.format(directory=current_dir))
                return DefaultValues.DEFAULT_STOPWORDS
            
            stopwords = []
            for stop_word_filepath in stop_word_filepath_list:
                try:
                    with open(stop_word_filepath, 'r', encoding='utf-8') as fp:
                        # 读取时去掉空行和前后空格
                        file_stopwords = [line.strip() for line in fp if line.strip()]
                        stopwords.extend(file_stopwords)
                except Exception as e:
                    logging.error(LogMessages.STOPWORDS_READ_FAILED.value.format(filepath=stop_word_filepath, error=e))
            
            # 去除重复词并返回
            stopwords = list(set(stopwords))
            logging.info(LogMessages.STOPWORDS_LOADED.value.format(count=len(stopwords)))
            return stopwords
            
        except Exception as e:
            logging.error(LogMessages.STOPWORDS_LOAD_FAILED.value.format(error=e))
            return DefaultValues.DEFAULT_STOPWORDS
    
    def tokenize_nonstop(self, text: str) -> List[str]:
        """分词 - 使用停用词文件进行过滤"""
        tokens = list(jieba.cut(text))
        tokens = [token.strip() for token in tokens if token.strip() and token not in self._stop_words]
        return tokens
    
    def get_content_words(self, tokens: List[str]) -> List[str]:
        """获取内容词（非虚词） - 使用统一的停用词集合"""
        return [token for token in tokens if token not in self._stop_words and len(token) > 1]
    
    def is_short_text(self, text: str) -> bool:
        """判断是否为短文本（基于token数量）
        
        Args:
            text: 输入文本
        
        Returns:
            bool: True表示短文本（<=5个tokens），False表示长文本
        """
        cleaned_text = self.clean_and_normalize(text)
        tokens = self.tokenize_nonstop(cleaned_text)
        return len(tokens) <= 5  # 5个token以下为短文本
    
    def is_short_text_by_chars(self, text: str) -> bool:
        """判断是否为短文本（基于字符数，备用方法）
        
        Args:
            text: 输入文本
        
        Returns:
            bool: True表示短文本，False表示长文本
        """
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        
        if chinese_chars > 0 and english_words == 0:
            return chinese_chars <= DefaultValues.SHORT_TEXT_CHINESE_CHARS
        elif chinese_chars == 0 and english_words > 0:
            return english_words <= DefaultValues.SHORT_TEXT_ENGLISH_WORDS
        elif chinese_chars > 0 and english_words > 0:
            return chinese_chars <= DefaultValues.SHORT_TEXT_CHINESE_CHARS and english_words <= DefaultValues.SHORT_TEXT_ENGLISH_WORDS
        else:
            return True
    
    def preprocess(self, text: str, enable_entity_extraction: bool = True, is_short: bool = None) -> Dict[str, Any]:
        """
        完整预处理流程 - 多阶段架构，解决循环依赖
        
        Args:
            text: 输入文本
            enable_entity_extraction: 是否启用实体抽取（只在短-短文本对中启用）
            is_short: 是否为短文本（如果提供则直接使用，避免重复计算）
        
        Note:
            新的多阶段架构：
            1. 基础清洗：clean_and_normalize()
            2. 分词：tokenize_nonstop()
            3. 短文本判断：基于token数量判断（如果is_short未提供）
            4. 条件实体抽取：基于短文本判断结果决定是否进行实体抽取
        """
        # 基础清洗
        cleaned_text = self.clean_and_normalize(text)
        
        # 分词
        tokens = self.tokenize_nonstop(cleaned_text)
        
        # 条件实体抽取
        if enable_entity_extraction :
            # 只在短文本且启用实体抽取时进行实体抽取
            normalized_text, entities_info = self.entity_extractor.extract_and_normalize_entities(cleaned_text)
            
            entities = {
                EntityType.NUMBERS.value: [entity.original for entity in entities_info[EntityType.NUMBERS.value]],
                EntityType.DATES.value: [entity.original for entity in entities_info[EntityType.DATES.value]],
                EntityType.ADDRESSES.value: [entity.original for entity in entities_info[EntityType.ADDRESSES.value]]
            }
        else:
            normalized_text = cleaned_text
            entities_info = {EntityType.NUMBERS.value: [], EntityType.DATES.value: [], EntityType.ADDRESSES.value: []}
            entities = {EntityType.NUMBERS.value: [], EntityType.DATES.value: [], EntityType.ADDRESSES.value: []}
        
        
        content_words = self.get_content_words(tokens)
        
        return {
            'original': text,
            'cleaned': cleaned_text,
            'normalized': normalized_text,
            'tokens': tokens,
            'content_words': content_words,
            'entities': entities,
            'entities_info': entities_info,
            'token_count': len(tokens),
            'entity_extraction_enabled': enable_entity_extraction,
            'is_short': is_short
        }


class SentenceSimilarityCalculator:
    """句子相似度计算器主类"""
    
    _model_cache = {}
    
    def __init__(self,
                 api_base_url: str = None,
                 api_key: str = None,
                 llm_model_id: str = "gpt-4.1",
                 embedding_model_id: str = "qzhou-embedding",
                 use_local_embedding: bool = False,
                 local_embedding_model: str = "all-MiniLM-L6-v2",
                 use_word2vec: bool = True,
                 word2vec_model_name: str = "word2vec-google-news-300"):
        """
        初始化句子相似度计算器
        
        Args:
            api_base_url: 统一的API基础URL（LLM和embedding共用）
            api_key: API密钥
            llm_model_id: LLM模型ID
            embedding_model_id: embedding模型ID
            use_local_embedding: 是否使用本地embedding模型
            local_embedding_model: 本地embedding模型名称
            use_word2vec: 是否使用word2vec模型进行长短文本匹配
            word2vec_model_name: word2vec模型名称
        """
        self.preprocessor = TextPreprocessor()
        
        self.api_base_url = api_base_url
        self.api_key = api_key
        self.llm_model_id = llm_model_id
        self.embedding_model_id = embedding_model_id
        
        self.use_local_embedding = use_local_embedding
        if use_local_embedding:
            self.embedding_model = SentenceTransformer(local_embedding_model)
        else:
            self.embedding_model = None
        
        # 缓存加载word2vec模型
        self.use_word2vec = use_word2vec
        self.word2vec_model = None
        self.word2vec_model_name = word2vec_model_name
        
        if use_word2vec:
            print("Word2Vec功能已启用，尝试加载Word2Vec模型...")
            self.word2vec_model = self._load_word2vec_model_with_smart_cache(word2vec_model_name)
            self.word2vec_api_available = True  
        else:
            self.word2vec_api_available = False
        
        self.explainability_log: List[ExplainabilityData] = []
        self.current_explainability: Optional[ExplainabilityData] = None
        if api_key:
            self._init_openai_client(api_key, api_base_url)
        else:
            self.openai_client = None
    
    def _init_openai_client(self, api_key: str, api_base_url: str = None):
        """初始化OpenAI客户端
        
        Args:
            api_key: API密钥
            api_base_url: 统一API基础URL
            
        Returns:
            None
        """
        self.openai_client = OpenAI(
            api_key=api_key,
            base_url=api_base_url
        )
        
        self.explainability_log: List[ExplainabilityData] = []
        self.current_explainability: Optional[ExplainabilityData] = None
        
        # 统一的置信度阈值定义
        self.confidence_thresholds = {
            "related": 0.8,    # >= 0.8 视为"相关"
            "similar": 0.7,    # >= 0.7 视为"相似"
            "unrelated": 0.0   # < 0.6 视为"不相关"
        }
        
    
    def _call_llm(self, prompt: str) -> str:
        """调用LLM模型进行推理
        
        Args:
            prompt: 提示文本
            
        Returns:
            LLM响应文本
            
        Raises:
            ValueError: 当OpenAI客户端未初始化时
        """
        if not self.openai_client:
            raise ValueError("OpenAI客户端未初始化")
            
        response = self.openai_client.chat.completions.create(
            model=self.llm_model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.1
        )
        
        return response.choices[0].message.content.strip()
    
    def _load_word2vec_model_with_smart_cache(self, model_name: str, default_cache_dir: str = os.path.expanduser("~/.gensim-data")):
        """
        智能加载Word2Vec模型，支持多级缓存机制
        1. 内存缓存：同一脚本实例中避免重复加载
        2. 磁盘缓存：gensim自动管理的本地缓存
        
        Args:
            model_name: 模型名称
            
        Returns:
            加载的模型对象，如果失败则返回None
        """
        try:
            # 首先检查内存缓存
            if model_name in self._model_cache:
                print(f"从内存缓存加载模型: {model_name}")
                return self._model_cache[model_name]
            
            import gensim.downloader as api
            import os
            
            # 确保缓存目录存在
            if not os.path.exists(default_cache_dir):
                os.makedirs(default_cache_dir)
                print(f"创建缓存目录: {default_cache_dir}")
            
            # 检查磁盘缓存（Gensim会自动管理缓存）
            # 注意：api.load()会自动处理缓存，我们只需要检查文件是否存在
            model_cache_path = os.path.join(default_cache_dir, model_name)
            
            # 检查模型是否已经在本地缓存
            if os.path.exists(model_cache_path):
                print(f"从磁盘缓存加载模型: {model_name}")
                print(f"  缓存路径: {model_cache_path}")
                model = api.load(model_name)
                print(f"  模型加载成功 (向量维度: {model.vector_size}, 词汇表大小: {len(model.key_to_index)})")
                
                # 加载后存入内存缓存
                self._model_cache[model_name] = model
                return model
            else:
                # 模型需要下载
                print(f"模型未缓存，开始下载: {model_name}")
                print("首次下载可能需要较长时间，完成后会永久缓存到本地...")
                print(f"下载目标: {model_cache_path}")
                
                # 下载并加载模型
                model = api.load(model_name)
                
                print(f"Word2Vec模型下载并加载成功！")
                print(f"模型名称: {model_name}")
                print(f"向量维度: {model.vector_size}")
                print(f"词汇表大小: {len(model.key_to_index)}")
                print(f"缓存位置: {model_cache_path}")
                print("下次运行将直接从缓存加载，无需重新下载")
                
                # 存入内存缓存
                self._model_cache[model_name] = model
                return model
            
        except ImportError as e:
            print(f"gensim库导入失败: {e}")
            return None
        except Exception as e:
            print(f"Word2Vec模型加载失败: {e}")
            return None
    
    @classmethod
    def clear_model_cache(cls):
        """清空内存中的模型缓存（用于释放内存）"""
        cls._model_cache.clear()
        logging.info("  Word2Vec内存缓存已清空")
    
    @classmethod
    def get_cached_models(cls):
        """获取当前缓存的模型列表"""
        return list(cls._model_cache.keys())
    
    def _get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        获取文本embeddings，统一通过API或本地模型
        
        Args:
            texts: 需要获取embedding的文本列表
            
        Returns:
            文本的embedding向量数组
        """
        # 优先尝试使用本地embedding模型（如果启用）
        if self.use_local_embedding:
            return self.embedding_model.encode(texts)
        
        # 使用API获取embeddings
        try:
            if not self.openai_client:
                raise ValueError("OpenAI客户端未初始化")
            
            # 直接调用openai client的embeddings API
            response = self.openai_client.embeddings.create(
                model=self.embedding_model_id,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            return np.array(embeddings)
                
        except Exception as e:
            logging.error(f"Embedding API调用失败: {e}")
            # 如果API调用失败且本地模型可用，降级使用本地模型
            if self.embedding_model:
                logging.warning("降级使用本地embedding模型")
                return self.embedding_model.encode(texts)
            else:
                raise e
    
    def _init_explainability_for_pair(self, text1: str, text2: str, norm_text1: str = "", norm_text2: str = ""):
        """为新的文本对初始化可解释性数据"""
        self.current_explainability = ExplainabilityData(
            input_text1=text1,
            input_text2=text2,
            normalized_text1=norm_text1,
            normalized_text2=norm_text2
        )
    
    def _log_stage_score(self, stage: ProcessingStage, score: float = 0.0, confidence: float = 0.0,
                        result: SimilarityResult = None, details: Dict[str, Any] = None, processed: bool = True):
        """记录单个阶段的分数"""
        if self.current_explainability:
            self.current_explainability.update_stage_score(
                stage, score, confidence, result, details, processed
            )
    
    def _finalize_explainability(self, final_result: str, final_confidence: float, final_stage: str):
        """完成当前文本对的可解释性记录并添加到日志中 - 只保留早停之前的阶段数据"""
        if self.current_explainability:
            self.current_explainability.final_result = final_result
            self.current_explainability.final_confidence = final_confidence
            self.current_explainability.final_stage = final_stage
           
            self._remove_unprocessed_stages_after_final(final_stage)
            
            self.explainability_log.append(self.current_explainability)
            self.current_explainability = None
    
    def _remove_unprocessed_stages_after_final(self, final_stage: str):
        """移除早停后未实际执行的阶段数据"""
        if not self.current_explainability:
            return
        
        # 定义阶段执行顺序
        stage_order = [
            ProcessingStage.PREPROCESSING.value,
            ProcessingStage.QUICK_CHECK.value,
            ProcessingStage.SUBSTRING_FILTER.value,
            ProcessingStage.ENTITY_CHANNEL.value,
            ProcessingStage.LONG_SHORT_SEMANTIC.value,
            ProcessingStage.OPTIMIZED_LCS.value,
            ProcessingStage.SEMANTIC_SIMILARITY.value,
            ProcessingStage.LLM_DECISION.value
        ]
        
        try:
            final_stage_index = stage_order.index(final_stage)
        except ValueError:
            return
        
        stages_to_remove = stage_order[final_stage_index + 1:]
        
        for stage_name in stages_to_remove:
            if stage_name in self.current_explainability.stage_scores:
                stage_score = self.current_explainability.stage_scores[stage_name]
                # 只移除未被实际处理的阶段
                if not stage_score.processed:
                    del self.current_explainability.stage_scores[stage_name]
    
    def jaccard_similarity(self, set1: set, set2: set) -> float:
        """计算Jaccard相似度"""
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0.0
    
    def normalized_edit_distance(self, s1: str, s2: str) -> float:
        """计算归一化编辑距离"""
        if not s1 and not s2:
            return 0.0
        if not s1 or not s2:
            return 1.0
        
        # 动态规划计算编辑距离
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        
        edit_distance = dp[m][n]
        max_len = max(m, n)
        return edit_distance / max_len if max_len > 0 else 0.0
    
    def quick_check(self, proc1: Dict[str, Any], proc2: Dict[str, Any], text_pair_info: TextPairInfo) -> Optional[str]:
        """快速检查阶段 - 使用统一的文本对信息，避免重复计算"""
        text1_norm = proc1['normalized']
        text2_norm = proc2['normalized']
        tokens1 = set(proc1['tokens'])
        tokens2 = set(proc2['tokens'])
        
        details = {}
        
        if text1_norm == text2_norm:
            self._log_stage_score(ProcessingStage.QUICK_CHECK, score=1.0, confidence=1.0, result=SimilarityResult.RELATED,
                                 details={"reason": "same text"}, processed=True)
            return SimilarityResult.RELATED.display_name
        
        # Token Jaccard相似度
        jaccard_sim = self.jaccard_similarity(tokens1, tokens2)
        details['jaccard_similarity'] = jaccard_sim
        
        # 归一化编辑距离
        edit_dist = self.normalized_edit_distance(text1_norm, text2_norm)
        details['normalized_edit_distance'] = edit_dist
        
        # 使用传入的文本对信息，避免重复判断
        details['text_pair_type'] = {
            'is_short_pair': text_pair_info.is_short_pair,
            'is_long_short': text_pair_info.is_long_short,
            'is_long_pair': text_pair_info.is_long_pair
        }
        
        if text_pair_info.is_short_pair:
            if edit_dist <= 0.02:
                result = SimilarityResult.RELATED
                confidence = 1.0 - edit_dist
                score = confidence
            elif edit_dist <= 0.08:
                result = SimilarityResult.SIMILAR
                confidence = 1.0 - edit_dist
                score = confidence
            else:
                result = None
                confidence = 0.0
                score = max(jaccard_sim, 1.0 - edit_dist)
        else:
            # 正常阈值
            if jaccard_sim >= 0.95 or edit_dist <= 0.03:
                result = SimilarityResult.RELATED
                confidence = max(jaccard_sim, 1.0 - edit_dist)
                score = confidence
            elif jaccard_sim >= 0.85 or edit_dist <= 0.10:
                result = SimilarityResult.SIMILAR
                confidence = max(jaccard_sim, 1.0 - edit_dist)
                score = confidence
            else:
                result = None
                confidence = 0.0
                score = max(jaccard_sim, 1.0 - edit_dist)
        
        # 记录阶段分数
        log_result = result if result else SimilarityResult.NO_RESULT
        self._log_stage_score(ProcessingStage.QUICK_CHECK, score=score, confidence=confidence,
                             result=log_result, details=details, processed=True)
        
        return result.display_name if result else None
    
    def substring_filter(self, proc1: Dict[str, Any], proc2: Dict[str, Any], text_pair_info: TextPairInfo) -> Optional[str]:
        """子串过滤阶段 - 使用统一的文本对信息，避免重复计算"""
        text1 = proc1['normalized']
        text2 = proc2['normalized']
        
        if not text1 or not text2 or text_pair_info.is_long_short:
            return None
        
        # 一次性确定长短文本及对应的处理对象
        if len(text1) <= len(text2):
            short_text, long_text = text1, text2
            short_original, long_original = proc1['original'], proc2['original']
        else:
            short_text, long_text = text2, text1
            short_original, long_original = proc2['original'], proc1['original']
        
        # 计算基本属性
        is_substring = short_text in long_text
        
        # 初始化基本详情，使用传入的文本对信息
        details = {
            'short_tokens': short_text,
            'long_tokens': long_text,
            'is_substring': is_substring,
            'short_text': short_original,
            'long_text': long_original,
            'text_pair_type': {
                'is_short_pair': text_pair_info.is_short_pair,
                'is_long_short': text_pair_info.is_long_short,
                'is_long_pair': text_pair_info.is_long_pair
            }
        }
        
        if is_substring:
            result = SimilarityResult.RELATED
            confidence = 0.8
        else:
            result = None
            confidence = 0.0
            
        # 记录结果并返回
        if result:
            self._log_stage_score(
                ProcessingStage.SUBSTRING_FILTER,
                score=confidence,
                confidence=confidence,
                result=result,
                details=details,
                processed=True
            )
            return result.display_name
        else:
            # 无子串关系
            details['reason'] = '两个文本之间不存在子串关系'
            self._log_stage_score(
                ProcessingStage.SUBSTRING_FILTER,
                score=0.0,
                confidence=0.0,
                result=SimilarityResult.NO_RESULT,
                details=details,
                processed=True
            )
        
        return None
    
    def _convert_numpy_types(self, obj):
        """递归转换numpy类型和不可序列化的对象为Python原生类型，用于JSON序列化"""
        if isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, '__dict__') and hasattr(obj, '__class__'):
            # 处理自定义类对象（如EntityInfo），转换为字典
            if obj.__class__.__name__ == 'EntityInfo':
                return {
                    'original': obj.original if hasattr(obj, 'original') else '',
                    'normalized': obj.normalized if hasattr(obj, 'normalized') else '',
                    'entity_type': obj.entity_type if hasattr(obj, 'entity_type') else '',
                    'confidence': float(obj.confidence) if hasattr(obj, 'confidence') else 0.0
                }
            else:
                try:
                    return self._convert_numpy_types(obj.__dict__)
                except:
                    return str(obj)
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        else:
            return obj
    
    def save_explainability_data(self, filename: str = None):
        """保存可解释性数据到JSON文件 - 新版本包含所有阶段分数"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"similarity_explainability_{timestamp}.json"
        
        data = []
        
        for i, exp in enumerate(self.explainability_log, 1):
            exp_dict = {
                "test_case_id": i,
                "input_text1": exp.input_text1,
                "input_text2": exp.input_text2,
                "normalized_text1": exp.normalized_text1,
                "normalized_text2": exp.normalized_text2,
                "final_result": exp.final_result,
                "final_confidence": exp.final_confidence,
                "final_stage": exp.final_stage,
                "timestamp": exp.timestamp,
                "stage_scores": exp.get_all_scores()
            }
            
            # 转换numpy类型
            exp_dict = self._convert_numpy_types(exp_dict)
            data.append(exp_dict)
        
        # 添加汇总信息
        summary = {
            "total_test_cases": len(data),
            "generation_time": datetime.now().isoformat(),
            "data_structure_version": "v1.0",
            "note": "concludes all processing stages with detailed scores",
            "stage_list": [
                "Preprocessing and Standardization", "Quick Check", ProcessingStage.SUBSTRING_FILTER.value, ProcessingStage.ENTITY_CHANNEL.value,
                ProcessingStage.LONG_SHORT_SEMANTIC.value, ProcessingStage.OPTIMIZED_LCS.value, ProcessingStage.SEMANTIC_SIMILARITY.value, ProcessingStage.LLM_DECISION.value
            ],
            "stage_score_fields": {
                "score": "Score calculated for the stage (0-1)",
                "confidence": "Confidence level for the stage (0-1)",
                "result": "Result determined in the stage",
                "processed": "Whether the stage was processed",
                "details": "Detailed calculation information for the stage"
            }
        }

        
        final_data = {
            "summary": summary,
            "explainability_logs": data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        
        print(f"  保存了 {len(data)} 个测试用例的完整阶段分数数据")
        print(f"  数据文件: {filename}")
        print(f"  每个测试用例包含 {len(summary['stage_list'])} 个处理阶段的分数信息")
        return filename
    
    def save_final_explainability_data(self):
        """在所有计算完成后保存一次可解释性数据"""
        if self.explainability_log:
            try:
                filename = self.save_explainability_data()
                print(f"\n✓ 所有测试完成，已保存完整的可解释性数据到: {filename}")
                return filename
            except Exception as e:
                print(f"\n✗ 保存可解释性数据失败: {e}")
                return None
        else:
            logging.warning("\n⚠ 没有可解释性数据可保存")
            return None
    
    def calculate_similarity(self, text1: str, text2: str, clear_log: bool = False, auto_save: bool = False) -> Tuple[str, float, str]:
        """
        计算句子相似度的主函数 - 统一文本类型判断，避免重复计算
        
        Args:
            text1: 第一个句子
            text2: 第二个句子
            clear_log: 是否清空之前的可解释性日志（默认False，保持累积）
            auto_save: 是否自动保存可解释性数据到文件（默认False）
            
        Returns:
            Tuple[str, float, str]: (result, confidence, stage)
            result: 判断结果（'相关'，'相似'，'不相关'）
            confidence: 归一化的置信度 (0-1)
            stage: 早停的阶段名称
        """
        if clear_log:
            self.explainability_log = []
        
        # 统一计算文本对信息，避免后续方法重复判断
        text_pair_info = TextPairInfo.create(text1, text2, self.preprocessor)
        
        # 预处理与标准化 - 传递已计算的短文本信息，避免重复判断
        proc1 = self.preprocessor.preprocess(text1, text_pair_info.enable_entity_extraction, text_pair_info.is_short1)
        proc2 = self.preprocessor.preprocess(text2, text_pair_info.enable_entity_extraction, text_pair_info.is_short2)
        
        # 初始化当前文本对的可解释性记录
        self._init_explainability_for_pair(text1, text2, proc1['normalized'], proc2['normalized'])
        
        # 记录预处理阶段
        self._log_stage_score(ProcessingStage.PREPROCESSING, score=1.0, confidence=1.0, result=SimilarityResult.COMPLETED,
                             details={
                                 "proc1": proc1,
                                 "proc2": proc2,
                                 "text_pair_info": {
                                     "is_short1": text_pair_info.is_short1,
                                     "is_short2": text_pair_info.is_short2,
                                     "is_short_pair": text_pair_info.is_short_pair,
                                     "is_long_short": text_pair_info.is_long_short,
                                     "is_long_pair": text_pair_info.is_long_pair,
                                     "enable_entity_extraction": text_pair_info.enable_entity_extraction
                                 }
                             }, processed=True)
        
        # 执行各阶段判断逻辑并得到最终结果
        final_result = None
        final_confidence = 0.0
        final_stage = ""
        
        # 1. 快速检查
        result = self.quick_check(proc1, proc2, text_pair_info)
        if result:
            confidence = self.current_explainability.stage_scores[ProcessingStage.QUICK_CHECK.value].confidence
            # 获取文本对信息
            text_pair_info_dict = {
                'is_short_pair': text_pair_info.is_short_pair,
                'is_long_short': text_pair_info.is_long_short,
                'is_long_pair': text_pair_info.is_long_pair
            }
            self._finalize_explainability(result, confidence, ProcessingStage.QUICK_CHECK.value)
            final_result = result
            final_confidence = confidence
            final_stage = ProcessingStage.QUICK_CHECK.value
        else:
            # 2. 子串过滤
            result = self.substring_filter(proc1, proc2, text_pair_info)
            if result:
                confidence = self.current_explainability.stage_scores[ProcessingStage.SUBSTRING_FILTER.value].confidence
                # 获取文本对信息
                text_pair_info_dict = {
                    'is_short_pair': text_pair_info.is_short_pair,
                    'is_long_short': text_pair_info.is_long_short,
                    'is_long_pair': text_pair_info.is_long_pair
                }
                
                self._finalize_explainability(result, confidence, ProcessingStage.SUBSTRING_FILTER.value)
                final_result = result
                final_confidence = confidence
                final_stage = ProcessingStage.SUBSTRING_FILTER.value
            else:
                # 3. 专名通道 - 只在短-短文本中执行
                if text_pair_info.enable_entity_extraction:
                    result = self.entity_channel(proc1, proc2, text_pair_info)
                    if result:
                        confidence = self.current_explainability.stage_scores[ProcessingStage.ENTITY_CHANNEL.value].confidence
                        # 获取文本对信息
                        text_pair_info_dict = {
                            'is_short_pair': text_pair_info.is_short_pair,
                            'is_long_short': text_pair_info.is_long_short,
                            'is_long_pair': text_pair_info.is_long_pair
                        }
                        
                        self._finalize_explainability(result, confidence, ProcessingStage.ENTITY_CHANNEL.value)
                        final_result = result
                        final_confidence = confidence
                        final_stage = ProcessingStage.ENTITY_CHANNEL.value
                else:
                    # 记录专名通道未处理的情况
                    self._log_stage_score(ProcessingStage.ENTITY_CHANNEL, score=0.0, confidence=0.0, result="跳过",
                                          details={"reason": "not is_short_pair"}, processed=False)
                
                if not final_result:
                    # 3.5. 长-短文本语义匹配（word2vec）
                    if text_pair_info.is_long_short:
                        result = self.long_short_semantic_match(proc1, proc2, text_pair_info)
                        if result:
                            confidence = self.current_explainability.stage_scores[ProcessingStage.LONG_SHORT_SEMANTIC.value].confidence
                            # 获取文本对信息
                            text_pair_info_dict = {
                                'is_short_pair': text_pair_info.is_short_pair,
                                'is_long_short': text_pair_info.is_long_short,
                                'is_long_pair': text_pair_info.is_long_pair
                            }
                            
                            self._finalize_explainability(result, confidence, ProcessingStage.LONG_SHORT_SEMANTIC.value)
                            final_result = result
                            final_confidence = confidence
                            final_stage = ProcessingStage.LONG_SHORT_SEMANTIC.value
                    else:
                        # 记录长短语义匹配未处理
                        self._log_stage_score(ProcessingStage.LONG_SHORT_SEMANTIC, score=0.0, confidence=0.0, result="跳过",
                                              details={"reason": "not is_long_short"}, processed=False)
                
                if not final_result:
                    # 4. 优化LCS
                    result = self.optimized_lcs(proc1, proc2, text_pair_info)
                    if result:
                        confidence = self.current_explainability.stage_scores[ProcessingStage.OPTIMIZED_LCS.value].confidence
                        # 获取文本对信息
                        text_pair_info_dict = {
                            'is_short_pair': text_pair_info.is_short_pair,
                            'is_long_short': text_pair_info.is_long_short,
                            'is_long_pair': text_pair_info.is_long_pair
                        }
                        
                        self._finalize_explainability(result, confidence, ProcessingStage.OPTIMIZED_LCS.value)
                        final_result = result
                        final_confidence = confidence
                        final_stage = ProcessingStage.OPTIMIZED_LCS.value
                
                if not final_result:
                    # 5. 语义相似
                    result = self.semantic_similarity(proc1, proc2, text_pair_info)
                    if result:
                        confidence = self.current_explainability.stage_scores[ProcessingStage.SEMANTIC_SIMILARITY.value].confidence
                        # 获取文本对信息
                        text_pair_info_dict = {
                            'is_short_pair': text_pair_info.is_short_pair,
                            'is_long_short': text_pair_info.is_long_short,
                            'is_long_pair': text_pair_info.is_long_pair
                        }
                        
                        self._finalize_explainability(result, confidence, ProcessingStage.SEMANTIC_SIMILARITY.value)
                        final_result = result
                        final_confidence = confidence
                        final_stage = ProcessingStage.SEMANTIC_SIMILARITY.value
                
                if not final_result:
                    # 6. LLM裁决
                    result = self.llm_decision(proc1, proc2, text_pair_info)
                    confidence = self.current_explainability.stage_scores[ProcessingStage.LLM_DECISION.value].confidence
                    # 获取文本对信息
                    text_pair_info_dict = {
                        'is_short_pair': text_pair_info.is_short_pair,
                        'is_long_short': text_pair_info.is_long_short,
                        'is_long_pair': text_pair_info.is_long_pair
                    }
                    
                    self._finalize_explainability(result, confidence, ProcessingStage.LLM_DECISION.value)
                    final_result = result
                    final_confidence = confidence
                    final_stage = ProcessingStage.LLM_DECISION.value
        
        return final_result, final_confidence
    
    def entity_channel(self, proc1: Dict[str, Any], proc2: Dict[str, Any], text_pair_info: TextPairInfo) -> Optional[str]:
        """专名通道阶段 - 使用统一的文本对信息，避免重复计算"""
        entities1 = proc1.get('entities_info', {})
        entities2 = proc2.get('entities_info', {})
        
        # 检查是否有实体
        has_entities = any(entities1.values()) or any(entities2.values())
        
        details = {
            'entities1_count': {k: len(v) for k, v in entities1.items()},
            'entities2_count': {k: len(v) for k, v in entities2.items()},
            'text_pair_type': {
                'is_short_pair': text_pair_info.is_short_pair,
                'is_long_short': text_pair_info.is_long_short,
                'is_long_pair': text_pair_info.is_long_pair
            }
        }
        
        if not has_entities:
            # 记录没有实体的情况
            self._log_stage_score(ProcessingStage.ENTITY_CHANNEL, score=0.0, confidence=0.0, result="no entitys",
                                 details={**details, "reason": "both no entitys"}, processed=True)
            return None
        
        # 使用新的实体比较功能
        entity_similarities = self.preprocessor.entity_extractor.compare_entities(entities1, entities2)
        details['entity_similarities'] = entity_similarities
        
        # 根据实体相似度判断
        max_similarity = 0.0
        best_entity_type = ""
        
        for entity_type, similarity in entity_similarities.items():
            if similarity > max_similarity:
                max_similarity = similarity
                best_entity_type = entity_type
        
        details['max_similarity'] = max_similarity
        details['best_entity_type'] = best_entity_type
        
        if max_similarity > 0:
            if max_similarity >= 0.95:
                result = SimilarityResult.RELATED.display_name
                confidence = max_similarity
            elif max_similarity >= 0.85:
                result = SimilarityResult.SIMILAR.display_name
                confidence = max_similarity
            else:
                result = None
                confidence = max_similarity
            
            if result:
                self._log_stage_score(ProcessingStage.ENTITY_CHANNEL, score=confidence, confidence=confidence,
                                     result=result, details=details, processed=True)
                return result
            else:
                # 记录有实体但相似度不满足阈值的情况
                self._log_stage_score(ProcessingStage.ENTITY_CHANNEL, score=max_similarity, confidence=max_similarity,
                                     result="low entity similarity", details=details, processed=True)
        else:
            # 记录实体相似度为0的情况
            self._log_stage_score(ProcessingStage.ENTITY_CHANNEL, score=0.0, confidence=0.0, result="no entity similarity",
                                 details={**details, "reason": "no similar entity"}, processed=True)
        
        return None
    
    def long_short_semantic_match(self, proc1: Dict[str, Any], proc2: Dict[str, Any], text_pair_info: TextPairInfo) -> Optional[str]:
        """
        长-短文本语义匹配阶段 - 使用统一的文本对信息，避免重复计算
        基于Word2Vec的实现
        
        实现思路：
        1. 使用预训练的word2vec模型获取词向量
        2. 长文本分割成单元，每个单元词向量取平均得到"单元向量", 再取平均
        3. 短文本词向量取平均得到"短文本向量"
        4. 计算每个单元向量与短文本向量的余弦相似度
        5. 根据相似度阈值和匹配占比进行判断
        """
        # 如果没有启用word2vec功能，跳过此阶段
        if not self.use_word2vec:
            self._log_stage_score(ProcessingStage.LONG_SHORT_SEMANTIC, score=0.0, confidence=0.0,
                                 result="skipped",
                                 details={"reason": "Word2Vec unavailable or disabled"},
                                 processed=False)
            return None
        
        # 使用传入的文本对信息确定长短文本
        if text_pair_info.is_short1:
            short_proc, long_proc = proc1, proc2
        else:
            short_proc, long_proc = proc2, proc1
        
        short_tokens = short_proc['tokens']
        long_tokens = long_proc['tokens']
        
        if not short_tokens or not long_tokens:
            return None
        
        details = {
            'short_tokens': short_tokens,
            'long_tokens': long_tokens,
            'short_tokens_count': len(short_tokens),
            'long_tokens_count': len(long_tokens),
            'text_pair_type': {
                'is_short_pair': text_pair_info.is_short_pair,
                'is_long_short': text_pair_info.is_long_short,
                'is_long_pair': text_pair_info.is_long_pair
            }
        }
        
        try:
            # 1. 获取短文本向量
            short_vector = self._get_text_vector_word2vec(short_tokens)
            if short_vector is None:
                # Word2Vec无法处理，记录并跳过此阶段
                self._log_stage_score(ProcessingStage.LONG_SHORT_SEMANTIC, score=0.0, confidence=0.0,
                                     result="Word2Vec cannot process",
                                     details={
                                         'reason': 'Word2Vec cannot obtain short text vector',
                                         'short_tokens': short_tokens,
                                         'model_name': self.word2vec_model_name
                                     }, processed=True)
                return None
            
            # 2. 长文本分割成单元，使用滑动窗口为原窗口的1.5倍
            window_size = max(3, int(len(short_tokens) * 1.5)) 
            long_units = self._split_long_text_into_units(long_tokens, window_size)
            details['window_size'] = window_size
            details['long_units_count'] = len(long_units)
            
            # 3. 计算每个长文本单元的向量
            unit_vectors = []
            unit_similarities = []
            
            for i, unit_tokens in enumerate(long_units):
                unit_vector = self._get_text_vector_word2vec(unit_tokens)
                if unit_vector is not None:
                    unit_vectors.append(unit_vector)
                    
                    # # 计算与短文本的余弦相似度
                    
                    # unit_similarities.append({
                    #     'unit_index': i,
                    #     'unit_tokens': unit_tokens,
                    #     'similarity': similarity
                    # })
            
            if not unit_vectors:
                self._log_stage_score(ProcessingStage.LONG_SHORT_SEMANTIC, score=0.0, confidence=0.0,
                                     result="Word2Vec cannot process",
                                     details={
                                         'reason': 'Word2Vec cannot obtain any long text unit vectors',
                                         'long_tokens': long_tokens,
                                         'model_name': self.word2vec_model_name
                                     }, processed=True)
            
            long_text_avg_vector = np.mean(unit_vectors, axis=0)
            similarity = self._cosine_similarity(short_vector, long_text_avg_vector)
            details['similarity'] = similarity
            
        
            is_topic_match = False
            confidence = 0.0
            
            if similarity >= 0.80:
                # 高置信度匹配
                is_topic_match = True
                confidence = similarity
                result = SimilarityResult.RELATED.display_name
            elif similarity >= 0.70:
                # 阈值+占比匹配
                is_topic_match = True
                confidence = similarity
                result = SimilarityResult.SIMILAR.display_name
            else:
                result = None
                confidence = similarity
            
            details['is_topic_match'] = is_topic_match
            details['final_confidence'] = confidence
            details['decision_reason'] = f"sim={similarity:.3f}"
            
            if result:
                try:
                    self._log_stage_score(ProcessingStage.LONG_SHORT_SEMANTIC, score=confidence, confidence=confidence,
                                         result=result, details=details, processed=True)
                except Exception as log_error:
                    print(f"   日志记录失败: {log_error}")
                    # 即使日志失败，也要返回结果
                return result
                
        except Exception as e:
            logging.error(f"   Word2Vec匹配过程出错: {e}")
            details['error'] = str(e)
            self._log_stage_score(ProcessingStage.LONG_SHORT_SEMANTIC, score=0.0, confidence=0.0,
                                    result="error", details=details, processed=True)
        
        return None
    
    def _get_text_vector_word2vec(self, tokens: List[str]) -> Optional[np.ndarray]:
        """
        使用Word2Vec方法获取文本向量（词向量的平均值）
        
        Args:
            tokens: 分词后的词列表
            
        Returns:
            文本向量，如果无法获取则返回None
        """
        if not tokens:
            return None
        
        try:
            word_vectors = []
            
            for token in tokens:
                # 尝试从Word2Vec模型获取词向量
                word_vector = self._get_word_vector_from_word2vec(token)
                if word_vector is not None:
                    word_vectors.append(word_vector)
            
            if not word_vectors:
                return None
            
            # 计算所有词向量的平均值
            text_vector = np.mean(word_vectors, axis=0)
            return text_vector
            
        except Exception as e:
            logging.error(f"获取Word2Vec文本向量失败: {e}")
            return None
    
    def _get_word_vector_from_word2vec(self, word: str) -> Optional[np.ndarray]:
        """
        从Word2Vec模型获取单个词的词向量
        
        Args:
            word: 单词
            
        Returns:
            词向量，如果无法获取则返回None
        """
        try:
            if self.word2vec_model is not None:
                if word in self.word2vec_model:
                    return self.word2vec_model[word]
                else:
                    return None
            
            # 暂时降级到embedding方式
            embeddings = self._get_embeddings([word])
            return embeddings[0]
            
        except Exception as e:
            print(f"获取词向量失败 (word: {word}): {e}")
            return None
    
    def _split_long_text_into_units(self, tokens: List[str], window_size: int) -> List[List[str]]:
        """
        将长文本分割成重叠的单元
        
        Args:
            tokens: 长文本的词列表
            window_size: 窗口大小
            
        Returns:
            分割后的单元列表
        """
        if len(tokens) <= window_size:
            return [tokens]
        
        units = []
        step_size = max(1, window_size // 2)  # 步长为窗口大小的一半，产生重叠
        
        for i in range(0, len(tokens) - window_size + 1, step_size):
            unit = tokens[i:i + window_size]
            units.append(unit)
        
        # 确保最后一个单元包含文本末尾
        if units and units[-1][-1] != tokens[-1]:
            last_unit = tokens[-window_size:]
            units.append(last_unit)
        
        return units
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            vec1: 向量1
            vec2: 向量2
            
        Returns:
            余弦相似度值
        """
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    
    def optimized_lcs(self, proc1: Dict[str, Any], proc2: Dict[str, Any], text_pair_info: TextPairInfo) -> Optional[str]:
        """优化LCS阶段 - 使用统一的文本对信息，避免重复计算"""
        text1 = proc1['normalized']
        text2 = proc2['normalized']
        
        if not text1 or not text2:
            return None
        
        # 计算LCS长度（空间优化版本）
        lcs_length = self._calculate_lcs_length_optimized(text1, text2)
        
        len1, len2 = len(text1), len(text2)
        lcs_ratio_max = lcs_length / max(len1, len2) if max(len1, len2) > 0 else 0
        lcs_ratio_min = lcs_length / min(len1, len2) if min(len1, len2) > 0 else 0
        
        details = {
            'lcs_length': lcs_length,
            'text1_length': len1,
            'text2_length': len2,
            'lcs_ratio_max': lcs_ratio_max,
            'lcs_ratio_min': lcs_ratio_min,
            'text_pair_type': {
                'is_short_pair': text_pair_info.is_short_pair,
                'is_long_short': text_pair_info.is_long_short,
                'is_long_pair': text_pair_info.is_long_pair
            }
        }
        
        
        if lcs_ratio_min >= 0.8 and lcs_ratio_max >= 0.4:
            result = SimilarityResult.RELATED.display_name
            confidence = lcs_ratio_min
        elif lcs_ratio_min >= 0.7 and lcs_ratio_max >= 0.3:
            result = SimilarityResult.SIMILAR.display_name
            confidence = lcs_ratio_min
        else:
            result = None
            confidence = 0.0
        
        if result:
            self._log_stage_score(ProcessingStage.OPTIMIZED_LCS, score=confidence, confidence=confidence,
                                 result=result, details=details, processed=True)
        else:
            self._log_stage_score(ProcessingStage.OPTIMIZED_LCS, score=max(lcs_ratio_max, lcs_ratio_min), confidence=0.0,
                                 result="LCS similarity is low", details=details, processed=True)
        
        return result
    
    def _calculate_lcs_length_optimized(self, s1: str, s2: str) -> int:
        """优化的LCS长度计算（空间优化 + 剪枝）"""
        m, n = len(s1), len(s2)
        if m == 0 or n == 0:
            return 0
        #空间优化使用一位数组
        prev = [0] * (n + 1)
        curr = [0] * (n + 1)
        
        max_possible_remaining = m
        current_max = 0
        
        for i in range(1, m + 1):
            max_possible_remaining -= 1
            
            # 剪枝
            if current_max + max_possible_remaining <= current_max:
                break
            
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    curr[j] = prev[j-1] + 1
                else:
                    curr[j] = max(prev[j], curr[j-1])
                
                current_max = max(current_max, curr[j])
            
            prev, curr = curr, prev
        
        return current_max
    
    def semantic_similarity(self, proc1: Dict[str, Any], proc2: Dict[str, Any], text_pair_info: TextPairInfo) -> Optional[str]:
        """语义相似阶段 - 使用统一的文本对信息，避免重复计算"""
        text1 = proc1['normalized']
        text2 = proc2['normalized']
        
        if not text1 or not text2:
            return None
        
        # 生成向量
        embeddings = self._get_embeddings([text1, text2])
        vec1, vec2 = embeddings[0], embeddings[1]
        
        # 计算余弦相似度
        cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        s_sem_norm = cosine_sim * 100
        
        details = {
            'cosine_similarity': cosine_sim,
            'semantic_score_normalized': s_sem_norm,
            'text_pair_type': {
                'is_short_pair': text_pair_info.is_short_pair,
                'is_long_short': text_pair_info.is_long_short,
                'is_long_pair': text_pair_info.is_long_pair
            }
        }
        
        if s_sem_norm >= 85:
            result = SimilarityResult.RELATED.display_name
            confidence = s_sem_norm / 100
        elif s_sem_norm >= 75:
            result = SimilarityResult.SIMILAR.display_name
            confidence = s_sem_norm / 100
        else:
            result = None
            confidence = s_sem_norm / 100
        
        score = s_sem_norm / 100
        self._log_stage_score(ProcessingStage.SEMANTIC_SIMILARITY, score=score, confidence=confidence,
                             result=result or "no result", details=details, processed=True)
        
        return result
    
    def llm_decision(self, proc1: Dict[str, Any], proc2: Dict[str, Any], text_pair_info: TextPairInfo) -> str:
        """LLM裁决阶段 - 使用统一的文本对信息，避免重复计算"""
        if not self.api_key:
            result = SimilarityResult.UNRELATED.display_name
            confidence = 0.5
            details = {"reason": "no LLM API key provided"}
            self._log_stage_score(ProcessingStage.LLM_DECISION, score=confidence, confidence=confidence,
                                 result=SimilarityResult.UNRELATED, details=details, processed=True)
            return result
        
        # 使用传入的文本对信息确定文本类型描述
        if text_pair_info.is_short_pair:
            text_type_desc = "短-短文本对"
        elif text_pair_info.is_long_short:
            text_type_desc = "长-短文本对"
        else:
            text_type_desc = "长-长文本对"
        
        prompt = f"""
### 任务目标
基于「文本类型」的领域特性和句子核心语义，精准判断以下两个句子的相似度关系，并给出0.0-1.0的相关性分数（分数越高，语义关联度越强），**严格避免将无关文本误判为相似**。

### 核心信息
1. 句子1（原始文本）：{proc1['original']}
2. 句子2（原始文本）：{proc2['original']}
3. 文本类型及领域特性说明：{text_type_desc}
   - 请优先结合该文本类型的专业场景（如法律文本需关注条款主体/权责，医疗文本需关注病症/治疗方案，日常对话需关注意图/核心诉求）判断语义关联，而非仅看字面重合度。

### 严格判断标准（含反例说明）
请先判断句子是否满足「核心语义一致/关联」，再匹配对应等级及分数范围，**无关文本必须归为UNRELATED且分数≤0.5**：
1. 【{SimilarityResult.RELATED.display_name}】- 分数0.8-1.0
   - 判定条件：核心语义完全一致（或仅存在表述方式差异，无信息增减），且符合文本类型的专业逻辑。
   - 示例：文本类型为"产品说明"，句子1="手机续航时长约12小时"，句子2="该手机连续使用可支持12小时左右"（核心信息"手机续航12小时"完全一致）。
   - 反例：句子1="手机续航12小时"，句子2="手机充电12小时"（核心动作"续航"vs"充电"相反，不归属此类）。

2. 【{SimilarityResult.SIMILAR.display_name}】- 分数0.7-0.8
   - 判定条件：核心语义存在3/4以上重合，仅在次要信息（如时间、数量、范围的细微差异）上有区别，且无核心矛盾。
   - 示例：文本类型为"会议通知"，句子1="周三下午3点召开项目会"，句子2="周三下午3:10召开项目会"（核心信息"周三下午项目会"一致，仅时间细微差异）。
   - 反例：句子1="周三开项目会"，句子2="周四开部门会"（核心信息"时间""会议类型"均不同，不归属此类）。

3. 【{SimilarityResult.UNRELATED.display_name}】- 分数0.0-0.5
   - 判定条件：满足以下任一情况即归为此类：
     ① 核心语义无关联（如句子1谈"天气"，句子2谈"电脑"）；
     ② 核心语义存在矛盾（如句子1="产品合格"，句子2="产品不合格"）；
     ③ 核心信息重合度低于1/2（如句子1="苹果手机的拍照功能"，句子2="华为电脑的续航能力"）。
   - 强制要求：若判定为该等级，分数必须≤0.5，且分数需体现关联度（如完全无关给0.0-0.2，微弱关联给0.3-0.5）。

### 输出要求
1. 必须先梳理两个句子的「核心语义」（无需写出，仅用于内部判断），再匹配等级和分数，禁止仅因字面有重合而误判。
2. 严格按照以下JSON格式返回，不允许添加任何额外文字（包括解释、说明），JSON字段值必须与上述等级名称完全一致：
{{"think": 思考以及裁决原因（小于50字）, "result": "{SimilarityResult.RELATED.display_name}"|"{SimilarityResult.SIMILAR.display_name}"|"{SimilarityResult.UNRELATED.display_name}", "confidence": 0.0-1.0的浮点数（保留2位小数）}}

### 错误案例警示（需避免）
- 错误1：句子1="今天会下雨"，句子2="明天会晴天"，误判为SIMILAR（分数0.7）→ 正确应为UNRELATED（核心语义"时间""天气状况"均矛盾，分数0.1）。
- 错误2：句子1="数学考试时间为9点"，句子2="英语作业需9点提交"，误判为RELATED（分数0.85）→ 正确应为UNRELATED（核心语义"数学考试"vs"英语作业"无关联，分数0.0）。
"""
        
        try:
            # 使用抽象的_call_llm方法
            llm_response = self._call_llm(prompt)
            details = {
                "llm_response": llm_response,
                'text_pair_type': {
                    'is_short_pair': text_pair_info.is_short_pair,
                    'is_long_short': text_pair_info.is_long_short,
                    'is_long_pair': text_pair_info.is_long_pair
                }
            }
            
            # 尝试解析JSON格式的响应
            try:
                import json
                parsed_response = json.loads(llm_response)
                result_text = parsed_response.get("result", SimilarityResult.UNRELATED.display_name)
                raw_confidence = float(parsed_response.get("confidence", 0.5))
                thinking = parsed_response.get("think", "")
                
                # 验证结果有效性并转换为display_name
                if result_text == SimilarityResult.RELATED.display_name:
                    result = SimilarityResult.RELATED.display_name
                elif result_text == SimilarityResult.SIMILAR.display_name:
                    result = SimilarityResult.SIMILAR.display_name
                else:
                    result = SimilarityResult.UNRELATED.display_name
                    # 对于不相关结果，确保置信度较低
                    if raw_confidence > 0.5:
                        # 如果LLM返回了较高的不相关置信度，将其转换为较低的相关性置信度
                        raw_confidence = 0.3  # 固定为较低的相关性置信度
                
                # 确保置信度在合理范围内
                confidence = max(0.0, min(1.0, raw_confidence))
                
                details["parsed_result"] = result
                details["parsed_confidence"] = confidence
                details["thinking"] = thinking
                
            except (json.JSONDecodeError, ValueError, KeyError) as parse_error:
                # JSON解析失败，尝试从文本中提取结果
                details["parse_error"] = str(parse_error)
                
                if SimilarityResult.RELATED.display_name in llm_response and SimilarityResult.UNRELATED.display_name not in llm_response:
                    result = SimilarityResult.RELATED.display_name
                    confidence = 0.85  # 高相关性
                elif SimilarityResult.SIMILAR.display_name in llm_response:
                    result = SimilarityResult.SIMILAR.display_name
                    confidence = 0.7   # 中等相关性
                else:
                    result = SimilarityResult.UNRELATED.display_name
                    confidence = 0.2   # 低相关性
                
                details["fallback_parsing"] = True
                details["fallback_result"] = result
                details["fallback_confidence"] = confidence
            
        except Exception as e:
            result = SimilarityResult.UNRELATED.display_name
            confidence = 0.3  # 降低不相关情况下的置信度
            details = {"error": str(e)}
        
        # 记录阶段分数 - 需要传递正确的枚举值
        score = confidence
        result_enum = None
        if result == SimilarityResult.RELATED.display_name:
            result_enum = SimilarityResult.RELATED
        elif result == SimilarityResult.SIMILAR.display_name:
            result_enum = SimilarityResult.SIMILAR
        else:
            result_enum = SimilarityResult.UNRELATED
        
        # Ensuring the result is always serialized properly as string
        self._log_stage_score(ProcessingStage.LLM_DECISION, score=score, confidence=confidence,
                             result=result_enum.value, details=details, processed=True)
        
        return result


def load_test_data_from_excel(excel_path: str) -> List[Tuple[str, str, str]]:
    """
    从Excel文件加载测试数据，包含文本对和标签
    
    Args:
        excel_path: Excel文件路径
        
    Returns:
        测试用例列表，每个元素为(文本1, 文本2, 标签)的元组
    """
    try:
        df = pd.read_excel(excel_path)
        
        # 新增'标签'列到必需列列表
        required_columns = ['序号', '文本1', '文本2', '标签']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"   Excel文件缺少必需的列: {missing_columns}")
            print(f"当前列名: {list(df.columns)}")
            return []
        
        test_cases = []
        for index, row in df.iterrows():
            text1 = str(row['文本1']).strip()
            text2 = str(row['文本2']).strip()
            label = str(row['标签']).strip()  # 读取标签并处理
            
            # 跳过空值或无效数据
            if (not text1 or not text2 or not label or 
                text1 == 'nan' or text2 == 'nan' or label == 'nan'):
                print(f"   跳过无效数据行 {index+1}: 存在空值")
                continue
                
            # 验证标签有效性
            valid_labels = [Label.UNRELATED.value, Label.RELATED.value, Label.SIMILAR.value]
            if label not in valid_labels:
                print(f"   跳过无效数据行 {index+1}: 标签'{label}'不合法，必须是{valid_labels}")
                continue
                
            test_cases.append((text1, text2, label))
        
        print(f"  成功从Excel文件加载 {len(test_cases)} 个有效测试用例")
        return test_cases
        
    except FileNotFoundError:
        print(f"   Excel文件不存在: {excel_path}")
        return []
    except Exception as e:
        print(f"   读取Excel文件失败: {e}")
        return []


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    calculator = SentenceSimilarityCalculator(
        api_base_url="https://api.ai.ksyun.com/v1/",                    # 统一API URL
        api_key="m3msg1fz3cbxt7x8qq49yc8t7y94ourz",                    # API密钥
        llm_model_id="gpt-4.1",         # LLM模型ID
        embedding_model_id="qzhou-embedding",  # Embedding模型ID
        use_local_embedding=False,             # 是否使用本地embedding
        local_embedding_model="all-MiniLM-L6-v2",  # 本地embedding模型名称
        use_word2vec=True,                     # 是否使用Word2Vec进行长短文本匹配
        word2vec_model_name="word2vec-google-news-300"  # 多语言Word2Vec模型名称
    )
    
    excel_file_path = "case_test.xlsx"
    test_cases = load_test_data_from_excel(excel_file_path)
    execution_times = []
    true_labels = []  # 存储真实标签
    pred_labels = []  # 存储预测标签
    results = []      # 存储详细结果用于后续分析
    
    # 标签映射：将文本标签转换为数字以便计算
    label_mapping = {Label.UNRELATED.value: 0, Label.RELATED.value: 1, Label.SIMILAR.value: 2}
    reverse_mapping = {v: k.value for k, v in label_mapping.items()}
    
    # 测试示例
    if test_cases:
        logging.info(f"成功加载 {len(test_cases)} 条测试用例")
        
        # 修正：元组解包数量从4个改为3个，与数据加载函数返回格式一致
        for idx, (text1, text2, true_label) in enumerate(test_cases):
            # 使用索引作为case_id（如果需要保留原始序号，可以在load函数中返回）
            case_id = idx + 1  # 从1开始编号
            
            logging.info(f"\n=== 测试用例 {case_id}（{idx+1}/{len(test_cases)}） ===")
            logging.info(f"文本1: {text1[:100]}...")  # 只显示前100字符，避免过长
            logging.info(f"文本2: {text2[:100]}...")
            logging.info(f"真实标签: {true_label}")
            
            try:
                # 验证标签有效性
                if true_label not in label_mapping:
                    raise ValueError(f"无效标签: {true_label}，必须是'不相关'、'相关'或'相似'")
                
                # 记录开始时间
                start_time = time.time()
                
                # 第一次调用清空日志
                clear_log = (idx == 0)
                result, confidence = calculator.calculate_similarity(text1, text2, clear_log=clear_log)
                
                # 计算耗时并存储
                end_time = time.time()
                execution_time = end_time - start_time
                execution_times.append(execution_time)
                
                logging.info(f"预测结果: {result}")
                logging.info(f"置信度: {confidence:.3f}")
                logging.info(f"耗时: {execution_time:.4f}秒")
                
                # 存储真实标签和预测标签（转换为数字）
                true_labels.append(label_mapping[true_label])
                pred_labels.append(label_mapping[result])
                
                # 存储详细结果
                results.append({
                    "序号": case_id,
                    "文本1": text1,
                    "文本2": text2,
                    "真实标签": true_label,
                    "预测标签": result,
                    "置信度": confidence,
                    "耗时(秒)": execution_time,
                    "是否正确": (true_label == result)
                })
                
            except Exception as e:
                logging.error(f"计算出错: {e}")

        # 在所有测试用例执行完后保存解释性数据
        calculator.save_final_explainability_data()
        
        # 计算并打印时间统计信息
        if execution_times:
            min_time = min(execution_times)
            max_time = max(execution_times)
            avg_time = mean(execution_times)
            total_time = sum(execution_times)
            
            logging.info("\n=== 性能统计 ===")
            logging.info(f"测试用例总数: {len(execution_times)}")
            logging.info(f"总耗时: {total_time:.4f}秒")
            logging.info(f"平均耗时: {avg_time:.4f}秒")
            logging.info(f"最短耗时: {min_time:.4f}秒")
            logging.info(f"最长耗时: {max_time:.4f}秒")
        
        # 计算并打印评估指标
        if true_labels and pred_labels:
            # 多分类准确率
            accuracy = accuracy_score(true_labels, pred_labels)
            
            # 宏平均精确率、召回率、F1分数
            precision, recall, f1, _ = precision_recall_fscore_support(
                true_labels, pred_labels, average="macro"
            )
            
            # 混淆矩阵
            cm = confusion_matrix(true_labels, pred_labels)
            
            logging.info("\n=== 评估指标 ===")
            logging.info(f"多分类准确率: {accuracy:.4f}")
            logging.info(f"宏平均精确率: {precision:.4f}")
            logging.info(f"宏平均召回率: {recall:.4f}")
            logging.info(f"宏平均F1分数: {f1:.4f}")
            
            logging.info("\n=== 混淆矩阵 ===")
            logging.info("行: 真实标签, 列: 预测标签")
            logging.info(f"标签对应: {reverse_mapping}")
            for row in cm:
                logging.info(f"    {row}")
                
            # 打印每类的详细指标
            class_precision, class_recall, class_f1, class_support = precision_recall_fscore_support(
                true_labels, pred_labels, average=None
            )
            
            logging.info("\n=== 每类详细指标 ===")
            for i in range(len(class_precision)):
                logging.info(
                    f"{reverse_mapping[i]}: 精确率={class_precision[i]:.4f}, "
                    f"召回率={class_recall[i]:.4f}, F1分数={class_f1[i]:.4f}, "
                    f"样本数={class_support[i]}"
                )
            
            # 保存详细结果到Excel
            results_df = pd.DataFrame(results)
            results_df.to_excel("test_results_with_metrics.xlsx", index=False)
            logging.info("\n详细结果已保存至 test_results_with_metrics.xlsx")
                
    else:
        # 如果没有测试数据，使用默认示例
        logging.info("\n=== 未加载到测试数据，使用默认示例 ===")
        text1 = "今天天气很好"
        text2 = "今天的天气非常不错"
        true_label = "相似"  # 手动指定默认示例的真实标签
        case_id = 1
        logging.info(f"测试用例 {case_id}")
        logging.info(f"文本1: {text1}")
        logging.info(f"文本2: {text2}")
        logging.info(f"真实标签: {true_label}")
        
        # 记录开始时间
        start_time = time.time()
        
        result, confidence = calculator.calculate_similarity(text1, text2, clear_log=True)
        
        # 计算耗时
        end_time = time.time()
        execution_time = end_time - start_time
        
        logging.info(f"预测结果: {result}")
        logging.info(f"置信度: {confidence:.3f}")
        logging.info(f"耗时: {execution_time:.4f}秒")
        
        # 计算单个示例的简单指标
        true_labels = [label_mapping[true_label]]
        pred_labels = [label_mapping[result]]
        accuracy = accuracy_score(true_labels, pred_labels)
        logging.info(f"准确率: {accuracy:.4f}")

    # text1 = "务。有关部门对中介机构作出的违法违规决定和\"黑名单\"情况,要\n通过企业信用信息公示系统依法公示。对严重失信中介机构及其法定\n代表人,主要负责人和对失信行为负有直接责任的从业人员等,要联\n合实施市场和行业禁入措施。逐步建立全国房地产中介行业信用管理\n平台,并纳入全国社会信用体系。\n\n(十四)强化行业自律管理。充分发挥行业协会作用,建立健全\n地方行业协会组织。行业协会要建立健全行规行约,职业道德准则,\n争议处理规则,推行行业质量检查,公开检查和处分的信息,增强行\n业协会在行业自律,监督,协调,服务等方面的功能。各级行业协会\n要积极开展行业诚信服务承诺活动,督促房地产中介从业人员遵守职\n业道德准则,保护消费者权益,及时向主管部门提出行业发展的意见\n和建议。\n\n(十五)建立多部门联动机制。省级房地产,价格,通信,金融,\n税务,工商行政等主管部门要加强对市,县工作的监督和指导,建立\n联动监管机制。市,县房地产主管部门负责房地产中介行业管理和组\n织协调,加强中介机构和从业人员管理;价格主管部门负责中介价格\n行为监管,充分发挥12358价格监管平台作用,及时处理投诉举报,\n依法查处价格违法行为;通信主管部门负责房地产中介网站管理,依\n法处置违法违规房地产中介网站;工商行政主管部门负责中介机构工\n商登记,依法查处未办理营业执照从事中介业务的机构;金融,税务\n等监管部门按照职责分工,配合做好房地产中介行业管理工作。\n\n(十六)强化行业监督检查。市,县房地产主管部门要加强房地"
    # text2 = "第六条 本会的业务范围是:(一)组织开展房地产估价和经纪理论,方法及其应用的研究,讨论,交流和考察;(二)拟订并推行房地产估价和经纪执业标准,规则;(三)协助行政主管部门组织实施全国房地产估价师,房地产经纪人执业资格考试;(四)办理房地产经纪人执业资格注册;(五)开展房地产估价和经纪业务培训,对房地产估价师,房地产经纪人进(六)建立房地产估价师和房地产估价机构,房地产经纪人和房地产经纪机构信用档案,开展房地产估价机构和房地产经纪机构资信评价;(七)提供房地产估价和经纪咨询和技术服务;(八)编辑出版房地产估价和经纪刊物,着作,建立有关网站,开展行业宣传;(九)代表中国房地产估价和经纪行业开展国际交往活动,参加相关国际组织;(十)向政府有关部门反映会员的意见,建议和要求,维护会员的合法权益,支持会员依法执业;(十一)办理法律,法规规定和行政主管部门委托或授权的其他有关工作。第三章 会 员。"

    # result = calculator.llm_decision(
    #     calculator.preprocessor.preprocess(text1),
    #     calculator.preprocessor.preprocess(text2),
    #     TextPairInfo.create(text1, text2, calculator.preprocessor)
    # )
    # logging.info(f"LLM裁决结果: {result}")
        


