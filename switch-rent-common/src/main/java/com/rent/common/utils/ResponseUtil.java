package com.rent.common.utils;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.ToString;

/**
 * @Classname ResponseUtil
 * @Description TODO
 * @Date 2025/8/12 11:23
 * @Created by pc
 */
@Data
@ToString
@NoArgsConstructor
@AllArgsConstructor
public class ResponseUtil {
    private Integer code;
    private String msg;
    private Object data;

    public ResponseUtil(Integer code, String msg) {
        this.code = code;
        this.msg = msg;
    }

    // 带参数的返回
    public static ResponseUtil get(ResponseEnum responseEnum,Object object){
        return  new ResponseUtil(responseEnum.getCode(), responseEnum.getMsg(),object);
    }
    // 不带参数的返回
    public static ResponseUtil get(ResponseEnum responseEnum){
        return  new ResponseUtil(responseEnum.getCode(), responseEnum.getMsg());
    }
}
