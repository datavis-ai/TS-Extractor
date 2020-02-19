<template>
	<div id="network-info-view">
	    <el-collapse v-model="activeNames" @change="handleChange">
	      <el-collapse-item title="Network Information" name="Network Information">
	        <div v-if="lenGlobalGraphInfo.length > 0" class="global-graph-info">
	          <span>global graph</span>
	          <div id="global-box">
	          	<p>	          		
	          		|V|: {{globalGraphInfo.numnodes}}&nbsp&nbsp 
	          		|E|: {{globalGraphInfo.numedges}}&nbsp&nbsp
	          		directed: {{globalGraphInfo.directed}}
	          	</p>
	          </div>         
	        </div>
	        <div v-if="lenDoiGraphInfo.length > 0" class="doi-graph-info">
	          <span>DOI subgraph</span>
	          <div id="doi-box">
	          	<p>	          		
	          		|V|: {{doiGraphInfo.numnodes}}&nbsp&nbsp 
	          		|E|: {{doiGraphInfo.numedges}}&nbsp&nbsp	          		 
	          	</p>
	          </div>         
	        </div>
	      </el-collapse-item>
	    </el-collapse>
	</div>	
</template>
<script>
  import axios from 'axios' // 用于AJAX请求
  import * as d3 from 'd3'
  import {vueFlaskRouterConfig} from '../vueFlaskRouterConfig'
  import bus from '../eventbus.js' // 事件总线.
  
  export default {
    data() {
      return {
        activeNames: [], // 用于折叠项,里面用于保存激活的折叠项的name.
        globalGraphInfo: {}, // 全局图信息.
        doiGraphInfo:{}, // DOI子图信息.        
      }
    },
    methods: {     
       handleChange(val) {  // 输出已经点开的项的名字(name).
        console.log(val);  // 比如已经点开了折叠项1 + 折叠项2,那么点开折叠项3时,输出[折叠项1,折叠项2,折叠项3]
      },
    },
    mounted(){
    	let this_ = this;          
     
    },
    created(){
      console.log("this.scaleOfSingleFocus created");
      let this_ = this;
      // this_.$store.state.networkInformationView.doiGraphInfo = this_.doiGraphInfo; // 用于地址操作.
      bus.$on("dbLoadedState", function(data){
         // todo: 数据库装载成功后,直接获取全局图的各种统计信息.
         if(data){
         //   	let param = {};
         //    axios.post(vueFlaskRouterConfig.networkInformation, {
         //            param: JSON.stringify(param)
      			// })
            let path = vueFlaskRouterConfig.networkInformation;
            axios.get(path)
      			.then((res) => { 
      			  
      			    // TODO: 以下是原来发送焦点+节点数量,获得DOI子图数据的代码,以后还要用的.
      			    console.log("后台已经响应graph information数据!");
      			    let data = res.data;  // 通过查询选中焦点,然后用焦点的id获得图数据.	
      			    this_.globalGraphInfo = data;
      			    // console.log(data);		     
      			     
      			})
      			.catch((error) => {            
      			  console.error(error);
      			});
         }
         
      });
      bus.$on("sendDoiGraphInfo", function(data){
      	this_.doiGraphInfo = data;
      	// console.log("datajjjjjjjjjjjjjjj");console.log(data);
      }); 
    },
    computed:{
       lenGlobalGraphInfo: function(){
       	 return Object.keys(this.globalGraphInfo);
       },
       lenDoiGraphInfo: function(){
         return Object.keys(this.doiGraphInfo);
       },
    },
    beforeDestroy(){        
       bus.$off("dbLoadedState");  // 数据库装载成功.  
       bus.$off("sendDoiGraphInfo"); // 接收DOI graph 数据.      
    },
    watch:{ // 侦听器,用于侦听data里面定义的变量,只要变化就执行对应的动作.
    	 
    }

  }
</script>
<style>
.global-graph-info{
   border-style: solid;
   border-color:#E0E0E0;
   border-top-width: 1px;
   border-right-width: 0px;
   border-bottom-width: 0px;
   border-left-width: 0px;
}
.doi-graph-info{
   border-style: solid;
   border-color:#E0E0E0;
   border-top-width: 1px;
   border-right-width: 0px;
   border-bottom-width: 0px;
   border-left-width: 0px;
}   
</style>