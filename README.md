# python-mysql
将函数转换成SQL语句，可以让你写得轻松一些~

## 如何使用？
假设你的数据库test中有这样一张表student

ID | name | score
---|---|---
1 | leo | 60 
2 | tom | 70


**- 1 连接数据库**
1. 直接连接
```
mysql = MySQL() # 单例模式
if not mysql.connect(host, user, password, database):
    print('数据库连接失败，错误原因：', mysql.error)

```
2. 通过配置文件连接
```
mysql = MySQL() # 单例模式
if not mysql.connect_from_file('my.cnf'):
    print('数据库连接失败，错误原因：', mysql.error)

```
3. 配置文件格式

```
[client]
host = localhost
user = root
password = root
database = test
port = 3306
bind-address = 127.0.0.1
default-character-set = utf-8
```
默认字符编码为UTF-8（可修改），默认游标类型为字典游标（可修改）

**- 2 查询操作**

```
table_name = 'student'  # 表名
fields = ['name', 'score'] or 'name, score' # 字段列表
condition = 'name = "leo"' or {'name': 'leo'}   # 条件（dict形式仅支持=情况）
result = mysql.query(table_name, fields, condition)
print(result)   # [{'name': 'leo', 'score': 60}]
```

**- 3 插入操作**

```
data = {'name': 'jane', 'score': 80}
mysql.insert(table_name, data, authocommit=True)
```
autocommit（自动提交）默认为True，在sql语句执行成功后自动提交。得到结果：

ID | name | score
---|---|---
1 | leo | 60 
2 | tom | 70
3 | jane | 80

**- 4 回退操作**

若设为False，则不会提交，可以执行回退操作。

```
mysql.rollback()
```

**- 5 替换操作**

```
data = {'id': 3, name': 'rose', 'score': 90}
mysql.replace(table_name, data)
```

若数据在表中不存在，则插入数据；

若数据已经存在（字段中必须有不重复字段unique、primary_key），则更新数据。得到结果：

ID | name | score
---|---|---
1 | leo | 60 
2 | tom | 70
3 | rose | 90


**- 6 更新操作**

```
data = {name': 'tom', 'score': 93}
condition = {'id': 2}
mysql.update(table_name, data, condition)
```
得到结果：

ID | name | score
---|---|---
1 | leo | 60
2 | tom | 93
3 | rose | 90

**- 7 删除操作**

```
condition = 'score > 80'
mysql.delete(table_name, condition)
```
得到结果：

ID | name | score
---|---|---
1 | leo | 60 

**- 8 插入多行**
```
data_matrix = [
    ['ben', 95],
    ['jack', 75]
]
mysql.excuteMany(table_name, fields, data_matrix)
```

得到结果：

ID | name | score
---|---|---
1 | leo | 60 
4 | ben | 95
5 | jack | 75

**- 9 查看数据库连接状态**

```
state = mysql.get_state()
print(state)    # True
```




