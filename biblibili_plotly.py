import plotly
import plotly.graph_objs as go
import plotly.exceptions as px
import numpy as np
import pandas as pd

data = pd.read_csv("F:\BILIBILI_USERS_INFO_api.csv",encoding="gb18030")   #读取csv文件
LEL = data['等级']  #获取某一列

level = {}
for i in LEL:           #统计每个元素出现次数
    level[i] = 0
for j in LEL:
    level[j] = level[j]+1
level_sort = sorted(level.items(),key = lambda x:x[0])
level_sort = dict(level_sort)
print(level_sort)
key = []

for i in level_sort.keys():
    key.append(i)


values = []
for i in level_sort.values():
    values.append(i)


fig= go.Bar(x=key,y = values,
            text=values, textposition='outside'  )
sh = go.Figure(fig)
sh.update_layout(
    title = "哔哩哔哩等级分布",
    yaxis_title = "人数",
    xaxis_title = "等级"
)
sh.show()

