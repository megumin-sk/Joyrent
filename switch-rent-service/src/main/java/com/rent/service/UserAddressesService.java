package com.rent.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.rent.common.entity.UserAddresses;

/**
* @author jie17
* @description 针对表【user_addresses(地址簿)】的数据库操作Service
* @createDate 2025-11-18 23:33:58
*/
public interface UserAddressesService extends IService<UserAddresses> {

    /**
     * 设置默认地址
     * @param userId 用户ID
     * @param addressId 地址ID
     * @return 是否成功
     */
    boolean setDefaultAddress(Long userId, Long addressId);
}
