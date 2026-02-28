package com.rent.mapper;

import com.rent.common.entity.Cart;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

/**
 * 购物车 Mapper
 */
public interface CartMapper extends BaseMapper<Cart> {

    /**
     * 根据用户ID和游戏ID查询购物车
     */
    Cart selectByUserAndGame(@Param("userId") Long userId, @Param("gameId") Long gameId);

    /**
     * 查询用户购物车列表(含游戏信息)
     */
    List<Map<String, Object>> selectCartWithGame(@Param("userId") Long userId);

    /**
     * 新增购物车
     */
    int insertCart(Cart cart);

    /**
     * 更新租期
     */
    int updateRentDays(@Param("id") Long id, @Param("userId") Long userId, @Param("rentDays") Integer rentDays);

    /**
     * 删除购物车项
     */
    int deleteByIdAndUser(@Param("id") Long id, @Param("userId") Long userId);

    /**
     * 清空用户购物车
     */
    int deleteByUserId(@Param("userId") Long userId);
}
