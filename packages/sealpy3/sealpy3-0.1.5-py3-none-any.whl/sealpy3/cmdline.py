import os
import sys
import getopt
import configparser

from sealpy3.seal_py import start_encrypt


def usage():
    """
python代码 加密|加固
参数说明：
    build                     使用当前目录下的 .sealpy3.cfg 配置文件
    -i | --input_file_path    待加密文件或文件夹路径，可是相对路径或绝对路径
    -o | --output_file_path   加密后的文件输出路径，默认在input_file_path下创建dist文件夹，存放加密后的文件
    -I | --ignore_files       不需要加密的文件或文件夹，逗号分隔
    -m | --except_main_file   不加密包含__main__的文件(主文件加密后无法启动), 值为0、1。 默认为1
    -c | --conf               使用配置文件传递参数，配置文件路径。如果指定了配置文件，则忽略其他命令行参数。
    """


def load_config(config_path):
    """从配置文件中加载参数"""
    config = configparser.ConfigParser()
    config.read(config_path)
    # .sealpy.cfg
    # [sealpy]
    # ; 将被编译的文件
    # paths = package_a
    # ; 编译时忽略的文件
    # ignores = setup.py
    # ; The build directory
    # build_dir = build
    # main_py = main.py
    params = {}
    if 'sealpy' in config:
        params['input_file_path'] = config['sealpy'].get('paths', '')
        params['output_file_path'] = config['sealpy'].get('build_dir', '')
        params['ignore_files'] = config['sealpy'].get('ignores', '').split(',')
        params['except_main_file'] = config['sealpy'].getint('main_py', "main.py")
    
    return params


def execute():
    try:
        is_config_path = False
        options, args = getopt.getopt(
            sys.argv[1:],
            "hi:o:I:m:c:",
            [
                "help",
                "input_file_path=",
                "output_file_path=",
                "ignore_files=",
                "except_main_file=",
                "conf=",
            ],
        )
        print(args)
        for name in args:
            if name in ("-c", "--conf"):
                is_config_path = True
        
        print(is_config_path)
        # 检查是否有 build 参数
        if len(sys.argv) > 1 and sys.argv[1] == "build" and not is_config_path:
            # 自动使用当前目录下的 .sealpy3.cfg 文件
            current_dir = os.getcwd()
            config_path = os.path.join(current_dir, ".sealpy.cfg")
            if not os.path.exists(config_path):
                print(f"未找到配置文件: {config_path}")
                sys.exit(1)
            
            # 从配置文件中加载参数
            config_params = load_config(config_path)
            input_file_path = config_params.get('input_file_path', '')
            output_file_path = config_params.get('output_file_path', '')
            ignore_files = config_params.get('ignore_files', [])
            except_main_file = config_params.get('except_main_file', "main.py")
            
            # 执行加密
            start_encrypt(input_file_path, output_file_path, ignore_files, except_main_file)
            
            sys.exit(0)
        
        input_file_path = output_file_path = ignore_files = ""
        except_main_file = 1
        config_path = ""
        
        # 先检查是否有配置文件参数
        for idx, name in enumerate(args):
            if name in ("-c", "--conf"):
                config_path = args[idx + 1]
                break
        
        # 如果指定了配置文件，则完全从配置文件中加载参数
        if config_path:
            config_params = load_config(config_path)
            input_file_path = config_params.get('input_file_path', '')
            output_file_path = config_params.get('output_file_path', '')
            ignore_files = config_params.get('ignore_files', [])
            except_main_file = config_params.get('except_main_file', 1)
        else:
            # 检查必填参数
            if not input_file_path:
                print("需指定-i 或 input_file_path，或通过配置文件传递参数")
                print(usage.__doc__)
                sys.exit()
            # 如果没有指定配置文件，则从命令行参数中读取
            for name, value in options:
                if name in ("-h", "--help"):
                    print(usage.__doc__)
                    sys.exit()
                
                elif name in ("-i", "--input_file_path"):
                    input_file_path = value
                
                elif name in ("-o", "--output_file_path"):
                    output_file_path = value
                
                elif name in ("-I", "--ignore_files"):
                    ignore_files = value.split(",")
                
                elif name in ("-m", "--except_main_file"):
                    except_main_file = int(value)
        
        start_encrypt(input_file_path, output_file_path, ignore_files, except_main_file)
    
    except getopt.GetoptError:
        print(usage.__doc__)
        sys.exit()


if __name__ == "__main__":
    execute()