// script for agent

function populateTaskList() {

	let el = document.getElementById('agent-task-list');
	$http.get('/task/').then(result => {

		el.innerHTML = result;

	}).catch(err => {

		console.log('error in fetching agent list', err);
		M.toast({
			html: 'failed to fetch task list.'
		});

	});
}

function populateIncomingTask(){
    let el = document.getElementById('agent-incoming-task');
    $http.get('/task/latest').then(result=>{
    		el.innerHTML = result;
    }).catch(err=>{

    	console.log('error in fetching incoming task', err);
		M.toast({
			html: 'failed to fetch task incoming task.'
		});
    });
}
function completeTaskClicked(taskId) {
	performTaskAction(taskId, 'completed');
}

function declineTaskClicked(taskId) {
	performTaskAction(taskId, 'declined');
}

function acceptTaskClicked(taskId) {
	performTaskAction(taskId, 'accepted');
}

function performTaskAction(taskId, action) {

	$http.put('/task/' + taskId + '?action=' + action).then(result => {
		populateTaskList();
		if(action === 'accepted'){
		    populateIncomingTask();
		}
	}).catch(err => {
		console.log('error in fetching agent list');
		M.toast({
			html: 'failed to perform given operation.'
		});
	});
}

document.addEventListener('DOMContentLoaded', function () {
	populateTaskList();
	populateIncomingTask();
});

// code for websocket for realtime communication
let wsUrl = WEB_SOCKET_BASE_URL + '/agent/'

$socket.init(wsUrl).then((event) => {
	console.log(' event: ', event);

	$socket.sendMessage('message from agent');

}).catch(err => {
	console.log('error ', err);
});

$socket.onMessage = function (e) {
	console.log('inside onMessage client', e);
	try{
	    let data = JSON.parse(e);
	    console.log('data ',data)
	    if(data.event === 'new-task-request'){
	       let titleEl = document.getElementById('requested-task-title');
	       let detailEl = document.getElementById('requested-task-detail');
	       let buttonEl = document.getElementById('requested-task-button');

	       titleEl.innerText = data.data.title;
	       detailEl.innerText = data.data.detail;
	       buttonEl.onclick = acceptTaskClicked(data.data.id);
	    }
	}catch(e){
	}
}