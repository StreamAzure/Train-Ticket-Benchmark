import os
import re

def find_dockerfiles_and_process(root_dir):
    # 正则表达式匹配CMD指令和ENV指令
    cmd_pattern = re.compile(r'CMD \["java", "-Xmx200m",  "-jar", "/app/([^"]+)-1.0.jar')
    env_pattern = re.compile(r'^ENV SW_AGENT_NAME=')
    cnt = 0
    # 遍历当前目录及其子目录下的所有文件
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file == 'Dockerfile':
                # 构建完整的文件路径
                dockerfile_path = os.path.join(root, file)
                with open(dockerfile_path, encoding="gb18030") as df:
                    dockerfile_content = df.read()
                    
                    # 查找并提取jar文件名
                    cmd_match = cmd_pattern.search(dockerfile_content)
                    if cmd_match:
                        cnt += 1
                        jar_filename = cmd_match.group(1)
                        print(f'提取服务名: {jar_filename}')
                        
                        # 查找并修改ENV SW_AGENT_NAME指令
                        lines = dockerfile_content.split('\n')
                        modified = False
                        for i, line in enumerate(lines):
                            if env_pattern.match(line):
                                # 追加文本到ENV指令
                                line = line.split('=')
                                line[1] = jar_filename
                                line = line[0] + '=' + line[1]
                                print(line)
                                lines[i] = line
                                modified = True
                                break
                        if modified:
                            # 将修改后的内容写回Dockerfile
                            with open(dockerfile_path,'w',encoding="gb18030") as df:
                                df.write('\n'.join(lines))
                            print(f'Modified ENV instruction in {dockerfile_path}')
                        else:
                            print(f'No ENV SW_AGENT_NAME instruction found in {dockerfile_path}')
    print(f"共匹配 {cnt} 条")
# 从当前目录开始搜索Dockerfile
current_directory = os.getcwd()
find_dockerfiles_and_process(current_directory)