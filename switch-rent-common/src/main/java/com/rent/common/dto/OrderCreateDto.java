package com.rent.common.dto;

import lombok.Data;
import java.io.Serializable;
import java.util.List;

/**
 * 订单创建请求参数
 */
@Data
public class OrderCreateDto implements Serializable {
    /**
     * 收货地址ID
     */
    private Long addressId;

    /**
     * 购物车ID列表
     */
    private List<Long> cartIds;

    /**
     * 订单备注
     */
    private String remark;
}
