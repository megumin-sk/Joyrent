package com.rent.common.entity;

import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.io.Serializable;

/**
 * 人脸识别信息表
 * @TableName face_recognition
 */
@TableName(value ="face_recognition")
@Data
public class FaceRecognition implements Serializable {
    /**
     * 用户ID
     */
    private Integer userId;

    /**
     * 人脸特征信息（如向量数据、Base64编码等）
     */
    private String faceInfo;

    /**
     * 人脸状态启用标识：1-启用，0-禁用
     */
    private Integer faceEnable;

    /**
     * 云端的人脸库ID
     */
    private Integer faceId;

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
        FaceRecognition other = (FaceRecognition) that;
        return (this.getUserId() == null ? other.getUserId() == null : this.getUserId().equals(other.getUserId()))
                && (this.getFaceInfo() == null ? other.getFaceInfo() == null : this.getFaceInfo().equals(other.getFaceInfo()))
                && (this.getFaceEnable() == null ? other.getFaceEnable() == null : this.getFaceEnable().equals(other.getFaceEnable()))
                && (this.getFaceId() == null ? other.getFaceId() == null : this.getFaceId().equals(other.getFaceId()));
    }

    @Override
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + ((getUserId() == null) ? 0 : getUserId().hashCode());
        result = prime * result + ((getFaceInfo() == null) ? 0 : getFaceInfo().hashCode());
        result = prime * result + ((getFaceEnable() == null) ? 0 : getFaceEnable().hashCode());
        result = prime * result + ((getFaceId() == null) ? 0 : getFaceId().hashCode());
        return result;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append(getClass().getSimpleName());
        sb.append(" [");
        sb.append("Hash = ").append(hashCode());
        sb.append(", userId=").append(userId);
        sb.append(", faceInfo=").append(faceInfo);
        sb.append(", faceEnable=").append(faceEnable);
        sb.append(", faceId=").append(faceId);
        sb.append(", serialVersionUID=").append(serialVersionUID);
        sb.append("]");
        return sb.toString();
    }
}