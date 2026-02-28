package com.rent.common.exception;

import com.rent.common.utils.ResponseEnum;
import lombok.Data;
import lombok.EqualsAndHashCode;

@EqualsAndHashCode(callSuper = true)
@Data
public class CustomException extends RuntimeException {
    private Integer code;
    private String msg;

    public CustomException(Integer code, String msg) {
        super(msg);
        this.code = code;
        this.msg = msg;
    }

    public CustomException(ResponseEnum responseEnum) {
        super(responseEnum.getMsg());
        this.code = responseEnum.getCode();
        this.msg = responseEnum.getMsg();
    }
}
