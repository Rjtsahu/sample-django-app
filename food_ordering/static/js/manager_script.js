// code for webSocket for realtime communication
let wsUrl = WEB_SOCKET_BASE_URL + '/manager/'

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
		onItemStateUpdate(data);
	} catch {
		console.log('invalid json from $socket.onMessage, data:',e);
	}
}

function onItemStateUpdate(data) {
	console.log('event: ', data.event);
	let message = data.data;
	M.toast({
		html: message
	});

	// refresh view
	getTaskList();
}

// handle button click of cancel button
function cancelTask(taskId) {

	$http.delete('/task/' + taskId).then(result => {
		getTaskList()
	}).catch(err => {
		M.toast({
			html: 'Task cancellation failed'
		});
	});
}

function getTaskList() {
    let el = document.getElementById('manager-task-list');

	$http.get('/task/').then(result => {
        el.innerHTML = result;
	}).catch(err => {
		M.toast({
			html: 'Failed to fetch tasks'
		});
	});
}

document.addEventListener('DOMContentLoaded', function () {
	getTaskList();
});