package com.rent.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.rent.common.entity.Users;
import com.rent.common.utils.ResponseUtil;

/**
 * @author jie17
 * @description 针对表【users(用户表)】的数据库操作Service
 * @createDate 2025-11-18 23:33:58
 */
public interface UsersService extends IService<Users> {
    ResponseUtil loginByAdmin(String username, String password);

    ResponseUtil queryUserNum();

    ResponseUtil loginByUserPhone(String phone, String password);

    ResponseUtil getUserById(Long id);
}
