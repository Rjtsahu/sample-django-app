// script for agent

function populateTaskList(){

    let el  = document.getElementById('agent-task-list');
    $http.get('/task/').then(result=>{

        el.innerHTML = result;

    }).catch(err =>{

        console.log('error in fetching agent list');
        M.toast({html: 'failed to fetch task list.'});

    });
}

document.addEventListener('DOMContentLoaded', function() {
    populateTaskList();
});
