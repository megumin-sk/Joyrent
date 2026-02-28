package com.rent.config;

import com.rent.interceptor.JwtInterceptor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import org.springframework.web.servlet.config.annotation.CorsRegistry;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new JwtInterceptor())
                .addPathPatterns("/**") // 拦截所有请求
                .excludePathPatterns( // 配置白名单
                        "/auth/login/**", // 登录接口
                        "/doc.html", // Swagger/Knife4j
                        "/webjars/**",
                        "/swagger-resources/**",
                        "/v3/api-docs/**",
                        "/favicon.ico",
                        "/games/top-rented", // 热门游戏
                        "/games/all", // 所有游戏
                        "/games/searchByName/**", // 搜索游戏
                        "/games/searchByPlatform/**", // 平台游戏
                        "/games/*", // 单个游戏详情
                        "/face/**"
                );
    }

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOriginPatterns("*")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
    }
}
