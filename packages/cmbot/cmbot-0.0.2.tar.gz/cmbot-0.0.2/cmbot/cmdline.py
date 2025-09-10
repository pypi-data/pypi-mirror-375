# cli.py
import argparse
from pathlib import Path
from cmbot.commands.utils import render_template, create_file


def execute():
    parser = argparse.ArgumentParser(description='My Scaffold Tool')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # 创建生成process的子命令
    process_parser = subparsers.add_parser('genprocess', help='生成一个新的RPA流程')
    process_parser1 = subparsers.add_parser('hello', help='打印hello world')
    process_parser.add_argument('process_name', help='流程名称')
    process_parser.add_argument('--max-attempts', '-m',
                                type=int,
                                default=1,
                                help='最大重试次数 (默认: 1)')
    args = parser.parse_args()

    if args.command == 'genprocess':
        generate_process(args.process_name, args.max_attempts)
    elif args.command == 'hello':
        print('hello world!')


def generate_process(process_name, max_attempts):
    """生成爬虫文件"""
    # 模板变量
    context = {
        'process_name': process_name,
        'max_attempts': max_attempts,
        'class_name': 'RpaProcess'
    }

    # 模板文件路径
    template_path = Path(__file__).parent / 'templates' / f'process_template.py.tpl'

    # 输出文件路径
    output_path = Path('processes') / f'{process_name}.py'

    # 渲染模板并创建文件
    content = render_template(template_path, context)
    create_file(output_path, content)

    print(f"Created spider: {output_path}")


if __name__ == '__main__':
    execute()
