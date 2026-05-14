# legacy.json

`legacy.json` 是用于描述历史遗产项目的元数据文件规范。

## 概述

此处"遗产"**并非**指已过时但因使用范围广而难以替代的软件或硬件项目，而是指包括各类创建和实现活动，在人类社会发展过程中形成的、具有标志性意义、纪念意义、研究意义、社会意义等社区价值的物质资源和技术资源的总和，特别是体现民间的群体、团体、个人的努力的成果。

`legacy.json` 文件应存放于项目或其数字归档的根目录，采用 JSON 格式，支持 unicode。通过该文件，你得以在开源仓库中记录该项目的内部信息、项目历史、研究成果、技术细节、领域专业、重要知识、重要内涵等，以丰富在教育、研究、传播、自动化识别和处理、文化传承等方面的历史资料记载和信息化使用，促进人们对社会发展、技术起源、人类活动、历史发展的理解。

## 项目结构

```
legacy.json/
├── spec.md              # 完整的规范说明文档
├── examples/            # 示例文件
│   └── legacy.json      # 示例 legacy.json 文件
└── tools/               # 工具集
    ├── editor.py        # 图形化编辑器
    ├── Editor.README.md # 编辑器说明文档
    └── genpages/        # 网页生成工具
```

## 快速开始

### 1. 了解规范

阅读 [spec.md](spec.md) 了解完整的字段定义和使用规范。

### 2. 使用编辑器创建/编辑 legacy.json

运行图形化编辑器：

```bash
python tools/editor.py
```

### 3. 生成网页展示

使用网页生成工具创建展示页面：

```bash
cd tools/genpages
pip install -r requirements.txt
python genpages.py download
python genpages.py build
```

## 工具说明

- **editor.py**: 基于 tkinter 的图形化编辑器，用于创建和编辑 legacy.json 文件，详细说明请参考 [Editor.README.md](tools/Editor.README.md)
- **genpages/**: 网页生成工具，用于从多个 legacy.json 文件生成美观的展示网站，详细说明请参考 [genpages/README.md](tools/genpages/README.md)

## 示例

查看 [examples/legacy.json](examples/legacy.json) 了解如何填写 legacy.json 文件。

## 规范要点

所有字段均为可选，软件应能处理字段缺失的情况。主要字段包括：

- `id`: 项目标识符
- `names`: 项目名称（内部）
- `formal_names`: 项目名称（公开）
- `planning`: 项目计划与背景
- `description`: 项目最终状态（研究视角）
- `formal_description`: 项目公开描述（历史视角）
- `available_times`: 可用时间范围
- `milestones`: 里程碑
- `keywords`: 关键词
- `disciplines`: 学科领域
- `influencers`: 贡献者
- `resources`: 相关资源
- `subsequents`: 后继项目

完整规范请参考 [spec.md](spec.md)。

