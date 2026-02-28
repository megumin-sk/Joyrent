package com.rent.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rent.common.entity.OrderItems;
import com.rent.mapper.OrderItemsMapper;
import com.rent.service.OrderItemsService;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
* @author jie17
* @description 针对表【order_items(订单明细)】的数据库操作Service实现
* @createDate 2025-11-18 23:33:58
*/
@Service
@AllArgsConstructor
public class OrderItemsServiceImpl extends ServiceImpl<OrderItemsMapper, OrderItems>
    implements OrderItemsService {
    private OrderItemsMapper orderItemsMapper;
    @Override
    public Map<String, Integer> queryWeeklyGameRentNum() {
        // 1. 从数据库查出 List<Map>
        List<Map<String, Object>> list = orderItemsMapper.queryWeeklyGameRentNum();

        // 2. 转换成 Map<String, Integer>
        Map<String, Integer> resultMap = new HashMap<>();
        if (list != null) {
            for (Map<String, Object> item : list) {
                String name = (String) item.get("name");
                Number count = (Number) item.get("value");
                resultMap.put(name, count.intValue());
            }
        }
        return resultMap;
    }
}




