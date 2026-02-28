package com.rent.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rent.common.dto.ReviewSubmitDTO;
import com.rent.common.entity.GameReviews;
import com.rent.common.entity.OrderItems;
import com.rent.common.entity.Orders;
import com.rent.common.vo.GameReviewVO;
import com.rent.mapper.GameReviewsMapper;
import com.rent.mapper.OrderItemsMapper;
import com.rent.mapper.OrdersMapper;
import com.rent.service.GameReviewsService;
import com.rent.utils.PythonCommentClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

/**
 * @author jie17
 * @description 针对表【game_reviews(游戏评价表(含AI分析))】的数据库操作Service实现
 * @createDate 2025-12-03 21:24:47
 */
@Service
public class GameReviewsServiceImpl extends ServiceImpl<GameReviewsMapper, GameReviews>
        implements GameReviewsService {

    @Autowired
    private GameReviewsMapper gameReviewsMapper;

    @Autowired
    private OrdersMapper ordersMapper;

    @Autowired
    private OrderItemsMapper orderItemsMapper;

    @Autowired
    private PythonCommentClient pythonCommentClient;

    @Override
    public List<GameReviewVO> getReviewsByGameId(Long gameId) {
        return gameReviewsMapper.selectReviewsByGameId(gameId);
    }

    @Override
    public boolean submitReview(Long userId, ReviewSubmitDTO dto) {
        // 1. 如果 orderId 为空，自动匹配用户最近的已完成订单
        Long orderId = dto.getOrderId();
        if (orderId == null) {
            // 查询用户最近的符合条件的订单（租赁中或已完成）
            LambdaQueryWrapper<Orders> orderQuery = Wrappers.<Orders>lambdaQuery()
                    .eq(Orders::getUserId, userId)
                    .ge(Orders::getStatus, 30)
                    .orderByDesc(Orders::getCreatedAt)
                    .last("LIMIT 10");
//            QueryWrapper<Orders> orderQuery = new QueryWrapper<>();
//            orderQuery.eq("user_id", userId)
//                    .ge("status", 30)  // 30=租赁中, 40=归还中, 50=完成. 只要收到货(>=30)即可评价
//                    .orderByDesc("created_at")
//                    .last("LIMIT 10");
            
            List<Orders> recentOrders = ordersMapper.selectList(orderQuery);
            
            // 在这些订单中找到包含该游戏且未评价的订单
            for (Orders order : recentOrders) {
                // 检查订单是否包含该游戏
//                QueryWrapper<OrderItems> itemQuery = new QueryWrapper<>();
//                itemQuery.eq("order_id", order.getId())
//                        .eq("game_id", dto.getGameId());
                LambdaQueryWrapper<OrderItems> itemQuery = Wrappers.<OrderItems>lambdaQuery()
                        .eq(OrderItems::getOrderId, order.getId())
                        .eq(OrderItems::getGameId, dto.getGameId());
                if (orderItemsMapper.selectCount(itemQuery) > 0) {
                    // 检查是否已评价
                    QueryWrapper<GameReviews> reviewQuery = new QueryWrapper<>();
                    reviewQuery.eq("order_id", order.getId())
                            .eq("game_id", dto.getGameId());
                    if (gameReviewsMapper.selectCount(reviewQuery) == 0) {
                        // 找到了！使用这个订单ID
                        orderId = order.getId();
                        dto.setOrderId(orderId);
                        break;
                    }
                }
            }
            
            // 如果还是没找到，说明用户没有租赁过这款游戏
            if (orderId == null) {
                throw new RuntimeException("您还没有租赁过这款游戏，无法评价");
            }
        }
        
        // 2. 校验订单
        Orders order = ordersMapper.selectById(orderId);
        if (order == null) {
            throw new RuntimeException("订单不存在");
        }
        if (!order.getUserId().equals(userId)) {
            throw new RuntimeException("该订单不属于当前用户");
        }
        // 放宽限制: 只要发货/租赁中(>=30)即可评价
        if (order.getStatus() < 30) {
            throw new RuntimeException("您尚未收到游戏，暂无法评价");
        }

        // 2.1 校验游戏是否属于该订单
        QueryWrapper<OrderItems> itemQuery = new QueryWrapper<>();
        itemQuery.eq("order_id", orderId)
                .eq("game_id", dto.getGameId());
        if (orderItemsMapper.selectCount(itemQuery) == 0) {
            throw new RuntimeException("该订单未包含此游戏，无法评价");
        }

        // 2.2 校验是否重复评价
        QueryWrapper<GameReviews> query = new QueryWrapper<>();
        query.eq("order_id", orderId)
                .eq("game_id", dto.getGameId());
        if (gameReviewsMapper.selectCount(query) > 0) {
            throw new RuntimeException("您已评价过该游戏，请勿重复提交");
        }

        // 3. 调用 AI 级联分析引擎进行内容风控与情感提取
        Map<String, Object> aiResponse = pythonCommentClient.analyzeComment(dto.getContent());
        Integer aiJudge = 0; // 0=正常
        String aiEmotionStr = "";
        java.math.BigDecimal aiScore = java.math.BigDecimal.ZERO;
        
        if (aiResponse != null && aiResponse.get("code") != null && (int)aiResponse.get("code") == 200) {
            Map<String, Object> result = (Map<String, Object>) aiResponse.get("result");
            if ("block".equals(result.get("status"))) {
                throw new RuntimeException("评论包含违规或广告内容，已被系统拦截");
            }
            
            // 提取数据
            Map<String, Object> data = (Map<String, Object>) result.get("data");
            if (data != null) {
                aiEmotionStr = cn.hutool.json.JSONUtil.toJsonStr(data);
                
                // 计算所有维度的平均置信度
                double totalScore = 0.0;
                int count = 0;
                for (Map.Entry<String, Object> entry : data.entrySet()) {
                    Map<String, Object> dimData = (Map<String, Object>) entry.getValue();
                    String scoreStr = (String) dimData.get("score");
                    if (scoreStr != null) {
                        totalScore += Double.parseDouble(scoreStr);
                        count++;
                    }
                }
                // 计算平均值并保留4位小数
                if (count > 0) {
                    aiScore = new java.math.BigDecimal(totalScore / count)
                            .setScale(4, java.math.RoundingMode.HALF_UP);
                }
            }
        }

        // 4. 保存评价
        GameReviews review = new GameReviews();
        review.setUserId(userId);
        review.setOrderId(dto.getOrderId());
        review.setGameId(dto.getGameId());
        review.setRating(dto.getRating());
        review.setContent(dto.getContent());
        review.setIsHidden(0); 
        review.setAiJudge(aiJudge);
        review.setAiEmotion(aiEmotionStr);
        review.setAiScore(aiScore);
        
        // 4.1 填充8个维度 (如果有AI数据)
        if (aiResponse != null && aiResponse.get("result") != null) {
            Map result = (Map) aiResponse.get("result");
            Map data = (Map) result.get("data");
            if (data != null) {
                review.setDimLogistics(parseDim(data, "logistics"));
                review.setDimCondition(parseDim(data, "condition"));
                review.setDimService(parseDim(data, "service"));
                review.setDimPrice(parseDim(data, "price"));
                review.setDimGameplay(parseDim(data, "gameplay"));
                review.setDimVisuals(parseDim(data, "visuals"));
                review.setDimStory(parseDim(data, "story"));
                review.setDimAudio(parseDim(data, "audio"));
            } else {
                setDefaultDims(review);
            }
        } else {
            setDefaultDims(review);
        }

        return this.save(review);
    }

    // 解析辅助方法：将 AI 标签文本转换为 0-3 的数字
    private Integer parseDim(Map data, String key) {
        if (data == null || data.get(key) == null) return 3; // 默认为无
        Map dimInfo = (Map) data.get(key);
        String label = (String) dimInfo.get("label");
        
        // 标签映射需与 Python 端 inference.py 保持一致
        if (label == null) return 3;
        if (label.contains("差评") || label.contains("Negative")) return 0;
        if (label.contains("中立") || label.contains("Neutral")) return 1;
        if (label.contains("好评") || label.contains("Positive")) return 2;
        return 3; // 未提及
    }

    private void setDefaultDims(GameReviews review) {
        review.setDimLogistics(3);
        review.setDimCondition(3);
        review.setDimService(3);
        review.setDimPrice(3);
        review.setDimGameplay(3);
        review.setDimVisuals(3);
        review.setDimStory(3);
        review.setDimAudio(3);
    }
}
