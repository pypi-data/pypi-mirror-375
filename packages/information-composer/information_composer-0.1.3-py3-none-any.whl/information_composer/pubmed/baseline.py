import logging
import os
from os.path import basename, isfile
import pickle
from typing import Union

import pandas as pd
import pubmed_parser as pp


def load_baseline(xmlfile: str, *args, **kwargs) -> Union[pd.DataFrame, dict, list]:
    """
    从给定的XML文件中加载基线数据，并根据output_type参数返回不同格式的数据。

    参数:
    xmlfile (str): XML文件路径
    **kwargs: 支持的关键字参数:
        - output_type (str): 输出格式 ('pd', 'dict', 'list')
        - keywords (list): 关键词列表
        - kw_filter (str): 过滤类型 ('abstract', 'title', 'both')
        - impact_factor (float): 最小影响因子
        - log (bool): 是否启用日志

    返回:
    Union[pd.DataFrame, dict, list]: 根据output_type返回相应格式的数据
    """
    # 日志配置
    log = kwargs.get("log", False)
    if log:
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    if not isfile(xmlfile):
        raise FileNotFoundError(f"The specified file {xmlfile} does not exist.")

    # 参数验证和初始化
    output_type = kwargs.get("output_type", "list")
    if output_type not in ["list", "dict", "pd"]:
        raise ValueError('output_type must be "pd", "list" or "dict"')

    keywords = kwargs.get("keywords", [])
    kw_filter = kwargs.get("kw_filter", "abstract")
    if kw_filter not in ["abstract", "title", "both"]:
        raise ValueError('kw_filter must be "abstract", "title", or "both"')

    impact_factor = float(kwargs.get("impact_factor", 0))

    # 加载影响因子数据（使用缓存）
    impact_factor_dict = {}
    if impact_factor > 0:
        try:
            impact_factor_dict = load_dict_from_pickle("./if2024.pickle")
        except Exception as e:
            logging.warning(f"Failed to load impact factor data: {e}")
            impact_factor = 0

    # XML解析
    try:
        path_xml = pp.parse_medline_xml(xmlfile)
        baselineversion = os.path.basename(xmlfile).split(".")[0]
    except Exception as e:
        raise RuntimeError(f"Error parsing XML file {xmlfile}") from e

    # 数据处理
    data_dict = {}
    for entry in path_xml:
        if not _should_keep_entry(
            entry, keywords, kw_filter, impact_factor, impact_factor_dict
        ):
            continue

        data_dict[int(entry["pmid"])] = _create_entry_dict(entry, baselineversion)

    # 返回结果
    if output_type == "pd":
        return pd.DataFrame.from_dict(data_dict).T
    elif output_type == "dict":
        return data_dict
    return list(data_dict.values())


def _should_keep_entry(
    entry: dict,
    keywords: list,
    kw_filter: str,
    impact_factor: float,
    impact_factor_dict: dict,
) -> bool:
    """判断条目是否应该保留"""
    # 关键词过滤
    if keywords:
        if kw_filter == "both":
            if not (
                keywords_filter(entry["abstract"], keywords)
                or keywords_filter(entry["title"], keywords)
            ):
                return False
        elif not keywords_filter(entry[kw_filter], keywords):
            return False

    # 影响因子过滤
    if impact_factor > 0:
        journal_name = entry["journal"].rstrip().lower()
        if (
            journal_name not in impact_factor_dict
            or impact_factor_dict[journal_name] < impact_factor
        ):
            return False

    return True


def _create_entry_dict(entry: dict, version: str) -> dict:
    """创建标准化的条目字典"""
    return {
        "pmid": int(entry["pmid"]),
        "title": entry["title"],
        "abstract": entry["abstract"],
        "journal": entry["journal"],
        "pubdate": entry["pubdate"],
        "publication_types": entry["publication_types"],
        "authors": entry["authors"],
        "doi": entry["doi"],
        "version": version,
    }


def keywords_filter(text: str, keywords: list) -> bool:
    """
    检查文本是否包含任何关键词

    参数:
    text (str): 要检查的文本
    keywords (list): 关键词列表

    返回:
    bool: 如果找到任何关键词则返回True
    """
    if not text or not keywords:
        return False

    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)


def load_dict_from_pickle(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)
