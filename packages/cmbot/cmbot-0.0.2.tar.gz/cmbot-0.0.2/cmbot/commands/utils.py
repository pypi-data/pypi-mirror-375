# utils.py
from pathlib import Path
from string import Template


def render_template(template_path, context):
    """渲染模板文件"""
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # 使用字符串模板进行替换
    template = Template(template_content)
    return template.safe_substitute(**context)


def create_file(file_path, content):
    """创建文件"""
    # 确保目录存在
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
