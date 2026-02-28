package com.rent.dto;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * 管理员登录请求体。
 */
@Data
public class AdminLoginRequest {
    @Schema(description = "管理员账号")
    private String username;

    @Schema(description = "管理员密码")
    private String password;
}

