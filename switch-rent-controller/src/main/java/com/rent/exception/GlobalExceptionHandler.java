package com.rent.exception;

import com.rent.common.exception.CustomException;
import com.rent.common.utils.ResponseEnum;
import com.rent.common.utils.ResponseUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.bind.MethodArgumentNotValidException;

@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 处理自定义异常
     */
    @ExceptionHandler(CustomException.class)
    public ResponseUtil handleCustomException(CustomException e) {
        log.error("CustomException Detected: code={}, msg={}", e.getCode(), e.getMsg());
        return new ResponseUtil(e.getCode(), e.getMsg());
    }

    /**
     * 处理参数校验异常
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseUtil handleValidationExceptions(MethodArgumentNotValidException ex) {
        log.error("Validation Exception Detected", ex);
        StringBuilder sb = new StringBuilder();
        ex.getBindingResult().getAllErrors().forEach((error) -> {
            sb.append(error.getDefaultMessage()).append("; ");
        });
        return new ResponseUtil(ResponseEnum.PARAM_ERROR.getCode(), sb.toString());
    }

    /**
     * 处理其他未知异常
     */
    @ExceptionHandler(Exception.class)
    public ResponseUtil handleException(Exception e) {
        log.error("System Exception Detected", e);
        return ResponseUtil.get(ResponseEnum.FAIL);
    }
}
