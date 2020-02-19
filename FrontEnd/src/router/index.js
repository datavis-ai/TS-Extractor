/* eslint-disable */
import Vue from 'vue'
import Router from 'vue-router'

import overviewglobalheatmap from '@/components/overViewGlobalHeatMap'
import overviewglobalgraph from '@/components/overViewGlobalGraph'

Vue.use(Router)

/*
 这个文件用于指定:什么路由下渲染什么文件,即组件,比如:/jj路由下,渲染home文件.
 在routes中实现路由与组件的绑定,一个路由对应一个组件,这个组件里面又可以是由多个组件嵌套而成.
*/
export default new Router({
  routes: [
    //{ path: '/', redirect: '/jj' },
    // {
    //  	path:'/home',  // "XXXXX/home"绑定home组件.
    //  	// name: home,
    //     component:home, // 在/jj这个路由下,渲染home.vue
    //     children:[
		  //   {
		  //     path:'new1',
		  //     //name: 'HelloWorld',
		  //     component: new1  // 在/jj/hello, 这个路由下,渲染HelloWorld.vue
		  //   },
		  //   {
		  //     path:'new2',
		  //     //name: 'mty',
		  //     component: new2  // 在/jj/mty, 这个路由下,渲染mty.vue
		  //   },
		  //   {
		  //     path:'new3',
		  //     //name: 'mty',
		  //     component: new3  // 在/jj/mty, 这个路由下,渲染mty.vue
		  //   }
    //     ]
    // },
    // {
    //  	path:'/publication',
    //  	// name: home,
    //     component:publication // 在/jj这个路由下,渲染home.vue

    // },
    // {
    //  	path:'/about',
    //  	// name: home,
    //     component:about // 在/jj这个路由下,渲染home.vue

    // },
    // {
    //     path: '/network',
    //     component: network
    // }
    {
       path:'/',
       name: 'heatmap',
       component: overviewglobalheatmap
    },
    {
       path:'/globalgraphview/graph',
       name: 'graph',
       component: overviewglobalgraph
    },
    // { path: '/globalgraphview/graph', redirect: '/' }

  ]
})
