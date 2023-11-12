# grpc python 插件

https://grpc.io/docs/languages/python/basics/

https://github.com/jacquev6/Pyrraform/blob/9f401a35120ddf05e98b72e66ed81280b9feb8c8/Pyrraform/plugin.py#L140

## python 环境

在 windows 下的安装

```sh
D:\Python\Python311\python -m pip install --upgrade pip

D:\Python\Python311\python -m venv venv

.\venv\Scripts\Activate.ps1

.\venv\Scripts\python -m pip install -r requirements.txt

```

## 安装生成工具

安装 yao 的 protofu

```sh
python -m grpc_tools.protoc -I ./protos --python_out=./model --pyi_out=./model --grpc_python_out=./model ./protos/model.proto
python -m grpc_tools.protoc -I ./protos --python_out=./plugin --pyi_out=./plugin --grpc_python_out=./plugin ./protos/grpc_controller.proto

```

## 生成 exe 或是 dll

不能直接使用 python 脚本作为插件，需要转换成二进制文件，可以使用 pyinstaller 或是使用 golang 作一个调用器。

```sh
pyinstaller .\myplugin.py -F

#或是使用golang作一个封装
go build -o myplugin.dll .\myplugin.go

```

## 测试

```sh
yao run plugins.myplugin.hell

```
