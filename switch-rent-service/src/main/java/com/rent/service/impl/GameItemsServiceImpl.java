package com.rent.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rent.common.entity.GameItems;
import com.rent.mapper.GameItemsMapper;
import com.rent.service.GameItemsService;
import org.springframework.stereotype.Service;

/**
* @author jie17
* @description 针对表【game_items(实物库存)】的数据库操作Service实现
* @createDate 2025-11-18 23:33:58
*/
@Service
public class GameItemsServiceImpl extends ServiceImpl<GameItemsMapper, GameItems>
    implements GameItemsService {

}




