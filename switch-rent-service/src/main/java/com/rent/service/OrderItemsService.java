package com.rent.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.rent.common.entity.OrderItems;

import java.util.Map;

/**
* @author jie17
* @description 针对表【order_items(订单明细)】的数据库操作Service
* @createDate 2025-11-18 23:33:58
*/
public interface OrderItemsService extends IService<OrderItems> {
    Map<String, Integer> queryWeeklyGameRentNum();
}
