import os
import sys

PREFIX = "stream" # 镜像名前缀
VERSION = "one-database" # 镜像版本号

base_path = os.getcwd()
build_paths = []

def mvn_build():
    """
    1. maven 编译生成所有模块的 jar 包
    """
    mvn_status = os.system("mvn clean package -DskipTests")
    return mvn_status == 0

def init_docker_build_paths():
    """
    2. 获取各个模块的绝对路径
    """
    list_paths = os.listdir(os.getcwd())
    for p in list_paths:
        if os.path.isdir(p):
            if(p.startswith("ts-")):
                build_path=base_path + "/" + p
                build_paths.append(build_path)

def docker_build():
    """
    3. 根据各模块目录下的 dockerfile 构建镜像
    """
    total = len(build_paths)
    failed_images = []
    for build_path in build_paths:
        image_name = build_path.split("/")[-1]
        # 镜像名即模块目录名，如 ts-station-service

        os.chdir(build_path)
        # 将上级目录的 apache-skywalking-java-agent-9.1.0.tgz 拷贝到当前目录
        os.system(f"cp ../apache-skywalking-java-agent-9.1.0.tgz {build_path}")

        files = os.listdir(build_path)
        
        # # 逐个模块构建镜像
        if "Dockerfile" in files:
            docker_build = os.system(f"docker build . -t {PREFIX}/{image_name}:{VERSION}")
            # e.g. stream/ts-station-service:1.0
            if docker_build != 0:
                print(f"[FAIL] {image_name} build failed.")
                failed_images += image_name
            else:
                print(f"[SUCCESS] {image_name} build success.")
            # [FAIL] ts-avatar-service build failed.
        # 删除当前目录下的 apache-skywalking-java-agent-9.2.0.tgz
    
    print("\nAll building is done.")
    print(f"Total: {total}, Success: {total - len(failed_images)}, Failed: {len(failed_images)}")
    if len(failed_images) > 0:
        print("Building Failed: ", failed_images)

def after_clean():
    for build_path in build_paths:
        print(build_path)
        os.system(f"rm {build_path}/apache-skywalking-java-agent-9.1.0.tgz")

if __name__ == '__main__':
    if not mvn_build():
        print("mvn build failed")
        exit(1)
    init_docker_build_paths()
    docker_build()
    # after_clean()