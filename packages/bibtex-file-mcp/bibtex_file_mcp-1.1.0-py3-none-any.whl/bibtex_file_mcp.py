from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
import json
import re

# Initialize FastMCP server
mcp = FastMCP("bibtex-mcp-server")

class BibtexEntry(BaseModel):
    type: str
    key: str
    fields: Dict[str, str]

class BibtexParser:
    def parse(self, content: str) -> List[BibtexEntry]:
        """改进的BibTeX解析器，支持更复杂的格式"""
        entries = []
        content = self._clean_content(content)
        
        # 找到所有条目的开始位置
        entry_starts = []
        i = 0
        while i < len(content):
            if content[i] == '@':
                # 查找条目类型和键
                match = re.match(r'@(\w+)\s*\{\s*([^,\s}]+)\s*,?', content[i:])
                if match:
                    entry_starts.append(i)
            i += 1
        
        for i, start_pos in enumerate(entry_starts):
            # 确定条目结束位置
            end_pos = entry_starts[i + 1] if i + 1 < len(entry_starts) else len(content)
            entry_content = content[start_pos:end_pos].strip()
            
            entry = self._parse_single_entry(entry_content)
            if entry:
                entries.append(entry)
        
        return entries
    
    def _clean_content(self, content: str) -> str:
        """清理内容，移除注释"""
        lines = []
        for line in content.split('\n'):
            # 移除行注释（不在字符串内的%注释）
            if '%' in line and not self._is_in_string(line, line.find('%')):
                line = line[:line.find('%')]
            lines.append(line)
        return '\n'.join(lines)
    
    def _is_in_string(self, line: str, pos: int) -> bool:
        """检查位置是否在字符串内"""
        in_braces = 0
        in_quotes = False
        for i, char in enumerate(line[:pos]):
            if char == '"' and (i == 0 or line[i-1] != '\\'):
                in_quotes = not in_quotes
            elif not in_quotes:
                if char == '{':
                    in_braces += 1
                elif char == '}':
                    in_braces -= 1
        return in_quotes or in_braces > 0
    
    def _parse_single_entry(self, entry_content: str) -> Optional[BibtexEntry]:
        """解析单个条目"""
        # 提取条目类型和键
        match = re.match(r'@(\w+)\s*\{\s*([^,\s}]+)\s*,?', entry_content)
        if not match:
            return None
        
        entry_type = match.group(1).lower()
        key = match.group(2).strip()
        
        # 提取字段部分
        fields_start = match.end()
        fields_content = entry_content[fields_start:].rstrip(' \n\t}')
        
        fields = self._parse_fields(fields_content)
        
        return BibtexEntry(type=entry_type, key=key, fields=fields)
    
    def _parse_fields(self, fields_content: str) -> Dict[str, str]:
        """解析字段内容"""
        fields = {}
        i = 0
        
        while i < len(fields_content):
            # 跳过空白字符
            while i < len(fields_content) and fields_content[i].isspace():
                i += 1
            
            if i >= len(fields_content):
                break
            
            # 查找字段名
            field_start = i
            while i < len(fields_content) and (fields_content[i].isalnum() or fields_content[i] == '_'):
                i += 1
            
            if i == field_start:
                i += 1
                continue
                
            field_name = fields_content[field_start:i].strip()
            
            # 跳过空白和等号
            while i < len(fields_content) and (fields_content[i].isspace() or fields_content[i] == '='):
                i += 1
            
            # 解析字段值
            field_value, new_i = self._parse_field_value(fields_content, i)
            if field_value is not None:
                fields[field_name.lower()] = field_value
            
            i = new_i
        
        return fields
    
    def _parse_field_value(self, content: str, start: int) -> tuple[Optional[str], int]:
        """解析字段值，处理大括号和引号"""
        i = start
        
        # 跳过空白
        while i < len(content) and content[i].isspace():
            i += 1
        
        if i >= len(content):
            return None, i
        
        if content[i] == '{':
            # 大括号包围的值
            return self._parse_braced_value(content, i)
        elif content[i] == '"':
            # 引号包围的值
            return self._parse_quoted_value(content, i)
        else:
            # 字符串宏或数字
            return self._parse_unquoted_value(content, i)
    
    def _parse_braced_value(self, content: str, start: int) -> tuple[str, int]:
        """解析大括号包围的值"""
        i = start + 1  # 跳过开始的大括号
        brace_count = 1
        value_start = i
        
        while i < len(content) and brace_count > 0:
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
            i += 1
        
        value = content[value_start:i-1] if brace_count == 0 else content[value_start:]
        
        # 跳过后续的逗号
        while i < len(content) and (content[i].isspace() or content[i] == ','):
            i += 1
        
        return value.strip(), i
    
    def _parse_quoted_value(self, content: str, start: int) -> tuple[str, int]:
        """解析引号包围的值"""
        i = start + 1  # 跳过开始的引号
        value_chars = []
        
        while i < len(content):
            if content[i] == '"' and (i == 0 or content[i-1] != '\\'):
                i += 1
                break
            elif content[i] == '\\' and i + 1 < len(content):
                # 处理转义字符
                value_chars.append(content[i:i+2])
                i += 2
            else:
                value_chars.append(content[i])
                i += 1
        
        # 跳过后续的逗号
        while i < len(content) and (content[i].isspace() or content[i] == ','):
            i += 1
        
        return ''.join(value_chars), i
    
    def _parse_unquoted_value(self, content: str, start: int) -> tuple[str, int]:
        """解析不带引号的值（通常是数字或宏）"""
        i = start
        value_chars = []
        
        while i < len(content) and content[i] not in ',}':
            if not content[i].isspace() or value_chars:
                value_chars.append(content[i])
            i += 1
        
        # 跳过后续的逗号
        while i < len(content) and (content[i].isspace() or content[i] == ','):
            i += 1
        
        return ''.join(value_chars).strip(), i

