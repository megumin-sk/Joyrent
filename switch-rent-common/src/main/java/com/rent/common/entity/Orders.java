package com.rent.common.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;
import lombok.Data;

/**
 * 主订单
 * @TableName orders
 */
@TableName(value ="orders")
@Data
public class Orders implements Serializable {
    /**
     * 
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 
     */
    private Long userId;

    /**
     * 关联地址ID
     */
    private Long addressId;

    /**
     * 10=待支付, 20=待发货, 30=租赁中, 40=归还中, 50=完成, 60=取消
     */
    private Integer status;

    /**
     * 总租金
     */
    private BigDecimal totalRentFee;

    /**
     * 总押金
     */
    private BigDecimal totalDeposit;

    /**
     * 实付金额
     */
    private BigDecimal payAmount;

    /**
     * 
     */
    private String trackingNumberSend;

    /**
     * 
     */
    private String trackingNumberReturn;

    /**
     * 
     */
    private Date createdAt;

    /**
     * 
     */
    private Date payTime;

    /**
     * 
     */
    private Date finishedTime;

    @TableField(exist = false)
    private static final long serialVersionUID = 1L;

    @Override
    public boolean equals(Object that) {
        if (this == that) {
            return true;
        }
        if (that == null) {
            return false;
        }
        if (getClass() != that.getClass()) {
            return false;
        }
        Orders other = (Orders) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getUserId() == null ? other.getUserId() == null : this.getUserId().equals(other.getUserId()))
            && (this.getAddressId() == null ? other.getAddressId() == null : this.getAddressId().equals(other.getAddressId()))
            && (this.getStatus() == null ? other.getStatus() == null : this.getStatus().equals(other.getStatus()))
            && (this.getTotalRentFee() == null ? other.getTotalRentFee() == null : this.getTotalRentFee().equals(other.getTotalRentFee()))
            && (this.getTotalDeposit() == null ? other.getTotalDeposit() == null : this.getTotalDeposit().equals(other.getTotalDeposit()))
            && (this.getPayAmount() == null ? other.getPayAmount() == null : this.getPayAmount().equals(other.getPayAmount()))
            && (this.getTrackingNumberSend() == null ? other.getTrackingNumberSend() == null : this.getTrackingNumberSend().equals(other.getTrackingNumberSend()))
            && (this.getTrackingNumberReturn() == null ? other.getTrackingNumberReturn() == null : this.getTrackingNumberReturn().equals(other.getTrackingNumberReturn()))
            && (this.getCreatedAt() == null ? other.getCreatedAt() == null : this.getCreatedAt().equals(other.getCreatedAt()))
            && (this.getPayTime() == null ? other.getPayTime() == null : this.getPayTime().equals(other.getPayTime()))
            && (this.getFinishedTime() == null ? other.getFinishedTime() == null : this.getFinishedTime().equals(other.getFinishedTime()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getUserId() == null) ? 0 : getUserId().hashCode());
        result = prime * result + ((getAddressId() == null) ? 0 : getAddressId().hashCode());
        result = prime * result + ((getStatus() == null) ? 0 : getStatus().hashCode());
        result = prime * result + ((getTotalRentFee() == null) ? 0 : getTotalRentFee().hashCode());
        result = prime * result + ((getTotalDeposit() == null) ? 0 : getTotalDeposit().hashCode());
        result = prime * result + ((getPayAmount() == null) ? 0 : getPayAmount().hashCode());
        result = prime * result + ((getTrackingNumberSend() == null) ? 0 : getTrackingNumberSend().hashCode());
        result = prime * result + ((getTrackingNumberReturn() == null) ? 0 : getTrackingNumberReturn().hashCode());
        result = prime * result + ((getCreatedAt() == null) ? 0 : getCreatedAt().hashCode());
        result = prime * result + ((getPayTime() == null) ? 0 : getPayTime().hashCode());
        result = prime * result + ((getFinishedTime() == null) ? 0 : getFinishedTime().hashCode());
        return result;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(getClass().getSimpleName());
        sb.append(" [");
        sb.append("Hash = ").append(hashCode());
        sb.append(", id=").append(id);
        sb.append(", userId=").append(userId);
        sb.append(", addressId=").append(addressId);
        sb.append(", status=").append(status);
        sb.append(", totalRentFee=").append(totalRentFee);
        sb.append(", totalDeposit=").append(totalDeposit);
        sb.append(", payAmount=").append(payAmount);
        sb.append(", trackingNumberSend=").append(trackingNumberSend);
        sb.append(", trackingNumberReturn=").append(trackingNumberReturn);
        sb.append(", createdAt=").append(createdAt);
        sb.append(", payTime=").append(payTime);
        sb.append(", finishedTime=").append(finishedTime);
        sb.append(", serialVersionUID=").append(serialVersionUID);
        sb.append("]");
        return sb.toString();
    }
}