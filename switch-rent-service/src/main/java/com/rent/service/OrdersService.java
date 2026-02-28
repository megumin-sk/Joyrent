package com.rent.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.rent.common.entity.Orders;
import java.util.List;
import java.util.Map;

/**
 * @author jie17
 * @description 针对表【orders(主订单)】的数据库操作Service
 * @createDate 2025-11-18 23:33:58
 */
public interface OrdersService extends IService<Orders> {

    /**
     * 创建订单
     * @param userId 用户ID
     * @param dto 创建参数
     * @return 订单ID
     */
    Long createOrder(Long userId, com.rent.common.dto.OrderCreateDto dto);

    Integer queryWeeklyNum();

    Map<String, Integer> queryDailyOrderNum();

    /**
     * 查询最近七天每天成交额
     *
     * @return 日期与成交额
     */
    Map<String, Long> queryDailyTurnover();

    /**
     * 查询今日营收
     * 
     * @return 今日营收金额
     */
    Long queryTodayMoney();

    /**
     * 查询今日订单列表
     * 
     * @return 今日订单列表
     */
    List<Orders> queryTodayOrders();

    /**
     * 获取用户订单列表
     * @param userId 用户ID
     * @return 订单列表
     */
    List<Map<String, Object>> getMyOrders(Long userId);

    /**
     * 获取订单详情
     * @param orderId 订单ID
     * @param userId 用户ID（用于权限校验）
     * @return 订单详情
     */
    Map<String, Object> getOrderDetail(Long orderId, Long userId);

    /**
     * 模拟支付订单
     * @param orderId 订单ID
     * @param userId 用户ID
     * @return 是否成功
     */
    boolean payOrder(Long orderId, Long userId);
}
