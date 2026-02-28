package com.rent.utils;

import com.nimbusds.jose.*;
import com.nimbusds.jose.crypto.MACSigner;
import com.nimbusds.jose.crypto.MACVerifier;

import java.text.ParseException;
import java.util.Map;

public class JwtUtil {
    private static final String secretString = "token!Q2W#E$RWtoken!Q2W#E$RWtoken!Q2W#E$RW";

    public static String getToken(Map map) throws JOSEException {
        // 生成JWT头部
        JWSHeader header = new JWSHeader.Builder(JWSAlgorithm.HS256) // 设置加密方式
                .type(JOSEObjectType.JWT).build();// 设置jwt常量
        // 生成载荷部分
        Payload payload = new Payload(map);
        // MACSigner 对称加密
        JWSSigner jWSSigner = new MACSigner(secretString);
        // 生成签名
        // 生成签名部分 base64URL(header) + base64URL(payload) + 加密算法(秘钥)
        JWSObject jwsObject = new JWSObject(header, payload); // base64URL(header) + base64URL(payload)
        jwsObject.sign(jWSSigner); // 签名部分
        String token = jwsObject.serialize();
        return token;
    }

    public static boolean verifyJwt(String jwt) throws ParseException, JOSEException {
        // 解析jwt
        JWSObject jwsObject = JWSObject.parse(jwt);
        JWSVerifier jwsVerifier = new MACVerifier(secretString);
        // 验证JWT是否合法
        boolean verify = jwsObject.verify(jwsVerifier);
        return verify;
    }

    public static Map getPayload(String jwt) throws ParseException {
        // 获取JWT中的载荷信息
        JWSObject jwsObject = JWSObject.parse(jwt);
        Payload payload = jwsObject.getPayload();
        Map<String, Object> jsonObject = payload.toJSONObject();
        return jsonObject;
    }

    public static Integer getUserId(String jwt) throws ParseException {
        JWSObject parse = JWSObject.parse(jwt);
        Payload payload = parse.getPayload();
        Map<String, Object> map = payload.toJSONObject();
        Object idObj = map.get("id");
        if (idObj instanceof Integer) {
            return (Integer) idObj;
        } else if (idObj instanceof Long) {
            return ((Long) idObj).intValue();
        } else {
            throw new ClassCastException("Cannot cast " + idObj.getClass() + " to Integer");
        }
    }
}
