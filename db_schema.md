# Database Schema: joy_rent
**生成时间**: 2026-02-17 00:45:34
**表数量**: 10
---

## 📋 表: `cart`
**说明**: 用户购物车

### 字段列表
| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |
|--------|------|----------|-----|--------|------|------|
| id | bigint | NO | PRI | NULL | auto_increment |  |
| user_id | bigint | NO | MUL | NULL |  | 用户ID |
| game_id | bigint | NO |  | NULL |  | 游戏ID |
| rent_days | int | NO |  | 7 |  | 租期(天) |
| created_at | datetime | YES |  | CURRENT_TIMESTAMP | DEFAULT_GENERATED |  |
| updated_at | datetime | YES |  | CURRENT_TIMESTAMP | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |

### 索引列表
| 索引名 | 列名 | 唯一性 | 类型 |
|--------|------|--------|------|
| PRIMARY | id | ✅ 唯一 | BTREE |
| uk_user_game | user_id | ✅ 唯一 | BTREE |
| uk_user_game | game_id | ✅ 唯一 | BTREE |
| idx_user_id | user_id | ❌ 非唯一 | BTREE |

---

## 📋 表: `game_items`
**说明**: 实物库存

### 字段列表
| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |
|--------|------|----------|-----|--------|------|------|
| id | bigint | NO | PRI | NULL | auto_increment |  |
| game_id | bigint | NO | MUL | NULL |  |  |
| serial_code | varchar(64) | NO | UNI | NULL |  | 唯一编码 |
| status | tinyint | YES |  | 1 |  | 1=在库, 2=出租中, 3=维修, 4=丢失 |
| created_at | datetime | YES |  | CURRENT_TIMESTAMP | DEFAULT_GENERATED |  |

### 索引列表
| 索引名 | 列名 | 唯一性 | 类型 |
|--------|------|--------|------|
| PRIMARY | id | ✅ 唯一 | BTREE |
| uk_serial_code | serial_code | ✅ 唯一 | BTREE |
| idx_game_id | game_id | ❌ 非唯一 | BTREE |

---

## 📋 表: `game_reviews`
**说明**: 游戏评价表(含AI分析)

### 字段列表
| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |
|--------|------|----------|-----|--------|------|------|
| id | bigint | NO | PRI | NULL | auto_increment |  |
| user_id | bigint | NO | MUL | NULL |  | 评价人ID |
| game_id | bigint | NO | MUL | NULL |  | 被评价的游戏ID |
| order_id | bigint | NO | MUL | NULL |  | 关联订单ID |
| rating | tinyint | NO |  | 5 |  | 用户打分: 1-5 星 |
| content | varchar(1000) | YES |  | NULL |  | 评价内容 |
| ai_judge | tinyint | YES |  | 0 |  | SVM判断: 1=垃圾/广告, 0=正常 |
| ai_emotion | json | YES |  | NULL |  | BERT情感分析结果(JSON): 包含8个维度的详细评价 |
| ai_score | decimal(5,4) | YES |  | 0.0000 |  | BERT置信度分数 (0-1) |
| is_hidden | tinyint | YES |  | 0 |  | 最终显示状态 (1=隐藏) |
| created_at | datetime | YES |  | CURRENT_TIMESTAMP | DEFAULT_GENERATED |  |
| updated_at | datetime | YES |  | CURRENT_TIMESTAMP | DEFAULT_GENERATED on update CURRENT_TIMESTAMP | 更新时间 |
| dim_logistics | tinyint | YES |  | 3 |  | 物流评分(0差1中2好3无) |
| dim_condition | tinyint | YES |  | 3 |  | 成色评分 |
| dim_service | tinyint | YES |  | 3 |  | 服务评分 |
| dim_price | tinyint | YES |  | 3 |  | 价格评分 |
| dim_gameplay | tinyint | YES |  | 3 |  | 玩法评分 |
| dim_visuals | tinyint | YES |  | 3 |  | 画面评分 |
| dim_story | tinyint | YES |  | 3 |  | 剧情评分 |
| dim_audio | tinyint | YES |  | 3 |  | 音效评分 |

