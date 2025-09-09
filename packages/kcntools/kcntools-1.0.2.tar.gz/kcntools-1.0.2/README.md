## KCNtools Pip Project

![Python Logo](https://www.python.org/static/community_logos/python-logo.png "Sample inline image")

这是一个NLP的python项目，目的是解决ai项目组中常用到的NLP工具集合，该工具提供基本的字符串搜索，nromaize等工具

## Requirements

Python 3.8 or later with all requirements.txt
dependencies installed, including `build` and `twine`. To install run:

```bash
python -m pip install -U pip
pip install -r requirements.txt
```

## Pip Package Steps

### https://pypi.org/

```bash
# Build and upload https://pypi.org/
rm -rf build dist && python3 -m build && python3 -m twine upload -r ezone_snapshot_pypi_ai-repo dist/*
# username: __token__
# password: pypi-AgENdGVzdC5weXBpLm9yZ...

# Download and install
pip install -U kcntools
```

some sample python code

```python

from kcntools.strutils import normalize
from kcntools.chutils import wordLen,charSplit,charType
from kcntools.darray import Compile 
# 规范化同形异码字
print(normalize('test code ！这是一个测试，看看?'))
print(wordLen('test code ！这是一个测试，看看?'))
```
