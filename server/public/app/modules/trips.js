'use strict';
angular.module('Trips')

/* TRIPS CONTROLLER */      
.controller('TripsCtrl', function($scope, $http, $filter, ngTableParams) {
    
    // define refresh-fuction to update data-model
	$scope.refresh = function() {  
		$http.get('http://localhost:3000/api/trip').success(function(response) {
            
            //parse json
			console.log("Daten des GET-Requests empfangen!");
			$scope.trips = angular.fromJson(response);
            console.log($scope.trips);
            
            // instantiate ngTable
            $scope.tripsTable = new ngTableParams({
                page: 1,
                count: 10
            }, {
                total: $scope.trips.length, 
                getData: function ($defer, params) {
                    $scope.data = params.sorting() ? $filter('orderBy')($scope.trips, params.orderBy()) : $scope.trips;
                    $scope.data = $scope.data.slice((params.page() - 1) * params.count(), params.page() * params.count());
                    $defer.resolve($scope.data);
                }
            });
		});
	};
    
    // initial call to build data model
    $scope.refresh();
    
});