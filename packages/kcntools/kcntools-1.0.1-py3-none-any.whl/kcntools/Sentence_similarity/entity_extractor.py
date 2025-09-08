#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实体抽取与标准化模块 - 纯spaCy版本
使用spaCy NER进行实体识别，保留标准化和占位符生成功能
专门针对中文文本优化，支持人名、机构、地址、日期、货币等实体类型
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Set
import logging
from dataclasses import dataclass

# 导入常量
from .constants import EntityType, EntityExtractionConstants

# 检查 spaCy 是否可用
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None


@dataclass
class EntityInfo:
    """实体信息结构"""
    original: str          # 原始文本
    normalized: str        # 标准化值
    entity_type: str       # 实体类型
    start_pos: int         # 起始位置
    end_pos: int           # 结束位置
    confidence: float      # 置信度


class EntityExtractor:
    """实体抽取与标准化模块 - 纯spaCy版本，使用机器学习模型进行实体识别"""
    
    def __init__(self, use_spacy: bool = True, spacy_model: str = "zh_core_web_sm"):
        """
        初始化实体提取器
        
        Args:
            use_spacy: 是否启用spaCy NER增强（默认True）
            spacy_model: spaCy模型名称（默认中文小模型）
        """
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.nlp = None
        
        # 尝试加载spaCy模型
        if self.use_spacy:
            try:
                self.nlp = spacy.load(spacy_model)
                logging.info(f"✅ spaCy模型 {spacy_model} 加载成功，实体识别能力增强")
            except OSError as e:
                logging.warning(f"⚠️ spaCy模型 {spacy_model} 未找到，尝试备用模型...")
                # 尝试其他中文模型
                for backup_model in ["zh_core_web_md", "zh_core_web_lg"]:
                    try:
                        self.nlp = spacy.load(backup_model)
                        logging.info(f"✅ 使用备用spaCy模型 {backup_model}")
                        break
                    except OSError:
                        continue
                else:
                    logging.warning("❌ 未找到可用的中文spaCy模型，使用原有规则模式")
                    self.use_spacy = False
        
        # spaCy实体类型映射
        self.spacy_entity_mapping = {
            'PERSON': 'person',           # 人名
            'ORG': 'organization',        # 机构组织
            'GPE': 'location',           # 地理政治实体
            'LOC': 'location',           # 地理位置
            'DATE': 'date',              # 日期
            'TIME': 'date',              # 时间
            'MONEY': 'currency',         # 货币
            'PERCENT': 'percentage',     # 百分比
            'QUANTITY': 'quantity',      # 数量
            'ORDINAL': 'number',         # 序数
            'CARDINAL': 'number',        # 基数
            'LAW': 'legal',              # 法律
            'EVENT': 'event',            # 事件
            'FAC': 'facility',           # 设施
        }
        # 排除模式 - 避免误识别法条编号等
        self.exclusion_patterns = {
            # 法条编号：第X条、第X章、第X节等
            'legal_article': re.compile(r'第[一二三四五六七八九十百千万\d]+[条章节款项]'),
            # 序号：第X、第X个等
            'ordinal': re.compile(r'第[一二三四五六七八九十百千万\d]+[个位次]?(?![条章节款项])'),
        }
        
        # 中文数字映射
        self.chinese_num_map = EntityExtractionConstants.CHINESE_NUM_MAP
        
        # 单位标准化映射
        self.unit_normalize_map = EntityExtractionConstants.UNIT_NORMALIZE_MAP
    
    def extract_and_normalize_entities(self, text: str) -> Tuple[str, Dict[str, List[EntityInfo]]]:
        """
        主接口：使用spaCy进行实体抽取并标准化
        
        Args:
            text: 输入文本
            
        Returns:
            Tuple[str, Dict[str, List[EntityInfo]]]: (占位后的规范化文本, 实体表)
        """
        entities = {
            EntityType.NUMBERS.value: [],
            EntityType.DATES.value: [],
            EntityType.ADDRESSES.value: []
        }
        
        # 1. 预处理：标记排除区域
        excluded_ranges = self._find_excluded_ranges(text)
        
        # 2. 使用spaCy进行实体识别
        spacy_entities = []
        if self.use_spacy:
            spacy_entities = self._extract_with_spacy(text, excluded_ranges)
        
        # 3. 将spaCy识别的实体分类到对应类别
        for spacy_entity in spacy_entities:
            if spacy_entity.entity_type.startswith('number_') or spacy_entity.entity_type in ['currency', 'percentage', 'quantity']:
                entities[EntityType.NUMBERS.value].append(spacy_entity)
            elif spacy_entity.entity_type.startswith('date_'):
                entities[EntityType.DATES.value].append(spacy_entity)
            elif spacy_entity.entity_type.startswith('address_') or spacy_entity.entity_type == 'location':
                entities[EntityType.ADDRESSES.value].append(spacy_entity)
        
        # 4. 合并所有实体并按位置排序
        all_entities = []
        for entity in entities[EntityType.NUMBERS.value]:
            all_entities.append((EntityType.NUMBERS.value, entity))
        
        for entity in entities[EntityType.DATES.value]:
            all_entities.append((EntityType.DATES.value, entity))
            
        for entity in entities[EntityType.ADDRESSES.value]:
            all_entities.append((EntityType.ADDRESSES.value, entity))
        
        # 5. 按位置从后往前排序，避免替换时位置偏移
        all_entities.sort(key=lambda x: x[1].start_pos, reverse=True)
        
        # 6. 生成占位符文本 - 包含标准化值以避免误判
        text_with_placeholders = text
        
        for entity_type, entity in all_entities:
            # 占位符映射
            placeholder_map = {
                EntityType.NUMBERS.value: 'NUM',
                EntityType.DATES.value: 'DATE',
                EntityType.ADDRESSES.value: 'ADDR'
            }
            placeholder_prefix = placeholder_map.get(entity_type, entity_type.upper())
            
            # 生成包含标准化值的占位符，避免不同实体被替换为相同占位符
            # 对标准化值进行清理，移除特殊字符以避免解析问题
            clean_normalized = re.sub(r'[^\w\u4e00-\u9fff\-\.]', '_', entity.normalized)
            placeholder = f"[{placeholder_prefix}:{clean_normalized}]"
            
            text_with_placeholders = (
                text_with_placeholders[:entity.start_pos] +
                placeholder +
                text_with_placeholders[entity.end_pos:]
            )
        
        return text_with_placeholders, entities
    
    def _extract_with_spacy(self, text: str, excluded_ranges: List[Tuple[int, int]]) -> List[EntityInfo]:
        """
        使用spaCy进行实体识别，重点识别专有名词
        
        Args:
            text: 待处理文本
            excluded_ranges: 需要排除的文本范围列表
            
        Returns:
            List[EntityInfo]: 识别出的实体信息列表
        """
        if not self.nlp:
            return []
        
        entities = []
        doc = self.nlp(text)
        
        for ent in doc.ents:
            start, end = ent.start_char, ent.end_char
            original = ent.text
            label = ent.label_
            
            # 检查是否在排除范围内
            if self._is_in_excluded_range(start, end, excluded_ranges):
                continue
            
            # 映射spaCy实体类型到我们的分类
            if label in self.spacy_entity_mapping:
                entity_category = self.spacy_entity_mapping[label]
                
                # 使用原有的规范化逻辑
                if entity_category in ['currency', 'percentage', 'quantity', 'number']:
                    # 数字类实体：使用原有的数字规范化
                    normalized = self._normalize_number(original, entity_category)
                    entity_type = f"number_{entity_category}"
                    confidence = 0.85  # spaCy识别的置信度
                elif entity_category == 'date':
                    # 日期类实体：使用原有的日期规范化
                    normalized = self._normalize_date(original, 'spacy_date')
                    entity_type = f"date_spacy"
                    confidence = 0.85
                elif entity_category == 'location':
                    # 地址类实体：使用原有的地址规范化
                    normalized = self._normalize_address(original, 'spacy_location')
                    entity_type = f"address_spacy_location"
                    confidence = 0.80
                else:
                    # 其他类型（人名、机构等）：保持原样但标记
                    normalized = original
                    entity_type = f"proper_noun_{entity_category}"
                    confidence = 0.80
                
                # 验证实体合理性
                if self._validate_spacy_entity(original, text, start, end, label):
                    entity = EntityInfo(
                        original=original,
                        normalized=normalized,
                        entity_type=entity_type,
                        start_pos=start,
                        end_pos=end,
                        confidence=confidence
                    )
                    entities.append(entity)
        
        return entities
    
    def _validate_spacy_entity(self, original: str, text: str, start: int, end: int, label: str) -> bool:
        """
        验证spaCy识别的实体是否合理 - 添加严格的地理实体验证
        
        Args:
            original: 原始实体文本
            text: 完整文本
            start: 实体开始位置
            end: 实体结束位置
            label: spaCy实体标签
            
        Returns:
            bool: 实体是否合理
        """
        # 基本长度检查 - 放宽到1个字符
        if len(original.strip()) < 1:
            return False
        
        # 检查是否只包含标点符号
        if re.match(r'^[^\w\u4e00-\u9fff]+$', original):
            return False
        
        # 对于人名，只排除明显的代词
        if label == 'PERSON':
            if original in EntityExtractionConstants.PERSONAL_PRONOUNS:
                return False
        
        # 对于机构，放宽限制，允许更多机构名称
        if label == 'ORG':
            # 只排除过于通用的单字词
            if len(original) == 1 and original in EntityExtractionConstants.COMMON_WORDS:
                return False
        
        # 对于地理政治实体(GPE)和地理位置(LOC)，添加严格验证
        if label in ['GPE', 'LOC']:
            # 排除明显不是地名的词汇
            if original in EntityExtractionConstants.NON_LOCATION_WORDS:
                return False
            
            # 对于短词（≤2个字符），需要更严格的验证
            if len(original) <= 2:
                # 只有在白名单中的短词才被认为是地名
                if original not in EntityExtractionConstants.KNOWN_LOCATIONS:
                    return False
        
        # 对于其他类型，基本都接受
        return True
    
    def _find_excluded_ranges(self, text: str) -> List[Tuple[int, int]]:
        """
        找到需要排除的文本范围
        
        Args:
            text: 待处理文本
            
        Returns:
            List[Tuple[int, int]]: 排除范围列表，每个元素为(start, end)
        """
        excluded_ranges = []
        
        for pattern_name, pattern in self.exclusion_patterns.items():
            for match in pattern.finditer(text):
                excluded_ranges.append(match.span())
        
        # 合并重叠的范围
        excluded_ranges.sort()
        merged_ranges = []
        for start, end in excluded_ranges:
            if merged_ranges and start <= merged_ranges[-1][1]:
                merged_ranges[-1] = (merged_ranges[-1][0], max(merged_ranges[-1][1], end))
            else:
                merged_ranges.append((start, end))
        
        return merged_ranges
    
    def _is_in_excluded_range(self, start: int, end: int, excluded_ranges: List[Tuple[int, int]]) -> bool:
        """
        检查位置是否在排除范围内
        
        Args:
            start: 检查范围开始位置
            end: 检查范围结束位置
            excluded_ranges: 排除范围列表
            
        Returns:
            bool: 是否在排除范围内
        """
        for ex_start, ex_end in excluded_ranges:
            if not (end <= ex_start or start >= ex_end):
                return True
        return False
    
    
    def _is_overlapping(self, entities: List[EntityInfo], start: int, end: int) -> bool:
        """
        检查是否与已有实体重叠
        
        Args:
            entities: 已有实体列表
            start: 新实体开始位置
            end: 新实体结束位置
            
        Returns:
            bool: 是否存在重叠
        """
        for entity in entities:
            if not (end <= entity.start_pos or start >= entity.end_pos):
                return True
        return False
    
    
    def _normalize_number(self, number_str: str, pattern_type: str) -> str:
        """
        标准化数值
        
        Args:
            number_str: 原始数字字符串
            pattern_type: 模式类型
            
        Returns:
            str: 标准化后的数字字符串
        """
        try:
            # 提取数值部分
            if pattern_type == 'chinese_number':
                value = self._chinese_to_arabic(number_str)
            else:
                # 提取数字部分
                num_match = re.search(r'\d+(?:\.\d+)?', number_str)
                if not num_match:
                    return number_str
                value = float(num_match.group())
                
                # 处理中文数量词
                for word, multiplier in EntityExtractionConstants.CHINESE_QUANTITY_WORDS.items():
                    if word in number_str:
                        if word == '十' and value < 10:
                            value *= multiplier
                        elif word != '十':
                            value *= multiplier
                        break
            
            # 提取并标准化单位
            unit = self._extract_unit(number_str)
            if unit in self.unit_normalize_map:
                unit = self.unit_normalize_map[unit]
            
            # 格式化输出
            if value == int(value):
                return f"{int(value)}{unit}" if unit else str(int(value))
            else:
                return f"{value:.2f}{unit}" if unit else f"{value:.2f}"
                
        except (ValueError, KeyError, AttributeError) as e:
            # 记录具体的错误类型，便于调试
            logging.error(f"⚠️ 数字标准化失败: {e}, 原始值: {number_str}")
            return number_str
    
    def _normalize_date(self, date_str: str, pattern_type: str) -> str:
        """
        标准化日期
        
        Args:
            date_str: 原始日期字符串
            pattern_type: 模式类型
            
        Returns:
            str: 标准化后的日期字符串
        """
        try:
            if pattern_type == 'relative_date':
                # 相对日期转换为标准格式
                today = datetime.now()
                if date_str in EntityExtractionConstants.RELATIVE_DATE_KEYWORDS:
                    days_offset = EntityExtractionConstants.RELATIVE_DATE_KEYWORDS[date_str]
                    return (today + timedelta(days=days_offset)).strftime('%Y-%m-%d')
                else:
                    return date_str
            
            # 统一分隔符
            normalized = date_str
            normalized = re.sub(EntityExtractionConstants.DATE_YEAR_PATTERN, '-', normalized)
            normalized = re.sub(EntityExtractionConstants.DATE_MONTH_PATTERN, '-', normalized)
            normalized = re.sub(EntityExtractionConstants.DATE_DAY_PATTERN, '', normalized)
            
            # 补全格式
            parts = normalized.split('-')
            if len(parts) == 3:
                year, month, day = parts
                return f"{year.zfill(4)}-{month.zfill(2)}-{day.zfill(2)}"
            elif len(parts) == 2:
                year, month = parts
                return f"{year.zfill(4)}-{month.zfill(2)}"
            else:
                return normalized
                
        except (ValueError, AttributeError, IndexError) as e:
            # 记录具体的错误类型，便于调试
            logging.error(f"⚠️ 日期标准化失败: {e}, 原始值: {date_str}")
            return date_str
    
    def _normalize_address(self, address_str: str, pattern_type: str) -> str:
        """
        标准化地址
        
        Args:
            address_str: 原始地址字符串
            pattern_type: 模式类型
            
        Returns:
            str: 标准化后的地址字符串
        """
        normalized = re.sub(r'\s+', '', address_str.strip())
        
        # 标准化方向词
        for direction, replacement in EntityExtractionConstants.DIRECTION_NORMALIZE_MAP.items():
            normalized = re.sub(direction, replacement, normalized)
        
        return normalized
    
    def _chinese_to_arabic(self, chinese_num: str) -> float:
        """
        中文数字转阿拉伯数字
        
        Args:
            chinese_num: 中文数字字符串
            
        Returns:
            float: 对应的阿拉伯数字
        """
        try:
            result = 0
            temp = 0
            
            for char in chinese_num:
                if char in self.chinese_num_map:
                    num = self.chinese_num_map[char]
                    if num >= 10:
                        if num >= 10000:
                            result += temp * num
                            temp = 0
                        else:
                            temp *= num
                    else:
                        temp += num
            
            return result + temp
        except (KeyError, ValueError) as e:
            # 记录具体的错误类型，便于调试
            logging.error(f"⚠️ 中文数字转换失败: {e}, 原始值: {chinese_num}")
            return 0
    
    def _extract_unit(self, number_str: str) -> str:
        """
        提取数值的单位，优先匹配复合单位
        
        Args:
            number_str: 包含单位的数字字符串
            
        Returns:
            str: 提取出的单位，如果没有找到则返回空字符串
        """
        # 优先匹配复合单位
        for unit in EntityExtractionConstants.COMPOUND_UNITS:
            if unit in number_str:
                return unit
        
        # 匹配简单单位
        unit_pattern = re.compile(EntityExtractionConstants.UNIT_PATTERN_STRING)
        match = unit_pattern.search(number_str)
        return match.group() if match else ""
    
    
    def get_entity_statistics(self, entities: Dict[str, List[EntityInfo]]) -> Dict[str, int]:
        """
        获取实体统计信息
        
        Args:
            entities: 实体字典，包含各类型实体列表
            
        Returns:
            Dict[str, int]: 统计信息字典，包含各实体类型的数量
        """
        stats = {}
        for entity_type, entity_list in entities.items():
            stats[entity_type] = len(entity_list)
            for entity in entity_list:
                subtype = entity.entity_type
                stats[subtype] = stats.get(subtype, 0) + 1
        return stats
    
    def compare_entities(self, entities1: Dict[str, List[EntityInfo]],
                        entities2: Dict[str, List[EntityInfo]]) -> Dict[str, float]:
        """
        比较两个实体表的相似度
        
        Args:
            entities1: 第一个实体字典
            entities2: 第二个实体字典
            
        Returns:
            Dict[str, float]: 各实体类型的相似度分数
        """
        similarities = {}
        
        # 数值实体比较
        if entities1[EntityType.NUMBERS.value] and entities2[EntityType.NUMBERS.value]:
            number_sim = self._compare_numbers(entities1[EntityType.NUMBERS.value], entities2[EntityType.NUMBERS.value])
            similarities[EntityType.NUMBERS.value] = number_sim
        
        # 日期实体比较
        if entities1[EntityType.DATES.value] and entities2[EntityType.DATES.value]:
            date_sim = self._compare_dates(entities1[EntityType.DATES.value], entities2[EntityType.DATES.value])
            similarities[EntityType.DATES.value] = date_sim
        
        # 地址实体比较
        if entities1[EntityType.ADDRESSES.value] and entities2[EntityType.ADDRESSES.value]:
            address_sim = self._compare_addresses(entities1[EntityType.ADDRESSES.value], entities2[EntityType.ADDRESSES.value])
            similarities[EntityType.ADDRESSES.value] = address_sim
        
        return similarities
    
    def _compare_numbers(self, numbers1: List[EntityInfo], numbers2: List[EntityInfo]) -> float:
        """
        比较数值实体 - 严格匹配：相等则1.0，不等则0.0
        
        Args:
            numbers1: 第一组数值实体
            numbers2: 第二组数值实体
            
        Returns:
            float: 相似度分数，1.0表示完全匹配，0.0表示不匹配
        """
        for num1 in numbers1:
            for num2 in numbers2:
                try:
                    # 直接比较标准化后的完整字符串
                    if num1.normalized == num2.normalized:
                        return 1.0
                    
                    # 如果字符串不完全相等，尝试数值比较
                    val1_matches = re.findall(r'\d+(?:\.\d+)?', num1.normalized)
                    val2_matches = re.findall(r'\d+(?:\.\d+)?', num2.normalized)
                    
                    if val1_matches and val2_matches:
                        val1 = float(val1_matches[0])
                        val2 = float(val2_matches[0])
                        
                        # 严格数值相等检查
                        if val1 == val2:
                            return 1.0
                except (ValueError, IndexError, AttributeError):
                    # 忽略数值比较中的异常，继续下一个比较
                    continue
        
        # 如果没有找到相等的数值，返回0.0
        return 0.0
    
    def _compare_dates(self, dates1: List[EntityInfo], dates2: List[EntityInfo]) -> float:
        """
        比较日期实体 - 严格匹配：相等则1.0，不等则0.0
        
        Args:
            dates1: 第一组日期实体
            dates2: 第二组日期实体
            
        Returns:
            float: 相似度分数，1.0表示完全匹配，0.0表示不匹配
        """
        for date1 in dates1:
            for date2 in dates2:
                # 严格匹配标准化后的日期字符串
                if date1.normalized == date2.normalized:
                    return 1.0
        
        # 如果没有找到完全相等的日期，返回0.0
        return 0.0
    
    def _compare_addresses(self, addresses1: List[EntityInfo], addresses2: List[EntityInfo]) -> float:
        """
        比较地址实体
        
        Args:
            addresses1: 第一组地址实体
            addresses2: 第二组地址实体
            
        Returns:
            float: 相似度分数，0.0到1.0之间
        """
        max_similarity = 0.0
        for addr1 in addresses1:
            for addr2 in addresses2:
                if addr1.normalized == addr2.normalized:
                    max_similarity = 1.0
                    break
                else:
                    # 计算地址字符串相似度
                    common_chars = set(addr1.normalized) & set(addr2.normalized)
                    total_chars = set(addr1.normalized) | set(addr2.normalized)
                    similarity = len(common_chars) / len(total_chars) if total_chars else 0.0
                    max_similarity = max(max_similarity, similarity)
        
        return max_similarity


