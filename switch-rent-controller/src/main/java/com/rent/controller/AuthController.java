package com.rent.controller;

import com.rent.common.utils.ResponseEnum;
import com.rent.common.utils.ResponseUtil;
import com.rent.dto.AdminLoginRequest;
import com.rent.dto.UserLoginRequest;
import com.rent.service.UsersService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

import com.rent.common.exception.CustomException;

import javax.annotation.Resource;

/**
 * 授权认证相关接口。
 */
@Tag(name = "Auth", description = "认证授权接口")
@RestController
@RequestMapping("/auth")
public class AuthController {

    @Resource
    private UsersService usersService;

    @Operation(summary = "管理员登录", description = "管理员使用账号密码登录，后台自动进行 MD5 校验")
    @PostMapping("/login/admin")
    public ResponseUtil adminLogin(@RequestBody AdminLoginRequest request) {
        return usersService.loginByAdmin(request.getUsername(), request.getPassword());
    }

    @Operation(summary = "用户登录", description = "用户使用手机号和密码登录，后台自动进行 MD5 校验")
    @PostMapping("/login/user")
    public ResponseUtil userLogin(@RequestBody UserLoginRequest request) {
        return usersService.loginByUserPhone(request.getPhone(), request.getPassword());
    }

    @Operation(summary = "查询用户数量", description = "查询用户数量")
    @GetMapping("/user/number")
    public ResponseUtil queryUserNum() {
        return ResponseUtil.get(ResponseEnum.SUCCESS, usersService.queryUserNum());
    }

    @Operation(summary = "根据用户ID查询用户信息", description = "根据用户ID查询用户详细信息,返回数据不包含密码")
    @GetMapping("/user/{id}")
    public ResponseUtil getUserById(@PathVariable Long id) {
        return usersService.getUserById(id);
    }

    @Operation(summary = "测试自定义异常", description = "用于验证全局异常处理")
    @GetMapping("/test/exception")
    public ResponseUtil testException() {
        throw new CustomException(999, "测试自定义异常");
    }
}
