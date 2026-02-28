package com.rent.common.vo;

import com.rent.common.entity.GameReviews;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
public class GameReviewVO extends GameReviews {
    private String nickname;
    private String avatar;
}
