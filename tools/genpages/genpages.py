#!/usr/bin/env python3
import argparse
import json
import os
import re
import requests
import shutil
from datetime import datetime
from pathlib import Path
from Cheetah.Template import Template
from Cheetah.Filters import RawOrEncodedUnicode

INPUT_FILE = "input.txt"
CACHE_DIR = "__cache"
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "dist"

URL_RE = re.compile(r'(https?://[^\s<>\(\)"]+[^\s<>".,;:!?)])')

def process_text(text):
    if not text:
        return text
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('\n', '<br>')
    text = URL_RE.sub(r'<a href="\1" target="_blank" class="link">\1</a>', text)
    return text

def process_array(items):
    if not items:
        return []
    return [process_text(item) for item in items]

def process_named(items):
    if not items:
        return []
    result = []
    for item in items:
        if not item:
            result.append('')
            continue
        lines = item.split('\n', 1)
        first = lines[0].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        first = URL_RE.sub(r'<a href="\1" target="_blank" class="link">\1</a>', first)
        if len(lines) > 1 and lines[1].strip():
            rest = process_text(lines[1])
            result.append(f'<b>{first}</b><br>{rest}')
        else:
            result.append(f'<b>{first}</b>')
    return result

def process_milestones(items):
    if not items:
        return []
    result = []
    for m in items:
        if isinstance(m, list) and len(m) >= 2:
            time_str = format_date(m[0])
            desc = process_text(m[1])
            result.append(f'<span class="timeline-time">{time_str}</span><span class="timeline-desc">{desc}</span>')
    return result

def format_date(raw):
    if not raw:
        return ''
    if not isinstance(raw, str):
        raw = str(raw)
    raw = raw.strip()
    for fmt in [
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d',
    ]:
        try:
            dt = datetime.strptime(raw, fmt)
            return dt.strftime('%Y年%m月%d日 %H:%M')
        except ValueError:
            continue
    try:
        import email.utils as eutils
        dt = eutils.parsedate_to_datetime(raw)
        return dt.strftime('%Y年%m月%d日 %H:%M')
    except Exception:
        pass
    return raw

def format_period(start, end):
    s = str(start) if start else ''
    e = str(end) if end else ''
    has_start = any(c.isdigit() for c in s)
    has_end = any(c.isdigit() for c in e)
    if has_start and has_end:
        return f"{start} — {end}"
    elif has_start and not has_end:
        return f"始于 {start}"
    elif not has_start and has_end:
        return f"至 {end}"
    else:
        return "可用时间信息缺失"

def parse_github_url(url):
    pattern = r'^https?://github\.com/([^/]+)/([^/]+)/?$'
    match = re.match(pattern, url.strip())
    if match:
        return match.group(1), match.group(2)
    return None, None

def download_legacy_json(input_file, cache_dir):
    cache_path = Path(cache_dir)
    cache_path.mkdir(exist_ok=True)
    
    if not os.path.exists(input_file):
        print(f"❌ 错误: 输入文件 '{input_file}' 不存在")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if not lines:
        print("⚠️ 警告: 输入文件为空")
        return
    
    success_count = 0
    fail_count = 0
    failed_repos = []
    
    print("🚀 开始下载 legacy.json 文件...")
    print("-" * 60)
    
    for line in lines:
        url = line.strip()
        if not url:
            continue
        
        owner, repo = parse_github_url(url)
        if not owner or not repo:
            print(f"❌ 无效的 GitHub 地址: {url}")
            fail_count += 1
            failed_repos.append(url)
            continue
        
        output_file = cache_path / f"{owner}_{repo}.json"
        
        print(f"📥 正在下载: {owner}/{repo}")
        
        branches = ['main', 'master']
        downloaded = False
        
        for branch in branches:
            legacy_url = f"https://raw.githubusercontent.com/{owner}/{repo}/refs/heads/{branch}/legacy.json"
            
            try:
                response = requests.get(legacy_url, timeout=10)
                if response.status_code == 200:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"✅ 成功 (分支: {branch}): {output_file}")
                    success_count += 1
                    downloaded = True
                    break
                else:
                    print(f"ℹ️ 分支 {branch} 不存在或无 legacy.json")
            except requests.exceptions.RequestException as e:
                print(f"ℹ️ 分支 {branch} 请求失败: {str(e)}")
        
        if not downloaded:
            print(f"❌ 失败: 所有分支均未找到 legacy.json 文件")
            fail_count += 1
            failed_repos.append(url)
        
        print("-" * 60)
    
    print("\n📊 下载完成!")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    
    if failed_repos:
        print("\n❌ 失败的仓库列表:")
        for repo in failed_repos:
            print(f"  - {repo}")

