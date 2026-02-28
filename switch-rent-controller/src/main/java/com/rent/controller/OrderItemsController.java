package com.rent.controller;

import com.rent.common.utils.ResponseEnum;
import com.rent.common.utils.ResponseUtil;
import com.rent.service.OrderItemsService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import java.util.Map;

/**
 * 订单明细相关的 REST 控制器
 */
@Tag(name = "OrderItems", description = "订单明细资源的查询与维护接口")
@RestController
@RequestMapping("/order-items")
public class OrderItemsController {

    @Resource
    private OrderItemsService orderItemsService;

    /**
     * 查询近七天游戏租赁量
     */
    @Operation(summary = "查询周游戏租赁量", description = "查询近七天游戏租赁量")
    @GetMapping("/weekly-game-rent-num")
    public ResponseUtil queryWeeklyGameRentNum() {
        Map<String, Integer> result = orderItemsService.queryWeeklyGameRentNum();
        return ResponseUtil.get(ResponseEnum.SUCCESS, result);
    }
}
