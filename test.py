import os
import re

# 1. 查找子目录中的所有application.yml文件
def find_yml_files(directory):
    yml_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'application.yml' or file == 'application.yaml':
            # if file.endswith('.yml'):
                yml_files.append(os.path.join(root, file))
    return yml_files

# 2. 识别文件中的jdbc语句部分，并提取其中的值
def extract_jdbc_info(yml_file_path):
    with open(yml_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 使用正则表达式匹配jdbc语句
    pattern = re.compile(r'url:\s?jdbc:mysql://\${[A-Z_\d]+_MYSQL_HOST:(ts)}:\${\w+:3306}/\${[A-Z_\d]+_MYSQL_DATABASE:([a-z-]+)}\?.*')
    match = pattern.search(content)
    
    if match:
        host_value = match.group(1)
        db_value = match.group(2)
        
        return host_value, db_value
    else:
        return None, None

# 3. 将两个值位置互换，并更新文件内容
def swap_jdbc_values(yml_file_path, host_value, db_value):
    with open(yml_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 构建新的jdbc语句
    pattern = re.compile(r'url:\s?jdbc:mysql://(\${[A-Z_\d]+_MYSQL_HOST):(ts-[a-z-\d]+-mysql}):(\${\w+:3306})/(\${[A-Z_\d]+_MYSQL_DATABASE):([a-z]+})\?(.*)')
    match = pattern.search(content)
    origin_str = match.group()
    database_str = match.group(1)
    db_value = match.group(2)
    port_str = match.group(3)
    host_str = match.group(4)
    host_value = match.group(5)
    other_str = match.group(6)

    # print(f"{origin_str}")    
    new_jdbc_statement = f'url: jdbc:mysql://{database_str}:{host_value}:{port_str}/{host_str}:{db_value}?{other_str}'
    # print(new_jdbc_statement)   
    # 替换原始jdbc语句    
    new_content = re.sub(pattern, new_jdbc_statement, content)
    # print(new_content)
    # 将更新后的内容写回文件    
    with open(yml_file_path, 'w', encoding='utf-8') as file:        
        file.write(new_content)
        
# 主函数
def main():    
    directory = input("请输入要搜索的目录路径：")    
    yml_files = find_yml_files(directory)
    cnt = 0
    dbs = []
    for yml_file in yml_files:        
        host, db = extract_jdbc_info(yml_file)
        if(db != None):
            dbs.append(db)         
    with open('init.sql', 'w') as f:
        for db in dbs:
            f.write(f"CREATE DATABASE IF NOT EXISTS {db};\n")
        
            
if __name__ == "__main__":    
    main()