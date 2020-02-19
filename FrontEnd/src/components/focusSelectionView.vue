<template>
	<div id="focus-selection-view-box">
	    <el-collapse v-model="activeNames">
	      <el-collapse-item title="Focus Selection" name="Focus Selection">	        
	        <rankingList></rankingList>
          <searchView></searchView>
	      </el-collapse-item>
	    </el-collapse>
	</div>	
</template>

<script>
  import rankingList from '@/components/displayTopnNodeView'
  import searchView from '@/components/searchConditionView'
  export default {    
    data: function(){
      return {
        activeNames:["Focus Selection"],
      }
    },
    computed:{
      
    },
    components: {
      rankingList,
      searchView
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
#focus-selection-view-box .el-collapse-item__header{
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

#focus-selection-view-box .el-collapse-item__wrap{

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
#focus-selection-view-box .el-collapse-item__content{
  padding-bottom: 0px;
}
#search-result-table{
  margin:0px 5px 0px 5px;
}
#conditions-search-view{
  margin:0px 5px 0px 5px;
}
/* Ranking List*/
#focus-node-selection-rank{
  border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 0px;
  border-right-width: 0px;
  border-bottom-width: 0px;
  border-left-width: 0px;
  margin: 0px 5px 4px 5px;
}
#focus-node-selection-rank-box{
 /*border-style: solid;
 border-color:#E0E0E0;
 border-top-width: 1px;
 border-right-width: 1px;
 border-bottom-width: 1px;
 border-left-width: 1px;*/
 margin: 1px 5px 1px 5px;
}
/*Search View*/
#search-condition-view-box{
  border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 1px;
  border-right-width: 0px;
  border-bottom-width: 0px;
  border-left-width: 0px;
  margin: 2px 0px 0px 0px;
}

#search-condition-view-box-div{
  border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 0px;
  border-right-width: 0px;
  border-bottom-width: 0px;
  border-left-width: 0px;
  margin: 2px 5px 0px 5px;
}

  #search-condition-view-box-div .el-form-item{
     margin-bottom:5px;
  }
  #search-condition-view-box-div .el-input__inner{
     height: 30px;
  }
  #search-condition-view-box-div .el-form-item__content{
     line-height: 30px;
  }
  #search-condition-view-box-div .el-input__suffix{
     height: 113%;
  }
</style>