### 索引列表
| 索引名 | 列名 | 唯一性 | 类型 |
|--------|------|--------|------|
| PRIMARY | id | ✅ 唯一 | BTREE |
| uk_order_game | order_id | ✅ 唯一 | BTREE |
| uk_order_game | game_id | ✅ 唯一 | BTREE |
| idx_game_id | game_id | ❌ 非唯一 | BTREE |
| idx_user_id | user_id | ❌ 非唯一 | BTREE |

---

## 📋 表: `games`
**说明**: 游戏库

### 字段列表
| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |
|--------|------|----------|-----|--------|------|------|
| id | bigint | NO | PRI | NULL | auto_increment |  |
| title | varchar(128) | NO | MUL | NULL |  |  |
| platform | varchar(32) | YES |  | Switch |  |  |
| cover_url | varchar(255) | YES |  | NULL |  |  |
| description | text | YES |  | NULL |  |  |
| daily_rent_price | decimal(10,2) | NO |  | NULL |  | 日租金 |
| deposit_price | decimal(10,2) | NO |  | NULL |  | 押金 |
| available_stock | int | YES |  | 0 |  | 可用库存 |
| status | tinyint | YES |  | 1 |  | 1=上架, 0=下架 |
| created_at | datetime | YES |  | CURRENT_TIMESTAMP | DEFAULT_GENERATED |  |
| updated_at | datetime | YES |  | CURRENT_TIMESTAMP | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |
| total_rent_count | int | YES |  | 0 |  | 累计租赁次数 |

### 索引列表
| 索引名 | 列名 | 唯一性 | 类型 |
|--------|------|--------|------|
| PRIMARY | id | ✅ 唯一 | BTREE |
| idx_fulltext_title | title | ❌ 非唯一 | FULLTEXT |

---

## 📋 表: `order_items`
**说明**: 订单明细

### 字段列表
| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |
|--------|------|----------|-----|--------|------|------|
| id | bigint | NO | PRI | NULL | auto_increment |  |
| order_id | bigint | NO | MUL | NULL |  |  |
| game_id | bigint | NO |  | NULL |  |  |
| game_item_id | bigint | YES |  | NULL |  | 发货后填入 |
| rent_days | int | NO |  | NULL |  | 租期(天) |
| daily_rent_price | decimal(10,2) | NO |  | NULL |  | 下单时日租金 |
| sub_total | decimal(10,2) | NO |  | NULL |  | 该游戏租金小计 |
| start_date | date | YES |  | NULL |  | 起租日 |
| plan_end_date | date | YES |  | NULL |  | 预计归还日 |
| actual_end_date | date | YES |  | NULL |  | 实际归还日 |
| late_fee | decimal(10,2) | YES |  | 0.00 |  | 逾期费 |
| damage_fee | decimal(10,2) | YES |  | 0.00 |  | 赔偿金 |

### 索引列表
| 索引名 | 列名 | 唯一性 | 类型 |
|--------|------|--------|------|
| PRIMARY | id | ✅ 唯一 | BTREE |
| idx_order_id | order_id | ❌ 非唯一 | BTREE |

---

## 📋 表: `orders`
**说明**: 主订单

### 字段列表
| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |
|--------|------|----------|-----|--------|------|------|
| id | bigint | NO | PRI | NULL | auto_increment |  |
| user_id | bigint | NO | MUL | NULL |  |  |
| address_id | bigint | NO |  | NULL |  | 关联地址ID |
| status | tinyint | YES |  | 10 |  | 10=待支付, 20=待发货, 30=租赁中, 40=归还中, 50=完成, 60=取消 |
| total_rent_fee | decimal(10,2) | NO |  | NULL |  | 总租金 |
| total_deposit | decimal(10,2) | NO |  | NULL |  | 总押金 |
| pay_amount | decimal(10,2) | NO |  | NULL |  | 实付金额 |
| tracking_number_send | varchar(64) | YES |  | NULL |  |  |
| tracking_number_return | varchar(64) | YES |  | NULL |  |  |
| created_at | datetime | YES | MUL | CURRENT_TIMESTAMP | DEFAULT_GENERATED |  |
| pay_time | datetime | YES |  | NULL |  |  |
| finished_time | datetime | YES |  | NULL |  |  |

