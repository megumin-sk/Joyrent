---
name: Java Backend Professional (Hardcore Edition)
description: 深度对齐互联网大厂生产标准，专注于 JoyRent 租赁场景下的数据严谨性、并发安全及可观测性。
---

# 互联网大厂后端“防御性”开发规范

为了确保系统的金融级稳健性（涉及资金交易、高并发场景），编写代码时必须严格遵守以下规范：

## 1. 业务逻辑“防御性”要求
- **零 Null 容忍**：Service 层返回列表时，严禁返回 `null`，必须返回 `Collections.emptyList()`；查询对象时，建议使用 `Optional<T>` 包裹返回值，防止 NPE。
- **金额处理安全**：所有金额字段（如价格、余额）在代码中必须转为 `Long` (单位分) 或 `BigDecimal` 进行计算，严禁使用 `float/double` 以避免精度丢失。

## 2. 数据库与并发控制
- **乐观锁控制**：涉及状态变更或库存扣减的操作，必须在 SQL 层面加状态/版本判断（CAS 思想）：
  ```sql
  UPDATE orders SET status = 2 WHERE id = ? AND status = 1;
  ```
- **拒绝大事务**：严禁在 `@Transactional` 方法内执行 RPC 调用、发送短信、文件上传或处理大规模 IO，以防止数据库连接池耗尽。

## 3. 性能“红线”
- **大表查询禁令**：禁止任何不带 `limit` 的全表扫描或深分页查询。
- **内存组装优于 Join**：对于复杂业务关联，严禁 3 表以上 Join。建议采用单表查询，配合 Application 层（Map/Set）进行数据组装，降低数据库压力。


## 4. 可观测性与异常处理 (Observability)
- **全局异常兜底**：必须实现 `@RestControllerAdvice` 全局异常处理器。
  - **业务异常**：必须定义继承自 `RuntimeException` 的自定义异常（如 `CustomException`），在 Service 层遇到业务阻断时直接抛出，严禁层层返回 false 或错误对象。
  - **统一响应**：所有异常（包括 401、校验异常、500 系统错误）必须被全局处理器捕获并转化为统一的 JSON 格式（包含 code, msg），前端严禁展示默认的 HTML 报错页面。
- **结构化异常**：严禁在 catch 块里只写 `e.printStackTrace()`，必须使用 Logger 记录。
- **规范化日志埋点**：
  - [业务关键点]：记录关键状态变更，如 `log.info("BusinessObj [{}] - Status changed to [{}]", id, status);`
  - [错误上下文]：Error 日志必须带上上下文参数（如 userId, orderId），以便排查。
- **代码整洁与导包**：所有使用的类（包括异常、工具类、Entity 等）都必须通过 `import` 导入，**严禁**在代码逻辑中直接书写全限定名（如 `com.example.exception.CustomException`）。保持代码的简洁性和可读性。

## 5. 接口契约与 DTO
## 6. 数据库治理与结构洞察 (Database Governance)
- **结构先行原则**：在修改任何 Mapper 或 Service 逻辑前，必须查阅最新的数据库表结构，确保字段名、类型及注释一致。
- **统一数据库管理工具**：
  - 本 Skill 提供统一的数据库管理脚本：`scripts/db_manager.py`。
  - **核心功能**：
    - 📋 查询表结构（单表或全库导出）
    - ✏️ 字段管理（增删改）
    - 🔍 索引管理（增删）
    - 💾 表备份
    - 🛠️ 执行自定义SQL
  - **常用命令**：
    ```bash
    # 导出所有表结构到文件
    python .agent/skills/java-backend-pro/scripts/db_manager.py inspect -o db_schema.md
    
    # 查看单个表结构
    python .agent/skills/java-backend-pro/scripts/db_manager.py show game_reviews
    
    # 列出所有表
    python .agent/skills/java-backend-pro/scripts/db_manager.py list
    ```
  - **详细文档**：参见 `scripts/DB_MANAGER_GUIDE.md`

