package com.rent.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.rent.common.entity.Games;
import com.rent.common.utils.ResponseUtil;

/**
 * @author jie17
 * @description 针对表【games(游戏库)】的数据库操作Service
 * @createDate 2025-11-18 23:33:58
 */
public interface GamesService extends IService<Games> {
    /**
     * 查询所有游戏
     */
    ResponseUtil getAllGames();

    /**
     * 根据ID查询游戏详情
     * 
     * @param id 游戏ID
     * @return 游戏详情
     */
    ResponseUtil getGameById(Long id);

    /**
     * 根据名称模糊查询游戏
     */
    ResponseUtil getGamesByName(String name);

    /**
     * 根据平台查询游戏
     */
    ResponseUtil getGamesByPlatform(String platform);

    /**
     * 获取租赁次数最多的前5款游戏
     */
    ResponseUtil getTopRentedGames();

    /**
     * 更新游戏信息
     */
    ResponseUtil updateGame(Games game);

    /**
     * 创建游戏
     */
    ResponseUtil createGame(Games game);

    /**
     * 删除游戏
     */
    ResponseUtil deleteGame(Long id);
}
