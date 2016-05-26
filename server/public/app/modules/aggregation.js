'use strict';
angular.module('Aggregation')

/* DASHBOARD CONTROLLER */      
.controller('AggregationCtrl', function($scope, $http, $routeParams, $window, $filter, ngTableParams) {
    
    var id = $routeParams.id;
    
    $scope.refresh = function() {  
		$http.get('http://localhost:3000/api/aggregation/' + id).success(function(response) {
            
            // parse json
			console.log("Daten des GET-Requests empfangen!");
			$scope.aggregation = angular.fromJson(response);
            console.log($scope.aggregation);
        });
    };
    
    // delete aggregation data in db
    $scope.deleteAggregation = function() { 
        var r = confirm("Soll diese Aggregation wirklich gelöscht werden? Alle Daten zu dieser Aggregation werden unwiderruflich entfernt!");
        if (r == true) {
            $http.delete('http://localhost:3000/api/aggregation/' + id).success(function(response) { 
                $window.location.href = '/#/aggregations';
            });
        };
	};
    
    // initial call to build data model
    $scope.refresh();
    
});