# Architecture Analyzer

基于Claude Code的源码架构设计质量分析工具，支持多维度架构缺陷检测。

## 功能特性

- **多维度分析**: 支持9个架构度量域的专业分析
- **同步执行**: 利用Claude Code原生多代理能力，一次性运行所有分析
- **自动安装**: 首次运行自动检查并安装所需的Claude Code子代理
- **双输出模式**: 支持JSON模式（纯JSON）和可读模式（彩色终端输出）
- **自动化执行**: 一键调用所有Claude Code子代理
- **结果聚合**: 智能合并分析结果并生成综合评分
- **灵活配置**: 支持选择性运行特定分析代理
- **高效分析**: 单次调用同时执行多个分析维度
- **标准输出**: JSON格式结果，便于后续处理

## 支持的分析维度

| 代理名称 | 分析域 | 描述 |
|---------|-------|------|
| modularity | 模块化 | 模块边界、规模均衡、职责单一 |
| dependency | 依赖方向 | 依赖环检测、层次依赖、稳定性分析 |
| coupling | 耦合与内聚 | 类间耦合度、内聚性、契约设计 |
| abstraction | 抽象层次 | 层次清晰度、接口设计、信息隐藏 |
| complexity | 复杂度 | 圈复杂度、认知复杂度、可维护性 |
| standard | 一致性与规范 | 编码规范、命名一致性、工具配置 |
| testability | 可测性 | 测试覆盖率、可替换性、测试稳定性 |
| performance | 性能与弹性 | 性能基线、并发控制、弹性机制 |
| security | 安全与合规 | 漏洞扫描、访问控制、数据保护 |

## 安装

### 通过PyPI安装（推荐）

```bash
# 使用pip安装
pip install arch-analyzer

# 或使用pipx安装（推荐用于CLI工具）
pipx install arch-analyzer
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/username/arch-analyzer.git
cd arch-analyzer

# 使用pip安装
pip install -e .

# 或使用hatch构建并安装
pip install build
python -m build
pip install dist/*.whl
```

## 依赖要求

1. **Python 3.7+**
2. **Claude Code CLI**: 确保已安装并配置Claude Code命令行工具

```bash
# 检查Claude Code是否可用
claude --version
```

## 使用方法

### 基本用法

在代码库根目录运行完整分析（首次运行会自动安装子代理）：

```bash
arch-analyzer
```

### 指定目录

分析特定目录：

```bash
arch-analyzer /path/to/your/codebase
```

### 选择性分析

只运行特定的分析代理：

```bash
arch-analyzer --agents modularity dependency coupling
```

### 多代理执行

```bash
# 默认运行所有9个代理
arch-analyzer

# 一次性运行多个指定代理
arch-analyzer --agents modularity dependency coupling
```

### 子代理管理

```bash
# 查看可用代理
arch-analyzer --list-agents

# 强制重新安装所有子代理
arch-analyzer --force-install
```

### 输出选项

```bash
# 默认可读模式（彩色终端输出）
arch-analyzer

# JSON模式（纯JSON输出，无过程日志）
arch-analyzer --json

# 美化JSON输出
arch-analyzer --json --pretty

# 保存到文件
arch-analyzer --output analysis_results.json

# JSON模式保存到文件
arch-analyzer --json --output analysis_results.json
```

### 完整命令示例

```bash
# 默认模式：彩色终端输出，便于阅读
arch-analyzer

# JSON模式：获取JSON数据用于程序集成
arch-analyzer --json --pretty

# 只分析特定维度并保存结果
arch-analyzer --agents security performance --output security_perf.json

# JSON模式分析并保存，适用于CI/CD集成
arch-analyzer --json --output ci_results.json

# 强制重装代理后运行JSON模式分析
arch-analyzer --force-install && arch-analyzer --json
```

## 输出格式

### 可读模式输出

默认运行时显示彩色终端输出，便于人工阅读：

- 🔴 **问题 (bad)**: 红色显示，按严重程度排序
- 🟢 **优势 (good)**: 绿色显示，突出架构亮点  
- 🟡 **建议 (recommendations)**: 黄色显示，按优先级排序
- 📊 **评分**: 根据分数使用不同颜色（绿色≥3.5，黄色≥2.5，红色<2.5）

### JSON模式输出

使用`--json`参数时输出标准JSON格式，包含两个主要部分：

#### 1. 综合摘要 (summary)

```json
{
  "summary": {
    "score": 3.2,
    "good": "架构整体模块化设计合理，依赖层次清晰",
    "bad": [
      {"severity": "high", "issue": "[复杂度] 存在5个超过20圈复杂度的函数需要拆分"},
      {"severity": "medium", "issue": "[安全] 缺少输入验证和SQL注入防护"}
    ],
    "recommendations": [
      {"priority": "high", "action": "[复杂度] 拆分UserService.processComplexWorkflow()方法"},
      {"priority": "medium", "action": "[安全] 引入参数化查询替代字符串拼接"}
    ]
  }
}
```

#### 2. 详细结果 (detailed_results)

每个代理的完整分析结果：

```json
{
  "detailed_results": {
    "modularity": {
      "domain": "模块化",
      "score": 3.8,
      "good": "模块边界清晰，职责分离良好",
      "bad": [
        {"severity": "medium", "issue": "用户模块包含152个文件，建议拆分"}
      ],
      "recommendations": [
        {"priority": "high", "action": "拆分用户模块为认证、权限、配置三个子模块"}
      ]
    }
  }
}
```

## 工作原理

1. **自动安装**: 检查`.claude/agents/`目录，自动安装缺失的子代理
2. **多代理调用**: 单次Claude Code调用同时执行多个子代理分析
3. **结果解析**: 从Claude Code输出中提取各个代理的JSON结果
4. **智能聚合**: 使用Claude Code生成综合评分和建议
5. **去重优化**: 合并相似问题，按严重程度和优先级排序
6. **标准输出**: 生成结构化JSON报告

## 技术优势

- **自动化部署**: 首次运行自动安装所需子代理，无需手动配置
- **原生支持**: 利用Claude Code内置的多代理协作能力
- **高效执行**: 单次调用完成所有分析，无需额外线程管理
- **智能解析**: 自动识别和分离各代理的分析结果
- **简化架构**: 移除复杂的并发控制，代码更加简洁可靠

## 注意事项

- 确保在代码库根目录运行以获得最佳分析效果
- 首次运行会自动创建`~/.claude/agents/`目录并安装子代理
- 默认模式提供彩色终端输出，便于人工查看；JSON模式适合程序集成
- 大型代码库分析可能需要几分钟时间
- 多代理分析有10分钟超时限制
- 建议定期运行以跟踪架构质量变化
- 子代理文件更新后可使用`--force-install`重新安装

## 错误处理

- 单个代理失败不会影响其他代理运行
- 网络超时会自动跳过对应代理
- 详细错误信息会输出到控制台

## 集成建议

- 集成到CI/CD流水线中定期检查
- 结合代码审查流程使用
- 设置质量门禁和改进跟踪