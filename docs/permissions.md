# WeFastAPI 权限管理

在 [we-fast-api](https://github.com/hekaiyou/we-fast-api) 项目中, 包含三种接口权限管理模式和一个白名单机制:

- 开放式接口 *(直接访问)*
- 无权限接口 *(登录后可以访问)*
- 有权限接口 *(用户角色有对应权限才能访问)*
- 白名单机制 *(指定的IP或网段可以直接访问除核心接口外的其他接口)*

这些模式和机制不需要额外的开发, 只需要简单的配置就可以实现。

## 开放式接口

在模块接口文件 *(api_xxx.py)* 中, 为接口访问路径的最后添加一层 `open/` 路径, 就可以使接口不受任何限制的被请求:

```python
from fastapi import APIRouter

router = APIRouter(prefix='/items', )

@router.get('/open/', summary='第一个接口 (开放)', )
async def read_hello():
    return {'message': 'Hello World'}
```

访问接口路径, 将看到如下的 JSON 响应:

```json
{"message":"Hello World"}
```

## 无权限接口

在模块接口文件 *(api_xxx.py)* 中, 为接口访问路径的最后添加一层 `free/` 路径, 只要用户完成登录, 不需要额外分配角色权限, 就可以请求该接口:

```python
from fastapi import APIRouter, Depends
from apis.bases.models import UserGlobal
from apis.bases.api_me import read_me_info

router = APIRouter(prefix='/items', )

@router.get('/free/', summary='第一个接口 (无权限)', )
async def read_hello(user: UserGlobal = Depends(read_me_info)):
    return {'message': f'Hello {user.username}'}
```

访问接口路径, 将看到如下的 JSON 响应:

- 用户没有登录
   ```json
   {"detail": "未认证"}
   ```
- 用户已完成登录
   ```json
   {"message": "Hello admin"}
   ```

如果不是需求如此, 不建议将接口设置为无权限接口, 推荐将接口权限分配给包含 **Default** 角色在内的全部角色, 这样虽然麻烦但利于接口的管理。

## 有权限接口

与前面两者不同, 常规的有权限接口不需要在访问路径上添加 *(但是应该避免使用 `open` 和 `free` 作为路径层级)* 内容:

```python
from fastapi import APIRouter, Depends
from apis.bases.models import UserGlobal
from apis.bases.api_me import read_me_info

router = APIRouter(prefix='/items', )

@router.get('/', summary='第一个接口', )
async def read_hello(user: UserGlobal = Depends(read_me_info)):
    return {'message': f'Hello {user.username}'}
```

而是通过访问 [轻前端站点](http://127.0.0.1:8083/) 创建角色、设置角色权限, 然后为用户分配角色。

访问接口路径, 将看到如下的 JSON 响应:

- 用户没有登录
   ```json
   {"detail": "未认证"}
   ```
- 用户已完成登录, 未分配角色及其权限
   ```json
   {"detail": "无 第一个接口 权限"}
   ```
- 用户已完成登录, 已分配角色及其权限
   ```json
   {"message": "Hello admin"}
   ```

## 白名单机制

如果需要让某个网段或主机直接调用模块的有权限接口，可以通过配置白名单来实现，以 “119.75.217.109” 这个 IP 地址为例:

- `TOKEN_EXEMPT_IP=["119.75.217"]` : 来自该网段的 IP 都放行
- `TOKEN_EXEMPT_HOST=["119.75.217.109"]` : 来自该主机的 IP 都放行

| 环境变量 | 描述 | 类型 | 默认值 |
| ------- | ------- | ------- | ------- |
| TOKEN_EXEMPT_IP | 令牌豁免 IP 网络列表 (前面3段) | list | [] |
| TOKEN_EXEMPT_HOST | 令牌豁免 IP 主机列表 (完整4段) | list | [] |

在开发和测试阶段，可以通过访问 [轻前端站点](http://127.0.0.1:8083/) 的参数设置页面，选择 **模块 bases 相关变量** 来配置 *令牌豁免 IP 网络列表 (前面3段)* 或者 *令牌豁免 IP 主机列表 (完整4段)* 环境变量。

在发布阶段，则需要在 `apis/bases/.env` 配置文件中，直接配置 *TOKEN_EXEMPT_IP* 或者 *TOKEN_EXEMPT_HOST* 环境变量:

```bash
TOKEN_EXEMPT_IP=["119.75.217"]
TOKEN_EXEMPT_HOST=["119.75.217.109"]
```

需要注意的是，为防止白名单访问篡改关键数据，限制了白名单不能访问除 `/api/bases/logs/` 以外的任何 `/api/bases/` 开头的接口。
