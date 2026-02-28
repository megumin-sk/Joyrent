package com.rent.common.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.io.Serializable;

/**
 * 
 * @TableName user_face
 */
@TableName(value ="user_face")
@Data
public class UserFace implements Serializable {
    /**
     * 人脸特征向量
     */
    private String faceEncoding;

    /**
     * 人脸唯一标识
     */
    private String faceId;

    /**
     * 用户id
     */
    private Long userId;

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
        UserFace other = (UserFace) that;
        return (this.getFaceEncoding() == null ? other.getFaceEncoding() == null : this.getFaceEncoding().equals(other.getFaceEncoding()))
            && (this.getFaceId() == null ? other.getFaceId() == null : this.getFaceId().equals(other.getFaceId()))
            && (this.getUserId() == null ? other.getUserId() == null : this.getUserId().equals(other.getUserId()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getFaceEncoding() == null) ? 0 : getFaceEncoding().hashCode());
        result = prime * result + ((getFaceId() == null) ? 0 : getFaceId().hashCode());
        result = prime * result + ((getUserId() == null) ? 0 : getUserId().hashCode());
        return result;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(getClass().getSimpleName());
        sb.append(" [");
        sb.append("Hash = ").append(hashCode());
        sb.append(", faceEncoding=").append(faceEncoding);
        sb.append(", faceId=").append(faceId);
        sb.append(", userId=").append(userId);
        sb.append(", serialVersionUID=").append(serialVersionUID);
        sb.append("]");
        return sb.toString();
    }
}