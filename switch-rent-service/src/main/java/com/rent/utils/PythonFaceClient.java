package com.rent.utils;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.HashMap;
import java.util.Map;

@Component
public class PythonFaceClient {

    @Autowired
    private WebClient webClient;

    @Value("${python.face.url}")
    private String pythonUrl;

    /**
     * 识别图像内容
     *
     * @param imageBase64 图像的Base64编码字符串
     * @return 包含识别结果的Map，如果调用失败则返回包含错误信息的Map
     */
    public Map<String, Object> recognize(String imageBase64) {
        Map<String, String> request = new HashMap<>();
        request.put("image", imageBase64); // 修改为 image

        try {
            // 使用 WebClient 发送异步 POST 请求
            return webClient.post()
                    .uri(pythonUrl + "/login") // 修改为 /login
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error_code", -1);
            error.put("error_msg", "Python 服务不可用: " + e.getMessage());
            return error;
        }
    }


    /**
     * 向Python服务注册用户图像
     *
     * @param imageBase64 用户图像的Base64编码字符串
     * @param userId 用户唯一标识符
     * @return 包含注册结果的Map，成功时返回Python服务的响应，失败时返回错误信息
     */
    public Map<String, Object> register(String imageBase64, String userId) {
        Map<String, String> request = new HashMap<>();
        request.put("image", imageBase64); 
        request.put("user_id", userId);     

        try {
            // 使用 WebClient 发送异步 POST 请求到Python服务的注册接口
            return webClient.post()
                    .uri(pythonUrl + "/register")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("error_code", -1);
            error.put("error_msg", "Python 服务不可用: " + e.getMessage());
            return error;
        }
    }

     /**
     * 删除用户信息
     * 通过调用Python服务的删除接口来删除指定用户
     *
     * @param userId 用户ID，用于标识要删除的用户
     * @return Map<String, Object> 包含删除操作结果的映射表
     *         成功时返回Python服务的响应结果
     *         失败时返回包含错误码(-1)和错误信息的映射表
     */
    public Map<String, Object> delete(String userId) {
        Map<String, String> request = new HashMap<>();
        request.put("user_id", userId);

        // 构建请求并发送到Python服务
        try {
            return webClient.post()
                    .uri(pythonUrl + "/delete")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
        } catch (Exception e) {
            // Python服务调用失败时返回错误信息
            Map<String, Object> error = new HashMap<>();
            error.put("error_code", -1);
            error.put("error_msg", "Python 服务不可用: " + e.getMessage());
            return error;
        }
    }
}
