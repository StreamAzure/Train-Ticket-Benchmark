#!/bin/bash

# 指定要复制的文件名
file_to_copy="apache-skywalking-java-agent-9.2.0.tgz"

# 检查要复制的文件是否存在
if [[ ! -f "$file_to_copy" ]]; then
  echo "Error: File '$file_to_copy' does not exist."
  exit 1
fi

# 遍历当前目录下的所有子目录
find . -type d | while read -r dir; do
  # 检查子目录中是否存在 pom.xml 文件
  if [[ -f "$dir/pom.xml" ]]; then
    # 复制指定的文件到子目录
    echo "Copying $file_to_copy to $dir"
    cp "$file_to_copy" "$dir"
  fi
done

echo "Finished copying files."
