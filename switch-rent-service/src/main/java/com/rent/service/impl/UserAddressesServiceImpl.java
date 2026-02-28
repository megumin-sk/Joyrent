package com.rent.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rent.common.entity.UserAddresses;
import com.rent.mapper.UserAddressesMapper;
import com.rent.service.UserAddressesService;
import org.springframework.stereotype.Service;

import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import org.springframework.transaction.annotation.Transactional;

/**
* @author jie17
* @description 针对表【user_addresses(地址簿)】的数据库操作Service实现
* @createDate 2025-11-18 23:33:58
*/
@Service
public class UserAddressesServiceImpl extends ServiceImpl<UserAddressesMapper, UserAddresses>
    implements UserAddressesService {

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean setDefaultAddress(Long userId, Long addressId) {
        // 1. 将该用户所有地址设为非默认
        UpdateWrapper<UserAddresses> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("user_id", userId).set("is_default", 0);
        this.update(updateWrapper);

        // 2. 将指定地址设为默认
        UserAddresses address = new UserAddresses();
        address.setId(addressId);
        address.setIsDefault(1);
        return this.updateById(address);
    }
}




