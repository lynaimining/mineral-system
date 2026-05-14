# OpenClaw 老板任务监控配置指南

## 已完成的配置

✅ **Agent 创建成功**
- Agent ID: `boss-monitor`
- 名称: 老板任务助手 📋
- 模型: Claude Sonnet 4.6
- 工作空间: `C:\Users\39555\.openclaw\workspace-boss`
- 系统提示词: `C:\Users\39555\.openclaw\agents\boss-monitor\agent\CLAUDE.md`

✅ **Gateway 已重启**
- 新配置已生效

## 需要完成的最后步骤

### 方案一：通过微信实际交互配置路由（推荐）

由于 OpenClaw 的微信插件不支持通过联系人名称直接配置路由，需要通过实际的微信消息交互来获取"王选策师兄"的用户 ID，然后配置路由绑定。

**步骤：**

1. **让老板发一条测试消息**
   - 请王选策师兄发送一条测试消息到你的微信
   - 这条消息会被 OpenClaw 接收

2. **查看 OpenClaw 日志获取用户 ID**
   ```bash
   openclaw channels logs --channel openclaw-weixin --tail 50
   ```
   在日志中找到类似这样的信息：
   ```
   [openclaw-weixin] Message from user_id: wxid_xxxxxxxxxxxxx
   ```
   记录下这个 `user_id`

3. **配置路由绑定**
   ```bash
   openclaw agents bind --agent boss-monitor --bind "openclaw-weixin:default:wxid_xxxxxxxxxxxxx"
   ```
   将 `wxid_xxxxxxxxxxxxx` 替换为实际的用户 ID

4. **验证配置**
   ```bash
   openclaw agents bindings
   ```
   应该能看到 boss-monitor 的路由规则

### 方案二：修改配置文件（备选）

如果方案一不可行，可以直接修改 OpenClaw 的配置文件：

1. **编辑配置文件**
   ```bash
   code C:\Users\39555\.openclaw\openclaw.json
   ```

2. **在 `agents.list` 中找到 `boss-monitor` 配置，添加路由规则**
   ```json
   {
     "id": "boss-monitor",
     "name": "boss-monitor",
     "workspace": "C:\\Users\\39555\\.openclaw\\workspace-boss",
     "agentDir": "C:\\Users\\39555\\.openclaw\\agents\\boss-monitor\\agent",
     "model": "anthropic/claude-sonnet-4-6",
     "identity": {
       "name": "老板任务助手",
       "emoji": "📋",
       "theme": "专门处理王选策师兄交办的工作任务，零遗漏，自动调研"
     },
     "routing": {
       "bindings": [
         {
           "channel": "openclaw-weixin",
           "accountId": "default",
           "peerId": "wxid_xxxxxxxxxxxxx"
         }
       ]
     }
   }
   ```

3. **重启 Gateway**
   ```bash
   openclaw gateway restart
   ```

### 方案三：使用通配符路由（最简单但不精确）

如果只想让所有微信消息都由 boss-monitor 处理：

```bash
openclaw agents bind --agent boss-monitor --bind "openclaw-weixin:default"
```

**注意：** 这会让所有微信消息都转到 boss-monitor，不仅仅是老板的消息。

## 功能说明

配置完成后，当"王选策师兄"发送消息时，boss-monitor agent 会：

1. **立即确认** - 回复"收到！正在处理：[任务概括]"
2. **自动分类** - 识别任务类型（调研/文档/数据/安排/闲聊）
3. **执行处理** - 根据任务类型自动执行
4. **返回结果** - 发送处理结果到微信

### 支持的任务类型

- **调研类**：查一下、调研、了解、搜集、找找、看看市场、分析一下
- **文档撰写类**：写个、起草、拟一份、帮我写
- **数据查询类**：多少、什么价格、有没有数据
- **安排协调类**：安排、联系、跟进、提醒
- **闲聊/非工作内容**：简短礼貌回应

### 边界保护

以下情况会回复"这个需要您确认"：
- 涉及金额决策（>1万元）
- 对外承诺（交付时间、合作条款）
- 合同/协议相关
- 人事安排

## 任务日志

所有处理的任务会记录到：
```
C:\Users\39555\.claude\temp\boss-tasks-log.jsonl
```

## 故障排查

### 问题：老板发消息没有自动回复

1. **检查 Gateway 状态**
   ```bash
   openclaw channels status
   ```

2. **检查路由绑定**
   ```bash
   openclaw agents bindings
   ```

3. **查看日志**
   ```bash
   openclaw channels logs --channel openclaw-weixin --tail 100
   ```

### 问题：回复内容不符合预期

1. **检查系统提示词**
   ```bash
   code C:\Users\39555\.openclaw\agents\boss-monitor\agent\CLAUDE.md
   ```

2. **修改后重启 Gateway**
   ```bash
   openclaw gateway restart
   ```

## 下一步优化

1. **添加更多任务类型识别**
2. **集成本地数据源（矿业数据库）**
3. **添加任务优先级管理**
4. **生成每日任务摘要报告**

---

**配置文件位置：**
- 主配置：`C:\Users\39555\.openclaw\openclaw.json`
- Agent 配置：`C:\Users\39555\.openclaw\agents\boss-monitor\agent\CLAUDE.md`
- 技能配置（参考）：`C:\Users\39555\.claude\temp\boss-task-monitor.md`
