package com.rent.common.dto;

import lombok.Data;

import java.io.Serializable;

@Data
public class ReviewSubmitDTO implements Serializable {
    private Long orderId;
    private Long gameId;
    private Integer rating;
    private String content;
}
