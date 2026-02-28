package com.rent.interceptor;

import com.rent.common.utils.ResponseEnum;
import com.rent.common.utils.ResponseUtil;
import com.rent.utils.JwtUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.web.servlet.HandlerInterceptor;

import com.rent.common.exception.CustomException;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.PrintWriter;

public class JwtInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {
        // 1. 获取请求头中的 token
        String authHeader = request.getHeader("Authorization");

        // 2. 判断 token 是否存在
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            returnJson(response);
            return false;
        }

        // 3. 提取 token
        String token = authHeader.substring(7);

        try {
            // 4. 验证 token
            boolean verify = JwtUtil.verifyJwt(token);
            if (verify) {
                return true;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        // 5. 验证失败
        returnJson(response);
        return false;
    }

    private void returnJson(HttpServletResponse response) {
        throw new CustomException(ResponseEnum.USER_NOT_LOGIN);
    }
}
