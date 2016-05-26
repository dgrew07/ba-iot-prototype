'use strict';
angular.module('Trip')

/* TRIPS CONTROLLER */      
.controller('TripCtrl', function($scope, $http, $routeParams, $window, $filter, ngTableParams, leafletData) {
    
    var id = $routeParams.id;
    
    // helper function to sort arrays by key
    var sortByKey = function(array, key) {
        return array.sort(function(a, b) {
            var x = a[key]; var y = b[key];
            return ((x < y) ? -1 : ((x > y) ? 1 : 0));
        });
    };

    // define refresh-fuction to update data-model
	$scope.refresh = function() {  
		$http.get('http://localhost:3000/api/trip/' + id).success(function(response) {
            
            // parse json
			console.log("Daten des GET-Requests empfangen!");
			$scope.trip = angular.fromJson(response);
            console.log($scope.trip);
            
            // instantiate ngTable
            $scope.reportsTable = new ngTableParams({
                page: 1,
                count: 10
            }, {
                total: $scope.trip.reports.length, 
                getData: function ($defer, params) {
                    $scope.data = params.sorting() ? $filter('orderBy')($scope.trip.reports, params.orderBy()) : $scope.trip.reports;
                    $scope.data = $scope.data.slice((params.page() - 1) * params.count(), params.page() * params.count());
                    $defer.resolve($scope.data);
                }
            });
            
            // get lat/long values from reports
            // define starting, ending and map center location
            var arr_reports = $scope.trip.reports;
            // sort array by counter
            arr_reports = sortByKey(arr_reports, 'counter');
            
            var loc_center = {};
            var loc_start = {};
            var loc_end = {};
            var arr_latlong = [];
            var latlonglen = arr_reports.length;
            
            var counter_start = 1;
            var counter_end = latlonglen - 1;
            var found_start = false;
            var found_end = false;
            
            // find starting point for the map icon / polyline in the first 15 entries
            for(var i = 0; i < 15; i++) { 
                if (typeof arr_reports[i].gps_latitude !== 'undefined' && typeof arr_reports[i].gps_longitude !== 'undefined' && isNaN(arr_reports[i].gps_latitude) === false && isNaN(arr_reports[i].gps_longitude) === false && arr_reports[i].gps_latitude !== null && arr_reports[i].gps_longitude !== null && found_start === false) {
                    loc_start = {
                        lat: arr_reports[i].gps_latitude,
                        lng: arr_reports[i].gps_longitude,
                        icon: {
                            iconUrl: 'img/map_start.png',
                            iconSize: [60, 80],
                            iconAnchor: [40, 80],
                            popupAnchor: [0, 0],
                            shadowSize: [0, 0],
                            shadowAnchor: [0, 0]
                        }
                    };
                    found_start = true;
                } else {
                    counter_start++;
                };
            };
            
            // find end point for the map icon / polyline
            for(var j = latlonglen - 1; j > latlonglen - 15; j = j - 1) { 
                if (typeof arr_reports[j].gps_latitude !== 'undefined' && typeof arr_reports[j].gps_longitude !== 'undefined' && isNaN(arr_reports[j].gps_latitude) === false && isNaN(arr_reports[j].gps_longitude) === false && arr_reports[j].gps_latitude !== null && arr_reports[j].gps_longitude !== null && found_end === false) {
                    loc_end = {
                        lat: arr_reports[j].gps_latitude,
                        lng: arr_reports[j].gps_longitude,
                        icon: {
                            iconUrl: 'img/map_end.png',
                            iconSize: [60, 80],
                            iconAnchor: [40, 80],
                            popupAnchor: [0, 0],
                            shadowSize: [0, 0],
                            shadowAnchor: [0, 0]
                        }
                    };
                    found_end = true;
                } else {
                    counter_end = counter_end - 1;
                };
            };

            // find the points for the polyline  between start/end
            for(var k = counter_start; k < counter_end; k=k+5) { 
                if (typeof arr_reports[k].gps_latitude !== 'undefined' && typeof arr_reports[k].gps_longitude !== 'undefined' && isNaN(arr_reports[k].gps_latitude) === false && isNaN(arr_reports[k].gps_longitude) === false && arr_reports[k].gps_latitude !== null && arr_reports[k].gps_longitude !== null) {
                    arr_latlong.push({lat: arr_reports[k].gps_latitude, lng: arr_reports[k].gps_longitude}) 
                };
            };
            
            var midmap = Math.round(latlonglen / 2);
            // find a valid position to center the map
            for(var l = midmap - 15; l < midmap + 15; l++) { 
                    if (typeof arr_reports[l].gps_latitude !== 'undefined' && typeof arr_reports[l].gps_longitude !== 'undefined' && isNaN(arr_reports[l].gps_latitude) === false && isNaN(arr_reports[l].gps_longitude) === false && arr_reports[l].gps_latitude !== null && arr_reports[l].gps_longitude !== null) {
                        loc_center = {
                            lat: arr_reports[l].gps_latitude,
                            lng: arr_reports[l].gps_longitude,
                            zoom: 12
                        };
                    };
            };
            
            console.log(loc_center);
            console.log(loc_start);
            console.log(loc_end);
            console.log(arr_latlong);
            
            
            // leaflet map directive params
            angular.extend($scope, {
                mapCenter: loc_center,
                mapPaths: {
                    p1: {
                        color: '#008000',
                        weight: 9,
                        latlngs: arr_latlong
                    }
                },
                mapMarkers: {
                    start: loc_start,
                    end: loc_end
                },
                mapDefaults: {
                    scrollWheelZoom: false
                }
            });
            
		});
	};
    
    // start analyses of trip data on the server
    $scope.analyseTrip = function() { 
        $http.get('http://localhost:3000/api/analysis/' + id).success(function(response) {
            alert("Analyse abgeschlossen!");
            $scope.refresh();
		});
	};
    
    // delete trip data in db
    $scope.deleteTrip = function() { 
        var r = confirm("Soll diese Fahrt wirklich gelöscht werden? Alle Daten zu dieser Fahrt werden unwiderruflich entfernt!");
        if (r == true) {
            $http.delete('http://localhost:3000/api/trip/' + id).success(function(response) { 
                $window.location.href = '/#/trips';
            });
        };
	};

    $scope.currentTab = 1;
    
    // initial call to build data model
    $scope.refresh();
    
});