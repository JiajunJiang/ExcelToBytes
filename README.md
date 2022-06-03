# 表格导出工具

## 依赖库

pip install -r requirements.txt  
其中protobuf的版本可根据需求更改为3.X的任意版本

## 配置修改

config.yml 可以进行修改

#### client_language

#### server_language

可以进行客户端和服务器语言选择 支持 C++ C# Java Go Python php js kotlin obj-c

#### package_name

命名空间 所有语言都需要填写

#### java_package

仅java中使用 导出package目录结构有关

#### java_outer_classname

仅java使用 一般和package_name 一致即可

#### java_multiple_files

仅java使用 True则导出多文件 False则导出一个文件

#### optimize_for

仅java和C++使用 可选 SPEED CODE_SIZE LITE_RUNTIME 3种模式

#### cc_enable_arenas

仅C++使用 可优化内存并提高性能

#### objc_class_prefix

仅OBJ-C使用 用于前缀命名

#### client_file_ext

#### server_file_ext

分别代表客户端模式和服务器模式导出元数据的后缀名

## 使用方式参考

#### py main.py Monster.xlsx

导出Monster.xlsx

#### py main.py Monster.xlsx c

仅导出跟客户端数据有关的Monster.xlsx

#### py main.py Monster.xlsx s

仅导出跟服务器数据有关的Monster.xlsx

## 配置表规范

可参考Monster.xlsx  
![image](https://github.com/JiajunJiang/ExcelToBytes/blob/Master/Example.png)

#### 1.修改工作簿名字

这个名字将会是导出后的类名，工作簿名字中带有#或者带有Sheet将不会导出

#### 2.第一行为参数类型

可填 optional、repeated(数组)、map(键值对)

#### 3.第二行为参数类型

可填 int32 int64 uint32 uint64 sint32 sint64 fixed32 fixed64 sfixed32 sfixed64 float double bool string  
map类型可填2个类型以 , 分割


#### 4.第三行为参数类型

这个名字将会是导出后的参数名

#### 5.第四行为备注

本行可随意填写

#### 6.第五行为客户端和服务器标记

主要目的是部分服务器数据不用导出给客户端防止被反编译 部分客户端数据服务器可以不加载以此减少内存占用  
可填 c 导出客户端数据的时候导出此列  
可填 s 导出服务器数据的时候导出此列  
可填 cs 代表同时支持c或s

#### 7.默认第一列会主键

主键带有#的话表示注释 此行都不会导出

#### 8.repeated格式要求

repeated字段所属列 需要使用 ; 进行数据分割

#### 9.bool类型要求

bool 可使用快捷填法 1 = true 0 = false

## 自动归档

./Client/bin  
./Client/proto  
./Client/script  
./Server/bin   
./Server/proto  
./Server/script  
元数据目录  
proto协议目录  
脚本目录

## 打包指令

pyinstaller -F main.py
