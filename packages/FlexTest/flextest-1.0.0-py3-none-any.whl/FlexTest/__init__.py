import time
from colorama import Fore, Style, init

__version__ = "1.0.0"

# Initialize colors
init(autoreset=True)

class SimpleTest:
    def __init__(self):
        self.results = []
        self.start_time = None
        self.test_count = 0
    
    def start(self):
        """Start testing session"""
        self.start_time = time.time()
        print("Testing...")
        return self
    
    def TestEq(self, test_name, func, *args, expected):
        """Equality test: func(*args) == expected"""
        self.test_count += 1
        test_id = self.test_count
        
        try:
            result = func(*args)
            if result == expected:
                self.results.append(('·', test_id, f"Eq-{test_name}", "Test passed", 
                                   f"Expected:{expected} Got:{result} {expected}={result}"))
                return True
            else:
                self.results.append(('X', test_id, f"Eq-{test_name}", "Result mismatch", 
                                   f"Expected:{expected} Got:{result} {expected}!={result}"))
                return False
        except Exception as e:
            self.results.append(('E', test_id, f"Eq-{test_name}", "Error thrown", 
                               f"Expected:{expected} Error:{type(e).__name__}: {str(e)}"))
            return False
    
    def TestIs(self, test_name, func, *args, expected):
        """Identity test: func(*args) is expected"""
        self.test_count += 1
        test_id = self.test_count
        
        try:
            result = func(*args)
            if result is expected:
                self.results.append(('·', test_id, f"Is-{test_name}", "Test passed", 
                                   f"Expected:{expected} Got:{result} {expected} is {result}"))
                return True
            else:
                self.results.append(('X', test_id, f"Is-{test_name}", "Result mismatch", 
                                   f"Expected:{expected} Got:{result} {result} !is {expected}"))
                return False
        except Exception as e:
            self.results.append(('E', test_id, f"Is-{test_name}", "Error thrown", 
                               f"Expected:{expected} Error:{type(e).__name__}: {str(e)}"))
            return False
    
    def TestEr(self, test_name, func, *args, expected_exception):
        """Exception test: expect function to throw specified exception"""
        self.test_count += 1
        test_id = self.test_count
        
        try:
            result = func(*args)
            self.results.append(('X', test_id, f"Er-{test_name}", "Result mismatch", 
                               f"Expected:throw \"{expected_exception.__name__}\" but returned:{result}"))
            return False
        except expected_exception as e:
            self.results.append(('·', test_id, f"Er-{test_name}", "Test passed", 
                               f"Expected:throw \"{expected_exception.__name__}\" Error thrown:{type(e).__name__}: {str(e)}"))
            return True
        except Exception as e:
            self.results.append(('E', test_id, f"Er-{test_name}", "Error thrown", 
                               f"Expected:throw \"{expected_exception.__name__}\" Error:{type(e).__name__}: {str(e)}"))
            return False
    
    def TestCustom(self, test_name, test_func, *args):
        """Custom test: test_func(*args) returns True to pass"""
        self.test_count += 1
        test_id = self.test_count
        
        try:
            result = test_func(*args)
            if result is True:
                self.results.append(('·', test_id, f"Custom-{test_name}", "Test passed", 
                                   "Custom condition returned True"))
                return True
            elif result is False:
                self.results.append(('X', test_id, f"Custom-{test_name}", "Result mismatch", 
                                   "Custom condition returned False"))
                return False
            else:
                self.results.append(('E', test_id, f"Custom-{test_name}", "Configuration error", 
                                   f"Custom test function should return True/False, but returned: {result}"))
                return False
        except Exception as e:
            self.results.append(('E', test_id, f"Custom-{test_name}", "Error thrown", 
                               f"Custom test threw error:{type(e).__name__}: {str(e)}"))
            return False
    
    def summary(self):
        """Output test summary"""
        elapsed = time.time() - self.start_time
        
        # Output test result symbols
        symbols = ''.join([result[0] for result in self.results])
        print(f"\n{symbols}")
        print("-" * 10)
        
        # Output detailed results
        for symbol, test_id, test_type, status, message in self.results:
            if symbol == '·':
                color = Fore.GREEN
            elif symbol == 'X':
                color = Fore.YELLOW
            else:  # E
                color = Fore.RED
            
            print(f"{test_id}. {test_type} {status} [{color}{symbol}{Style.RESET_ALL}]")
            print(message)
            print("-" * 10)
        
        # Statistics
        total_tests = len(self.results)
        ok_tests = [r[1] for r in self.results if r[0] == '·']
        x_tests = [r[1] for r in self.results if r[0] == 'X']
        e_tests = [r[1] for r in self.results if r[0] == 'E']
        
        print(f"Ran {total_tests} tests in {elapsed:.4f}s")
        print("-" * 10)
        print(f"Successfully ran {total_tests} tests")
        
        if ok_tests:
            print(f"Tests passed:{len(ok_tests)}(Test {', '.join(map(str, ok_tests))})")
        else:
            print("Tests passed:0")
            
        if x_tests:
            print(f"Result mismatch:{len(x_tests)}(Test {', '.join(map(str, x_tests))})")
        else:
            print("Result mismatch:0")
            
        if e_tests:
            print(f"Errors thrown:{len(e_tests)}(Test {', '.join(map(str, e_tests))})")
        else:
            print("Errors thrown:0")
        
        if len(ok_tests) == total_tests:
            print(f"{Fore.GREEN}All tests passed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Tests failed{Style.RESET_ALL}")
            return False

# Create global instance
tester = SimpleTest().start()

# Simplified calling methods
def TestEq(test_name, func, *args, expected):
    return tester.TestEq(test_name, func, *args, expected=expected)

def TestIs(test_name, func, *args, expected):
    return tester.TestIs(test_name, func, *args, expected=expected)

def TestEr(test_name, func, *args, expected_exception):
    return tester.TestEr(test_name, func, *args, expected_exception=expected_exception)

def TestCustom(test_name, test_func, *args):
    return tester.TestCustom(test_name, test_func, *args)

def summary():
    return tester.summary()
