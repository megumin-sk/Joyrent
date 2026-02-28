package com.rent.controller;

import com.rent.common.entity.Games;
import com.rent.common.utils.ResponseUtil;
import com.rent.service.GamesService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;

/**
 * 游戏信息相关的 REST 控制器,负责对外暴露查询、创建、修改与删除接口。
 */
@Tag(name = "Games", description = "游戏资源的查询与维护接口")
@RestController
@RequestMapping("/games")
public class GamesController {

    @Resource
    private GamesService gamesService;

    /**
     * 查询所有游戏信息。
     */
    @Operation(summary = "查询所有游戏", description = "返回系统内所有游戏的完整列表")
    @GetMapping("/all")
    public ResponseUtil getAllGames() {
        return gamesService.getAllGames();
    }

    /**
     * 根据ID查询游戏详情。
     *
     * @param id 游戏ID
     */
    @Operation(summary = "查询游戏详情", description = "根据游戏ID查询游戏的详细信息")
    @GetMapping("/{id}")
    public ResponseUtil getGameById(@Parameter(description = "游戏ID", required = true) @PathVariable Long id) {
        return gamesService.getGameById(id);
    }

    /**
     * 根据名称模糊查询游戏。
     *
     * @param name 游戏名称关键字
     */
    @Operation(summary = "名称模糊查询", description = "根据游戏名称关键字进行模糊匹配")
    @GetMapping("/searchByName/{name}")
    public ResponseUtil getGamesByName(@Parameter(description = "游戏名称关键字", required = true) @PathVariable String name) {
        return gamesService.getGamesByName(name);
    }

    /**
     * 根据平台查询游戏。
     *
     * @param platform 游戏所属平台
     */
    @Operation(summary = "按平台查询", description = "根据所属平台过滤游戏")
    @GetMapping("/searchByPlatform/{platform}")
    public ResponseUtil getGamesByPlatform(
            @Parameter(description = "游戏平台", required = true) @PathVariable String platform) {
        return gamesService.getGamesByPlatform(platform);
    }

    /**
     * 获取租赁次数前五名的游戏。
     */
    @Operation(summary = "热门游戏排行", description = "获取租赁次数最多的前5款游戏")
    @GetMapping("/top-rented")
    public ResponseUtil getTopRentedGames() {
        return gamesService.getTopRentedGames();
    }

    /**
     * 新增一条游戏记录。
     *
     * @param game 待创建的游戏实体
     */
    @Operation(summary = "新增游戏", description = "创建一条新的游戏记录")
    @PostMapping("/create")
    public ResponseUtil createGame(@RequestBody Games game) {
        return gamesService.createGame(game);
    }

    /**
     * 更新游戏信息。
     *
     * @param game 待更新的游戏实体
     */
    @Operation(summary = "更新游戏", description = "根据提交的实体信息更新游戏记录")
    @PostMapping("/update")
    public ResponseUtil updateGame(@RequestBody Games game) {
        return gamesService.updateGame(game);
    }

    /**
     * 根据主键删除游戏。
     *
     * @param id 游戏主键 ID
     */
    @Operation(summary = "删除游戏", description = "根据主键 ID 删除对应游戏")
    @GetMapping("/delete/{id}")
    public ResponseUtil deleteGame(@Parameter(description = "游戏主键 ID", required = true) @PathVariable Long id) {
        return gamesService.deleteGame(id);
    }
}
