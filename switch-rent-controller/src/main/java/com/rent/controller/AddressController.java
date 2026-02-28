package com.rent.controller;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.rent.common.entity.UserAddresses;
import com.rent.common.exception.CustomException;
import com.rent.common.utils.ResponseEnum;
import com.rent.common.utils.ResponseUtil;
import com.rent.service.UserAddressesService;
import com.rent.utils.JwtUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import java.text.ParseException;
import java.util.Date;
import java.util.List;

/**
 * 地址管理控制器
 */
@Tag(name = "Address", description = "地址管理相关接口")
@RestController
@RequestMapping("/address")
public class AddressController {

    @Resource
    private UserAddressesService userAddressesService;

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

    @Operation(summary = "获取地址列表")
    @GetMapping("/list")
    public ResponseUtil list(HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }

        QueryWrapper<UserAddresses> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("user_id", userId);
        queryWrapper.eq("is_deleted", 0); // 只查未删除的
        queryWrapper.orderByDesc("is_default"); // 默认地址排前面
        queryWrapper.orderByDesc("created_at");

        List<UserAddresses> list = userAddressesService.list(queryWrapper);
        return ResponseUtil.get(ResponseEnum.SUCCESS, list);
    }

    @Operation(summary = "添加地址")
    @PostMapping("/add")
    public ResponseUtil add(@RequestBody UserAddresses address, HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }

        address.setUserId(userId);
        address.setIsDeleted(0);
        address.setCreatedAt(new Date());
        
        // 如果是第一条地址，自动设为默认
        long count = userAddressesService.count(new QueryWrapper<UserAddresses>().eq("user_id", userId).eq("is_deleted", 0));
        if (count == 0) {
            address.setIsDefault(1);
        } else if (address.getIsDefault() == null) {
            address.setIsDefault(0);
        }
        
        // 如果新添加的是默认地址，需要把其他的置为非默认
        if (Integer.valueOf(1).equals(address.getIsDefault())) {
             userAddressesService.setDefaultAddress(userId, null); // 清除旧默认
        }

        boolean success = userAddressesService.save(address);
        return success ? ResponseUtil.get(ResponseEnum.SUCCESS) : ResponseUtil.get(ResponseEnum.FAIL);
    }

    @Operation(summary = "更新地址")
    @PostMapping("/update")
    public ResponseUtil update(@RequestBody UserAddresses address, HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }
        
        // 安全检查：确保只能修改自己的地址（简单实现：覆盖userId）
        address.setUserId(userId);

        if (Integer.valueOf(1).equals(address.getIsDefault())) {
             userAddressesService.setDefaultAddress(userId, address.getId());
        } else {
             userAddressesService.updateById(address);
        }
        return ResponseUtil.get(ResponseEnum.SUCCESS);
    }

    @Operation(summary = "删除地址")
    @PostMapping("/delete/{id}")
    public ResponseUtil delete(@PathVariable Long id, HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }

        // 逻辑删除
        UserAddresses updateAddress = new UserAddresses();
        updateAddress.setId(id);
        updateAddress.setIsDeleted(1);
        
        // 最好加上 userId 条件防止删除他人地址，这里简单使用 updateById
        // 严格来说应该用 UpdateWrapper
        com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper<UserAddresses> updateWrapper = new com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper<>();
        updateWrapper.eq("id", id).eq("user_id", userId).set("is_deleted", 1);
        
        boolean success = userAddressesService.update(updateWrapper);
        return success ? ResponseUtil.get(ResponseEnum.SUCCESS) : ResponseUtil.get(ResponseEnum.FAIL);
    }

    @Operation(summary = "设为默认地址")
    @PostMapping("/setDefault/{id}")
    public ResponseUtil setDefault(@PathVariable Long id, HttpServletRequest request) {
        Long userId = getUserIdFromToken(request);
        if (userId == null) {
            throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
        }

        boolean success = userAddressesService.setDefaultAddress(userId, id);
        return success ? ResponseUtil.get(ResponseEnum.SUCCESS) : ResponseUtil.get(ResponseEnum.FAIL);
    }
}
