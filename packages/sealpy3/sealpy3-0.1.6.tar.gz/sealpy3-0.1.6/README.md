## 简介

使用cythonize将python代码一键加密为so或pyd。支持单个文件加密，整个项目加密。
(seal your pyfiles or project by using cythonize.)

Git仓库地址: https://github.com/limoncc/sealpy.git

## 安装

```shell
pip install sealpy3
```
    

## 使用方法

使用参数
```shell
sealpy -i "xxx project dir" [-o output dir]
```

加密后的文件默认存储在 dist/project_name/ 下

使用配置文件

```
; 工作目录下的./.sealpy.cfg
[sealpy]
; the file that will be compiled
paths = test
; files that are ignored at compile time. If an empty string is not used, multiple files and folders are separated by commas
ignores = ''
; The build directory
build_dir = build
; If there is an entry file, it needs to be specified to exclude compilation
main_py = main.py
```

运行命令
```shell
sealpy build
```


