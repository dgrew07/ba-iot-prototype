'use strict';
angular.module('Aggregations')

/* TRIPS CONTROLLER */      
.controller('AggregationsCtrl', function($scope, $http, $filter, ngTableParams) {
    
    // define refresh-fuction to update data-model
	$scope.refresh = function() {  
		$http.get('http://localhost:3000/api/aggregation').success(function(response) {
            
            //parse json
			console.log("Daten des GET-Requests empfangen!");
			$scope.aggregations = angular.fromJson(response);
            console.log($scope.aggregations);
            
            // instantiate ngTable
            $scope.aggregationsTable = new ngTableParams({
                page: 1,
                count: 10
            }, {
                total: $scope.aggregations.length, 
                getData: function ($defer, params) {
                    $scope.data = params.sorting() ? $filter('orderBy')($scope.aggregations, params.orderBy()) : $scope.aggregations;
                    $scope.data = $scope.data.slice((params.page() - 1) * params.count(), params.page() * params.count());
                    $defer.resolve($scope.data);
                }
            });
		});
	};
    
    // start aggregation of trips 
    $scope.aggregateNew = function() { 
        $http.get('http://localhost:3000/api/newaggregation').success(function(response) {
            alert("Aggregation abgeschlossen!");
            $scope.refresh();
		});
	};
    
    // initial call to build data model
    $scope.refresh();
    
});