"""数据格式转换模块"""
import json
import csv
import logging
from io import StringIO, BytesIO
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

logger = logging.getLogger(__name__)


class DataConverter:
    """学术数据格式转换器"""

    SUPPORTED_FORMATS = ["json", "csv", "excel", "jsonl", "markdown", "xml"]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化数据转换器"""
        self.config = config or {}

    def convert(self, data: Any, target_format: str, **kwargs) -> Union[str, bytes]:
        """转换数据格式"""
        target_format = target_format.lower()

        if target_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的格式: {target_format}")

        converter_map = {
            "json": self.to_json,
            "csv": self.to_csv,
            "excel": self.to_excel,
            "jsonl": self.to_jsonl,
            "markdown": self.to_markdown,
            "xml": self.to_xml
        }

        return converter_map[target_format](data, **kwargs)

    def to_json(self, data: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
        """转换为JSON格式"""
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, default=str)

    def to_jsonl(self, data: List[Any]) -> str:
        """转换为JSON Lines格式"""
        lines = []
        for item in data:
            if hasattr(item, 'to_dict'):
                item = item.to_dict()
            lines.append(json.dumps(item, ensure_ascii=False, default=str))
        return "\n".join(lines)

    def to_csv(self, data: List[Any], headers: Optional[List[str]] = None) -> str:
        """转换为CSV格式"""
        if not data:
            return ""

        dict_data = []
        for item in data:
            if hasattr(item, 'to_dict'):
                dict_data.append(item.to_dict())
            elif isinstance(item, dict):
                dict_data.append(item)

        if not dict_data:
            return ""

        if not headers:
            headers = list(dict_data[0].keys())

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()

        for row in dict_data:
            flat_row = self._flatten_dict(row)
            writer.writerow({k: flat_row.get(k, "") for k in headers})

        return output.getvalue()

    def to_excel(self, data: List[Any], sheet_name: str = "Sheet1") -> bytes:
        """转换为Excel格式"""
        try:
            from openpyxl import Workbook
        except ImportError:
            raise ImportError("请安装openpyxl: pip install openpyxl")

        dict_data = []
        for item in data:
            if hasattr(item, 'to_dict'):
                dict_data.append(item.to_dict())
            elif isinstance(item, dict):
                dict_data.append(item)

        if not dict_data:
            return b""

        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name

        headers = list(dict_data[0].keys())
        ws.append(headers)

        for row in dict_data:
            flat_row = self._flatten_dict(row)
            ws.append([str(flat_row.get(h, "")) for h in headers])

        output = BytesIO()
        wb.save(output)
        return output.getvalue()

    def to_markdown(self, data: List[Any], title: str = "") -> str:
        """转换为Markdown表格格式"""
        if not data:
            return ""

        dict_data = []
        for item in data:
            if hasattr(item, 'to_dict'):
                dict_data.append(item.to_dict())
            elif isinstance(item, dict):
                dict_data.append(item)

        if not dict_data:
            return ""

        headers = list(dict_data[0].keys())
        lines = []

        if title:
            lines.append(f"## {title}\n")

        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        for row in dict_data:
            flat_row = self._flatten_dict(row)
            values = [str(flat_row.get(h, ""))[:50] for h in headers]
            lines.append("| " + " | ".join(values) + " |")

        return "\n".join(lines)

    def to_xml(self, data: Any, root_name: str = "data") -> str:
        """转换为XML格式"""
        import xml.etree.ElementTree as ET

        def dict_to_xml(d, parent):
            if isinstance(d, dict):
                for key, value in d.items():
                    child = ET.SubElement(parent, str(key))
                    dict_to_xml(value, child)
            elif isinstance(d, list):
                for item in d:
                    child = ET.SubElement(parent, "item")
                    dict_to_xml(item, child)
            else:
                parent.text = str(d) if d is not None else ""

        root = ET.Element(root_name)
        dict_to_xml(data, root)
        return ET.tostring(root, encoding='unicode')

    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """扁平化嵌套字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                items.append((new_key, ', '.join(str(x) for x in v)))
            else:
                items.append((new_key, v))
        return dict(items)

    def save_to_file(self, data: Any, filepath: str, format: Optional[str] = None):
        """保存数据到文件"""
        path = Path(filepath)

        if not format:
            format = path.suffix.lstrip('.')

        converted = self.convert(data, format)

        mode = 'wb' if isinstance(converted, bytes) else 'w'
        with open(path, mode, encoding='utf-8' if mode == 'w' else None) as f:
            f.write(converted)

        logger.info(f"数据已保存到: {filepath}")
