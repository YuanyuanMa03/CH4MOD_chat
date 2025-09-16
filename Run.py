import pandas as pd
from CH4MOD import CH4Flux_day  # 确保 CH4MOD.py 在同一目录下

# 读取 CSV 文件
data = pd.read_csv("run.csv")

# 读取气温数据
T = pd.read_csv("长沙气温2003.txt", header=None)

# 调用 CH4Flux_day 函数
result = CH4Flux_day(
    day_begin=data['StartDay'][0],
    day_end=data['EndDay'][0],
    IP=data['WaterRegime'][0],
    sand=data['SoilSand'][0],
    Tair=T[0],
    OMS=data['OMS'][0],
    OMN=data['OMN'][0],
    GY=data['GrainYield'][0]
)

# 将结果写入文件
result.to_csv("result_py.txt", index=False, sep='\t')