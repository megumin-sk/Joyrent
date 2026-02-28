package com.rent.service;

import com.rent.common.entity.GameReviews;
import com.baomidou.mybatisplus.extension.service.IService;

import com.rent.common.vo.GameReviewVO;
import java.util.List;

/**
 * @author jie17
 * @description 针对表【game_reviews(游戏评价表(含AI分析))】的数据库操作Service
 * @createDate 2025-12-03 21:24:47
 */
public interface GameReviewsService extends IService<GameReviews> {

    List<GameReviewVO> getReviewsByGameId(Long gameId);

    boolean submitReview(Long userId, com.rent.common.dto.ReviewSubmitDTO reviewSubmitDTO);
}