class BibtexWriter:
    def write(self, entries: List[BibtexEntry]) -> str:
        lines = []
        for entry in entries:
            lines.append(f"@{entry.type}{{{entry.key},")
            for field_name, field_value in entry.fields.items():
                lines.append(f"  {field_name} = {{{field_value}}},")
            lines.append("}")
            lines.append("")  # Empty line between entries
        return "\n".join(lines)

parser = BibtexParser()
writer = BibtexWriter()

@mcp.tool(description="Read BibTeX file and return all keys or show first 5 entries")
def read_bibtex_file(filepath: str, show_details: bool = False) -> str:
    """读取BibTeX文件，默认返回所有key，可选显示前5条详细信息"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = parser.parse(content)
    
    if show_details:
        # 显示前5条的详细信息
        result = f"文件: {filepath} (总计 {len(entries)} 个条目)\n\n"
        result += "前5条条目详细信息:\n"
        for i, entry in enumerate(entries[:5]):
            result += f"\n{i+1}. Key: {entry.key}\n"
            result += f"   Type: {entry.type}\n"
            for field, value in entry.fields.items():
                result += f"   {field}: {value}\n"
        
        if len(entries) > 5:
            result += f"\n... 还有 {len(entries) - 5} 个条目"
        
        return result
    else:
        # 返回所有key
        all_keys = [entry.key for entry in entries]
        result = f"文件: {filepath} (总计 {len(entries)} 个条目)\n\n"
        result += "所有条目的key:\n"
        result += "\n".join(all_keys)
        return result

@mcp.tool(description="Get detailed information for a specific BibTeX entry by key")
def get_bibtex_entry(filepath: str, key: str) -> str:
    """根据key获取单条entry的详细信息"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = parser.parse(content)
    
    for entry in entries:
        if entry.key == key:
            result = f"条目详细信息:\n"
            result += f"Key: {entry.key}\n"
            result += f"Type: {entry.type}\n"
            result += f"Fields:\n"
            for field, value in entry.fields.items():
                result += f"  {field}: {value}\n"
            return result
    
    available_keys = [entry.key for entry in entries]
    return f"未找到key '{key}' 的条目。\n可用的keys: {available_keys[:10]}{'...' if len(available_keys) > 10 else ''}"

@mcp.tool(description="Write selected BibTeX entries to a new file")
def write_bibtex_entries(source_filepath: str, target_filepath: str, keys: List[str], mode: Literal["append", "overwrite"] = "append") -> str:
    """
    根据key列表写入选定的条目到新文件
    mode 只能为 "append" 或 "overwrite"，默认 "append"
    """
    if mode not in ["append", "overwrite"]:
        raise ValueError("mode 参数只能为 'append' 或 'overwrite'")
    
    with open(source_filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = parser.parse(content)
    
    # 筛选指定的条目
    selected_entries = []
    found_keys = []
    not_found_keys = []
    
    for key in keys:
        found = False
        for entry in entries:
            if entry.key == key:
                selected_entries.append(entry)
                found_keys.append(key)
                found = True
                break
        if not found:
            not_found_keys.append(key)
    
    # 写入文件
    bibtex_content = writer.write(selected_entries)
    
    if mode == "append":
        with open(target_filepath, 'a+', encoding='utf-8') as f:
            f.write(bibtex_content)
        result = f"成功追加 {len(selected_entries)} 个条目到 {target_filepath}\n"
    elif mode == "overwrite":
        with open(target_filepath, 'w', encoding='utf-8') as f:
            f.write(bibtex_content)
        result = f"成功写入 {len(selected_entries)} 个条目到 {target_filepath}\n"
    
    result += f"找到的keys: {found_keys}\n"
    if not_found_keys:
        result += f"未找到的keys: {not_found_keys}\n"
    
    return result

def main():
    """Entry point for uvx"""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()