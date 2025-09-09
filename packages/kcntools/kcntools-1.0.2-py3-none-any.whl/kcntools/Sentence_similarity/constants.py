#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
句子相似度计算系统常量定义
用于替代魔法字符串和中文变量名
"""

from enum import Enum


class ProcessingStage(Enum):
    """处理阶段枚举"""
    PREPROCESSING = "preprocessing"
    QUICK_CHECK = "quick_check"  
    SUBSTRING_FILTER = "substring_filter"
    ENTITY_CHANNEL = "entity_channel"
    LONG_SHORT_SEMANTIC = "long_short_semantic"
    OPTIMIZED_LCS = "optimized_lcs"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    LLM_DECISION = "llm_decision"
    
    @property
    def display_name(self) -> str:
        """返回阶段的中文显示名称"""
        display_map = {
            self.PREPROCESSING: "预处理与标准化",
            self.QUICK_CHECK: "快速检查",
            self.SUBSTRING_FILTER: "子串过滤", 
            self.ENTITY_CHANNEL: "专名通道",
            self.LONG_SHORT_SEMANTIC: "长短语义匹配",
            self.OPTIMIZED_LCS: "优化LCS",
            self.SEMANTIC_SIMILARITY: "语义相似",
            self.LLM_DECISION: "LLM裁决"
        }
        return display_map[self]


class SimilarityResult(Enum):
    """相似度判断结果枚举"""
    RELATED = "related"
    SIMILAR = "similar"  
    UNRELATED = "unrelated"
    NO_RESULT = "no_result"
    SKIPPED = "skipped"
    COMPLETED = "completed"
    ERROR = "error"
    
    @property
    def display_name(self) -> str:
        """返回结果的中文显示名称"""
        display_map = {
            self.RELATED: "相关",
            self.SIMILAR: "相似", 
            self.UNRELATED: "不相关",
            self.NO_RESULT: "无结果",
            self.SKIPPED: "跳过",
            self.COMPLETED: "完成",
            self.ERROR: "错误"
        }
        return display_map[self]


class Label(Enum):
    """标签枚举"""
    UNRELATED = "不相关"
    RELATED = "相关"
    SIMILAR = "相似"
        
class EntityType(Enum):
    """实体类型枚举"""
    NUMBERS = "numbers"
    DATES = "dates"
    ADDRESSES = "addresses"


class EntityExtractionConstants:
    """实体抽取相关常量类"""
    # 代词列表 - 用于排除人名识别
    PERSONAL_PRONOUNS = ['我', '你', '他', '她', '它']
    
    # 通用词汇 - 用于排除机构识别
    COMMON_WORDS = {'的', '了', '是', '在', '有', '和', '与'}
    
    # 非地名词汇 - 用于排除地理实体识别
    NON_LOCATION_WORDS = {
        # 动作词汇
        '下海', '上山', '下山', '上岸', '下岸', '出海', '入海',
        '上车', '下车', '上船', '下船', '上楼', '下楼',
        # 方向词汇（单独出现时）
        '上', '下', '左', '右', '前', '后', '东', '西', '南', '北',
        # 其他容易误识别的词
        '出来', '进去', '回来', '过去', '起来', '下来',
        '上去', '下去', '出去', '进来'
    }
    
    # 已知地名白名单 - 用于地理实体验证
    KNOWN_LOCATIONS = {
        '上海', '北京', '天津', '重庆', '广州', '深圳', '杭州', '南京',
        '武汉', '成都', '西安', '长沙', '郑州', '济南', '青岛', '大连',
        '厦门', '福州', '昆明', '贵阳', '南昌', '合肥', '太原', '石家庄',
        '呼和浩特', '银川', '西宁', '拉萨', '乌鲁木齐', '哈尔滨', '长春', '沈阳',
        # 省份简称
        '京', '津', '沪', '渝', '冀', '晋', '辽', '吉', '黑', '苏',
        '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '桂',
        '琼', '川', '贵', '云', '藏', '陕', '甘', '青', '宁', '新',
        # 常见地名
        '中国', '美国', '日本', '韩国', '英国', '法国', '德国', '意大利',
        '台湾', '香港', '澳门'
    }
    
    # 相对日期关键词映射
    RELATIVE_DATE_KEYWORDS = {
        '今天': 0, '今日': 0,
        '明天': 1, '明日': 1,
        '昨天': -1, '昨日': -1,
        '前天': -2,
        '后天': 2
    }
    
    # 复合单位列表 - 优先匹配
    COMPOUND_UNITS = ['平方米', '立方米', '平方公里', '平方千米', '平方厘米', '°C']
    
    # 单位正则表达式字符串
    UNIT_PATTERN_STRING = r'[元块钱米公里千米厘米毫米克千克公斤吨升毫升个只台辆套件张本页次倍人家条根支%度]+'
    
    # 中文数字映射
    CHINESE_NUM_MAP = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
        '百': 100, '千': 1000, '万': 10000
    }
    
    # 单位标准化映射
    UNIT_NORMALIZE_MAP = {
        '块': '元', '钱': '元',
        '公里': '千米', 'km': '千米', 'KM': '千米',
        'cm': '厘米', 'CM': '厘米',
        'mm': '毫米', 'MM': '毫米',
        'm': '米', 'M': '米',
        'kg': '千克', 'KG': '千克',
        'g': '克', 'G': '克',
        'l': '升', 'L': '升',
        'ml': '毫升', 'ML': '毫升',
        '℃': '度', 'C': '度'
    }
    
    # 中文数量词
    CHINESE_QUANTITY_WORDS = {
        '万': 10000,
        '千': 1000,
        '百': 100,
        '十': 10
    }
    
    # 日期正则表达式模式
    DATE_YEAR_PATTERN = r'[年\-/\.]'
    DATE_MONTH_PATTERN = r'[月\-/\.]'
    DATE_DAY_PATTERN = r'[日号]'
    
    # 地址方向词标准化映射
    DIRECTION_NORMALIZE_MAP = {
        '东部': '东区',
        '西部': '西区',
        '南部': '南区',
        '北部': '北区'
    }


class ExcelColumns(Enum):
    """Excel文件列名枚举"""
    SEQUENCE = "sequence"
    TEXT1 = "text1"
    TEXT2 = "text2"
    
    @property
    def display_name(self) -> str:
        """返回列的中文显示名称"""
        display_map = {
            self.SEQUENCE: "序号",
            self.TEXT1: "文本1", 
            self.TEXT2: "文本2"
        }
        return display_map[self]


class LogMessages(Enum):
    """日志消息常量"""
    # 警告消息
    OPENCC_NOT_INSTALLED = "警告: OpenCC未安装，繁体转简体功能将被禁用"
    OPENCC_INIT_FAILED = "警告: OpenCC初始化失败: {error}"
    BEAUTIFULSOUP_NOT_INSTALLED = "警告: BeautifulSoup未安装，HTML/Markdown标签清理功能将被禁用"
    TRADITIONAL_TO_SIMPLIFIED_FAILED = "警告: 繁体转简体失败: {error}"
    UNICODE_NORMALIZE_FAILED = "警告: Unicode标准化失败: {error}"
    HTML_CLEAN_FAILED = "警告: HTML标签清理失败: {error}"
    MARKDOWN_CLEAN_FAILED = "警告: Markdown标签清理失败: {error}"
    STOPWORDS_FILE_NOT_FOUND = "警告: 在 {directory} 中未找到停用词文件，使用基本停用词集合"
    STOPWORDS_READ_FAILED = "警告: 读取停用词文件 {filepath} 失败: {error}"
    STOPWORDS_LOAD_FAILED = "警告: 加载停用词失败: {error}，使用基本停用词集合"
    
    # Word2Vec相关消息
    WORD2VEC_ENABLED = "Word2Vec功能已启用，尝试加载Word2Vec模型..."
    WORD2VEC_CACHE_LOADED = "从内存缓存加载模型: {model}"
    WORD2VEC_DISK_CACHE_LOADED = "从磁盘缓存加载模型: {model}"
    WORD2VEC_CACHE_PATH = "  缓存路径: {path}"
    WORD2VEC_MODEL_SUCCESS = "  模型加载成功 (向量维度: {dimension})"
    WORD2VEC_CACHE_CLEARED = "  Word2Vec内存缓存已清空"
    WORD2VEC_MODEL_NOT_AVAILABLE = "模型 '{model}' 不在可用模型列表中"
    WORD2VEC_AVAILABLE_MODELS = "可用的Word2Vec/GloVe模型:"
    WORD2VEC_FIRST_DOWNLOAD = "模型未缓存，开始下载: {model}"
    WORD2VEC_DOWNLOAD_NOTICE = "首次下载可能需要较长时间，完成后会永久缓存到本地..."
    WORD2VEC_DOWNLOAD_TARGET = "下载目标: {path}"
    WORD2VEC_DOWNLOAD_SUCCESS = "Word2Vec模型下载并加载成功！"
    WORD2VEC_MODEL_INFO = "模型名称: {name}"
    WORD2VEC_VECTOR_DIMENSION = "向量维度: {dimension}"
    WORD2VEC_VOCAB_SIZE = "词汇表大小: {size}"
    WORD2VEC_CACHE_LOCATION = "缓存位置: ~/.gensim-data/{name}"
    WORD2VEC_NEXT_LOAD = "下次运行将直接从缓存加载，无需重新下载"
    GENSIM_IMPORT_FAILED = "gensim库导入失败: {error}"
    WORD2VEC_LOAD_FAILED = "Word2Vec模型加载失败: {error}"
    
    # 成功消息
    STOPWORDS_LOADED = "成功加载 {count} 个停用词"
    
    # Embedding相关消息
    OPENAI_CLIENT_NOT_INITIALIZED = "OpenAI客户端未初始化"
    EMBEDDING_API_FAILED = "Embedding API调用失败: {error}"
    EMBEDDING_FALLBACK_LOCAL = "降级使用本地embedding模型"
    
    # 可解释性数据相关
    EXPLAINABILITY_SAVED = "  保存了 {count} 个测试用例的完整阶段分数数据"
    EXPLAINABILITY_FILE_SAVED = "  数据文件: {filename}"
    EXPLAINABILITY_STAGES_INFO = "  每个测试用例包含 {count} 个处理阶段的分数信息"
    EXPLAINABILITY_ALL_COMPLETED = "\n✓ 所有测试完成，已保存完整的可解释性数据到: {filename}"
    EXPLAINABILITY_SAVE_FAILED = "\n✗ 保存可解释性数据失败: {error}"
    EXPLAINABILITY_NO_DATA = "\n⚠ 没有可解释性数据可保存"
    
    # Excel加载相关
    EXCEL_MISSING_COLUMNS = "   Excel文件缺少必需的列: {columns}"
    EXCEL_CURRENT_COLUMNS = "当前列名: {columns}"
    EXCEL_LOADED_SUCCESS = "  成功从Excel文件加载 {count} 个测试用例"
    EXCEL_FILE_NOT_FOUND = "   Excel文件不存在: {path}"
    EXCEL_READ_FAILED = "   读取Excel文件失败: {error}"
    
    # Word2Vec匹配相关
    WORD2VEC_UNIT_LOG_FAILED = "   日志记录失败: {error}"
    WORD2VEC_MATCH_ERROR = "   Word2Vec匹配过程出错: {error}"
    WORD2VEC_ERROR_LOG_FAILED = "   错误日志记录也失败"
    WORD2VEC_VECTOR_FAILED = "获取Word2Vec文本向量失败: {error}"
    WORD2VEC_WORD_VECTOR_FAILED = "获取词向量失败 (word: {word}): {error}"


class ThresholdConstants:
    """阈值常量类"""
    # 快速检查阈值
    QUICK_CHECK_RELATED_EDIT_DIST_SHORT = 0.02
    QUICK_CHECK_SIMILAR_EDIT_DIST_SHORT = 0.08
    QUICK_CHECK_RELATED_JACCARD = 0.95
    QUICK_CHECK_RELATED_EDIT_DIST = 0.03
    QUICK_CHECK_SIMILAR_JACCARD = 0.85
    QUICK_CHECK_SIMILAR_EDIT_DIST = 0.10
    
    # 子串过滤阈值
    SUBSTRING_SHORT_RELATED = 0.9
    SUBSTRING_SHORT_SIMILAR = 0.8
    SUBSTRING_NORMAL_RELATED = 0.5
    SUBSTRING_NORMAL_SIMILAR = 0.2
    
    # 实体通道阈值
    ENTITY_SHORT_RELATED = 0.95
    ENTITY_SHORT_SIMILAR = 0.85
    ENTITY_NORMAL_RELATED = 0.90
    ENTITY_NORMAL_SIMILAR = 0.75
    
    # 长短语义匹配阈值
    LONG_SHORT_SIMILARITY_THRESHOLD = 0.6
    LONG_SHORT_HIGH_CONFIDENCE = 0.7
    LONG_SHORT_VERY_HIGH_CONFIDENCE = 0.8
    LONG_SHORT_MATCH_RATIO = 0.2
    LONG_SHORT_FINAL_CONFIDENCE = 0.6
    
    # LCS阈值
    LCS_LONG_SHORT_MIN_RATIO = 0.9
    LCS_NORMAL_RELATED_MIN_RATIO = 0.8
    LCS_NORMAL_RELATED_MAX_RATIO = 0.4
    LCS_NORMAL_SIMILAR_MIN_RATIO = 0.7
    LCS_NORMAL_SIMILAR_MAX_RATIO = 0.3
    
    # 语义相似阈值
    SEMANTIC_LONG_SHORT_RELATED = 85
    SEMANTIC_LONG_SHORT_SIMILAR = 75
    SEMANTIC_NORMAL_RELATED = 70
    SEMANTIC_NORMAL_SIMILAR = 60


class DefaultValues:
    """默认值常量类"""
    # 默认停用词列表
    DEFAULT_STOPWORDS = [
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', 
        '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', 
        '你', '会', '着', '没有', '看', '好', '自己', '这'
    ]
    
    # 短文本判断阈值
    SHORT_TEXT_CHINESE_CHARS = 5
    SHORT_TEXT_ENGLISH_WORDS = 1
    
    # Word2Vec相关默认值
    WORD2VEC_WINDOW_SIZE_MULTIPLIER = 1.5
    WORD2VEC_MIN_WINDOW_SIZE = 3
    WORD2VEC_STEP_SIZE_DIVISOR = 2
    
    # 其他默认值
    DEFAULT_LLM_CONFIDENCE = 0.5
    MAX_UNITS_TO_LOG = 10


class FilePatterns:
    """文件模式常量类"""
    STOPWORDS_PATTERN = "qzhou_stopwords.txt"
    EXPLAINABILITY_FILENAME_PATTERN = "similarity_explainability_v2_{timestamp}.json"
    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


# 为了向后兼容，提供一个映射函数
def get_stage_display_name(stage: ProcessingStage) -> str:
    """获取阶段的中文显示名称"""
    return stage.display_name


def get_result_display_name(result: SimilarityResult) -> str:
    """获取结果的中文显示名称"""
    return result.display_name


def get_entity_type_name(entity_type: EntityType) -> str:
    """获取实体类型名称"""
    return entity_type.value


def get_excel_column_name(column: ExcelColumns) -> str:
    """获取Excel列的中文显示名称"""
    return column.display_name