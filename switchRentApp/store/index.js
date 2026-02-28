import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    // 1. 初始化时优先从本地存储读取，防止刷新丢失
    token: uni.getStorageSync('token') || '',
    userInfo: uni.getStorageSync('userInfo') || {}
  },

  getters: {
    // 方便判断是否登录
    isLoggedIn: state => !!state.token,
    getToken: state => state.token,
    userInfo: state => state.userInfo  // 直接使用 userInfo
  },

  mutations: {
    SET_TOKEN(state, token) {
      state.token = token;
      // 2. 数据变更时，同步保存到本地
      if (token) {
        uni.setStorageSync('token', token);
      } else {
        uni.removeStorageSync('token');
      }
    },
    SET_USER_INFO(state, info) {
      state.userInfo = info;
      if (info) {
        uni.setStorageSync('userInfo', info);
      } else {
        uni.removeStorageSync('userInfo');
      }
    },
    CLEAR_AUTH(state) {
      state.token = '';
      state.userInfo = {};
      uni.removeStorageSync('token');
      uni.removeStorageSync('userInfo');
    }
  },

  actions: {
    // 登录：同时保存 token 和用户信息
    login({ commit }, { token, userInfo }) {
      commit('SET_TOKEN', token);
      if (userInfo) {
        commit('SET_USER_INFO', userInfo);
      }
    },
    // 退出登录
    logout({ commit }) {
      commit('CLEAR_AUTH');
    },
    // 单独更新用户信息（比如用户修改了头像）
    updateUserInfo({ commit }, userInfo) {
      commit('SET_USER_INFO', userInfo);
    }
  }
});

export default store;
