"""
Parser module for extracting gene information from ricedata.cn
"""

import json
import os
import re
import traceback
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RiceGeneParser:
    """Parser for extracting gene information from ricedata.cn"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        self.base_url = "https://www.ricedata.cn/gene/list"

    def parse_gene_page(
        self, gene_id: str, output_dir: str = "downloads/genes"
    ) -> Dict:
        """
        Parse gene information from ricedata.cn webpage.
        """
        url = f"{self.base_url}/{gene_id}.htm"

        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)

            # Get webpage content
            response = requests.get(url, headers=self.headers)
            response.encoding = "gbk"
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract tables
            tables = soup.find_all("table")
            if not tables:
                print(f"No data found for gene ID: {gene_id}")
                return {}

            # Parse information
            gene_info = {
                "gene_id": gene_id,
                "url": url,
                "basic_info": self._parse_basic_info(tables[0]),
                "ontology": self._parse_ontology(tables[1]) if len(tables) > 1 else {},
                "ontology_terms": self._parse_ontology_terms(tables[2])
                if len(tables) > 2
                else [],
                "references": self._parse_references(tables[3])
                if len(tables) > 3
                else [],
            }

            # Save to JSON file
            output_file = os.path.join(output_dir, f"gene_{gene_id}.json")
            self.save_to_json(gene_info, output_file)

            return gene_info

        except Exception as e:
            print(f"Error parsing gene page: {e!s}")
            return {}

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove special characters and normalize spaces
        text = text.replace("：", "").replace(":", "")
        text = re.sub(r"\s+", " ", text)
        # Remove any potential BOM or special characters
        text = text.replace("\ufeff", "")
        return text.strip()

    def _parse_basic_info(self, table) -> Dict:
        """Parse basic gene information"""
        basic_info = {}
        rows = table.find_all("tr")

        current_key = None
        current_value = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                # Get the text content
                key_text = self._clean_text(cols[0].get_text(strip=True))
                value_text = self._clean_text(cols[1].get_text(strip=True))

                # If it's a new key
                if key_text:
                    # Save previous key-value pair if exists
                    if current_key and current_value:
                        basic_info[current_key] = " ".join(current_value)
                    # Start new key-value pair
                    current_key = key_text
                    current_value = [value_text]
                else:
                    # Append to current value if it's a continuation
                    if current_key and value_text:
                        current_value.append(value_text)

        # Save the last key-value pair
        if current_key and current_value:
            basic_info[current_key] = " ".join(current_value)

        return basic_info

    def _parse_ontology(self, table) -> Dict:
        """Parse gene ontology information"""
        ontology = {}
        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                key = self._clean_text(cols[0].get_text(strip=True))

                # Extract ontology terms and their links
                terms = []
                links = cols[1].find_all("a")
                for link in links:
                    terms.append(
                        {
                            "term": self._clean_text(link.get_text(strip=True)),
                            "id": link.get("href", "").split("=")[-1],
                        }
                    )

                if key and terms:
                    ontology[key] = terms

        return ontology

    def _parse_ontology_terms(self, table) -> List[Dict]:
        """Parse ontology terms information"""
        terms = []
        rows = table.find_all("tr")

        current_section = None
        for row in rows:
            text_content = row.get_text(strip=True)
            if not text_content:
                continue

            # Check if this is a section header
            if text_content.startswith("·"):
                current_section = text_content.replace("·", "").strip()
                continue

            # Parse terms with their IDs
            if current_section:
                items = []
                for term in row.stripped_strings:
                    term = term.strip()
                    if term and not term.startswith("·"):
                        items.append(term)

                if items:
                    term_dict = {
                        "section": current_section,
                        "content": ", ".join(items),
                    }
                    # Extract GO/TO IDs
                    ids = re.findall(r"[GT]O:\d{7}", term_dict["content"])
                    if ids:
                        term_dict["ontology_ids"] = ids
                    terms.append(term_dict)

        return terms

    def _fetch_reference_details(self, url: str) -> Dict:
        """
        Fetch detailed information for a reference from its URL.
        """
        details = {}

        try:
            request_url = url.replace("@", "") if url.startswith("@") else url

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            }

            response = requests.get(request_url, headers=headers)
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, "html.parser")

            # 获取标题
            title = soup.find("h1")
            if title:
                details["title"] = title.get_text(strip=True)

            # 获取 DOI
            h5_elements = soup.find_all("h5")
            for h5 in h5_elements:
                if "DOI:" in h5.get_text():
                    doi_text = h5.get_text()
                    doi_match = re.search(
                        r"DOI:\s*(10\.\d{4,}/[-._;()/:\w]+)", doi_text
                    )
                    if doi_match:
                        details["doi"] = doi_match.group(1)
                    break

            # 获取摘要
            paragraphs = soup.find_all("p", style=lambda x: x and "margin" in x)
            for p in paragraphs:
                text = p.get_text(strip=True)
                if not text:
                    continue

                # 检查文本语言
                chinese_ratio = len(
                    [c for c in text if "\u4e00" <= c <= "\u9fff"]
                ) / len(text)

                if chinese_ratio > 0.3:  # 如果超过30%是中文字符
                    details["abstract_cn"] = text
                else:
                    details["abstract_en"] = text

        except Exception as e:
            print(f"Error fetching paper details from {url}: {e!s}")
            traceback.print_exc()

        return details

    def _parse_references(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse reference information from the reference table."""
        references = []

        try:
            # 找到所有参考文献的表格行
            ref_rows = soup.find_all(
                "td",
                style=lambda x: x
                and (
                    "BACKGROUND-COLOR:#eef9de" in x or "BACKGROUND-COLOR:#ffffcc" in x
                ),
            )

            for row in ref_rows:
                # 获取链接和文本
                link = row.find("a")
                if not link:
                    continue

                # 修正URL构建方式
                url = "https://www.ricedata.cn/" + link["href"].replace("../../", "")

                # 提取完整的引用文本
                text_parts = []
                for content in row.stripped_strings:
                    if content not in [".", "(", ")", ":"]:
                        text_parts.append(content)

                reference_info = " ".join(text_parts[1:])  # 跳过序号

                reference = {"reference_info": reference_info, "reference_url": url}
                references.append(reference)

            print(f"Found {len(references)} references")

        except Exception as e:
            print(f"Error parsing references: {e!s}")
            import traceback

            traceback.print_exc()

        return references

    def save_to_json(self, data: Dict, output_file: str) -> None:
        """Save parsed data to JSON file."""
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Data saved to: {output_file}")
        except Exception as e:
            print(f"Error saving to JSON: {e!s}")

    def parse_multiple_genes(
        self, gene_ids: List[str], output_dir: str = "downloads/genes"
    ) -> List[Dict]:
        """
        Parse multiple genes and save their information.

        Args:
            gene_ids (List[str]): List of gene IDs to parse
            output_dir (str, optional): Directory to save the JSON files. Defaults to "downloads/genes"

        Returns:
            List[Dict]: List of parsed gene information
        """
        results = []
        for gene_id in gene_ids:
            print(f"\nParsing gene ID: {gene_id}")
            gene_info = self.parse_gene_page(gene_id, output_dir)
            results.append(gene_info)
        return results

    def _parse_gene_description(self, soup: BeautifulSoup) -> str:
        """Parse gene description from the content cell."""
        try:
            # 找到包含描述内容的单元格（colspan=2 的 td）
            content_cell = soup.find(
                "td", attrs={"colspan": "2", "style": "padding: 5px; font-size: 14px"}
            )
            if not content_cell:
                return ""

            # 获取所有描述文本，包括标题
            description_text = []

            # 获取红色文本部分（位点信息）
            red_text = content_cell.find(
                "p", style="color: rgb(255, 0, 0); font-weight: bold"
            )
            if red_text:
                description_text.append(red_text.get_text(strip=True))

            # 获取所有 h5 标题和对应的段落
            current_section = None
            for element in content_cell.children:
                if element.name == "h5":
                    current_section = element.get_text(strip=True)
                    description_text.append(f"\n{current_section}")
                elif element.name == "p":
                    # 移除 HTML 标签但保留文本格式
                    text = element.get_text(strip=True)
                    if text:
                        description_text.append(text)

            # 过滤掉【相关登录号】部分
            filtered_text = []
            for text in description_text:
                if "【相关登录号】" not in text:
                    filtered_text.append(text)

            # 合并所有文本，使用换行符分隔
            return "\n".join(filtered_text)

        except Exception as e:
            print(f"Error parsing gene description: {e!s}")
            return ""

    def _get_reference_details(self, ref_url: str) -> Dict:
        """Get detailed information for a reference."""
        try:
            if ref_url.startswith("@"):
                ref_url = ref_url[1:]

            if not ref_url.startswith("http"):
                ref_url = f"https://www.ricedata.cn/{ref_url}"

            response = requests.get(ref_url, headers=self.headers)
            response.raise_for_status()
            response.encoding = "utf-8"

            soup = BeautifulSoup(response.text, "html.parser")
            details = {}

            # 获取标题
            title = soup.find("h1")
            if title:
                details["title"] = title.get_text(strip=True)

            # 获取 DOI
            h5_elements = soup.find_all("h5")
            for h5 in h5_elements:
                if "DOI:" in h5.get_text():
                    doi_text = h5.get_text()
                    doi_match = re.search(
                        r"DOI:\s*(10\.\d{4,}/[-._;()/:\w]+)", doi_text
                    )
                    if doi_match:
                        details["doi"] = doi_match.group(1)
                    break

            # 获取英文摘要
            en_p = soup.find(
                "p", style=lambda x: x and "margin" in x and "margin-bottom:10" in x
            )
            if en_p:
                details["abstract_en"] = en_p.get_text(strip=True)

            # 获取中文摘要
            cn_title = soup.find("h1", style=lambda x: x and "color: orangered" in x)
            if cn_title:
                cn_p = cn_title.find_next("p")
                if cn_p:
                    # 保留换行和缩进
                    text_parts = []
                    for element in cn_p.children:
                        if element.name == "br":
                            text_parts.append("\n")
                        elif (
                            element.name == "em"
                            or element.name == "sup"
                            or element.name == "sub"
                        ):
                            text_parts.append(element.get_text())
                        elif isinstance(element, str):
                            # 替换 HTML 空格为实际空格
                            text = element.replace("&emsp;", "    ")
                            text_parts.append(text)

                    details["abstract_cn"] = "".join(text_parts).strip()

            return details

        except Exception as e:
            print(f"Error getting reference details from {ref_url}: {e!s}")
            traceback.print_exc()
            return {}

    def parse_gene_page(
        self, gene_id: str, output_dir: str = "downloads/genes"
    ) -> Dict:
        url = f"https://www.ricedata.cn/gene/list/{gene_id}.htm"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            response.encoding = "gb2312"  # 基因页面使用 GB2312 编码

            soup = BeautifulSoup(response.text, "html.parser")

            # 获取基本参考文献信息
            references = self._parse_references(soup)

            # 获取每个参考文献的详细信息
            for ref in references:
                if "reference_url" in ref:
                    ref_url = ref["reference_url"]
                    if not ref_url.startswith("http"):
                        ref_url = f"https://www.ricedata.cn/{ref_url.lstrip('/')}"
                    print(f"Getting details for {ref_url}")
                    details = self._get_reference_details(ref_url)
                    ref.update(details)

            gene_info = {
                "gene_id": gene_id,
                "url": url,
                "basic_info": self._parse_basic_info(soup),
                "description": self._parse_gene_description(soup),
                "ontology": self._parse_ontology(soup),
                "references": references,
            }

            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"gene_{gene_id}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(gene_info, f, ensure_ascii=False, indent=2)

            return gene_info

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Gene ID {gene_id} not found (404 error)")
                return None
            raise
