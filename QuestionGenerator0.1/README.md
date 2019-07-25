# Questions

## 打包方法
python setup.py sdist bdist_wheel 生成的包QuestionGenerator-x.y-py3-none-any.whl 在dist文件夹下

## 包的安装方法：
包可以通过whl文件安装。 注意在需要使用这个包的虚拟环境中安装。

pip install QuestionGenerator-1.0-py3-none-any.whl

## 卸载已安装的包
pip uninstall QuestionGenerator

## 创建虚拟环境
environment.yaml 用来创建虚拟环境

## 创建conda虚拟环境
在 environment.yaml 所在文件夹中使用命令： conda env create -f environment.yaml

## 删除虚拟环境
conda remove -n dbserver --all