package com.rent.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.rent.common.entity.UserFace;
import java.util.List;

/**
* @author jie17
* @description 针对表【user_face】的数据库操作Mapper
* @createDate 2025-11-19 20:05:54
* @Entity com.rent.common.entity.UserFace
*/
public interface UserFaceMapper extends BaseMapper<UserFace> {
    Long queryByFaceId(String faceId);
    
    List<String> queryFaceIdsByUserId(Long userId);
}




