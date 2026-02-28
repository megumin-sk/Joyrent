package com.rent.controller;

import com.rent.common.entity.Cart;
import com.rent.common.entity.Games;
import com.rent.service.CartService;
import com.rent.service.GamesService;
import com.rent.common.utils.ResponseEnum;
import com.rent.common.utils.ResponseUtil;
import com.rent.utils.JwtUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;
import com.rent.common.exception.CustomException;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.text.ParseException;
import java.util.List;
import java.util.Map;

/**
 * 购物车控制器
 */
@Tag(name = "Cart", description = "购物车相关接口")
@RestController
@RequestMapping("/cart")
public class CartController {

    @Resource
    private CartService cartService;

    @Resource
    private GamesService gamesService;

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

    /**
     * 加入购物车
     */
    @Operation(summary = "加入购物车")
    @PostMapping("/add")
    public ResponseUtil addToCart(@RequestBody Map<String, Object> params, HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }

        Long gameId = Long.parseLong(params.get("gameId").toString());
        Integer rentDays = Integer.parseInt(params.getOrDefault("rentDays", 7).toString());

        // 检查游戏是否存在且有库存
        Games game = gamesService.getById(gameId);
        if (game == null) {
            throw new CustomException(ResponseEnum.GAME_NOT_EXIST);
        }
        if (game.getAvailableStock() == null || game.getAvailableStock() <= 0) {
            throw new CustomException(ResponseEnum.GAME_NOT_ENOUGH);
        }

        Cart cart = cartService.addToCart(userId, gameId, rentDays);
        return ResponseUtil.get(ResponseEnum.SUCCESS, cart);
    }

    /**
     * 获取购物车列表
     */
    @Operation(summary = "获取购物车列表")
    @GetMapping("/list")
    public ResponseUtil getCartList(HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }

        List<Map<String, Object>> list = cartService.getCartList(userId);
        return ResponseUtil.get(ResponseEnum.SUCCESS, list);
    }

    /**
     * 更新租期
     */
    @Operation(summary = "更新购物车租期")
    @PostMapping("/update/{id}")
    public ResponseUtil updateCartItem(@PathVariable Long id, @RequestBody Map<String, Object> params, HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }

        Integer rentDays = Integer.parseInt(params.get("rentDays").toString());
        boolean success = cartService.updateRentDays(userId, id, rentDays);
        if (success) {
            return ResponseUtil.get(ResponseEnum.SUCCESS, null);
        }
        throw new CustomException(ResponseEnum.FAIL);
    }

    /**
     * 删除购物车项
     */
    @Operation(summary = "删除购物车项")
    @DeleteMapping("/delete/{id}")
    public ResponseUtil deleteCartItem(@PathVariable Long id, HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }

        boolean success = cartService.deleteCartItem(userId, id);
        if (success) {
            return ResponseUtil.get(ResponseEnum.SUCCESS, null);
        }
        throw new CustomException(ResponseEnum.FAIL);
    }

    /**
     * 清空购物车
     */
    @Operation(summary = "清空购物车")
    @DeleteMapping("/clear")
    public ResponseUtil clearCart(HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }

        cartService.clearCart(userId);
        return ResponseUtil.get(ResponseEnum.SUCCESS, null);
    }
}
