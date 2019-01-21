
    // handle button click of cancel button
    function cancelTask(taskId){

       $http.delete('/task/' + taskId).then(result=>{
         M.toast({html: 'Task cancelled'});

         setTimeout(function(){
            location.reload();
         },500);
       }).catch(err=>{
          M.toast({html: 'Task cancellation failed'});
       });

    }
