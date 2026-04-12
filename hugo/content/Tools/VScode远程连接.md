+++
course = "CSDS"
date = 2025-06-18T18:26:21+08:00
draft = false
tags = ["技巧工具"]
title = "VScode远程连接"
+++

### 使用完整的VSCode桌面版启用隧道

此方法需首先在远程服务器上安装完整的VSCode桌面版，具体启用方法如下。  
在远程服务器上的VSCode账户菜单中，选择“Turn on Remote Tunnel Access”选项。

[![](https://img2023.cnblogs.com/blog/1437865/202311/1437865-20231109083744188-1547550133.png)](https://img2023.cnblogs.com/blog/1437865/202311/1437865-20231109083744188-1547550133.png)

此方法同样会获得一个与此远程服务器相关联的vscode.dev URL。

## 在本地客户端连接安全隧道

点击左侧的扩展按钮(或用 Ctrl+Shift+X)，搜索插件`Remote - Tunnels`进行安装

[![](https://img2023.cnblogs.com/blog/1437865/202311/1437865-20231109083807468-2040033700.png)](https://img2023.cnblogs.com/blog/1437865/202311/1437865-20231109083807468-2040033700.png)

按照下方提示登录GitHub查看注册的隧道
已经为乐宝注册好了 Github 账号
EloiseBabe
L5VGfP4ky9cRQXC

[![](https://img2023.cnblogs.com/blog/1437865/202311/1437865-20231109083827498-248586091.png)](https://img2023.cnblogs.com/blog/1437865/202311/1437865-20231109083827498-248586091.png)

按照下方提示即可连接到远程服务器

[![](https://img2023.cnblogs.com/blog/1437865/202311/1437865-20231109083848838-782567713.png)](https://img2023.cnblogs.com/blog/1437865/202311/1437865-20231109083848838-782567713.png)