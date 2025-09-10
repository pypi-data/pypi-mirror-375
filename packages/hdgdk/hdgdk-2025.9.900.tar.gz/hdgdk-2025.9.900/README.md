# HD-Python模块

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

HD引擎的Python调用模块，提供丰富的Windows平台自动化控制功能，包括窗口操作、键鼠模拟、图像识别、内存读写等功能接口。

## 功能特性

HD-Python模块为Windows应用程序自动化提供了全面的功能支持：

- **环境管理**：DLL加载、调试模式设置、环境初始化
- **窗口操作**：窗口查找、窗口控制、多开管理
- **键鼠模拟**：键盘输入、鼠标控制、组合操作
- **图像识别**：截图、识图、识字、智能识图
- **内存操作**：内存读写、进程内存管理
- **系统功能**：HOOK、注入、汇编执行、多线程支持
- **网络功能**：IP操作、网络通讯
- **UI自动化**：内置浏览器控制、UI元素识别
- **高级功能**：YOLOV图像识别、黑屏模式、主板机控制

## 安装

### 使用pip安装（推荐）

```bash
pip install hdgdk -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install hdgdk
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/HD-Python.git
cd HD-Python

# 安装依赖
pip install -r requirements.txt

# 安装模块
pip install -e .
```

## 快速开始

以下是使用HD-Python模块的基本流程：

```python
from HD import *
HD_Path("./HDDebug64.dll")
HD环境_调试模式(True)
ret = HD登录_登录("你的账号","你的密码")
print("HD登录_登录",ret)
```
## 更新日志
hdgdk 2025.9.9  
优化封装修复了一些已知问题
hdgdk 2025.9.801   
```txt
1.优化yolo综合工具*
2.火山 易语言 Python 炫语言 模块更新*
3.修复多点偏移找色的实时绘制*
4.增加组件panddle-ocr V5 接口 和 相关工具-序号7*
-HCPOCR_AddModel
-HCPOCR_Identify
-HCPOCR_IdentifyByFile
-HCPOCR_IdentifyByMem
-HCPOCR_GetLastError
-HCPOCR_Close
-智能识字-*
-训练工具-*
-标注工具-*
5.优化内存池-防止几十开导致内存不足*
6.优化综合工具-方便操作*
7.优化实时绘制当进程消失自动关闭和仅单开*
8.优化下安装方式1的返回值*
9.增加保护盾增强版-序号8*
-HCHDVTPP_OnProtect
-HCHDVTPP_OffProtect
-HCHDVTPP_OnCapture
-HCHDVTPP_ReadBytes
-HCHDVTPP_WriteBytes
10.综合工具优化开发文档页面*
11.兼容可定制C++ 无导出接口DLL版本-防止检查(仅C++)*
12.优化开发文档线上版本*
13.移除大部分代码警告-类型转换显示转换*
14.增加15个预留空位驱动组件序号-以便后面热更新*
-10~14:预留HD版本1档空位 0.2*0.7 共5个*
-15~19:预留HD版本2档空位 0.3*0.7 共5个*
-20~24:预留HD版本3档空位 0.5*0.7 共5个*
15.综合工具优化界面布局*
16.优化驱动加载验证-必须登录成功-才能加载驱动*
17.优化后台键鼠绑定中消息拦截机制X86X64*
18.增加几个错误值*
-#define LOGINERROR_版本异常  -2700
-#define ERROR_窗口数量上限 -1243//只能开启一个 比如实时绘制窗口一个就行
-#define ERROR_释放失败 -1244  //释放失败
19.HD升级工具6.0版本发布*
20.优化版本识别和校验*
21.HD后台系统增加微信自动充值-备注写上需要充值的账号*
```

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

感谢所有为HD-Python模块开发和维护做出贡献的开发者！