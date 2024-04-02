# 1. 项目背景
# 2. 数据集介绍
![img.npg](data/img/img.png)
![img.npg](data/img/img_1.png)
# 3. 分析方法与分析思虑
# 4. 数据清洗
##    4.1 数据导入

```
import pandas as pd
data_user = pd.read_csv("data/old date/jdata_user.csv", index_col=0)
data_shop = pd.read_csv("data/old date/jdata_shop.csv", index_col=0)
data_product = pd.read_csv("data/old date/jdata_product.csv", index_col=0)
data_comment = pd.read_csv("data/old date/jdata_comment.csv", index_col=0)
data_action = pd.read_csv("data/jdata_action.csv", index_col=0)
```
##    4.2 缺失值处理
###       4.2.1 查看缺失值
###       4.2.2 填充缺失值
##    4.3 数据类型确定
##    4.4 异常值处理
##    4.5 重复值处理
###       4.5.1 查看重复值
###       4.5.2 查看重复值的具体情况
##    4.6 辅助列处理
##    4.7 保存清洗后的数据
# 5. 数据分析
