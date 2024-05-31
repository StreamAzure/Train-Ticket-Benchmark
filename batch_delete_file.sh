#!/bin/bash

# 指定要删除的文件名
TARGET_FILE="apache-skywalking-java-agent-9.2.0.tgz"

# 遍历以 ts- 开头的所有子目录
for dir in ts-*/; do
    # 检查子目录是否存在指定的文件
    if [ -e "${dir}${TARGET_FILE}" ]; then
        # 删除指定的文件
        rm "${dir}${TARGET_FILE}"
        echo "Deleted ${dir}${TARGET_FILE}"
    fi
done
