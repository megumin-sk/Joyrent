package com.rent.utils;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.HashMap;
import java.util.Map;

/**
 * 远程调用 Python 评论分析服务的客户端
 * 采用 WebClient 实现异步非阻塞请求
 */
@Component
public class PythonCommentClient {

    @Autowired
    private WebClient webClient;

    @Value("${python.comment.url}")
    private String pythonUrl;

    /**
     * 调用 Python 接口分析评论
     * 
     * @param text 评论文本
     * @return 包含分析结果的 Map (包括 SVM 过滤状态和 BERT 多维度情感得分)
     */
    public Map<String, Object> analyzeComment(String text) {
        Map<String, String> requestBody = new HashMap<>();
        requestBody.put("text", text);

        try {
            return webClient.post()
                    .uri(pythonUrl + "/api/comment/analyze")
                    .bodyValue(requestBody)
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block(); // 在 Service 层同步阻塞获取结果
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("code", 500);
            error.put("msg", "评论分析服务调用失败: " + e.getMessage());
            Map<String, Object> fallbackResult = new HashMap<>();
            fallbackResult.put("status", "error");
            error.put("result", fallbackResult);
            return error;
        }
    }
}
