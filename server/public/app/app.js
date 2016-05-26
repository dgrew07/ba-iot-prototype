'use strict';

/* DECLARE MODULES */
angular.module('Trips', []);
angular.module('Trip', []);
angular.module('Aggregations', []);
angular.module('Aggregation', []);

angular.module('baApp', [
    'Trips',
    'Trip',
    'Aggregations',
    'Aggregation',
    'ui.bootstrap',
    'ngRoute',
    'ngTable',
    'leaflet-directive'
])

/* ROUTING + DEBUGGING CONFIG */
.config(['$routeProvider', function ($routeProvider) {

    $routeProvider
    
        .when('/', {
            redirectTo: '/trips'
        })

        .when('/trips', {
            controller: 'TripsCtrl',
            templateUrl: 'app/views/trips.html'
        })
		
		.when('/trips/:id', {
            controller: 'TripCtrl',
            templateUrl: 'app/views/trip.html'
        })
        
        .when('/aggregations', {
            controller: 'AggregationsCtrl',
            templateUrl: 'app/views/aggregations.html'
        })
        
        .when('/aggregations/:id', {
            controller: 'AggregationCtrl',
            templateUrl: 'app/views/aggregation.html'
        })
		
        .otherwise({ redirectTo: '/trips' });
}])

.filter('duration', function() {
    //returns duration from milliseconds in hh:mm:ss format
    return function(millseconds) {
        var seconds = Math.floor(millseconds / 1000);
        var h = 3600;
        var m = 60;
        var hours = Math.floor(seconds/h);
        var minutes = Math.floor( (seconds % h)/m );
        var scnds = Math.floor( (seconds % m) );
        var timeString = '';
        if(scnds < 10) scnds = "0"+scnds;
        if(hours < 10) hours = "0"+hours;
        if(minutes < 10) minutes = "0"+minutes;
        timeString = hours +":"+ minutes +":"+scnds;
        return timeString;
    }
})


