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

function populateIncomingTask() {
	let el = document.getElementById('agent-incoming-task');
	$http.get('/task/latest').then(result => {
		el.innerHTML = result;
		disableAcceptButtonWhenAcceptedCountExceedsThree()
	}).catch(err => {

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
		if (action === 'accepted') {
			populateIncomingTask();
		}
	}).catch(err => {
		console.log('error in fetching agent list');
		M.toast({
			html: 'failed to perform given operation.'
		});
	});
}

function disableAcceptButtonWhenAcceptedCountExceedsThree() {
	try {
		let itemCount = document.getElementsByTagName('tbody')[0].childElementCount;
		let buttonEl = document.getElementById('requested-task-button');

		if (itemCount >= 3) {
			buttonEl.setAttribute('class', 'btn-small disabled');
		} else{
			buttonEl.setAttribute('class', 'btn-small waves-light');
		}
	} catch {
		console.log('some elements not find, ignoring disable button');
	}
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
	try {
		let data = JSON.parse(e);
		console.log('data ', data)
		if (data.event === 'new-task-request') {
			let headingEl = document.getElementById('requested-task-heading');
			let titleEl = document.getElementById('requested-task-title');
			let detailEl = document.getElementById('requested-task-detail');
			let buttonEl = document.getElementById('requested-task-button');
			let divEl = document.getElementById('requested-task-div');

			headingEl.innerText = 'Incoming request';
			titleEl.innerText = 'TITLE:  ' + data.data.title;
			detailEl.innerText = 'DETAIL:  ' + data.data.detail;
			buttonEl.setAttribute('onclick', "acceptTaskClicked(" + data.data.id + ")");
			divEl.setAttribute('style', 'display:block;');

			disableAcceptButtonWhenAcceptedCountExceedsThree()
		}
	} catch (e) {}
}
