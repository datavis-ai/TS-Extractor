// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
// import router from './router/index';
// import router from './router';  // 以后用到路由再去掉注释
import BootstrapVue from 'bootstrap-vue'
// 导入全局element-ui
import Element from 'element-ui' 
import 'element-ui/lib/theme-chalk/index.css'
import locale from 'element-ui/lib/locale/lang/en'
Vue.use(Element,{ locale })  // 使用Element这个组件
// 导入boostract.
import 'bootstrap-vue/dist/bootstrap-vue.min.css'

// 全局引入echarts
// import echarts from 'echarts' //引入echarts, 和axios一样, 不能使用Vue.use(),
// Vue.prototype.$echarts = echarts //挂载到Vue.prototype, 以后在组件中直接用: this.$echarts就可以了.

// main.js作为程序入口文件.
Vue.config.productionTip = false;
Vue.use(BootstrapVue);

import VueLocalForage from 'vue-localforage'
Vue.use(VueLocalForage);

import {store} from './store'

// 导入sigma.js
// import sigma from '../static/js/sigma.min.js'
// Vue.prototype.$sigma = sigma;

// String.prototype.format = function(){
//   var args = arguments;
//   return this.replace(/\{(\d+)\}/g, function(a, num){
//     return args[num] || a
//   })
// }
/*
// 引入cookies
import VueCookies from 'vue-cookies'
Vue.use(VueCookies)
*/

/*
//设置cookie
Vue.prototype.setCookie = (c_name, value, expiredays) => { 
  console.log("I am in setCookie");console.log(c_name);
  // c_name是键,value是值一个object对象,expiredays是失效时间,用于控制cookie的保存时间,如果为null表示一直保存,知道关闭工程.
  let exdate = new Date();　　　　
  exdate.setDate(exdate.getDate() + expiredays);　　// expiredays是一个非常重要的参数,它指定了cookies的有效时间,一旦时间到达就会失效.　　
  document.cookie = c_name + "=" + JSON.stringify(value) + ((expiredays == null) ? "" : ";expires=" + exdate.toGMTString());
  // document.cookie = c_name + "=" + value + ((expiredays == null) ? "" : ";expires=" + exdate.toGMTString());
}
//获取cookie、
function getCookie(name) {
  let arr;
  let reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");  // RegExp是正则表达.  
  console.log("reg");console.log(reg);
  if(arr = document.cookie.match(reg)){
    console.log("arr");console.log(document.cookie.keys);
    return (arr[2]); 
  }
  else
    return null;
}
Vue.prototype.getCookie = getCookie;
//删除cookie
Vue.prototype.delCookie =(name) => {
    let exp = new Date();
    exp.setTime(exp.getTime() - 1); // 1秒的有效时间,1秒后失效,以这种方式删除cookie.
    let cval = getCookie(name); // 获得name对应的值.
    if (cval != null)
      document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString();  // 通过修改失效时间来删除cookies.
}*/
 /* eslint-disable */
/* eslint-disable no-new */
new Vue({
  el: '#app',// 为实例提供挂载元素,即将APP页面渲染后替代这个元素,注意:这个元素将被替代. 如果repalce:false将直接插入元素中. 接下来,实例将进入编译过程.
  // router, // 以后用到路由再去掉注释
//  replace: true,
  store,  // 使用vuex,状态管理,这样在所有组件中都可以使用了.
  components: { App },
  template: '<App/>'// 这个指明要挂载的页面,即APP.vue.
});