### 索引列表
| 索引名 | 列名 | 唯一性 | 类型 |
|--------|------|--------|------|
| PRIMARY | id | ✅ 唯一 | BTREE |
| idx_user_status | user_id | ❌ 非唯一 | BTREE |
| idx_user_status | status | ❌ 非唯一 | BTREE |
| idx_created_status | created_at | ❌ 非唯一 | BTREE |
| idx_created_status | status | ❌ 非唯一 | BTREE |

---

## 📋 表: `transactions`
**说明**: 资金流水

### 字段列表
| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |
|--------|------|----------|-----|--------|------|------|
| id | bigint | NO | PRI | NULL | auto_increment |  |
| user_id | bigint | NO | MUL | NULL |  |  |
| order_id | bigint | YES |  | NULL |  |  |
| type | tinyint | NO |  | NULL |  | 1=充值, 2=租金押金, 3=退押金, 4=扣费 |
| amount | decimal(10,2) | NO |  | NULL |  |  |
| pay_method | varchar(32) | YES |  | WeChat |  |  |
| created_at | datetime | YES |  | CURRENT_TIMESTAMP | DEFAULT_GENERATED |  |

### 索引列表
| 索引名 | 列名 | 唯一性 | 类型 |
|--------|------|--------|------|
| PRIMARY | id | ✅ 唯一 | BTREE |
| idx_user_id | user_id | ❌ 非唯一 | BTREE |

---

## 📋 表: `user_addresses`
**说明**: 地址簿

### 字段列表
| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |
|--------|------|----------|-----|--------|------|------|
| id | bigint | NO | PRI | NULL | auto_increment |  |
| user_id | bigint | NO | MUL | NULL |  |  |
| receiver_name | varchar(64) | NO |  | NULL |  |  |
| receiver_phone | varchar(20) | NO |  | NULL |  |  |
| province | varchar(64) | NO |  | NULL |  |  |
| city | varchar(64) | NO |  | NULL |  |  |
| district | varchar(64) | NO |  | NULL |  |  |
| detail_address | varchar(255) | NO |  | NULL |  |  |
| is_default | tinyint | YES |  | 0 |  | 1=默认 |
| is_deleted | tinyint | YES |  | 0 |  | 1=逻辑删除 |
| created_at | datetime | YES |  | CURRENT_TIMESTAMP | DEFAULT_GENERATED |  |

### 索引列表
| 索引名 | 列名 | 唯一性 | 类型 |
|--------|------|--------|------|
| PRIMARY | id | ✅ 唯一 | BTREE |
| idx_user_id | user_id | ❌ 非唯一 | BTREE |

---

## 📋 表: `user_face`

### 字段列表
| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |
|--------|------|----------|-----|--------|------|------|
| face_encoding | text | YES |  | NULL |  | 人脸特征向量 |
| user_id | bigint | NO |  | NULL |  | 用户id |
| face_id | varchar(255) | YES |  | NULL |  | 百度人脸库的唯一标识 |

### 索引列表
| 索引名 | 列名 | 唯一性 | 类型 |
|--------|------|--------|------|

---

## 📋 表: `users`
**说明**: 用户表

### 字段列表
| 字段名 | 类型 | 允许NULL | 键 | 默认值 | 额外 | 说明 |
|--------|------|----------|-----|--------|------|------|
| id | bigint | NO | PRI | NULL | auto_increment | 主键 |
| username | varchar(64) | NO | UNI | NULL |  | 用户名 |
| password | varchar(255) | NO |  | NULL |  | 密码 |
| phone | varchar(20) | NO | UNI | NULL |  | 手机号 |
| nickname | varchar(64) | YES |  | NULL |  | 昵称 |
| avatar | varchar(255) | YES |  | NULL |  | 头像 |
| role | tinyint | YES |  | 10 |  | 10=普通, 20=管理员 |
| balance | decimal(10,2) | YES |  | 0.00 |  | 余额 |
| status | tinyint | YES |  | 1 |  | 1=启用, 0=禁用 |
| created_at | datetime | YES |  | CURRENT_TIMESTAMP | DEFAULT_GENERATED |  |
| updated_at | datetime | YES |  | CURRENT_TIMESTAMP | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |

### 索引列表
| 索引名 | 列名 | 唯一性 | 类型 |
|--------|------|--------|------|
| PRIMARY | id | ✅ 唯一 | BTREE |
| uk_phone | phone | ✅ 唯一 | BTREE |
| uk_username | username | ✅ 唯一 | BTREE |

---
