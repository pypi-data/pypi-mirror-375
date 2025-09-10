from termcolor import colored

class BriefTest:
    def __init__(self):
        self.test_num = 0
        self.pass_num = 0

    def print_Brief_Test(self,message:str,color:str = None):
        print(colored(message,color))
        
    
    def run_test(self, test_func, detail = None, expected_source=None, expected_message=None):
        """运行单个测试用例"""
        self.test_num += 1

        try:
            # 如果传入的是可调用对象（如 lambda），先求值 --为异常
            eval_detail  = detail() if callable(detail) else detail
            eval_source  = expected_source() if callable(expected_source) else expected_source
            eval_message = expected_message() if callable(expected_message) else expected_message

            test_func()

            # 如果传入的是可调用对象（如 lambda），先求值 
            eval_detail  = detail() if callable(detail) else detail
            eval_source  = expected_source() if callable(expected_source) else expected_source
            eval_message = expected_message() if callable(expected_message) else expected_message

            if eval_source is not None:
                # 正常测试，期望成功
                if eval_source == eval_message:
                    self.pass_num += 1
                    self.print_Brief_Test(f"✓ 测试 {eval_detail if eval_detail else self.test_num} 正常\r\n")
                else:
                    self.print_Brief_Test(f"✗ 测试 {eval_detail if eval_detail else self.test_num} 失败\r\n", "red")

                return True
            else:
                # 期望异常但未发生
                self.print_Brief_Test(f"✗ 测试 {eval_detail if eval_detail else self.test_num} 失败：期望异常但未发生", "red")
                return False
        except Exception as e:
            if eval_source is None and str(e) == (eval_message if eval_message is not None else ""):
                # 异常符合预期
                self.pass_num += 1
                self.print_Brief_Test(f"✓ 测试 {eval_detail if eval_detail else self.test_num} 异常处理正常\r\n")
                return True
            else:
                # 异常不符合预期
                self.print_Brief_Test(f"✗ 测试 {eval_detail if eval_detail else self.test_num} 异常处理失败：{e}", "red")
                return False
    
    def get_stats(self):
        """获取测试统计"""
        return self.pass_num * 100 / self.test_num if self.test_num > 0 else 0
