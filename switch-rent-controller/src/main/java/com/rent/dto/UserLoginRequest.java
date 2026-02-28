package com.rent.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 用户登录请求体。
 */
@Data
public class UserLoginRequest {
    @Schema(description = "用户手机号", example = "13800138000")
    private String phone;

    @Schema(description = "用户密码(明文,后台自动进行 MD5 摘要校验)", example = "123456")
    private String password;
}
