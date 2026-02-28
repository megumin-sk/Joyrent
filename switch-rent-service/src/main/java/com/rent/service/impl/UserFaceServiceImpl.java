package com.rent.service.impl;

import com.alibaba.csp.sentinel.annotation.SentinelResource;
import com.baidu.aip.face.AipFace;
import com.nimbusds.jose.JOSEException;
import com.rent.common.entity.UserFace;
import com.rent.common.entity.Users;
import com.rent.common.utils.IdGeneratorUtil;
import com.rent.mapper.UserFaceMapper;
import com.rent.mapper.UsersMapper;
import com.rent.service.UserFaceService;
import com.rent.utils.JwtUtil;
import com.rent.utils.PythonFaceClient;
import lombok.extern.slf4j.Slf4j;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
public class UserFaceServiceImpl implements UserFaceService {
    @Autowired
    private UserFaceMapper userFaceMapper;

    @Autowired
    private UsersMapper usersMapper;

    @Autowired
    private PythonFaceClient pythonFaceClient;

    @Value("${baidu.face.APP_ID}")
    private String appId;

    @Value("${baidu.face.API_KEY}")
    private String apiKey;

    @Value("${baidu.face.SECRET_KEY}")
    private String secretKey;

    private static final String face = "app_face";

    private AipFace getClient() {
        return new AipFace(appId, apiKey, secretKey);
    }
    @Override
    public Map<String, Object> detectFace(String imageBase64) {
        AipFace aipFace = getClient();
        JSONObject detect = aipFace.detect(imageBase64, "BASE64", null);
        return new JSONObject(detect.toString()).toMap();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Map<String, Object> registerFace(String imageBase64, String userId) {
        log.info("开始双端人脸注册，本地用户ID: {}", userId);
        AipFace aipFace = getClient();
        
        // 生成唯一的 faceId，用于在百度和 Python 库中标识该人脸
        String faceId = IdGeneratorUtil.generateUUID();
        log.info("生成本次注册的 faceId: {}", faceId);

        // 1. 先调用百度进行人脸检测，确保图片质量
        JSONObject detectResult = aipFace.detect(imageBase64, "BASE64", null);
        if (detectResult.getInt("error_code") != 0) {
            log.error("人脸检测失败，放弃注册。error: {}", detectResult.getString("error_msg"));
            return new JSONObject(detectResult.toString()).toMap();
        }

        boolean pythonRegistered = false;
        try {
            // 2. 调用 Python 端进行特征提取
            Map<String, Object> pythonResult = pythonFaceClient.register(imageBase64, faceId);
            Boolean pythonSuccess = (Boolean) pythonResult.get("success");
            
            if (pythonSuccess == null || !pythonSuccess) {
                log.error("本地 Python 特征提取失败. Reason: {}", pythonResult.get("message"));
                return pythonResult;
            }
            
            // 获取特征向量 (List类型)
            Object faceEncodingObj = pythonResult.get("face_encoding");
            String faceEncodingStr = faceEncodingObj != null ? faceEncodingObj.toString() : null;
            
            pythonRegistered = true;
            log.info("Step 1: 本地 Python 人脸特征提取成功.");

            // 3. 调用百度端进行注册 (使用 faceId)
            HashMap<String, String> options = new HashMap<>();
            options.put("user_info", "userId_" + userId); 
            options.put("quality_control", "NORMAL");
            options.put("liveness_control", "LOW");
            options.put("action_type", "APPEND");

            JSONObject baiduResult = aipFace.addUser(imageBase64, "BASE64", face, faceId, options);

            if (baiduResult.getInt("error_code") == 0) {
                log.info("Step 2: 百度端人脸注册完成.");
                
                // 4. 保存关联关系及特征向量到本地数据库
                UserFace userFace = new UserFace();
                userFace.setFaceId(faceId);
                userFace.setUserId(Long.parseLong(userId));
                userFace.setFaceEncoding(faceEncodingStr); // 保存从Python拿到的特征向量
                userFaceMapper.insert(userFace);
                log.info("Step 3: 本地关联映射及特征向量保存成功 [faceId: {} -> userId: {}]", faceId, userId);

                Map<String, Object> response = new HashMap<>();
                response.put("error_code", 0);
                response.put("error_msg", "SUCCESS");
                response.put("face_id", faceId); // 这里的 face_id 是我们生成的 UUID
                response.put("user_id", userId);
                return response;
            } else {
                log.error("百度端人脸注册失败: {}", baiduResult.getString("error_msg"));
                return new JSONObject(baiduResult.toString()).toMap();
            }
        } catch (Exception e) {
            log.error("注册失败: {}", e.getMessage());
            throw new RuntimeException("注册过程发生异常: " + e.getMessage());
        }
    }

    
    @Override
    public Map<String, Object> recognizeFace(String imageBase64) {
        AipFace aipFace = getClient();
        JSONObject result = aipFace.search(imageBase64, "BASE64", face, null);
        return new JSONObject(result.toString()).toMap();
    }

    @Override
    public Map<String, Object> getFaceUserList() {
        AipFace aipFace = getClient();
        JSONObject result = aipFace.getGroupUsers(face,null);
        return new JSONObject(result.toString()).toMap();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Map<String, Object> deleteFaceUser(String userId) {
        log.info("开始双端人脸数据删除（Java DB + 百度云），本地用户ID: {}", userId);
        Map<String, Object> response = new HashMap<>();
        
        // 1. 查找该用户绑定的 faceId
        List<String> faceIds = userFaceMapper.queryFaceIdsByUserId(Long.parseLong(userId));
        
        if (faceIds == null || faceIds.isEmpty()) {
            log.warn("用户 {} 未绑定任何面部信息，无需删除", userId);
            response.put("error_code", 0);
            response.put("error_msg", "SUCCESS");
            response.put("message", "用户未绑定面部信息");
            return response;
        }

        AipFace aipFace = getClient();
        for (String faceId : faceIds) {
            // 2. 调用百度端进行删除 (百度云端销毁)
            JSONObject deleteRes = aipFace.deleteUser(face, faceId, null);
            if (deleteRes.getInt("error_code") != 0 && deleteRes.getInt("error_code") != 216602) { 
                // 216602 是用户不存在错误，通常可以忽略。其他错误需抛出异常触发回滚
                log.error("百度端人脸删除失败，faceId: {}, error: {}", faceId, deleteRes.getString("error_msg"));
                throw new RuntimeException("同步删除百度端人脸失败: " + deleteRes.getString("error_msg"));
            }
            log.info("百度云端人脸销毁成功，faceId: {}", faceId);
        }

        // 4. 清理本地数据库 (MyBatis Plus 提供的 deleteByMap 或自定义)
        Map<String, Object> columnMap = new HashMap<>();
        columnMap.put("user_id", userId);
        userFaceMapper.deleteByMap(columnMap);
        
        log.info("本地数据库关联关系已清理，用户ID: {}", userId);

        response.put("error_code", 0);
        response.put("error_msg", "SUCCESS");
        response.put("message", "该用户的所有人脸数据均已清理完成");
        return response;
    }


    @Override
    @SentinelResource(value = "callBaidu", fallback = "callBaiduFallback")
    public Map<String, Object> callBaidu(String imageBase64) throws InterruptedException, JOSEException {
        Map<String, Object> result = recognizeFace(imageBase64);
//        throw new RuntimeException();
        
        // 百度成功了,处理它的响应
        Integer errorCode = (Integer) result.get("error_code");
        if (errorCode != null && errorCode == 0) {
            // 从返回结果中提取 user_list
            Map<String, Object> resultData = (Map<String, Object>) result.get("result");
            List<Map<String, Object>> userList = (List<Map<String, Object>>) resultData.get("user_list");

            if (userList == null || userList.isEmpty()) {
                throw new RuntimeException("未找到匹配的用户");
            }

            // 获取匹配度最高的用户（第一个识别结果是百度的 user_id，也就是我们的 faceId / 影子ID）
            Map<String, Object> topUser = userList.get(0);
            String recognizedFaceId = (String) topUser.get("user_id");
            Double score = (Double) topUser.get("score");

            log.info("百度识别成功，faceId: {}, 分数: {}", recognizedFaceId, score);

            // 通过 faceId 查找本地关联的 userId (通过本地映射表翻译)
            Long localUserId = userFaceMapper.queryByFaceId(recognizedFaceId);
            if (localUserId == null) {
                log.error("数据库中未找到 faceId: {} 对应的本地用户关联关系", recognizedFaceId);
                throw new RuntimeException("该人脸未绑定本地账号");
            }

            // 通过翻译后的本地用户 ID 查询用户详细信息
            Users user = usersMapper.getUserById(localUserId);
            if (user == null) {
                throw new RuntimeException("该关联用户已从系统中移除");
            }

            // 生成内部业务 JWT token
            Map<String, Object> payload = new HashMap<>();
            payload.put("id", user.getId());
            payload.put("username", user.getUsername());
            payload.put("role", user.getRole());
            String token = JwtUtil.getToken(payload);

            // 构建返回的 Map 结构
            Map<String, Object> response = new HashMap<>();
            response.put("error_code", 0);
            response.put("token", token);
            response.put("face_id", recognizedFaceId); // 标记识别到的脸
            response.put("user_id", localUserId);     // 标记最终识别到的人
            response.put("score", score);
            response.put("user", user);

            return response;
        } else {
            String errorMsg = (String) result.get("error_msg");
            log.error("百度端人脸识别失败: {}, 切换到Python端人脸识别...", errorMsg);
            throw new RuntimeException("百度端人脸识别失败"); // 抛出异常触发 Sentinel 降级
        }
    }

    /**
     * Sentinel 降级方法：当百度 API 不可用或报错时，调用 Python 本地服务
     */
    public Map<String, Object> callBaiduFallback(String imageBase64) throws JOSEException {
        log.info("Sentinel: 使用Python端人脸识别降级...");
        Map<String, Object> result = pythonFaceClient.recognize(imageBase64);

        // Python 端的返回结构是 { "success": true, "userInfo": { "id": ... } }
        if (result != null && Boolean.TRUE.equals(result.get("success"))) {
            Map<String, Object> userInfo = (Map<String, Object>) result.get("userInfo");
            if (userInfo != null && userInfo.get("id") != null) {
                Long userId = Long.valueOf(userInfo.get("id").toString());
                
                //  查找本地关联的真实 userId
                Users user = usersMapper.getUserById(userId);
                if (user != null) {
                    Map<String, Object> payload = new HashMap<>();
                    payload.put("id", user.getId());
                    payload.put("username", user.getUsername());
                    payload.put("role", user.getRole());
                    String token = JwtUtil.getToken(payload);

                    Map<String, Object> response = new HashMap<>();
                    response.put("error_code", 0);
                    response.put("token", token);
                    response.put("user", userInfo);
                    response.put("fallback", true);
                    log.info("Python端人脸识别降级成功，用户: {}", user.getUsername());
                    return response;
                }
            }
        }
        
        log.error("Python端人脸识别降级失败: {}", result != null ? result.get("message") : "无响应");
        throw new RuntimeException("人脸识别彻底失败，请使用账号密码登录");
    }

    @Override
    public boolean isFaceRegistered(String userId) {
        List<String> faceIds = userFaceMapper.queryFaceIdsByUserId(Long.parseLong(userId));
        return faceIds != null && !faceIds.isEmpty();
    }
}
