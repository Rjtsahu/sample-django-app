
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

// code for webSocket for realtime communication
let wsUrl = WEB_SOCKET_BASE_URL + '/manager'

$socket.init(wsUrl).then((event) => {
 console.log(' event: ', event);

 $socket.sendMessage('message from agent');

}).catch(err => {
 console.log('error ', err);
});

$socket.onMessage = function(e) {
 console.log('inside onMessage client', e)
}
