# python-tools
    Python useful small tools

<p align="center">
   <a href="./doc//README_zh.md">中文文档</a> |
   <a href="./README.md">English Doc</a>
</p>

## ***anytree***
Modified from the Python package [Anytree](https://pypi.org/project/anytree/) with some additions:
1. Added some normal type annotations for easier usage
2. Added a copy module to optimize speed

## ***excel***
Small tools for use with Excel

### [tools.py](./excel/tools.py)
1. `unmerge_and_fill_cells`: Unmerge all merged cells in the given worksheet and fills the resulting individual cells with the value of the original merged cell.