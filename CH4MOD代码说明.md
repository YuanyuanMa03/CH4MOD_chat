# CH4MOD模型说明文档

1. 输入数据
2. 逐日的温度数据（℃），仅需要从水稻种植开始日期到结束日期的数据，具体格式见“长沙气温2003.txt”。
3. 水稻种植相关统计数据（样例数据run.csv文件），具体如下：

表 1 输入数据介绍

|  |  |  |
| --- | --- | --- |
| 名称 | 单位 | 说明 |
| GrainYield | kg/ha | 水稻的稻谷产量 |
| SoilSand | % | 土壤中的砂粒含量百分率 |
| OMN | kg/ha | 稻田外源有机质的易分解组分含量 |
| OMS | kg/ha | 稻田外源有机质的难分解组分含量 |
| WaterRegime | — | 稻田水管理措施 |
| StartDay | — | 水稻移栽日期 |
| EndDay | — | 水稻收获日期 |

其中水管理措施用1~5表示，具体含义见下表：

表 2 水管理措施介绍

|  |  |  |
| --- | --- | --- |
| 水管理措施 | 模式组成 | 描述 |
| 1 | 淹水-烤田-淹水-间歇灌溉 | 多见于华北和华东的单季稻 |
| 2 | 淹水-烤田-间歇灌溉 | 多见于华南和西南的单、双季稻 |
| 3 | 淹水-间歇灌溉 | 类似于模式2，但没有明显的烤田 |
| 4 | 淹水 | 排灌条件欠佳的高地稻田和盐碱稻田 |
| 5 | 间歇灌溉 | 低洼稻田，地下水位通常较高 |

1. 调用方法

使用CH4MOD模型主要需要调用CH4MOD.py文件中的CH4Flux\_day函数。调用代码在Run.py文件中（具体如下）

import pandas as pd

from CH4MOD import CH4Flux\_day # 确保 CH4MOD.py 在同一目录下

# 读取 CSV 文件

data = pd.read\_csv("run.csv")

# 读取气温数据

T = pd.read\_csv("长沙气温2003.txt", header=None)

# 调用 CH4Flux\_day 函数

result = CH4Flux\_day(

day\_begin=data['StartDay'][0],

day\_end=data['EndDay'][0],

IP=data['WaterRegime'][0],

sand=data['SoilSand'][0],

Tair=T[0],

OMS=data['OMS'][0],

OMN=data['OMN'][0],

GY=data['GrainYield'][0]

)

# 将结果写入文件

result.to\_csv("result\_py.txt", index=False, sep='\t')

1. 输出结果

最后结果输出一个dataframe，是逐日CH4排放的结果，主要包括以下数据：

表 3 输出数据说明

|  |  |  |
| --- | --- | --- |
| 名称 | 单位 | 说明 |
| DAT | d | 日期 |
| W | g/m2 | 稻田的地上生物量 |
| Wroot | g/m2 | 水稻根系的生物量 |
| Tsoil | ℃ | 稻田土壤的温度 |
| Eh | mv | 土壤的氧化还原电位 |
| Com | g/m2·d | 稻田外源有机质分解产生的甲烷基质 |
| Cr | g/m2·d | 水稻植株代谢产生的土壤甲烷基质 |
| P | g/m2·d | 土壤中甲烷的产生率 |
| Ebl | g/m2·d | 甲烷通过气泡方式排放的排放速率 |
| Ep | g/m2·d | 甲烷通过植株排放的排放速率 |
| E | g/m2·d | 稻田甲烷的总排放 |