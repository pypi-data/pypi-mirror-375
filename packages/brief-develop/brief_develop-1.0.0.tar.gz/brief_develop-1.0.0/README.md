# Brief-Develop

一个轻量级的Python测试框架，提供简洁的测试运行和彩色输出功能。

## 功能特性

- 🎨 彩色终端输出，提升测试结果的可读性
- 📊 自动统计测试通过率
- 🧪 支持正常测试和异常测试
- 🔧 简单易用的API设计
- 📦 轻量级无依赖（仅需termcolor）

## 安装

### 使用pip安装

```bash
pip install brief_develop
```

## 快速开始

### 基本用法

```python
from brief_develop import BriefTest

# 创建测试实例
brief_test = BriefTest()

# 运行正常测试
def test_addition(a,b):
    return a+b

brief_test.run_test(    test_func        = lambda:test_addition(1,1),
                        detail           = lambda:f"test_addition 功能测试",
                        expected_source  = lambda:test_addition(1,1),
                        expected_message = 2
                    )

# 运行异常测试
def test_division_by_zero():
    1 / 0

brief_test.run_test(    test_func        = lambda: test_division_by_zero(),
                        detail           = lambda:f"test_division_by_zero 功能测试",
                        expected_message = "division by zero"
                    )

# 获取测试统计
print(f"测试通过率: {brief_test.get_stats()}%")

```

## API文档

### BriefTest类

#### `__init__()`
初始化测试实例。

#### `print_Brief_Test(message: str, color: str = None)`
打印彩色消息到终端。

- `message`: 要显示的消息
- `color`: 颜色名称（如 'red', 'green', 'blue' 等）

#### `run_test(test_func, detail=None, expected_source=None, expected_message=None)`
运行单个测试用例。

- `test_func`: 测试函数或可调用对象
- `detail`: 测试描述信息
- `expected_source`: 期望的返回值（正常测试）
- `expected_message`: 期望的异常消息（异常测试）

#### `get_stats()`
获取测试统计信息，返回通过率百分比。

## 项目结构

```
brief_develop/
├── src/
│   └── brief_develop/
│       ├── __init__.py      # 包初始化文件
│       └── module.py        # 主要功能实现
├── .gitignore              # Git忽略规则
├── requirements.txt        # 项目依赖
├── LICENSE                # 许可证文件
└── README.md              # 项目说明文档
```

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。在提交代码前请确保：
1. 所有现有测试通过
2. 新增功能包含相应的测试用例
3. 代码风格符合项目规范

## 许可证

本项目基于MIT许可证开源 - 详见[LICENSE](LICENSE)文件。


## 版本信息

- **v1.0.0** - 初始版本发布
  - 基础测试框架功能
  - 彩色输出支持
  - 测试统计功能

## 作者

- **hh66dw** - 项目创建者和维护者

## 第三方库致谢 (Acknowledgements)
本项目得益于以下优秀的开源库：

termcolor - Copyright (c) 2008-2011 Volvox Development Team - 基于MIT许可证

感谢所有开源贡献者的辛勤工作。
