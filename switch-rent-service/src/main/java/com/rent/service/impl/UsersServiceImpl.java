package com.rent.service.impl;

import cn.hutool.crypto.digest.DigestUtil;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.nimbusds.jose.JOSEException;
import com.rent.common.entity.Users;
import com.rent.common.utils.ResponseEnum;
import com.rent.common.utils.ResponseUtil;
import com.rent.mapper.UsersMapper;
import com.rent.service.UsersService;
import com.rent.utils.JwtUtil;
import org.springframework.stereotype.Service;

import javax.annotation.Resource;
import java.util.HashMap;
import java.util.Map;

/**
 * @author jie17
 * @description 针对表【users(用户表)】的数据库操作Service实现
 */
@Service
public class UsersServiceImpl extends ServiceImpl<UsersMapper, Users>
        implements UsersService {
    @Resource
    private UsersMapper usersMapper;

    @Override
    public ResponseUtil loginByAdmin(String username, String password) {
        Users user = usersMapper.loginByAdmin(username);
        if (user == null) {
            return ResponseUtil.get(ResponseEnum.USER_NOT_EXIST);
        }
        String requestPassword = DigestUtil.md5Hex(password);
        if (!requestPassword.equalsIgnoreCase(user.getPassword())) {
            return ResponseUtil.get(ResponseEnum.USER_PASSWORD_ERROR);
        }
        user.setPassword(null);
        try {
            Map<String, Object> payload = new HashMap<>();
            payload.put("id", user.getId());
            payload.put("username", user.getUsername());
            String token = JwtUtil.getToken(payload);

            Map<String, Object> result = new HashMap<>();
            result.put("user", user);
            result.put("token", token);
            return ResponseUtil.get(ResponseEnum.SUCCESS, result);
        } catch (JOSEException e) {
            throw new RuntimeException("Failed to generate token", e);
        }
    }

    @Override
    public ResponseUtil queryUserNum() {
        return ResponseUtil.get(ResponseEnum.SUCCESS, usersMapper.queryUserNum());
    }

    @Override
    public ResponseUtil loginByUserPhone(String phone, String password) {
        Users user = usersMapper.loginByUserPhone(phone);
        if (user == null) {
            return ResponseUtil.get(ResponseEnum.USER_NOT_EXIST);
        }
        String requestPassword = DigestUtil.md5Hex(password);
        if (!requestPassword.equalsIgnoreCase(user.getPassword())) {
            return ResponseUtil.get(ResponseEnum.USER_PASSWORD_ERROR);
        }
        user.setPassword(null);
        try {
            Map<String, Object> payload = new HashMap<>();
            payload.put("id", user.getId());
            payload.put("username", user.getUsername());
            String token = JwtUtil.getToken(payload);

            Map<String, Object> result = new HashMap<>();
            result.put("user", user);
            result.put("token", token);
            return ResponseUtil.get(ResponseEnum.SUCCESS, result);
        } catch (JOSEException e) {
            throw new RuntimeException("Failed to generate token", e);
        }
    }

    @Override
    public ResponseUtil getUserById(Long id) {
        Users user = usersMapper.getUserById(id);
        if (user == null) {
            return ResponseUtil.get(ResponseEnum.USER_NOT_EXIST);
        }
        // 清除密码字段,保护用户隐私
        user.setPassword(null);
        return ResponseUtil.get(ResponseEnum.SUCCESS, user);
    }
}
