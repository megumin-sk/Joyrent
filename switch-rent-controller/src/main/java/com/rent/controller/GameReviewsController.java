package com.rent.controller;

import com.rent.common.vo.GameReviewVO;
import com.rent.common.dto.ReviewSubmitDTO;
import com.rent.service.GameReviewsService;
import com.rent.common.utils.ResponseUtil;
import com.rent.common.utils.ResponseEnum;
import com.rent.utils.JwtUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/reviews")
@Tag(name = "GameReviews", description = "游戏评价接口")
public class GameReviewsController {

    @Autowired
    private GameReviewsService gameReviewsService;

    @Operation(summary = "根据游戏ID获取评价列表")
    @GetMapping("/game/{gameId}")
    public ResponseUtil getReviewsByGameId(@PathVariable Long gameId) {
        List<GameReviewVO> list = gameReviewsService.getReviewsByGameId(gameId);
        return ResponseUtil.get(ResponseEnum.SUCCESS, list);
    }

    @Operation(summary = "提交评价")
    @PostMapping("/submit")
    public ResponseUtil submitReview(@RequestHeader("Authorization") String authHeader,
            @RequestBody ReviewSubmitDTO dto) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return ResponseUtil.get(ResponseEnum.USER_NOT_LOGIN);
        }
        String token = authHeader.substring(7); // 去掉 "Bearer " 前缀
        try {
            if (!JwtUtil.verifyJwt(token)) {
                return ResponseUtil.get(ResponseEnum.USER_NOT_LOGIN);
            }
            Map<String, Object> payload = JwtUtil.getPayload(token);
            Object idObj = payload.get("id");
            Long userId;
            if (idObj instanceof Integer) {
                userId = ((Integer) idObj).longValue();
            } else if (idObj instanceof Long) {
                userId = (Long) idObj;
            } else {
                userId = Long.valueOf(String.valueOf(idObj));
            }

            boolean success = gameReviewsService.submitReview(userId, dto);
            if (success) {
                return ResponseUtil.get(ResponseEnum.SUCCESS);
            } else {
                return ResponseUtil.get(ResponseEnum.FAIL);
            }
        } catch (Exception e) {
            e.printStackTrace();
            // 返回具体的错误信息给前端
            return new ResponseUtil(500, e.getMessage());
        }
    }
}
