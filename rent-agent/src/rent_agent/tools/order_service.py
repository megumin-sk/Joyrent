
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pymysql
from pymysql.cursors import DictCursor

from rent_agent.config import config
from rent_agent.state import AgentState, get_last_user_message

logger = logging.getLogger(__name__)

# ============================================================
#  1. 数据库封装类 (MySQL)
# ============================================================

class OrderDatabase:
    """封装 MySQL (orders, order_items) 操作"""

    def _connect(self):
        return pymysql.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB,
            cursorclass=DictCursor
        )

    def get_recent_orders(self, user_id: int, limit: int = 3) -> List[Dict]:
        """查询用户最近的订单"""
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                # 关联查询 orders 和 order_items，获取游戏名称
                # status: 10=待支付, 20=待发货, 30=租赁中, 40=归还中, 50=完成, 60=取消
                sql = """
                    SELECT 
                        o.id, o.status, o.total_rent_fee, o.tracking_number_send, o.created_at,
                        oi.rent_days, oi.actual_end_date, oi.plan_end_date,
                        g.title as game_title
                    FROM orders o
                    LEFT JOIN order_items oi ON o.id = oi.order_id
                    LEFT JOIN games g ON oi.game_id = g.id
                    WHERE o.user_id = %s
                    ORDER BY o.created_at DESC
                    LIMIT %s
                """
                cursor.execute(sql, (user_id, limit))
                results = cursor.fetchall()
                
                # 格式化日期
                for row in results:
                    if row.get('created_at'):
                        row['created_at'] = row['created_at'].strftime('%Y-%m-%d %H:%M')
                    if row.get('plan_end_date'):
                        row['plan_end_date'] = row['plan_end_date'].strftime('%Y-%m-%d')
                
                return results
        finally:
            conn.close()

    def get_renting_orders(self, user_id: int) -> List[Dict]:
        """查询用户当前正在租赁中 (Status=30) 的订单"""
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT 
                        o.id, o.tracking_number_send, o.created_at,
                        oi.rent_days, oi.plan_end_date,
                        g.title as game_title, g.cover_url
                    FROM orders o
                    JOIN order_items oi ON o.id = oi.order_id
                    JOIN games g ON oi.game_id = g.id
                    WHERE o.user_id = %s AND o.status = 30
                    ORDER BY oi.plan_end_date ASC
                """
                cursor.execute(sql, (user_id,))
                results = cursor.fetchall()
                
                for row in results:
                    if row.get('plan_end_date'):
                        # 计算剩余天数
                        today = datetime.now().date()
                        plan_date = row['plan_end_date']  #pymysql返回的是date对象
                        if isinstance(plan_date, str):
                            plan_date = datetime.strptime(plan_date, '%Y-%m-%d').date()
                            
                        delta = (plan_date - today).days
                        row['days_left'] = delta
                        row['plan_end_date'] = plan_date.strftime('%Y-%m-%d')
                        
                return results
        finally:
            conn.close()

    def submit_return_tracking(self, user_id: int, order_id: int, tracking_number: str) -> Dict:
        """用户提交归还物流单号"""
        conn = self._connect()
        try:
            with conn.cursor() as cursor:
                # 1. 校验订单归属权和状态 (必须是 30=租赁中)
                check_sql = "SELECT id, status FROM orders WHERE id = %s AND user_id = %s"
                cursor.execute(check_sql, (order_id, user_id))
                order = cursor.fetchone()
                
                if not order:
                    return {"success": False, "message": "未找到此订单"}
                
                if order['status'] != 30:
                    return {"success": False, "message": f"当前订单状态({order['status']})不支持归还操作，仅'租赁中'状态可归还"}

                # 2. 更新单号和状态 (30 -> 40 归还中)
                update_sql = """
                    UPDATE orders 
                    SET tracking_number_return = %s, status = 40 
                    WHERE id = %s
                """
                cursor.execute(update_sql, (tracking_number, order_id))
                conn.commit()
                
                if cursor.rowcount > 0:
                    logger.info(f"订单 {order_id} 归还提交成功，单号: {tracking_number}")
                    return {"success": True, "message": "归还单号已提交，等待平台收货确认"}
                else:
                    return {"success": False, "message": "更新失败"}
                    
        except Exception as e:
            logger.error(f"提交归还失败: {e}")
            return {"success": False, "message": f"系统错误: {str(e)}"}
        finally:
            conn.close()


# ============================================================
#  2. 核心工具类
# ============================================================

class OrderTool:
    """订单查询与操作工具"""

    def __init__(self):
        self.db = OrderDatabase()

    def query_my_orders(self, user_id: int, intent_detail: str = "recent") -> List[Dict]:
        """
        查询用户订单
        :param intent_detail: users的具体意图 ('recent'=最近订单, 'renting'=在租订单)
        """
        if not user_id:
            return []
            
        if intent_detail == "renting":
            return self.db.get_renting_orders(user_id)
        else:
            return self.db.get_recent_orders(user_id)

    def return_game(self, user_id: int, order_id: int, tracking_number: str) -> Dict:
        """
        处理归还请求
        """
        if not user_id or not order_id or not tracking_number:
             return {"success": False, "message": "缺少必要信息(订单号/快递单号)"}
             
        return self.db.submit_return_tracking(user_id, order_id, tracking_number)

    def as_tools(self) -> List[Any]:
        """将类方法暴露为 LangChain Tool 对象"""
        from langchain_core.tools import Tool, StructuredTool
        
        return [
            StructuredTool.from_function(
                func=self.query_my_orders,
                name="query_orders",
                description="查询用户订单信息。参数：user_id(int), intent_detail(str,可选'recent'或'renting')"
            ),
            StructuredTool.from_function(
                func=self.return_game,
                name="return_game",
                description="用户归还游戏并提交物流单号。参数：user_id(int), order_id(int), tracking_number(str)"
            )
        ]

