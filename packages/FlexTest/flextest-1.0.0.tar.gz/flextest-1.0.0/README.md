# FlexTest
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

A easy-to-use Python unit testing library, designed for beginners and ready to use out of the box.

## 📦 Installation
```bash
pip install FlexTest
```

## 📜 Changelog
See [CHANGELOG.md](https://github.com/qiufengcute/FlexTest/blob/main/CHANGELOG.md)

## QuickStart
```Python
from FlexTest import TestEq, TestIs, TestEr, TestCustom, summary

# Basic equality test
TestEq("Addition test", lambda a, b: a + b, 2, 3, expected=5)

# Object identity test
TestIs("Singleton test", lambda: None, expected=None)

# Exception test
TestEr("Division by zero test", lambda a, b: a / b, 1, 0, expected_exception=ZeroDivisionError)

# Custom test
TestCustom("Even number test", lambda x: x % 2 == 0, 4)

# Output test results
summary()
```
