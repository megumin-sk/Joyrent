package com.rent.service;

import com.nimbusds.jose.JOSEException;

import java.util.Map;

/**
* @author jie17
* @description 针对表【user_face】的数据库操作Service
* @createDate 2025-11-19 20:05:54
*/
public interface UserFaceService {
    /**
     * 人脸检测
     * @param imageBase64 图片base64编码
     * @return 检测结果
     */
    Map<String, Object> detectFace(String imageBase64);
    /**
     * 人脸注册
     * @param imageBase64 图片base64编码
     * @param userId 用户ID
     * @return 注册结果
     */
    Map<String, Object> registerFace(String imageBase64, String userId);

    /**
     * 人脸识别
     * @param imageBase64 图片base64编码
     * @return 识别结果
     */
    Map<String, Object> recognizeFace(String imageBase64);
    /**
     * 获取人脸库用户列表
     * @return 用户列表
     */
    Map<String, Object> getFaceUserList();

    /**
     * 删除人脸库用户
     * @param userId 用户ID
     * @return 删除结果
     */
    Map<String, Object> deleteFaceUser(String userId);


    /**
     * 调用百度的人脸识别api进行验证登录
     */
    Map<String, Object> callBaidu(String imageBase64) throws InterruptedException, JOSEException;

    /**
     * 检查用户是否已注册人脸
     * @param userId 用户ID
     * @return 是否已注册
     */
    boolean isFaceRegistered(String userId);
}
