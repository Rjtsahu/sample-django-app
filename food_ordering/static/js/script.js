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
        delete: async function(url) {
            return await privateMethods.http(url, 'DELETE');
        }
    }

})();