# 阿里云部署指南

本文面向阿里云轻量应用服务器（Lightweight Application Server），目标是把
Capital Market Simulator 部署成公网可访问的网页版。

## 1. 购买服务器

在阿里云控制台购买“轻量应用服务器”，推荐配置：

- 地域：华东（杭州）或华南（深圳），离你的用户近即可
- 镜像：Ubuntu 24.04（或 22.04）
- 规格：2 vCPU / 2 GB 内存起步，40 GB 磁盘足够
- 计费：按月或按年，新用户通常有优惠

购买时设置 root 密码，密码要足够复杂，后续 SSH 登录用。

## 2. 开放端口

在轻量服务器控制台的“防火墙”里放行：

- `22`：SSH 登录（默认已开）
- `8000`：游戏网页

如果之后接域名和 HTTPS，再放行 `80` 和 `443`。

## 3. SSH 登录

两种方式任选：

- 阿里云控制台自带的“远程连接”网页终端，无需额外软件
- 本机终端：`ssh root@服务器公网IP`

## 4. 一键部署

登录服务器后执行：

```bash
curl -fsSL https://raw.githubusercontent.com/JawLinker/capital-market-sim/main/deploy/setup-aliyun.sh -o setup-aliyun.sh
sudo bash setup-aliyun.sh
```

脚本会自动安装 Docker、拉取项目、构建镜像并启动服务。部署完成后终端会
打印管理员密码，请保存好。

访问 `http://服务器公网IP:8000`，用 `host` 和打印的密码登录。

想自定义管理员密码，可以先设置环境变量再运行：

```bash
export CMS_HOST_PASSWORD=你的强密码
sudo -E bash setup-aliyun.sh
```

## 5. 更新代码

重新执行一次 `setup-aliyun.sh` 即可，脚本会拉取最新代码并重建容器，游戏数据
保留在 Docker 卷里不会丢失。

## 6. 可选：域名和 HTTPS

1. 买一个域名，在域名解析里加一条 A 记录指向服务器公网 IP
2. 在服务器防火墙放行 `80` 和 `443`
3. 用 Nginx 反代 `http://127.0.0.1:8000`，再用 Certbot 申请免费 HTTPS 证书

## 常见问题

**打不开网页**：确认服务器防火墙放行了 `8000`，且运行了 `docker compose ps` 查看容器状态。

**忘记管理员密码**：先停止容器，再删除 Docker 卷重新部署（会清空游戏数据），
或者运行 `docker compose exec` 进容器改数据库。

**访问太慢**：确认选的地域离用户近；国内用户不要选海外地域。
