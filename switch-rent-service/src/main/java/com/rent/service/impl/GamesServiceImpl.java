package com.rent.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rent.common.entity.Games;
import com.rent.common.utils.ResponseEnum;
import com.rent.common.utils.ResponseUtil;
import com.rent.mapper.GamesMapper;
import com.rent.service.GamesService;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

import javax.annotation.Resource;
import java.util.Date;
import java.util.List;
import java.util.Random;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

/**
 * @author jie17
 * @description 针对表【games(游戏库)】的数据库操作Service实现
 * @createDate 2025-11-18 23:33:58
 */
@Service
public class GamesServiceImpl extends ServiceImpl<GamesMapper, Games>
        implements GamesService {
    @Resource
    private GamesMapper gamesMapper;

    @Resource
    private RedisTemplate<String, Object> redisTemplate;

    private static final String GAME_CACHE_PREFIX = "game:detail:";

    // 线程池用于执行双删中的第二次删除
    private final ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

    @Override
    public ResponseUtil getAllGames() {
        List<Games> games = gamesMapper.selectAll();
        return ResponseUtil.get(ResponseEnum.SUCCESS, games);
    }

    @Override
    public ResponseUtil getGameById(Long id) {
        if (id == null) {
            return ResponseUtil.get(ResponseEnum.FAIL, "游戏ID不能为空");
        }

        String cacheKey = GAME_CACHE_PREFIX + id;
        
        // 1. 尝试从 Redis 获取缓存
        Games game = (Games) redisTemplate.opsForValue().get(cacheKey);
        if (game != null) {
            return ResponseUtil.get(ResponseEnum.SUCCESS, game);
        }

        // 2. 缓存未命中，回源数据库
        game = gamesMapper.selectById(id);
        if (game == null) {
            return ResponseUtil.get(ResponseEnum.FAIL, "游戏不存在");
        }

        // 3. 写入缓存，设置随机过期时间防止缓存雪崩
        int expireTime = 30 + new Random().nextInt(10); // 30-40 分钟随机，防止同时过期
        redisTemplate.opsForValue().set(cacheKey, game, expireTime, TimeUnit.MINUTES);
        
        return ResponseUtil.get(ResponseEnum.SUCCESS, game);
    }

    @Override
    public ResponseUtil getGamesByName(String name) {
        List<Games> games = gamesMapper.selectByName(name);
        return ResponseUtil.get(ResponseEnum.SUCCESS, games);
    }

    @Override
    public ResponseUtil getGamesByPlatform(String platform) {
        List<Games> games = gamesMapper.selectByType(platform);
        return ResponseUtil.get(ResponseEnum.SUCCESS, games);
    }

    @Override
    public ResponseUtil updateGame(Games game) {
        if (game == null || game.getId() == null) {
            return ResponseUtil.get(ResponseEnum.FAIL);
        }
        
        String cacheKey = GAME_CACHE_PREFIX + game.getId();

        // 1. 延迟双删：第一删
        redisTemplate.delete(cacheKey);

        // 2. 更新数据库
        int updated = gamesMapper.updateById(game);
        if (updated == 0) {
            return ResponseUtil.get(ResponseEnum.FAIL);
        }

        // 3. 延迟双删：延时 500ms 后执行第二删，确保主从同步或并发读取导致的回填失效
        scheduler.schedule(() -> {
            redisTemplate.delete(cacheKey);
        }, 500, TimeUnit.MILLISECONDS);

        Games latest = gamesMapper.selectById(game.getId());
        return ResponseUtil.get(ResponseEnum.SUCCESS, latest);
    }

    @Override
    public ResponseUtil createGame(Games game) {
        if (game == null || !StringUtils.hasText(game.getTitle()) || !StringUtils.hasText(game.getPlatform())) {
            return ResponseUtil.get(ResponseEnum.FAIL);
        }
        Date now = new Date();
        if (game.getStatus() == null) {
            game.setStatus(1);
        }
        if (game.getAvailableStock() == null) {
            game.setAvailableStock(0);
        }
        game.setCreatedAt(now);
        game.setUpdatedAt(now);
        int inserted = gamesMapper.insert(game);
        if (inserted == 0) {
            return ResponseUtil.get(ResponseEnum.FAIL);
        }
        return ResponseUtil.get(ResponseEnum.SUCCESS, gamesMapper.selectById(game.getId()));
    }

    @Override
    public ResponseUtil getTopRentedGames() {
        List<Games> games = gamesMapper.selectGamesByRentNum();
        return ResponseUtil.get(ResponseEnum.SUCCESS, games);
    }

    @Override
    public ResponseUtil deleteGame(Long id) {
        if (id == null) {
            return ResponseUtil.get(ResponseEnum.FAIL);
        }
        
        // 同步清理缓存
        redisTemplate.delete(GAME_CACHE_PREFIX + id);

        int deleted = gamesMapper.deleteById(id);
        if (deleted == 0) {
            return ResponseUtil.get(ResponseEnum.FAIL);
        }
        return ResponseUtil.get(ResponseEnum.SUCCESS);
    }
}
