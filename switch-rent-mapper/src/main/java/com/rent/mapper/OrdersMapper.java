package com.rent.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.rent.common.entity.Orders;
import java.util.List;
import java.util.Map;

/**
 * @author jie17
 * @description 针对表【orders(主订单)】的数据库操作Mapper
 * @createDate 2025-11-18 23:33:58
 * @Entity com.rent.common.entity.Orders
 */
public interface OrdersMapper extends BaseMapper<Orders> {
    Integer queryWeeklyNum();

    List<Map<String, Object>> queryDailyOrderNum();

    /**
     * 查询最近七天每日成交额
     *
     * @return 日期与成交额列表
     */
    List<Map<String, Object>> queryDailyTurnover();

    Long queryTodayMoney();

    List<Orders> queryTodayOrders();
}
