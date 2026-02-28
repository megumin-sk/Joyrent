package com.rent.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.rent.common.entity.Users;

/**
 * @author jie17
 * @description 针对表【users(用户表)】的数据库操作Mapper
 * @createDate 2025-11-18 23:33:58
 * @Entity com.rent.common.entity.Users
 */
public interface UsersMapper extends BaseMapper<Users> {
    Users loginByAdmin(String username);

    Integer queryUserNum();

    Users loginByUserPhone(String phone);

    Users getUserById(Long id);

}
