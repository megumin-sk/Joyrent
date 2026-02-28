package com.rent.common.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.io.Serializable;
import java.math.BigDecimal;
import java.util.Date;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 游戏库
 * @TableName games
 */
@TableName(value ="games")
@Data
public class Games implements Serializable {
    /**
     * 
     */
    @Schema(description = "游戏ID", example = "1")
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 
     */
    @Schema(description = "游戏名称", example = "塞尔达传说：荒野之息")
    private String title;

    /**
     * 
     */
    @Schema(description = "游戏平台", example = "Switch")
    private String platform;

    /**
     * 
     */
    @Schema(description = "封面图地址")
    private String coverUrl;

    /**
     * 
     */
    @Schema(description = "游戏描述")
    private String description;

    /**
     * 日租金
     */
    @Schema(description = "日租金")
    private BigDecimal dailyRentPrice;

    /**
     * 押金
     */
    @Schema(description = "押金")
    private BigDecimal depositPrice;

    /**
     * 可用库存
     */
    @Schema(description = "可用库存")
    private Integer availableStock;

    /**
     * 1=上架, 0=下架
     */
    @Schema(description = "状态 (1:上架, 0:下架)")
    private Integer status;

    /**
     * 
     */
    private Date createdAt;

    /**
     * 
     */
    private Date updatedAt;

    /**
     * 累计租赁次数
     */
    @Schema(description = "累计租赁次数")
    private Integer totalRentCount;

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
        Games other = (Games) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getTitle() == null ? other.getTitle() == null : this.getTitle().equals(other.getTitle()))
            && (this.getPlatform() == null ? other.getPlatform() == null : this.getPlatform().equals(other.getPlatform()))
            && (this.getCoverUrl() == null ? other.getCoverUrl() == null : this.getCoverUrl().equals(other.getCoverUrl()))
            && (this.getDescription() == null ? other.getDescription() == null : this.getDescription().equals(other.getDescription()))
            && (this.getDailyRentPrice() == null ? other.getDailyRentPrice() == null : this.getDailyRentPrice().equals(other.getDailyRentPrice()))
            && (this.getDepositPrice() == null ? other.getDepositPrice() == null : this.getDepositPrice().equals(other.getDepositPrice()))
            && (this.getAvailableStock() == null ? other.getAvailableStock() == null : this.getAvailableStock().equals(other.getAvailableStock()))
            && (this.getStatus() == null ? other.getStatus() == null : this.getStatus().equals(other.getStatus()))
            && (this.getCreatedAt() == null ? other.getCreatedAt() == null : this.getCreatedAt().equals(other.getCreatedAt()))
            && (this.getUpdatedAt() == null ? other.getUpdatedAt() == null : this.getUpdatedAt().equals(other.getUpdatedAt()))
            && (this.getTotalRentCount() == null ? other.getTotalRentCount() == null : this.getTotalRentCount().equals(other.getTotalRentCount()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getTitle() == null) ? 0 : getTitle().hashCode());
        result = prime * result + ((getPlatform() == null) ? 0 : getPlatform().hashCode());
        result = prime * result + ((getCoverUrl() == null) ? 0 : getCoverUrl().hashCode());
        result = prime * result + ((getDescription() == null) ? 0 : getDescription().hashCode());
        result = prime * result + ((getDailyRentPrice() == null) ? 0 : getDailyRentPrice().hashCode());
        result = prime * result + ((getDepositPrice() == null) ? 0 : getDepositPrice().hashCode());
        result = prime * result + ((getAvailableStock() == null) ? 0 : getAvailableStock().hashCode());
        result = prime * result + ((getStatus() == null) ? 0 : getStatus().hashCode());
        result = prime * result + ((getCreatedAt() == null) ? 0 : getCreatedAt().hashCode());
        result = prime * result + ((getUpdatedAt() == null) ? 0 : getUpdatedAt().hashCode());
        result = prime * result + ((getTotalRentCount() == null) ? 0 : getTotalRentCount().hashCode());
        return result;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(getClass().getSimpleName());
        sb.append(" [");
        sb.append("Hash = ").append(hashCode());
        sb.append(", id=").append(id);
        sb.append(", title=").append(title);
        sb.append(", platform=").append(platform);
        sb.append(", coverUrl=").append(coverUrl);
        sb.append(", description=").append(description);
        sb.append(", dailyRentPrice=").append(dailyRentPrice);
        sb.append(", depositPrice=").append(depositPrice);
        sb.append(", availableStock=").append(availableStock);
        sb.append(", status=").append(status);
        sb.append(", createdAt=").append(createdAt);
        sb.append(", updatedAt=").append(updatedAt);
        sb.append(", totalRentCount=").append(totalRentCount);
        sb.append(", serialVersionUID=").append(serialVersionUID);
        sb.append("]");
        return sb.toString();
    }
}