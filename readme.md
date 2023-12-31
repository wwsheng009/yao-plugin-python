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

## 插件使用 方法一

嵌入式 grpc 服务。

这种方法是由 yao 框架来管理插件的生命周期：

在 yao 应用加载时，会自动的调用插件程序，或者说启动器，启动器再启动 grpc 服务器。

在 yao 应用退出时，会通过 grpc 通讯，调用插件的 GRPCController.Shutdown 的方法，自动即出 grpc 服务。

在这种方法下，需要一个启动器程序，比如是 exe 或是 dll，不能直接使用 python 脚本作为插件，需要转换成二进制文件，可以使用 pyinstaller 或是使用 golang 作一个调用器。

```sh
pyinstaller .\myplugin.py -F

#或是使用golang作一个封装
go build -o myplugin.dll .\myplugin.go



```

## 测试

```sh
yao run plugins.myplugin.hell

```

## 方法二：

分离式 grpc 插件。

分离式插件，yao 应用服务与 grpc 分开，在 yao 启动时，只需要启动器程序返回 grcp 的端口，通讯协议即可，grpc 服务额外单独启动。

```go
//grpc 插件通讯协议，由至少4个参数组成，并且使用|分隔
// CoreProtocolVersion,核心协议版本，目前是1，固定的，跟程序本身的版本有关
// protoVersion,协议版本,yao使用的是 1 ，服务器与客户端通讯的版本需要一样。
// tcp 网络协议
// 127.0.0.1:1234 网络地址
// grpc 协议类型，可选netgrpc,grpc，yao使用的是grpc
// serverCert 服务器证书,不需要

// 返回grpc的端口通讯协议即可
fmt.Println("1|1|tcp|127.0.0.1:1234|grpc")
```

```sh
go build -o py.dll .\py.go
```

同时，在这种场景下不要 grpc 服务不要响应 GRPCController.Shutdown 的方法。

```sh
yao run plugins.py.hello world
```

## text embedding

use the offline model for text embedding

```sh
pip install torch text2vec
```

```py

from text2vec import SentenceModel
# 自动下载并加载模型
model = SentenceModel('shibing624/text2vec-bge-large-chinese')
sentence = '这里是你想编码的文本输入'
vec = model.encode(sentence)
```
