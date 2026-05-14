# GenPages

从多个 legacy.json 文件生成美观的展示网站。

## 功能

- **下载**: 从 GitHub 仓库批量下载 legacy.json 文件
- **构建**: 生成汇总页面和详情页面
- **模板**: 使用 Cheetah3 模板引擎
- **美观**: 包含 CSS 样式，支持中文

## 安装依赖

```bash
pip install -r requirements.txt
```

依赖包：
- requests>=2.31.0
- Cheetah3>=3.2.6

## 快速开始

### 1. 准备输入文件

在 `input.txt` 中每行填写一个 GitHub 仓库地址：

```
https://github.com/user/repo1
https://github.com/user/repo2
```

### 2. 下载 legacy.json 文件

```bash
python genpages.py download
```

该命令会：
- 从 input.txt 读取仓库列表
- 尝试从 main 或 master 分支下载 legacy.json
- 保存到 __cache/ 目录

### 3. 构建网页

```bash
python genpages.py build
```

该命令会：
- 读取 __cache/ 目录下的 legacy.json 文件
- 生成汇总页面 (index.html)
- 为每个项目生成详情页面
- 复制 CSS 样式文件
- 输出到 dist/ 目录

### 4. 查看结果

在浏览器中打开 `dist/index.html` 查看生成的网站。

## 命令行选项

```bash
python genpages.py [--input INPUT] [--output OUTPUT] <command>
```

选项：
- `--input`: 指定输入文件（默认: input.txt）
- `--output`: 指定输出目录（默认: dist）

命令：
- `download`: 下载 legacy.json 文件
- `build`: 构建网页

## 目录结构

```
genpages/
├── genpages.py           # 主程序
├── input.txt             # 输入文件（仓库列表）
├── requirements.txt      # 依赖列表
├── templates/            # 模板目录
│   ├── index.tmpl        # 汇总页面模板
│   ├── detail.tmpl       # 详情页面模板
│   └── common.css        # 样式文件
├── __cache/              # 下载的 legacy.json 缓存
└── dist/                 # 生成的网页输出
```

## 示例

```bash
# 使用自定义输入和输出
python genpages.py --input my-repos.txt --output my-site download
python genpages.py --input my-repos.txt --output my-site build
```

## 注意事项

- 确保仓库的 legacy.json 文件位于根目录
- 程序会尝试 main 和 master 两个分支
- 下载失败的仓库会在控制台提示
- 构建时会自动处理文本中的 URL 链接

