# python-mysql
对pymysql的二次封装，让你免去写sql语句的麻烦（仅适用于Python3.5）

## 如何使用
- 1 第一步：连接数据库

```
# 直接连接 
mysql = MySQL()
if not mysql.connect(host, user, password, database):
    print('数据库连接失败，错误原因：', mysql.error)
```



