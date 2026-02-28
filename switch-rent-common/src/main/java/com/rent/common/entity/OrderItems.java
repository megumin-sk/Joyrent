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
 * 订单明细
 * @TableName order_items
 */
@TableName(value ="order_items")
@Data
public class OrderItems implements Serializable {
    /**
     * 
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 
     */
    private Long orderId;

    /**
     * 
     */
    private Long gameId;

    /**
     * 发货后填入
     */
    private Long gameItemId;

    /**
     * 日租金(快照)
     */
    private BigDecimal dailyRentPrice;

    /**
     * 小计
     */
    private BigDecimal subTotal;

    /**
     * 租期(天)
     */
    private Integer rentDays;

    /**
     * 起租日
     */
    private Date startDate;

    /**
     * 预计归还日
     */
    private Date planEndDate;

    /**
     * 实际归还日
     */
    private Date actualEndDate;

    /**
     * 逾期费
     */
    private BigDecimal lateFee;

    /**
     * 赔偿金
     */
    private BigDecimal damageFee;

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
        OrderItems other = (OrderItems) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getOrderId() == null ? other.getOrderId() == null : this.getOrderId().equals(other.getOrderId()))
            && (this.getGameId() == null ? other.getGameId() == null : this.getGameId().equals(other.getGameId()))
            && (this.getGameItemId() == null ? other.getGameItemId() == null : this.getGameItemId().equals(other.getGameItemId()))
            && (this.getRentDays() == null ? other.getRentDays() == null : this.getRentDays().equals(other.getRentDays()))
            && (this.getStartDate() == null ? other.getStartDate() == null : this.getStartDate().equals(other.getStartDate()))
            && (this.getPlanEndDate() == null ? other.getPlanEndDate() == null : this.getPlanEndDate().equals(other.getPlanEndDate()))
            && (this.getActualEndDate() == null ? other.getActualEndDate() == null : this.getActualEndDate().equals(other.getActualEndDate()))
            && (this.getLateFee() == null ? other.getLateFee() == null : this.getLateFee().equals(other.getLateFee()))
            && (this.getDamageFee() == null ? other.getDamageFee() == null : this.getDamageFee().equals(other.getDamageFee()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getOrderId() == null) ? 0 : getOrderId().hashCode());
        result = prime * result + ((getGameId() == null) ? 0 : getGameId().hashCode());
        result = prime * result + ((getGameItemId() == null) ? 0 : getGameItemId().hashCode());
        result = prime * result + ((getRentDays() == null) ? 0 : getRentDays().hashCode());
        result = prime * result + ((getStartDate() == null) ? 0 : getStartDate().hashCode());
        result = prime * result + ((getPlanEndDate() == null) ? 0 : getPlanEndDate().hashCode());
        result = prime * result + ((getActualEndDate() == null) ? 0 : getActualEndDate().hashCode());
        result = prime * result + ((getLateFee() == null) ? 0 : getLateFee().hashCode());
        result = prime * result + ((getDamageFee() == null) ? 0 : getDamageFee().hashCode());
        return result;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(getClass().getSimpleName());
        sb.append(" [");
        sb.append("Hash = ").append(hashCode());
        sb.append(", id=").append(id);
        sb.append(", orderId=").append(orderId);
        sb.append(", gameId=").append(gameId);
        sb.append(", gameItemId=").append(gameItemId);
        sb.append(", rentDays=").append(rentDays);
        sb.append(", startDate=").append(startDate);
        sb.append(", planEndDate=").append(planEndDate);
        sb.append(", actualEndDate=").append(actualEndDate);
        sb.append(", lateFee=").append(lateFee);
        sb.append(", damageFee=").append(damageFee);
        sb.append(", serialVersionUID=").append(serialVersionUID);
        sb.append("]");
        return sb.toString();
    }
}