def build(input_file, output_dir):
    print("🔨 开始构建网页...")
    
    cache_path = Path(CACHE_DIR)
    output_path = Path(output_dir)
    template_path = Path(TEMPLATE_DIR)
    
    output_path.mkdir(exist_ok=True)
    
    if not os.path.exists(input_file):
        print(f"❌ 错误: 输入文件 '{input_file}' 不存在")
        return
    
    if not cache_path.exists():
        print(f"❌ 错误: 缓存目录 '{CACHE_DIR}' 不存在")
        return
    
    if not template_path.exists():
        print(f"❌ 错误: 模板目录 '{TEMPLATE_DIR}' 不存在")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    git_urls = {}
    for line in lines:
        url = line.strip()
        if url:
            owner, repo = parse_github_url(url)
            if owner and repo:
                git_urls[f"{owner}_{repo}"] = url
    
    projects = []
    detail_pages = []
    
    print("\n📄 读取缓存的 legacy.json 文件...")
    
    for json_file in cache_path.glob("*.json"):
        file_key = json_file.stem
        git_url = git_urls.get(file_key, "")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project_id = data.get('id', file_key)
            detail_filename = f"{project_id}.html"
            detail_url = detail_filename
            
            formal_names = data.get('formal_names', [])
            if formal_names:
                formal_name = max(formal_names, key=len)
            else:
                formal_name = "missing"
            
            disciplines = data.get('disciplines', [])
            
            projects.append({
                'formal_name': formal_name,
                'disciplines': disciplines,
                'detail_url': detail_url
            })
            
            detail_pages.append({
                'data': data,
                'git_url': git_url,
                'filename': detail_filename
            })
            
            print(f"✅ 读取: {json_file.name}")
        except json.JSONDecodeError:
            print(f"❌ JSON 解析错误: {json_file.name}")
        except Exception as e:
            print(f"❌ 读取失败 {json_file.name}: {str(e)}")
    
    print(f"\n📊 共读取 {len(projects)} 个项目")
    
    print("\n🌐 生成汇总页面...")
    index_template_path = template_path / "index.tmpl"
    if index_template_path.exists():
        with open(index_template_path, 'r', encoding='utf-8') as f:
            index_template = f.read()
        
        name_spaces = [ { 'projects': projects } ]
        template = Template(index_template, searchList=name_spaces)
        index_html = str(template)
        
        index_output = output_path / "index.html"
        with open(index_output, 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print(f"✅ 汇总页面已生成: {index_output}")
    else:
        print(f"❌ 模板文件不存在: {index_template_path}")
    
    print("\n📄 生成详情页面...")
    detail_template_path = template_path / "detail.tmpl"
    if detail_template_path.exists():
        with open(detail_template_path, 'r', encoding='utf-8') as f:
            detail_template_content = f.read()
        
        for page in detail_pages:
            data = page['data']
            template = Template(detail_template_content)
            template._filter = RawOrEncodedUnicode
            
            formal_names = data.get('formal_names', [])
            template.title = max(formal_names, key=len) if formal_names else 'Legacy Project'
            template.git_url = page['git_url']
            
            template.id = data.get('id', '')
            template.has_id = bool(template.id)
            
            template.names = data.get('names', [])
            template.has_names = len(template.names) > 0
            
            template.formal_names = data.get('formal_names', [])
            template.has_formal_names = len(template.formal_names) > 0
            
            template.description = process_text(data.get('description', ''))
            template.has_description = bool(template.description)
            
            template.formal_description = process_text(data.get('formal_description', ''))
            template.has_formal_description = bool(template.formal_description)
            
            template.planning = process_text(data.get('planning', ''))
            template.has_planning = bool(template.planning)
            
            template.available_times = []
            raw_times = data.get('available_times', [])
            has_times = False
            for period in raw_times:
                if isinstance(period, list) and len(period) >= 2:
                    display = format_period(
                        format_date(period[0]),
                        format_date(period[1])
                    )
                    template.available_times.append(display)
                    has_times = True
            template.has_available_times = has_times
            
            template.milestones = process_milestones(data.get('milestones', []))
            template.has_milestones = len(template.milestones) > 0
            
            template.keywords = data.get('keywords', [])
            template.has_keywords = len(template.keywords) > 0
            
            template.disciplines = data.get('disciplines', [])
            template.has_disciplines = len(template.disciplines) > 0
            
            template.influencers = process_named(data.get('influencers', []))
            template.has_influencers = len(template.influencers) > 0
            
            template.resources = process_named(data.get('resources', []))
            template.has_resources = len(template.resources) > 0
            
            template.subsequents = process_named(data.get('subsequents', []))
            template.has_subsequents = len(template.subsequents) > 0
            
            template.extras = process_named(data.get('extras', []))
            template.has_extras = len(template.extras) > 0
            
            template.update_time = format_date(data.get('update_time', ''))
            template.has_update_time = bool(template.update_time)
            
            template.update_executor = data.get('update_executor', '')
            template.has_update_executor = bool(template.update_executor)
            
            template.commit_sha = data.get('commit_sha', '')
            template.has_commit_sha = bool(template.commit_sha)
            
            template.documentation = process_text(data.get('documentation', ''))
            template.has_documentation = bool(template.documentation)
            
            detail_html = str(template)
            
            detail_output = output_path / page['filename']
            with open(detail_output, 'w', encoding='utf-8') as f:
                f.write(detail_html)
            
            print(f"✅ 详情页面已生成: {detail_output}")
    else:
        print(f"❌ 模板文件不存在: {detail_template_path}")

    css_src = template_path / "common.css"
    if css_src.exists():
        shutil.copy2(css_src, output_path / "common.css")
        print(f"✅ CSS 文件已复制: common.css")
    
    print("\n🎉 构建完成!")
    print(f"📁 输出目录: {output_path.absolute()}")

def main():
    parser = argparse.ArgumentParser(description="网页生成脚本")
    parser.add_argument('--input', default=INPUT_FILE, help='指定输入文件路径 (默认: input.txt)')
    parser.add_argument('--output', default=OUTPUT_DIR, help='指定输出目录路径 (默认: dist)')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    subparsers.add_parser('download', help='下载 legacy.json 文件')
    subparsers.add_parser('build', help='构建网页')
    
    args = parser.parse_args()
    
    if args.command == 'download':
        download_legacy_json(args.input, CACHE_DIR)
    elif args.command == 'build':
        build(args.input, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()