package com.rent.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.rent.common.entity.Games;

import java.util.List;

/**
* @author jie17
* @description 针对表【games(游戏库)】的数据库操作Mapper
* @createDate 2025-11-18 23:33:58
* @Entity com.rent.common.entity.Games
*/
public interface GamesMapper extends BaseMapper<Games> {
    List<Games> selectAll();
    List<Games> selectGamesByRentNum();
    List<Games> selectByName(String name);
    List<Games> selectByType(String type);
}




