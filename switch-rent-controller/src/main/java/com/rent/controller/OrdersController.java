package com.rent.controller;

import com.rent.common.dto.OrderCreateDto;
import com.rent.common.exception.CustomException;
import com.rent.common.utils.ResponseEnum;
import com.rent.common.utils.ResponseUtil;
import com.rent.service.OrdersService;
import com.rent.utils.JwtUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.text.ParseException;
import java.util.Map;

/**
 * 订单相关的 REST 控制器
 */
@Tag(name = "Orders", description = "订单资源的查询与维护接口")
@RestController
@RequestMapping("/orders")
public class OrdersController {

    @Resource
    private OrdersService ordersService;

    /**
     * 从 Token 中解析用户 ID
     */
    private Long getUserIdFromToken(HttpServletRequest request) {
        String authHeader = request.getHeader("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            try {
                Integer userId = JwtUtil.getUserId(token);
                return userId != null ? userId.longValue() : null;
            } catch (ParseException e) {
                return null;
            }
        }
        return null;
    }

    @Operation(summary = "创建订单")
    @PostMapping("/create")
    public ResponseUtil create(@RequestBody OrderCreateDto dto, HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
              throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }
        
        Long orderId = ordersService.createOrder(userId, dto);
        return ResponseUtil.get(ResponseEnum.SUCCESS, orderId);
    }

    /**
     * 查询近七天订单成交量
     */
    @Operation(summary = "查询周成交量", description = "查询近七天订单成交量")
    @GetMapping("/weekly-num")
    public ResponseUtil queryWeeklyNum() {
        Integer count = ordersService.queryWeeklyNum();
        return ResponseUtil.get(ResponseEnum.SUCCESS, count);
    }

    /**
     * 查询近七天每天的订单成交量
     */
    @Operation(summary = "查询日成交量趋势", description = "查询近七天每天的订单成交量")
    @GetMapping("/weekly-daily-trend")
    public ResponseUtil queryDailyOrderNum() {
        Map<String, Integer> result = ordersService.queryDailyOrderNum();
        return ResponseUtil.get(ResponseEnum.SUCCESS, result);
    }

    /**
     * 查询近七天每天的成交额
     */
    @Operation(summary = "查询日成交额趋势", description = "查询近七天每天的成交额")
    @GetMapping("/weekly-daily-amount")
    public ResponseUtil queryDailyTurnover() {
        Map<String, Long> result = ordersService.queryDailyTurnover();
        return ResponseUtil.get(ResponseEnum.SUCCESS, result);
    }

    /**
     * 查询今日营收
     */
    @Operation(summary = "查询今日营收", description = "查询今日所有已支付订单的总金额")
    @GetMapping("/today-money")
    public ResponseUtil queryTodayMoney() {
        Long amount = ordersService.queryTodayMoney();
        return ResponseUtil.get(ResponseEnum.SUCCESS, amount);
    }

    /**
     * 查询今日订单列表
     */
    @Operation(summary = "查询今日订单", description = "查询今日创建的所有订单列表")
    @GetMapping("/today-list")
    public ResponseUtil queryTodayOrders() {
        return ResponseUtil.get(ResponseEnum.SUCCESS, ordersService.queryTodayOrders());
    }

    @Operation(summary = "获取我的订单列表")
    @GetMapping("/my")
    public ResponseUtil getMyOrders(HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }
        return ResponseUtil.get(ResponseEnum.SUCCESS, ordersService.getMyOrders(userId));
    }

    @Operation(summary = "获取订单详情")
    @GetMapping("/{id}")
    public ResponseUtil getOrderDetail(@PathVariable Long id, HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }
        return ResponseUtil.get(ResponseEnum.SUCCESS, ordersService.getOrderDetail(id, userId));
    }

    @Operation(summary = "模拟支付订单")
    @PostMapping("/{id}/pay")
    public ResponseUtil payOrder(@PathVariable Long id, HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }
        boolean success = ordersService.payOrder(id, userId);
        if (success) {
            return ResponseUtil.get(ResponseEnum.SUCCESS);
        } else {
            return ResponseUtil.get(ResponseEnum.FAIL);
        }
    }

}
