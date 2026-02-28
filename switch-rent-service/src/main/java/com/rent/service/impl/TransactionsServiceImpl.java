package com.rent.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.rent.common.entity.Transactions;
import com.rent.mapper.TransactionsMapper;
import com.rent.service.TransactionsService;
import org.springframework.stereotype.Service;

/**
* @author jie17
* @description 针对表【transactions(资金流水)】的数据库操作Service实现
* @createDate 2025-11-18 23:33:58
*/
@Service
public class TransactionsServiceImpl extends ServiceImpl<TransactionsMapper, Transactions>
    implements TransactionsService {

}




