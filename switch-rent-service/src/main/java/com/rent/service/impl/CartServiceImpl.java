package com.rent.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rent.common.entity.Cart;
import com.rent.common.exception.CustomException;
import com.rent.common.utils.ResponseEnum;
import com.rent.service.CartService;
import com.rent.mapper.CartMapper;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.List;
import java.util.Map;

/**
 * 购物车服务实现
 */
@Service
public class CartServiceImpl extends ServiceImpl<CartMapper, Cart> implements CartService {

    @Resource
    private CartMapper cartMapper;

    @Override
    public Cart addToCart(Long userId, Long gameId, Integer rentDays) {
        // 检查是否已在购物车
        Cart existing = cartMapper.selectByUserAndGame(userId, gameId);
        if (existing != null) {
            // 已存在则提示
            throw new CustomException(ResponseEnum.FAIL.getCode(), "该商品已在购物车中");
        }

        // 新增购物车项
        Cart cart = new Cart();
        cart.setUserId(userId);
        cart.setGameId(gameId);
        cart.setRentDays(rentDays);
        cartMapper.insertCart(cart);
        return cart;
    }

    @Override
    public List<Map<String, Object>> getCartList(Long userId) {
        return cartMapper.selectCartWithGame(userId);
    }

    @Override
    public boolean updateRentDays(Long userId, Long cartId, Integer rentDays) {
        return cartMapper.updateRentDays(cartId, userId, rentDays) > 0;
    }

    @Override
    public boolean deleteCartItem(Long userId, Long cartId) {
        return cartMapper.deleteByIdAndUser(cartId, userId) > 0;
    }

    @Override
    public boolean clearCart(Long userId) {
        return cartMapper.deleteByUserId(userId) >= 0;
    }
}
