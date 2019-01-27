/**
 * script to handle common client side operations in javascript
 * this is help as some of feature need realtime update, so reloading page every time
 * doesn't seems to be a good idea.
 * Instead we can use AJAX (fetch) to perform realtime and background operations
 */


/**
 * functions to handle http requests
 */
let $http = (function() {

    let privateMethods = {

        http: function(url, method) {

            let options = this.getOptions(method);
            return new Promise(function(accept, reject) {
                fetch(url, options).then(result => {
                    if (result.status == 200) {
                        result.text().then(data => {
                            accept(data);
                        }).catch(err => {
                            reject(err, 'error in reading response stream.');
                        });
                    } else {
                        reject(result.body, result.status);
                    }
                }).catch(err => {
                    reject(err);
                });
            });

        },
        getOptions: function(method) {
            let headerOption = this.getHeader();
            return {
                method: method,
                headers: headerOption
            }
        },
        getHeader: function() {
            let headers = {
                "Cookie": document.cookie
            }
            let csrfMiddlewareToken = this.getCsrfMiddlewareToken();
            if (csrfMiddlewareToken !== null) {
                headers["X-CSRFToken"] = csrfMiddlewareToken;
            }

            return headers
        },
        getCsrfMiddlewareToken: function() {
            try {
                return document.getElementsByName('csrfmiddlewaretoken')[0].defaultValue;
            } catch {
                return null;
            }
        }
    }

    return {
        get: async function(url) {
            return await privateMethods.http(url, 'GET');
        },
        post: async function(url) {
            return await privateMethods.http(url, 'POST');
        },
        put: async function(url) {
            return await privateMethods.http(url, 'PUT');
        },
        delete: async function(url) {
            return await privateMethods.http(url, 'DELETE');
        }
    }

})();

let protocol = location.protocol == 'https:' ? 'wss://' : 'ws://';
const WEB_SOCKET_BASE_URL = protocol + window.location.host +'/ws';

let $socket = (function() {

 let connected = false;
 let ws = null;

 this.connectionState = WebSocket.CLOSED;

 let that = this;

 this.init = function(url) {

  that.url = url;

  return new Promise(function(accept, reject) {

   if (ws && connected === true) {
    accept('Connection is already established');
    return;
   }
   const _ws = new WebSocket(url);
   ws = _ws;

   _ws.onopen = function(e) {
    console.log('connection opened ', e);
    _ws.onmessage = function(e) {
     that.onMessage(e.data || {});
    }
    accept(e);
    connected = true;
    that.connectionState = _ws.readystate;
   }

   _ws.onclose = function(e) {
    console.log('connection closed ', e);
    that.onConnectionError(e);
    reject(e);
    connected = false;
    that.connectionState = _ws.readystate;
   }

   _ws.onerror = function(e) {
    console.log('connection error ', e);
    that.onConnectionError(e);
    reject(e);
    connected = false;
    that.connectionState = _ws.readystate;
   }


  });
 }


 this.sendMessage = function(message) {
  if (ws == null || connected === false) throw ('You must initialize the connection first by calling init().');
  ws.send(message);
 }

 this.stop = function() {
  if (ws) {
   ws.close();
  }
 }

 this.onMessage = function(...args) {};
 this.onConnectionError = function(e){
     // attempt reconnect
     console.log('some error',e)
 };

 return this;
})();
