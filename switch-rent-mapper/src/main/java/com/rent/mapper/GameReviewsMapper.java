package com.rent.mapper;

import com.rent.common.entity.GameReviews;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.rent.common.vo.GameReviewVO;
import org.apache.ibatis.annotations.Param;
import java.util.List;

/**
 * @author jie17
 * @description 针对表【game_reviews(游戏评价表(含AI分析))】的数据库操作Mapper
 * @createDate 2025-12-03 21:24:47
 * @Entity com.rent.common.entity.GameReviews
 */
public interface GameReviewsMapper extends BaseMapper<GameReviews> {

    List<GameReviewVO> selectReviewsByGameId(@Param("gameId") Long gameId);
}
