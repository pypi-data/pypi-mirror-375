"""
Brief-Develop - 一个轻量级的Python测试框架

提供简洁的测试运行和彩色输出功能，支持正常测试和异常测试，
自动统计测试通过率,并具有简单易用的API设计。

主要功能：
- 🎨 彩色终端输出，提升测试结果的可读性
- 📊 自动统计测试通过率
- 🧪 支持正常测试和异常测试
- 🔧 简单易用的API设计

示例用法：

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

更多用法请参考项目README.md文档。
"""

try:
    from .module import BriefTest
except ImportError:
    from module import BriefTest

__version__ = "1.0.0"
__author__ = "hh66dw"
__description__ = "一个轻量级的Python测试框架,提供简洁的测试运行和彩色输出功能"
__license__ = "MIT"
__all__ = ['BriefTest', '__version__', '__author__', '__description__', '__license__']
