package com.rent.controller;

import com.rent.common.utils.ResponseEnum;
import com.rent.common.utils.ResponseUtil;
import com.rent.service.UserFaceService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@Tag(name = "Face", description = "人脸识别接口")
@RestController
@RequestMapping("/face")
public class FaceController {
    @Autowired
    private UserFaceService userFaceService;

    @PostMapping("/login")
    public ResponseUtil detectFace(@RequestBody Map<String, String> requestMap) {
        String imageBase64 = requestMap.get("imageBase64");
        try {
            Map<String, Object> result = userFaceService.callBaidu(imageBase64);
            if (result.get("error_code") != null && (Integer) result.get("error_code") == 0) {
                return ResponseUtil.get(ResponseEnum.SUCCESS, result);
            }
            return ResponseUtil.get(ResponseEnum.FACE_RECOGNIZE_FAILED, result);
        } catch (Exception e) {
            return new ResponseUtil(ResponseEnum.FACE_RECOGNIZE_FAILED.getCode(), e.getMessage());
        }
    }

    @PostMapping("/register")
    public ResponseUtil registerFace(@RequestBody Map<String, String> requestMap) {
        String imageBase64 = requestMap.get("imageBase64");
        String userId = requestMap.get("userId");
        
        try {
            Map<String, Object> result = userFaceService.registerFace(imageBase64, userId);
            // 检查注册结果
            if (result.get("error_code") != null && (Integer) result.get("error_code") == 0) {
                return ResponseUtil.get(ResponseEnum.SUCCESS, result);
            }
            
            // 如果是检测失败（百度 error_code 222202 等）
            Integer baiduErrorCode = (Integer) result.get("error_code");
            if (baiduErrorCode != null && baiduErrorCode != 0) {
                return ResponseUtil.get(ResponseEnum.FACE_DETECT_FAILED, result);
            }

            return ResponseUtil.get(ResponseEnum.FACE_REGISTER_FAILED, result);
        } catch (Exception e) {
            return new ResponseUtil(ResponseEnum.FACE_REGISTER_FAILED.getCode(), e.getMessage());
        }
    }

    @GetMapping("/delete/{userId}")
    public ResponseUtil deleteFace(@PathVariable String userId) {
        try {
            Map<String, Object> result = userFaceService.deleteFaceUser(userId);
            if (result.get("error_code") != null && (Integer) result.get("error_code") == 0) {
                return ResponseUtil.get(ResponseEnum.SUCCESS, result);
            }
            return ResponseUtil.get(ResponseEnum.FAIL, result);
        } catch (Exception e) {
            return new ResponseUtil(ResponseEnum.FAIL.getCode(), e.getMessage());
        }
    }

    @GetMapping("/status/{userId}")
    public ResponseUtil getFaceStatus(@PathVariable String userId) {
        try {
            boolean registered = userFaceService.isFaceRegistered(userId);
            return ResponseUtil.get(ResponseEnum.SUCCESS, registered);
        } catch (Exception e) {
            return ResponseUtil.get(ResponseEnum.FAIL, e.getMessage());
        }
    }
}
