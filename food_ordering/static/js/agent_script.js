// script for agent

function populateTaskList(){

    let el  = document.getElementById('agent-task-list');
    $http.get('/task/').then(result=>{

        el.innerHTML = result;

    }).catch(err =>{

        console.log('error in fetching agent list',err);
        M.toast({html: 'failed to fetch task list.'});

    });
}

function completeTaskClicked(taskId){
    performTaskAction(taskId,'completed');
}

function declineTaskClicked(taskId){
    performTaskAction(taskId,'declined');
}

function acceptTaskClicked(taskId){
    performTaskAction(taskId,'accepted');
}

function performTaskAction(taskId,action){

    $http.put('/task/'+taskId +'?action='+action).then(result=>{
        populateTaskList();
    }).catch(err =>{
         console.log('error in fetching agent list');
         M.toast({html: 'failed to perform given operation.'});
    });
}

document.addEventListener('DOMContentLoaded', function() {
    populateTaskList();
});
