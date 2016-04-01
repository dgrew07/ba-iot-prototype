var gpsApp = angular.module('gpsApp', ['ngMap']);

gpsApp.controller('MainCtrl', function($scope, $http, NgMap) {
    console.log("Hello World vom MainController! :-)");

	// define refresh-fuction to update data-model
	var refresh = function() {
		$http.get('/gpsdata').success(function(response) {
			console.log("Daten des GET-Requests empfangen!");
			$scope.items = response;
			$scope.currentItem = "";
		});
	};

	// initial call to build data model
	refresh();

	// add an item 
	// will take the object currentItem
	$scope.addItem = function() {
		console.log($scope.currentItem);
		$http.post('/gpsdata', $scope.currentItem).success(function(response) {
			console.log(response);
			refresh();
		});
	};

	// delete an item
	// needs valid item id
	$scope.deleteItem = function(id) {
		console.log(id);
		$http.delete('/gpsdata/' + id).success(function(response) {
			refresh();
		});
	};

	// edit an item
	// requests data of single item, needs valid item id
	$scope.editItem = function(id) {
		console.log(id);
		$http.get('/gpsdata/' + id).success(function(response) {
			$scope.currentItem = response;
		});
	};  
	
	// update an item
	// will take the object currentItem to update item by id
	$scope.updateItem = function() {
		console.log($scope.currentItem._id);
		$http.put('/gpsdata/' + $scope.currentItem._id, $scope.currentItem).success(function(response) {
			refresh();
		})
	};
	
	// clear object currentItem
	$scope.deselect = function() {
		$scope.currentItem = "";
	}

});﻿