import { createStore } from 'vuex';
import { getToken, setToken, removeToken } from '@/utils/auth.js'

const USER_KEY = 'joyrent-admin-user';

const getStoredUser = () => {
  if (typeof window === 'undefined') {
    return null;
  }
  const raw = window.localStorage.getItem(USER_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    window.localStorage.removeItem(USER_KEY);
    return null;
  }
};

export default createStore({
  state() {
    return {
      user: getStoredUser(),
      token: getToken()
    };
  },
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    currentUser: (state) => state.user,
    authToken: (state) => state.token
  },
  mutations: {
    SET_AUTH(state, { user, token }) {
      state.user = user || null;
      state.token = token || '';

      if (typeof window === 'undefined') {
        return;
      }
      if (user) {
        window.localStorage.setItem(USER_KEY, JSON.stringify(user));
      } else {
        window.localStorage.removeItem(USER_KEY);
      }

      if (token) {
        setToken(token)
      } else {
        removeToken()
      }
    },
    LOGOUT(state) {
      state.user = null;
      state.token = '';

      if (typeof window === 'undefined') {
        return;
      }
      window.localStorage.removeItem(USER_KEY);
      removeToken();
    }
  },
  actions: {
    loginSuccess({ commit }, payload) {
      const { user, token } = payload || {};
      commit('SET_AUTH', { user: user || null, token: token || '' });
    },
    logout({ commit }) {
      commit('LOGOUT');
    }
  }
});

