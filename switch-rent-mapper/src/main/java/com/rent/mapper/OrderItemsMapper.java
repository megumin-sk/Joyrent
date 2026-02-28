package com.rent.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.rent.common.entity.OrderItems;

import java.util.List;
import java.util.Map;

/**
 * @author jie17
 * @description 针对表【order_items(订单明细)】的数据库操作Mapper
 * @createDate 2025-11-18 23:33:58
 * @Entity com.rent.common.entity.OrderItems
 */
public interface OrderItemsMapper extends BaseMapper<OrderItems> {
    @SuppressWarnings("MybatisXMapperMethodInspection")
    List<Map<String, Object>> queryWeeklyGameRentNum();
}
