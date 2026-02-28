package com.rent.common.utils;

import java.security.SecureRandom;
import java.util.UUID;

/**
 * ID及随机字符串生成工具类
 */
public class IdGeneratorUtil {

    private static final String CHAR_POOL = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    private static final SecureRandom RANDOM = new SecureRandom();

    /**
     * 生成随机UUID字符串（去掉连字符）
     * 长度为32位，适合作为 user_id 或 group_id
     *
     * @return 32位随机字符串
     */
    public static String generateUUID() {
        return UUID.randomUUID().toString().replace("-", "");
    }

    /**
     * 生成指定长度的随机字符串（包含数字和大小写字母）
     *
     * @param length 指定长度
     * @return 随机字符串
     */
    public static String generateRandomString(int length) {
        if (length <= 0) {
            return "";
        }
        StringBuilder sb = new StringBuilder(length);
        for (int i = 0; i < length; i++) {
            int index = RANDOM.nextInt(CHAR_POOL.length());
            sb.append(CHAR_POOL.charAt(index));
        }
        return sb.toString();
    }

    /**
     * 生成带前缀的随机ID
     * 例如：FACE_32位随机串
     *
     * @param prefix 前缀
     * @return 拼接后的ID
     */
    public static String generateIdWithPrefix(String prefix) {
        return prefix + generateUUID();
    }
}