# 测试和示例代码
if __name__ == "__main__":
    # 创建实体抽取器实例
    extractor = EntityExtractor()
    
    # 测试用例
    test_texts = [
        # 原始问题文本
        "施工现场建筑垃圾的消纳和运输按照本市有关垃圾管理的规定处理。第二十六条 本市禁止现场搅拌混凝土,砂浆。砌筑,抹灰以及地面工程砂浆应当使用散装预拌砂浆。第二十七条 在噪声敏感建筑物集中区域内,夜间不得进行产生环境噪声污染的施工作业。因重点工程或者生产工艺要求连续作业,确需在 22 时至次日 6 时期间进行施工的,建设单位应当在施工前到建设工程所在地的区住房城乡建设行政主管部门提出申请,经批准后方可进行夜间施工,并公告施工期限。未经批准或者超过批准期限,施工单位不得进行夜间施工。",
        
        # 其他测试用例
        "我花了100万元买了一套房子",
        "价格是1000.50元，面积120平方米",
        "2023年12月25日在北京市海淀区签约",
        "温度达到了35度，湿度80%",
        "地址：上海市浦东新区张江高科技园区3号楼",
        "明天上午10点在三楼会议室开会"
    ]
    
    print("实体抽取与标准化测试 - 精准版")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n测试用例 {i}:")
        print(f"原文: {text}")
        
        try:
            normalized_text, entities = extractor.extract_and_normalize_entities(text)
            print(f"规范化文本: {normalized_text}")
            
            # 打印实体信息
            total_entities = 0
            for entity_type, entity_list in entities.items():
                if entity_list:
                    print(f"\n{entity_type}:")
                    for entity in entity_list:
                        print(f"  - 原始: '{entity.original}'")
                        print(f"    标准化: '{entity.normalized}'")
                        print(f"    类型: {entity.entity_type}")
                        print(f"    位置: {entity.start_pos}-{entity.end_pos}")
                        print(f"    置信度: {entity.confidence:.2f}")
                        total_entities += 1
            
            # 统计信息
            stats = extractor.get_entity_statistics(entities)
            print(f"\n实体统计: {stats}")
            print(f"总计实体数: {total_entities}")
            
        except Exception as e:
            print(f"处理出错: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 60)
