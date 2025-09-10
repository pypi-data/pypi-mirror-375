# Coding平台MCP服务

这是一个用于Coding平台的MCP（Model Context Protocol）服务，提供需求查询功能。

## 功能特性

- ✅ 查询Coding平台需求列表
- ✅ 支持多项目查询
- ✅ 可配置的分页和排序
- ✅ 环境变量配置

## 安装依赖

```bash
pip install -e .
```

## 环境变量配置

### 方法1：临时设置（当前终端会话）
```bash
# 设置必需的API访问令牌
export CODING_API_TOKEN="6ba7fa74ec2af91139e56a84960068b5c984b20a"

# 设置可选配置
export CODING_DEFAULT_PROJECT="gypaas"
export CODING_DEFAULT_LIMIT="10"

# 验证设置
echo "API Token: $CODING_API_TOKEN"
```

### 方法2：永久设置（推荐）
将环境变量添加到shell配置文件中（~/.bashrc, ~/.zshrc, 或 ~/.profile）：

```bash
# 编辑配置文件
nano ~/.zshrc

# 添加以下内容
export CODING_API_TOKEN="your_actual_coding_api_token"
export CODING_DEFAULT_PROJECT="your_project_name"
export CODING_DEFAULT_LIMIT="10"
export CODING_API_BASE_URL="https://it.devops.sinochem.com/open-api/"

# 重新加载配置
source ~/.zshrc
```

### 方法3：使用.env文件（推荐）
服务已配置为自动加载`.env`文件中的环境变量：

```bash
# 1. 安装python-dotenv（如果尚未安装）
pip install python-dotenv

# 2. 复制示例文件
cp .env.example .env

# 3. 编辑.env文件，填写实际值
nano .env

# 4. 启动服务（自动加载.env配置）
python main.py
```

**优势**：
- ✅ 配置与代码分离，更安全
- ✅ 无需手动设置环境变量
- ✅ 支持版本控制（可将.env.example提交到版本库）
- ✅ 多环境支持（开发、测试、生产使用不同的.env文件）

**.env文件示例**：
```bash
# 必需配置
CODING_API_TOKEN=your_actual_coding_api_token

# 可选配置  
CODING_DEFAULT_PROJECT=your_project_name
CODING_DEFAULT_LIMIT=10
```

### 方法4：脚本设置
使用提供的设置脚本：

```bash
# 修改setup_test_env.sh中的token值
nano setup_test_env.sh

# 运行设置脚本
source setup_test_env.sh

# 验证环境变量
env | grep CODING
```

### 环境变量说明

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `CODING_API_TOKEN` | ✅ | 无 | Coding平台API访问令牌 |
| `CODING_API_BASE_URL` | ❌ | `https://it.devops.sinochem.com/open-api/` | API基础URL |
| `CODING_DEFAULT_PROJECT` | ❌ | `gypaas` | 默认项目名称 |
| `CODING_DEFAULT_LIMIT` | ❌ | `10` | 默认查询条数 |
| `CODING_ISSUE_TYPE` | ❌ | `ALL` | 需求类型（ALL/REQUIREMENT/BUG/TASK） |
| `CODING_OFFSET` | ❌ | `0` | 分页偏移量 |
| `CODING_SORT_KEY` | ❌ | `CODE` | 排序字段 |
| `CODING_SORT_VALUE` | ❌ | `DESC` | 排序方式 |

## 使用方法

### 作为MCP服务器运行

```bash
python main.py
```

### 通过MCP客户端连接

配置你的MCP客户端（如Claude、Cursor等）连接到这个服务：

```json
{
  "mcpServers": {
    "coding-service": {
      "command": "python",
      "args": ["/path/to/main.py"]
    }
  }
}
```

## API说明

### get_requirements工具

查询Coding平台的需求列表：

- **参数**:
  - `project_name`: 项目名称（可选，默认为环境变量配置）
  - `limit`: 查询条数限制（可选，默认为环境变量配置）

- **返回**: 包含需求列表的JSON响应

## 开发说明

项目使用Python 3.13+，主要依赖：
- `mcp[cli]`: MCP协议实现
- `requests`: HTTP请求库

## 故障排除

1. **API令牌错误**: 确保`CODING_API_TOKEN`环境变量已正确设置
2. **网络连接问题**: 检查是否能访问Coding平台API
3. **权限问题**: 确认API令牌有足够的权限访问需求数据