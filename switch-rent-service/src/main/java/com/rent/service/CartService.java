package com.rent.service;

import com.rent.common.entity.Cart;
import com.baomidou.mybatisplus.extension.service.IService;

import java.util.List;
import java.util.Map;

/**
 * 购物车服务接口
 */
public interface CartService extends IService<Cart> {

    /**
     * 加入购物车
     */
    Cart addToCart(Long userId, Long gameId, Integer rentDays);

    /**
     * 获取用户购物车列表(含游戏信息)
     */
    List<Map<String, Object>> getCartList(Long userId);

    /**
     * 更新购物车租期
     */
    boolean updateRentDays(Long userId, Long cartId, Integer rentDays);

    /**
     * 删除购物车项
     */
    boolean deleteCartItem(Long userId, Long cartId);

    /**
     * 清空购物车
     */
    boolean clearCart(Long userId);
}
