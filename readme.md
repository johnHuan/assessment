# 消防环卫评估平台
Tips: 本项目依赖于arcgis，部署之前请自行安装 Arcgis

## 安装步骤
> 通过pip执行requirements.txt即可)
```shell
$ pip install -r ./requirements.txt
```

**项目结构**
```markdown
assessment
    |--code
    |--|--configs.yaml  # 修改这个配置文件里的路径
    |--|--info.json     # 修改这个配置文件里的路径
    |--|--index.py      # 执行这个入口文件
```
> 安装完成并执行了index.py 后项目会创建一个服务器，在浏览器端输入下列地址进入项目
> 
> http://127.0.0.1:5000
