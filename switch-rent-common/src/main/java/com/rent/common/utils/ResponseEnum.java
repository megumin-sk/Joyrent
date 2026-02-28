package com.rent.common.utils;

import lombok.Getter;

@Getter
public enum ResponseEnum {
    // 通用响应码
    SUCCESS(200, "操作成功"),
    FAIL(500, "操作失败"),
    // 用户响应码
    USER_NOT_EXIST(1001, "用户不存在"),
    USER_PASSWORD_ERROR(1002, "用户密码错误"),
    USER_NOT_LOGIN(401, "用户未登录"),
    NO_PERMISSION(403, "无权限操作"),
    PARAM_ERROR(400, "参数错误"),

    // 业务响应码 - 游戏/租赁
    GAME_NOT_EXIST(3001, "游戏不存在"),
    GAME_NOT_ENOUGH(3002, "游戏库存不足"),
    GAME_RENTED(3003, "游戏已被租出"),

    // 业务响应码 - 订单
    ORDER_NOT_EXIST(4001, "订单不存在"),
    ORDER_STATUS_ERROR(4002, "订单状态异常"),

    // 人脸识别响应码
    FACE_DETECT_FAILED(2001, "未检测到人脸或人脸质量不佳"),
    FACE_REGISTER_FAILED(2002, "人脸注册失败"),
    FACE_RECOGNIZE_FAILED(2003, "人脸识别失败"),
    
    // 系统
    CUSTOM_ERROR(999, "系统未知异常");

    private Integer code;
    private String msg;

    ResponseEnum(Integer code, String msg) {
        this.code = code;
        this.msg = msg;
    }
}
