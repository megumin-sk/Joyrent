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
 * 游戏评价表(含AI分析)
 * @TableName game_reviews
 */
@TableName(value ="game_reviews")
@Data
public class GameReviews implements Serializable {
    /**
     * 
     */
    @TableId(type = IdType.AUTO)
    private Long id;

    /**
     * 评价人ID
     */
    private Long userId;

    /**
     * 被评价的游戏ID
     */
    private Long gameId;

    /**
     * 关联订单ID
     */
    private Long orderId;

    /**
     * 用户打分: 1-5 星
     */
    private Integer rating;

    /**
     * 评价内容
     */
    private String content;

    /**
     * SVM判断: 1=垃圾/广告, 0=正常
     */
    private Integer aiJudge;

    /**
     * BERT情感分析结果(JSON): 包含8个维度的详细评价
     */
    private Object aiEmotion;

    /**
     * BERT置信度分数 (0-1)
     */
    private BigDecimal aiScore;

    /**
     * 最终显示状态 (1=隐藏)
     */
    private Integer isHidden;

    // --- 新增维度字段 (0=差, 1=中, 2=好, 3=无) ---
    private Integer dimLogistics;
    private Integer dimCondition;
    private Integer dimService;
    private Integer dimPrice;
    private Integer dimGameplay;
    private Integer dimVisuals;
    private Integer dimStory;
    private Integer dimAudio;

    /**
     * 
     */
    private Date createdAt;

    /**
     * 更新时间
     */
    private Date updatedAt;

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
        GameReviews other = (GameReviews) that;
        return (this.getId() == null ? other.getId() == null : this.getId().equals(other.getId()))
            && (this.getUserId() == null ? other.getUserId() == null : this.getUserId().equals(other.getUserId()))
            && (this.getGameId() == null ? other.getGameId() == null : this.getGameId().equals(other.getGameId()))
            && (this.getOrderId() == null ? other.getOrderId() == null : this.getOrderId().equals(other.getOrderId()))
            && (this.getRating() == null ? other.getRating() == null : this.getRating().equals(other.getRating()))
            && (this.getContent() == null ? other.getContent() == null : this.getContent().equals(other.getContent()))
            && (this.getAiJudge() == null ? other.getAiJudge() == null : this.getAiJudge().equals(other.getAiJudge()))
            && (this.getAiEmotion() == null ? other.getAiEmotion() == null : this.getAiEmotion().equals(other.getAiEmotion()))
            && (this.getAiScore() == null ? other.getAiScore() == null : this.getAiScore().equals(other.getAiScore()))
            && (this.getIsHidden() == null ? other.getIsHidden() == null : this.getIsHidden().equals(other.getIsHidden()))
            && (this.getCreatedAt() == null ? other.getCreatedAt() == null : this.getCreatedAt().equals(other.getCreatedAt()))
            && (this.getUpdatedAt() == null ? other.getUpdatedAt() == null : this.getUpdatedAt().equals(other.getUpdatedAt()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getId() == null) ? 0 : getId().hashCode());
        result = prime * result + ((getUserId() == null) ? 0 : getUserId().hashCode());
        result = prime * result + ((getGameId() == null) ? 0 : getGameId().hashCode());
        result = prime * result + ((getOrderId() == null) ? 0 : getOrderId().hashCode());
        result = prime * result + ((getRating() == null) ? 0 : getRating().hashCode());
        result = prime * result + ((getContent() == null) ? 0 : getContent().hashCode());
        result = prime * result + ((getAiJudge() == null) ? 0 : getAiJudge().hashCode());
        result = prime * result + ((getAiEmotion() == null) ? 0 : getAiEmotion().hashCode());
        result = prime * result + ((getAiScore() == null) ? 0 : getAiScore().hashCode());
        result = prime * result + ((getIsHidden() == null) ? 0 : getIsHidden().hashCode());
        result = prime * result + ((getCreatedAt() == null) ? 0 : getCreatedAt().hashCode());
        result = prime * result + ((getUpdatedAt() == null) ? 0 : getUpdatedAt().hashCode());
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
        sb.append(", gameId=").append(gameId);
        sb.append(", orderId=").append(orderId);
        sb.append(", rating=").append(rating);
        sb.append(", content=").append(content);
        sb.append(", aiJudge=").append(aiJudge);
        sb.append(", aiEmotion=").append(aiEmotion);
        sb.append(", aiScore=").append(aiScore);
        sb.append(", isHidden=").append(isHidden);
        sb.append(", createdAt=").append(createdAt);
        sb.append(", updatedAt=").append(updatedAt);
        sb.append(", serialVersionUID=").append(serialVersionUID);
        sb.append("]");
        return sb.toString();
    }
}