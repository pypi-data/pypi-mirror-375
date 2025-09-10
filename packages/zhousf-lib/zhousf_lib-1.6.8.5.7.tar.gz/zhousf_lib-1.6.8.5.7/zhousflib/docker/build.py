# -*- coding: utf-8 -*-
# @Author  : zhousf
# @Function:

import os


class DockerBuild:

    def __init__(self, docker_hub_domain: str = None, docker_hub_namespace: str = None):
        self.docker_hub_domain = docker_hub_domain
        self.docker_hub_namespace = docker_hub_namespace
        self.docker_hub_url = f"{docker_hub_domain}/{docker_hub_namespace}" if docker_hub_domain and docker_hub_namespace else None
        pass

    def login(self, username: str, password: str):
        self.__command(f"docker login -u {username} -p {password} {self.docker_hub_domain}",
                       command_tip="登录docker仓库")
        return self

    @staticmethod
    def __command(command: str, command_tip: str):
        print(f"正在{command_tip}...")
        print(command)
        ret = os.system(command)
        assert ret == 0, f"{command_tip}失败: {ret}"
        print(f"{command_tip}成功")

    def build_image(self, dockerfile: str, name: str, version: str, command_tip: str, push=False):
        image_name = f"{name}:{version}"
        self.__command(command=f"docker build --network=host -f {dockerfile} -t {image_name} .", command_tip=command_tip)
        if self.docker_hub_url and push:
            self.push_image(image_name)
        return self

    def build_image_compose(self, docker_compose_file: str, command_tip: str, name: str = None, version: str = None, push=False):
        """
        构建镜像
        :param docker_compose_file:
        :param command_tip:
        :param name:
        :param version:
        :param push:
        :return:
        """
        self.__command(command=f"docker-compose -f {docker_compose_file} build", command_tip=command_tip)
        if self.docker_hub_url and push:
            image_name = f"{name}:{version}"
            self.push_image(image_name)
        return self

    def start_image_compose(self, docker_compose_file: str, command_tip: str):
        """
        启动容器
        1. -d 后台运行
        :param docker_compose_file:
        :param command_tip:
        :return:
        """
        self.__command(command=f"docker-compose -f {docker_compose_file} up -d", command_tip=command_tip)
        return self

    def stop_image_compose(self, docker_compose_file: str, command_tip: str):
        """
        停止容器
        :param docker_compose_file:
        :param command_tip:
        :return:
        """
        self.__command(command=f"docker-compose -f {docker_compose_file} down", command_tip=command_tip)
        return self

    def show_logs_image_compose(self, docker_compose_file: str, command_tip: str):
        """
        实时查看日志
        :param docker_compose_file:
        :param command_tip:
        :return:
        """
        self.__command(command=f"docker-compose -f {docker_compose_file} logs -f", command_tip=command_tip)
        return self

    def restart_image_compose(self, dockerfile: str, command_tip: str):
        """
        重启容器
        :param dockerfile:
        :param command_tip:
        :return:
        """
        self.__command(command=f"docker-compose -f {dockerfile} restart", command_tip=command_tip)
        return self

    def show_container_status(self, docker_compose_file: str, command_tip: str):
        """
        查看容器状态
        :param docker_compose_file:
        :param command_tip:
        :return:
        """
        self.__command(command=f"docker-compose -f {docker_compose_file} ps", command_tip=command_tip)
        return self

    def go_into_container(self, container_name: str, command_tip: str):
        self.__command(command=f"docker exec -it {container_name} bash", command_tip=command_tip)
        return self

    def pull_image(self, tag: str, command_tip: str):
        self.__command(command=f"docker pull {self.docker_hub_url}/{tag}", command_tip=command_tip)
        return self

    def push_image(self, current_image_name: str, tag_image_name: str = None):
        """
        推送镜像
        :param current_image_name: 当前镜像名称（包括版本号）
        :param tag_image_name: 给镜像打标签（包括版本号），即重命名，默认空
        :return:
        """
        if self.docker_hub_url:
            if tag_image_name is None:
                self.__command(command=f"docker tag {current_image_name} {self.docker_hub_url}/{current_image_name}", command_tip="镜像打标签")
                self.__command(command=f"docker push {self.docker_hub_url}/{current_image_name}", command_tip="推送镜像")
            else:
                self.__command(command=f"docker tag {current_image_name} {self.docker_hub_url}/{tag_image_name}", command_tip="镜像打标签")
                self.__command(command=f"docker push {self.docker_hub_url}/{tag_image_name}", command_tip="推送镜像")
        return self


if __name__ == "__main__":
    _docker_hub_domain = "packages.xxx.com"
    _docker_hub_namespace = "docker-xxx"
    # _docker_hub_domain = "registry.cn-beijing.aliyuncs.com"
    # _docker_hub_namespace = "zhousf-ai"
    build = (DockerBuild(docker_hub_domain=_docker_hub_domain, docker_hub_namespace=_docker_hub_namespace)
             # .pull_image(tag="nvidia/cuda:11.3.1-cudnn8-devel-ubuntu20.04", command_tip="拉取基础镜像")
             # .pull_image(tag="registry.baidubce.com/paddlepaddle/paddle:2.3.1-gpu-cuda11.2-cudnn8 ", command_tip="拉取基础镜像")
             # .pull_image(tag="nvidia/cuda:11.6.1-cudnn8-runtime-ubuntu20.04", command_tip="拉取基础镜像")
             # .build_image(docker_compose_file="Dockerfile_env_cpu", name="zhousf_fd_py39_cpu", version="1.0.7", push=False, command_tip="构建环境镜像")
             # .build_image(docker_compose_file="Dockerfile_env_gpu", name="zhousf_fd_py39_cuda11.6.1-cudnn8", version="1.0.7", push=False, command_tip="构建环境镜像")
             .push_image(current_image_name="pdf_omni:web_py3.10_cuda11.8_cudnn8.6_v0.3.2")
             # .push_image(current_image_name="pdf_omni:env_py3.10_cuda11.8_cudnn8.6_v0.3")
             # .push_image(current_image_name="zhousf_fd_py39_cuda11.6.1-cudnn8:1.0.7", tag_image_name="fast_infer:py3.9_cuda11.6.1_cudnn8_v1.0.7")
             # .build_image(docker_compose_file="Dockerfile_pro", name="zhousf_image_classify_gpu", version="0.1", push=True, command_tip="构建工程镜像")
             )
