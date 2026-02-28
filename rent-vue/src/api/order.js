import server from "../utils/request.js";

/**
 * 查询最近一周每天的订单量
 */
export function queryWeekCount() {
    return server({
        url: "/orders/weekly-daily-trend",
        method: "get",
    });
}

/**
 * 获取今日的订单金额
 */
export function queryTodayMoney() {
    return server({
        url: "/orders/today-money",
        method: "get",
    });
}

/**
 * 查询最近七天每天成交额
 */
export function queryDailyTurnover() {
    return server({
        url: "/orders/weekly-daily-amount",
        method: "get",
    });
}

/**
 * 查询今日订单列表
 */
export function queryTodayOrders() {
    return server({
        url: "/orders/today-list",
        method: "get",
    });
}