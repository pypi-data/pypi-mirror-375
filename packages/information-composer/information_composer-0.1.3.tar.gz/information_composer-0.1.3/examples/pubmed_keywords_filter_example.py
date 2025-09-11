from pathlib import Path

import pandas as pd

from information_composer.pubmed.baseline import load_baseline


def clean_text(text):
    """清理文本，移除多余的换行和空格"""
    if pd.isna(text):
        return ""
    return " ".join(str(text).split())


def main():
    # 使用 Path 对象处理路径
    current_dir = Path(__file__).parent
    data_dir = (current_dir / ".." / "data" / "pubmedbaseline").resolve()
    xml_file = data_dir / "pubmed24n1219.xml.gz"

    # 定义关键词列表
    keywords = [
        "promoter",
        "cis-regulatory",
        "cis-element",
        "enhancer",
        "silencer",
        "operator",
    ]

    print(f"Looking for PubMed data file at: {xml_file}")
    print(f"Keywords: {', '.join(keywords)}")

    if not xml_file.exists():
        print(f"\nError: PubMed data file not found at {xml_file}")
        print("\nPlease ensure the file 'pubmed24n1219.xml.gz' exists in:")
        print(f"   {data_dir}")
        return

    try:
        # 加载并过滤数据
        df = load_baseline(
            str(xml_file),
            output_type="pd",
            keywords=keywords,
            kw_filter="both",
            log=True,
        )

        # 清理文本列
        text_columns = ["title", "abstract", "journal"]
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].apply(clean_text)

        # 显示结果统计
        print("\nResults Summary:")
        print(f"Total matching papers found: {len(df)}")

        # 统计每个关键词的出现次数
        keyword_counts = {}
        for keyword in keywords:
            title_count = df["title"].str.contains(keyword, case=False).sum()
            abstract_count = df["abstract"].str.contains(keyword, case=False).sum()
            keyword_counts[keyword] = {
                "title": title_count,
                "abstract": abstract_count,
                "total": title_count + abstract_count,
            }

        # 打印关键词统计
        print("\nKeyword Statistics:")
        print("-" * 60)
        print(f"{'Keyword':<15} {'Title':<10} {'Abstract':<10} {'Total':<10}")
        print("-" * 60)
        for keyword, counts in keyword_counts.items():
            print(
                f"{keyword:<15} {counts['title']:<10} {counts['abstract']:<10} {counts['total']:<10}"
            )

        # 保存结果到CSV文件
        output_file = data_dir / "pubmed_filtered_results.csv"
        df.to_csv(
            output_file, index=True, quoting=1
        )  # quoting=1 确保所有字段都被引号包围
        print(f"\nResults saved to {output_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
