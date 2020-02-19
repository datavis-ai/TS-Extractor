<template>
	<div id="search-condition-view-box">
	    <!-- <el-collapse v-model="activeNames"> -->
	      <!-- <el-collapse-item title="Search View" name="Text Search">	         -->
	        <div id="search-condition-view-box-div">
            <conditions></conditions>
            <resultssearch></resultssearch>
          </div>
	      <!-- </el-collapse-item> -->
	    <!-- </el-collapse> -->
	</div>	
</template>

<script>
  import conditions from '@/components/conditionsSearch'
  import resultssearch from '@/components/resultsSearchView'
  export default {    
    data: function(){
      return {
        activeNames:["Text Search"],
      }
    },
    computed:{

    },
    components: {
      conditions,
      resultssearch
    },
    methods:{
      
    },
    mounted(){
      let this_ = this;
      
    },
    beforeDestroy(){
      
    }   
  }
</script>

<style>
#search-condition-view-box .el-collapse-item__header{
  /*background-color: #f5f5f5;*/
  color: #333;  
  border-color:#ddd;
  border-style: solid;
  border-top-width: 1px;
  border-right-width: 1px;
  border-bottom-width: 1px;
  border-left-width: 1px;
  border-top-left-radius:0px;
  border-top-right-radius:0px; 
  border-bottom-left-radius:0px;
  border-bottom-right-radius:0px;
  margin:0px 0px 0px 0px;
  /*height:40px;*/
}

#search-condition-view-box .el-collapse-item__wrap{

  /*background-color: #f5f5f5;*/
  color: #333;  
  border-color:#ddd;
  border-style: solid;
  border-top-width: 0px;
  border-right-width: 1px;
  border-bottom-width: 1px;
  border-left-width: 1px;
  border-top-left-radius:0px;
  border-top-right-radius:0px; 
  border-bottom-left-radius:0px;
  border-bottom-right-radius:0px;
  /*margin:0px 0px 2px 0px;*/
}
#search-condition-view-box .el-collapse-item__content{
  padding-bottom: 0px;
}

</style>