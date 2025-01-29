/**
 * FreemobileSms config directive
 * Handle freemobilesms configuration
 */
angular
.module('Cleep')
.directive('freemobilesmsConfigComponent', ['toastService', 'freemobilesmsService', 'cleepService',
function(toast, freemobilesmsService, cleepService) {

    var freemobilesmsController = function() {
        var self = this;
        self.userid = '';
        self.apikey = '';

        self.$onInit = function() {
            cleepService.getModuleConfig('freemobilesms')
                .then(function(config) {
                    self.userid = config.userid;
                    self.apikey = config.apikey;
                });
        };

        self.setCredentials = function() {
            freemobilesmsService.setCredentials(self.userid, self.apikey)
                .then(function(resp) {
                    return cleepService.reloadModuleConfig('freemobilesms');
                })
                .then(function(config) {
                    self.userid = config.userid;
                    self.apikey = config.apikey;
                    toast.success('Configuration saved. Please use test button to validate credentials.');
                });
        };

        self.test = function() {
            freemobilesmsService.test()
                .then(function(resp) {
                    toast.success('Sms sent. Check your phone.');
                });
        };
    };

    return {
        templateUrl: 'freemobilesms.config.html',
        replace: true,
        scope: true,
        controller: freemobilesmsController,
        controllerAs: '$ctrl',
    };
}]);
