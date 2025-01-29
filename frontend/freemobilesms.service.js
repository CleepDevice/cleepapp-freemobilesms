/**
 * FreemobileSms service
 * Handle freemobilesms module requests
 */
angular
.module('Cleep')
.service('freemobilesmsService', ['rpcService',
function(rpcService) {
    const self = this;

    self.setCredentials = function (userid, apikey) {
        return rpcService.sendCommand('set_credentials', 'freemobilesms', {'userid':userid, 'apikey':apikey});
    };

    self.test = function () {
        return rpcService.sendCommand('test', 'freemobilesms');
    };

}]);
