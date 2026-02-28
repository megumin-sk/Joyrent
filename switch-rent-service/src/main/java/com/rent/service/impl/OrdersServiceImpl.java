package com.rent.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rent.common.dto.OrderCreateDto;
import com.rent.common.entity.*;
import com.rent.common.exception.CustomException;
import com.rent.common.utils.ResponseEnum;
import com.rent.mapper.CartMapper;
import com.rent.mapper.GamesMapper;
import com.rent.mapper.OrdersMapper;
import com.rent.service.OrderItemsService;
import com.rent.service.OrdersService;
import com.rent.service.UserAddressesService;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.*;
import java.util.stream.Collectors;

/**
 * @author jie17
 * @description 针对表【orders(主订单)】的数据库操作Service实现
 * @createDate 2025-11-18 23:33:58
 */
@Service
@AllArgsConstructor
public class OrdersServiceImpl extends ServiceImpl<OrdersMapper, Orders>
        implements OrdersService {
    
    private final OrdersMapper ordersMapper;
    private final CartMapper cartMapper;
    private final GamesMapper gamesMapper;
    private final OrderItemsService orderItemsService;
    private final UserAddressesService userAddressesService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Long createOrder(Long userId, OrderCreateDto dto) {
        // 1. 校验地址
        UserAddresses address = userAddressesService.getById(dto.getAddressId());
        if (address == null || !address.getUserId().equals(userId)) {
            throw new CustomException(ResponseEnum.FAIL.getCode(), "收货地址无效");
        }

        // 2. 获取购物车项
        List<Long> cartIds = dto.getCartIds();
        if (cartIds == null || cartIds.isEmpty()) {
            throw new CustomException(ResponseEnum.FAIL.getCode(), "请选择租赁商品");
        }
        
        List<Cart> cartList = cartMapper.selectBatchIds(cartIds);
        if (cartList.isEmpty()) {
             throw new CustomException(ResponseEnum.FAIL.getCode(), "购物车商品不存在");
        }
        
        // 校验购物车项所有权
        for (Cart c : cartList) {
            if (!c.getUserId().equals(userId)) {
                throw new CustomException(ResponseEnum.FAIL.getCode(), "非法操作购物车商品");
            }
        }

        // 3. 计算费用并构建订单项
        BigDecimal totalRentFee = BigDecimal.ZERO;
        BigDecimal totalDeposit = BigDecimal.ZERO;
        List<OrderItems> orderItemsList = new ArrayList<>();
        
        for (Cart cart : cartList) {
            Games game = gamesMapper.selectById(cart.getGameId());
            if (game == null) {
                throw new CustomException(ResponseEnum.FAIL.getCode(), "商品(ID:" + cart.getGameId() + ")不存在或已下架");
            }
            // 简单库存检查 (乐观策略)
            // if (game.getStock() <= 0) throw ...
            
            OrderItems item = new OrderItems();
            item.setGameId(game.getId());
            item.setDailyRentPrice(game.getDailyRentPrice()); // 保存价格快照
            item.setRentDays(cart.getRentDays());
            item.setStartDate(new Date()); // 起租日暂定当前
            
            // 计算截止日期
            Calendar calendar = Calendar.getInstance();
            calendar.add(Calendar.DAY_OF_YEAR, cart.getRentDays());
            item.setPlanEndDate(calendar.getTime());
            
            // 费用
            BigDecimal dailyPrice = game.getDailyRentPrice();
            BigDecimal rentFee = dailyPrice.multiply(new BigDecimal(cart.getRentDays()));
            item.setSubTotal(rentFee); // 设置小计
            
            totalRentFee = totalRentFee.add(rentFee);
            totalDeposit = totalDeposit.add(game.getDepositPrice());
            
            orderItemsList.add(item);
        }

        // 4. 构建主订单
        Orders order = new Orders();
        order.setUserId(userId);
        order.setAddressId(dto.getAddressId());
        order.setTotalRentFee(totalRentFee);
        order.setTotalDeposit(totalDeposit);
        // 信用免押：实付 = 总租金
        order.setPayAmount(totalRentFee); 
        order.setStatus(10); // 10=待支付
        order.setCreatedAt(new Date());
        // 简单生成订单号逻辑，这里不需要，数据库自增ID即可，或者后续加业务订单号字段
        
        this.save(order);
        
        // 5. 保存订单项
        for (OrderItems item : orderItemsList) {
            item.setOrderId(order.getId());
        }
        orderItemsService.saveBatch(orderItemsList);
        
        // 6. 清理购物车
        cartMapper.deleteBatchIds(cartIds);
        
        return order.getId();
    }

    @Override
    public Integer queryWeeklyNum() {
        return ordersMapper.queryWeeklyNum();
    }

    @Override
    public Map<String, Integer> queryDailyOrderNum() {
        List<Map<String, Object>> list = ordersMapper.queryDailyOrderNum();
        Map<String, Integer> resultMap = new LinkedHashMap<>();
        if (list != null) {
            for (Map<String, Object> item : list) {
                String date = (String) item.get("date");
                Number count = (Number) item.get("count");
                resultMap.put(date, count.intValue());
            }
        }
        return resultMap;
    }

    @Override
    public Map<String, Long> queryDailyTurnover() {
        List<Map<String, Object>> list = ordersMapper.queryDailyTurnover();
        Map<String, Long> resultMap = new LinkedHashMap<>();
        if (list != null) {
            for (Map<String, Object> item : list) {
                String date = (String) item.get("date");
                Number amount = (Number) item.get("amount");
                resultMap.put(date, amount.longValue());
            }
        }
        return resultMap;
    }

    @Override
    public Long queryTodayMoney() {
        return ordersMapper.queryTodayMoney();
    }

    @Override
    public List<Orders> queryTodayOrders() {
        return ordersMapper.queryTodayOrders();
    }

    @Override
    public List<Map<String, Object>> getMyOrders(Long userId) {
        QueryWrapper<Orders> query = new QueryWrapper<>();
        query.eq("user_id", userId)
             .orderByDesc("created_at");
        List<Orders> orders = this.list(query);
        
        List<Map<String, Object>> result = new ArrayList<>();
        for (Orders order : orders) {
            Map<String, Object> map = new HashMap<>();
            map.put("id", order.getId());
            map.put("status", order.getStatus());
            map.put("total_rent_fee", order.getTotalRentFee());
            map.put("total_deposit", order.getTotalDeposit());
            map.put("created_at", order.getCreatedAt());
            map.put("tracking_number_send", order.getTrackingNumberSend());
            result.add(map);
        }
        return result;
    }

    @Override
    public Map<String, Object> getOrderDetail(Long orderId, Long userId) {
        Orders order = this.getById(orderId);
        if (order == null) {
            throw new CustomException(ResponseEnum.FAIL.getCode(), "订单不存在");
        }
        if (!order.getUserId().equals(userId)) {
            throw new CustomException(ResponseEnum.FAIL.getCode(), "无权查看该订单");
        }
        
        Map<String, Object> result = new HashMap<>();
        result.put("id", order.getId());
        result.put("status", order.getStatus());
        result.put("totalRentFee", order.getTotalRentFee());
        result.put("totalDeposit", order.getTotalDeposit());
        result.put("payAmount", order.getPayAmount());
        result.put("createdAt", order.getCreatedAt());
        result.put("trackingNumberSend", order.getTrackingNumberSend());
        
        // 获取地址信息
        if (order.getAddressId() != null) {
            UserAddresses addr = userAddressesService.getById(order.getAddressId());
            if (addr != null) {
                Map<String, Object> addrMap = new HashMap<>();
                addrMap.put("receiverName", addr.getReceiverName());
                addrMap.put("receiverPhone", addr.getReceiverPhone());
                addrMap.put("province", addr.getProvince());
                addrMap.put("city", addr.getCity());
                addrMap.put("district", addr.getDistrict());
                addrMap.put("detailAddress", addr.getDetailAddress());
                result.put("address", addrMap);
            }
        }
        
        // 获取订单项
        QueryWrapper<OrderItems> itemQuery = new QueryWrapper<>();
        itemQuery.eq("order_id", orderId);
        List<OrderItems> items = orderItemsService.list(itemQuery);
        
        List<Map<String, Object>> itemList = new ArrayList<>();
        for (OrderItems item : items) {
            Map<String, Object> itemMap = new HashMap<>();
            itemMap.put("id", item.getId());
            itemMap.put("gameId", item.getGameId());
            itemMap.put("rentDays", item.getRentDays());
            itemMap.put("subTotal", item.getSubTotal());
            itemMap.put("dailyRentPrice", item.getDailyRentPrice());
            
            // 获取游戏信息
            Games game = gamesMapper.selectById(item.getGameId());
            if (game != null) {
                itemMap.put("title", game.getTitle());
                itemMap.put("coverUrl", game.getCoverUrl());
            }
            itemList.add(itemMap);
        }
        result.put("items", itemList);
        
        return result;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean payOrder(Long orderId, Long userId) {
        Orders order = this.getById(orderId);
        if (order == null) {
            throw new CustomException(ResponseEnum.FAIL.getCode(), "订单不存在");
        }
        if (!order.getUserId().equals(userId)) {
            throw new CustomException(ResponseEnum.FAIL.getCode(), "无权操作该订单");
        }
        if (order.getStatus() != 10) {
            throw new CustomException(ResponseEnum.FAIL.getCode(), "订单状态不支持支付");
        }
        
        // 模拟支付成功，更新状态为待发货
        order.setStatus(20);
        order.setPayTime(new Date());
        return this.updateById(order);
    }

}
