// server.js 
// author: 			Daniel Grewe

var express = require('express');
var mongojs = require('mongojs');
var app = express();

// include statistics package : https://www.npmjs.com/package/jsregress
var stat = require('jsregress');
// include haversine formula package : https://github.com/njj/haversine
var haversine = require('haversine')
// try synchronous request to hit the OSM API : https://www.npmjs.com/package/sync-request
var syncrequest = require('sync-request');

// establish db connection, connects to default port on localhost, otherwise use "mongojs(databaseUrl:port, database, collections);"
var db = mongojs('ba', ['trips', 'aggregations']);

// use bodyParser to parse json
var bodyParser = require('body-parser');

// use file size limit on payloads
app.use(bodyParser.json({limit: '50mb'}));
app.use(bodyParser.urlencoded({limit: '50mb', extended: true}));

// make the webinterface accessible
app.use(express.static(__dirname + '/public'));


/* HELPER FUNCTIONS */
// sorting function for arrays
var sortByKey = function(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        return ((x < y) ? -1 : ((x > y) ? 1 : 0));
    });
};

// get the element with the highest occurrence in an array
var mode = function(array) {
    if(array.length == 0)
        return null;
    var modeMap = {};
    var maxEl = array[0], maxCount = 1;
    for(var i = 0; i < array.length; i++){
        var el = array[i];
        if(modeMap[el] == null)
            modeMap[el] = 1;
        else
            modeMap[el]++;	
        if(modeMap[el] > maxCount) {
            maxEl = el;
            maxCount = modeMap[el];
        };
    };
    return maxEl;
};



/* API TOUCHPOINTS */

// route: /api/trip, method: GET
// return all trips in database
app.get('/api/trip', function (req, res) {
  console.log('I received a GET request on route /api/trip');
  db.trips.find(function (err, docs) {
    //console.log(docs);
    res.json(docs);
  });
});

// route /api/trip/id, method GET
// return single trip by id
app.get('/api/trip/:id', function (req, res) {
  var id = req.params.id;
  console.log('I received a GET request on route /api/trip/' + id);
  db.trips.findOne({_id: mongojs.ObjectId(id)}, function (err, doc) {
    res.json(doc);
  });
});

// route /api/trip/id, method GET
// return single trip by id
app.get('/api/trip/:id', function (req, res) {
  var id = req.params.id;
  console.log('I received a GET request on route /api/trip/' + id);
  db.trips.findOne({_id: mongojs.ObjectId(id)}, function (err, doc) {
    res.json(doc);
  });
});

// route /api/trip/id, method DELETE
// delete a single trip in the collection (by id)
app.delete('/api/trip/:id', function (req, res) {
  var id = req.params.id;
  console.log('I received a DELETE request on route /api/trip/' + id);
  db.trips.remove({_id: mongojs.ObjectId(id)},{justOne: true}, function (err, doc) {
    res.json('The trip ' + id + ' has been deleted!');
  });
});

// route: /api/analysis/id, method GET
// analyse the trip and update doc in collection
app.get('/api/analysis/:id', function (req, res) {
  var id = req.params.id;
  console.log('I received a GET request on route /api/analysis/' + id);
  db.trips.findOne({_id: mongojs.ObjectId(id)}, function (err, doc) {
    var arr = doc.reports;  
    
    // declare temp data arrays
    var arr_accxpos = [];
    var arr_accxneg = [];
    var arr_accypos = [];
    var arr_accyneg = [];
    var arr_speed = [];
    var arr_latlong = [];
    var arr_speedlatlong = [];
    
    // fill the arrays with raw data from trip reports
    // note that there are certain offsets for the raw values
    for (var i = 0, len = arr.length; i < len; i++) {
        if (arr[i].acc_axis_x >= 0.1) {
            arr_accxpos.push(arr[i].acc_axis_x);
        } else if (arr[i].acc_axis_x <= -0.1) {
            arr_accxneg.push(arr[i].acc_axis_x);
        };
        if (arr[i].acc_axis_y >= 0.1) {
            arr_accypos.push(arr[i].acc_axis_y);
        } else if (arr[i].acc_axis_y <= -0.1) {
            arr_accyneg.push(arr[i].acc_axis_y);
        };
        if (arr[i].gps_speed >= 0.5) {
            arr_speed.push(arr[i].gps_speed * 3.6);
        }; 
    };
    
    // STATISTICS 
    // calucate the max/min, mean and std error for the values of each array
    var accxpos_max = Math.max.apply(Math, arr_accxpos); 
    var accxneg_min = Math.abs(Math.min.apply(Math, arr_accxneg));
    var accypos_max = Math.max.apply(Math, arr_accypos); 
    var accyneg_min = Math.abs(Math.min.apply(Math, arr_accyneg));
    var speed_max = Math.max.apply(Math, arr_speed);
    var accxpos_mean = arr_accxpos.mean();
    var accxpos_std = arr_accxpos.std();
    var accxneg_mean = Math.abs(arr_accxneg.mean());
    var accxneg_std = Math.abs(arr_accxneg.std());
    var accypos_mean = arr_accypos.mean();
    var accypos_std = arr_accypos.std();
    var accyneg_mean = Math.abs(arr_accyneg.mean());
    var accyneg_std = Math.abs(arr_accyneg.std());
    var gpsspeed_mean = arr_speed.mean();
    var gpsspeed_std = arr_speed.std();
    
    // sort the array by counter to get the lat/long-values in correct order
    arr = sortByKey(arr, 'counter');
    
    // DISTANCE CALCULATION WITH HAVERSINE 
    // fill the array with lat/long data from trip reports
    for(var i = 1, len = arr.length; i < len; i++) { 
        if (isNaN(arr[i].gps_latitude) === false && isNaN(arr[i].gps_longitude) === false && arr[i].gps_latitude !== null && arr[i].gps_longitude !== null) {
            if(arr[i].gps_fixtime !== arr[i-1].gps_fixtime) {
                arr_latlong.push({latitude: arr[i].gps_latitude, longitude: arr[i].gps_longitude})
            };   
        };
    };
    //console.log(arr_latlong);
    
    // calculate trip distance with the haversine formula package
    var startpoint;
    var endpoint;
    var tempresult;
    var distancekm = 0;
    for(var i = 0, len = arr_latlong.length; i < len; i++) { 
        if(i + 1 < len) { 
            if(arr_latlong[i+1].latitude !== null && arr_latlong[i].longitude !== null && arr_latlong[i+1].longitude !== null && arr_latlong[i].longitude !== null)
                tempresult = haversine(arr_latlong[i], arr_latlong[i+1], {unit: 'km'})
                distancekm = distancekm + tempresult;
        }
    };
    //console.log(distancekm);

    // ANALYSE HIGHWAY TYPES AND SPEED LIMITS
    // fill the array with lat/long data and corresponding speeds from trip reports
    for(var i = 1, len = arr.length; i < len; i++) { 
        if (isNaN(arr[i].gps_latitude) === false && isNaN(arr[i].gps_longitude) === false && isNaN(arr[i].gps_speed) === false && arr[i].gps_latitude !== null && arr[i].gps_longitude !== null && arr[i].gps_speed !== null) {
            if(arr[i].gps_fixtime !== arr[i-1].gps_fixtime) {
                arr_speedlatlong.push({latitude: arr[i].gps_latitude, longitude: arr[i].gps_longitude, speed: arr[i].gps_speed * 3.6})
            };   
        };
    };
    //console.log(arr_speedlatlong);
    
    // declare temp data array for highway-tags of the OSM API
    var arr_highways = [];
    var speedlimit_counter = 0;
    var minbblat;
    var minbblon;
    var maxbblat;
    var maxbblon;
    var tempmaxspeed = 0;
    
    // determine the bounding box for the OSM API call, call the API, get desired values
    for(var i = 10, len = arr_speedlatlong.length; i + 10 < len; i = i + 120) { 
        // define the bounding box borders for in a 10 entry intervall
        if (arr_speedlatlong[i-10].latitude <= arr_speedlatlong[i].latitude) {
            minbblat = arr_speedlatlong[i-10].latitude;
            maxbblat = arr_speedlatlong[i].latitude;
        } else {
            minbblat = arr_speedlatlong[i].latitude;
            maxbblat = arr_speedlatlong[i-10].latitude;
        };
        if (arr_speedlatlong[i-10].longitude <= arr_speedlatlong[i].longitude) {
            minbblon = arr_speedlatlong[i-10].longitude;
            maxbblon = arr_speedlatlong[i].longitude;
        } else {
            minbblon = arr_speedlatlong[i].longitude;
            maxbblon = arr_speedlatlong[i-10].longitude;
        };
        // get the maximum speed out of the interval
        for (var j = i - 10; j < i; j++) {
            if (arr_speedlatlong[j].speed > tempmaxspeed) {
                tempmaxspeed = arr_speedlatlong[j].speed;
            };
        };
        
        // defines a function which is called for each object in the 'elements' array of the answer from the OSM Overpass API
        var getSpeedAndHighway = function(element, index, array) {
            try {
                // write highway tags to array (if given)
                // leave out trunks (Ausfahrten), footways (Fußgaengerwege), bridleway, steps, paths, cycleway,
                // explanation: http://wiki.openstreetmap.org/wiki/Key:highway
                if (element.tags.highway !== null && element.tags.highway !== 'footway' && element.tags.highway !== 'bridleway' && element.tags.highway !== 'steps' && element.tags.highway !== 'paths' && element.tags.highway !== 'cycleway') {
                    arr_highways.push(element.tags.highway);
                }
                
            } catch (e) {
                console.log('Kein highway-Tag vorhanden bzw. nicht definiert!');
            };
            try {
                // check if the allowed max speed was violated (if given)
                // use a tolerance factor of 6% for the speed
                if (element.tags.maxspeed !== null && element.tags.maxspeed < (tempmaxspeed * 1.06)) {
                    speedlimit_counter++;
                };
            } catch (e) {
                console.log('Kein maxspeed-Tag vorhanden bzw. nicht definiert!');
            };
        }
        
        // try to make synchronous http request (multiple async requests are too hard to handle)
        try {
            var request_str = 'https://www.overpass-api.de/api/interpreter?data=[out:json];way[highway](' + minbblat + ',' + minbblon + ',' + maxbblat + ',' + maxbblon + ');out%20meta;';
            console.log(request_str);
            var osmresponse = syncrequest('GET', request_str, {
                'headers': {
                    'Content-Type': 'application/json'
                }
            });
            var osmresponse_data = JSON.parse(osmresponse.getBody());
            console.log(JSON.stringify(osmresponse_data));
            // loop through the 'way'-elements of the OSM API response
            if (osmresponse_data.elements.length > 0) {
                // call a function on each element, which will rear the desired tags
                osmresponse_data.elements.forEach(getSpeedAndHighway);
            };
            
  
        // if the API answers with an error, this is usually due to the number of connections
        // just wait a few seconds and try with the next one
        } catch (e) {
            console.log('OSM Overpass API limit reached (possibly), waiting for a few seconds...');    
        }; 
    };
    
    // get most used street type and translate it
    var fav_highway = mode(arr_highways);
    var fav_highway_german;
    var location;
    if (fav_highway === 'motorway') {
        fav_highway_german = 'Autobahn';
        location = 'außerorts';
    } else if (fav_highway === 'trunk') {
         fav_highway_german = 'Bundesstraße';
         location = 'außerorts';
    } else if (fav_highway === 'primary') {
         fav_highway_german = 'Hauptstraße';
         location = 'innerorts';
    } else if (fav_highway === 'secondary') {
         fav_highway_german = 'Landstraße';
         location = 'außerorts';
    } else if (fav_highway === 'tertiary') {
         fav_highway_german = 'Kreisstraße';
         location = 'außerorts';
    } else if (fav_highway === 'residential') {
         fav_highway_german = 'Straße in Wohngebiet';
         location = 'innerorts';
    } else if (fav_highway === 'unclassified') {
         fav_highway_german = 'Erschließungs- oder Kreisstraße';
         location = 'innerorts';
    };
    // determine percentage of its occurence
    var count_fav_highway = 0;
    for (var i = 0; i < arr_highways.length; i++) {
        if (arr_highways[i] === fav_highway) { 
            count_fav_highway++; 
        };
    };
    var fav_highway_perc = count_fav_highway / arr_highways.length; 
    
   
    console.log(speedlimit_counter);
    console.log(arr_highways);

    // prepare analysis db input/update
    var trip_analysis = {
        max_ax_pos: accxpos_max,
        max_ay_pos: accypos_max,
        max_speed: speed_max,
        min_ax_neg: accxneg_min,
        min_ay_neg: accyneg_min,
        mean_ax_pos: accxpos_mean,
        mean_ay_pos: accypos_mean,
        mean_ax_neg: accxneg_mean,
        mean_ay_neg: accyneg_mean,
        mean_speed: gpsspeed_mean,
        std_ax_pos: accxpos_std,
        std_ay_pos: accypos_std,
        std_ax_neg: accxneg_std,
        std_ay_neg: accyneg_std,
        std_speed: gpsspeed_std,
        speed_violations: speedlimit_counter,
        favorite_highway: fav_highway_german,
        favorite_highway_perc: fav_highway_perc,
        favorite_location: location
    };
    
    // update db doc
    db.trips.findAndModify({
        query: { _id: mongojs.ObjectId(id) },
        update: { $set: { 
            analysis: trip_analysis,
            analysed: true,
            length: distancekm
        } },
        new: true
    }, function (err, doc, lastErrorObject) {
        // doc.tag === 'maintainer'
    })
    res.json('The trip ' + id + ' has been analysed!');
  });
});

// route /api/beacon, method POST
// receive json encoded trip data and write it to db
app.post('/api/beacon', function (req, res) {
  console.log('I received a POST request!');
  //console.log(req.body);
  // calculate duration
  var d1 = new Date(req.body.time_start);
  var d2 = new Date(req.body.time_end);
  req.body.time_diff = d2 - d1;
  req.body.analysed = false;
  var dayornight;
  if (d2.getHours() < 21) {
    dayornight = 'Tagfahrt';
  } else {
    daynight = 'Nachtfahrt';
  };
  req.body.daynight = dayornight;
  // insert trip into db
  db.trips.insert(req.body, function(err, doc) {
    res.json(doc);
  });
});

// route: /api/newaggregation, method GET
// aggregate all analysed trips and store the aggregation in the db
app.get('/api/newaggregation', function (req, res) {
    console.log('I received a GET request on route /api/analysis/aggregation');
    db.trips.find(function (err, docs) {
        var arr_alltrips = docs;

        // temp arrays
        var arr_accxpos_means = [];
        var arr_accxneg_means = [];
        var arr_accypos_means = [];
        var arr_accyneg_means = [];
        var arr_speed_means = [];
        
        var arr_accxpos_maxs = [];
        var arr_accxneg_mins = [];
        var arr_accypos_maxs = [];
        var arr_accyneg_mins = [];
        var arr_speed_maxs = [];
        
        var arr_lengths = [];
        var arr_durations = [];
        var arr_speedviol = [];
        var arr_highways = [];
        var arr_locations = [];
        
        var tripcount = 0;
   
        // function to push values of the analysis for each trip to temp arrays
        var aggregateAnalysed = function(element, index, array) {
            if (element.analysed === true) {
                
                tripcount++;
                
                // push the mean values for each element to arrays
                arr_accxpos_means.push(element.analysis.mean_ax_pos);
                arr_accxneg_means.push(element.analysis.mean_ax_neg);
                arr_accypos_means.push(element.analysis.mean_ay_pos);
                arr_accyneg_means.push(element.analysis.mean_ay_neg);
                arr_speed_means.push(element.analysis.mean_speed);
                
                // push max/min values for each element to arrays
                arr_accxpos_maxs.push(element.analysis.max_ax_pos);
                arr_accxneg_mins.push(element.analysis.min_ax_neg);
                arr_accypos_maxs.push(element.analysis.max_ay_pos);
                arr_accyneg_mins.push(element.analysis.min_ay_neg);
                arr_speed_maxs.push(element.analysis.max_speed);
                
                // other values
                arr_lengths.push(element.length);
                arr_durations.push(element.time_diff);
                arr_speedviol.push(element.analysis.speed_violations);
                arr_highways.push(element.analysis.favorite_highway);
                arr_locations.push(element.analysis.favorite_location);
            };
        };
        arr_alltrips.forEach(aggregateAnalysed);
        
        // means/stds for the mean-values of acceleration +/- x/y
        var aggr_accxpos_mean = arr_accxpos_means.mean();
        var aggr_accxpos_std = arr_accxpos_means.std();
        var aggr_accxneg_mean = arr_accxneg_means.mean();
        var aggr_accxneg_std = arr_accxneg_means.std();
        var aggr_accypos_mean = arr_accypos_means.mean();
        var aggr_accypos_std = arr_accypos_means.std();
        var aggr_accyneg_mean = arr_accyneg_means.mean();
        var aggr_accyneg_std = arr_accyneg_means.std();
        
        // means/stds for the min/max-values of acceleration +/- x/y
        var aggr_accxposmax_mean = arr_accxpos_maxs.mean();
        var aggr_accxposmax_std = arr_accxpos_maxs.std();
        var aggr_accxnegmin_mean = arr_accxneg_mins.mean();
        var aggr_accxnegmin_std = arr_accxneg_mins.std();
        var aggr_accyposmax_mean = arr_accypos_maxs.mean();
        var aggr_accyposmax_std = arr_accypos_maxs.std();
        var aggr_accynegmin_mean = arr_accyneg_mins.mean();
        var aggr_accynegmin_std = arr_accyneg_mins.std();
        
        // means/stds for all speed related values
        var aggr_speed_mean = arr_speed_means.mean();
        var aggr_speed_std = arr_speed_means.std();
        var aggr_speedmax_mean =  arr_speed_maxs.mean();
        var aggr_speedmax_std =  arr_speed_maxs.std();
        var aggr_speedviol_mean = arr_speedviol.mean();
        var aggr_speedviol_std = arr_speedviol.std();
        
        // means/stds for length, duration
        var aggr_duration_mean = arr_durations.mean(); 
        var aggr_duration_std = arr_durations.std(); 
        var aggr_length_mean = arr_lengths.mean();
        var aggr_length_std = arr_lengths.std();
        
        // most used street type and surrounding of trip
        var aggr_fav_highway = mode(arr_highways);
        var aggr_fav_location = mode(arr_locations);

        // time of the aggregation
        var aggr_time = new Date();
        
        // prepare the object for db operation
        var aggregation = {
            count: tripcount,
            time: aggr_time,
            
            accxpos_mean: aggr_accxpos_mean,
            accxpos_std: aggr_accxpos_std,
            accxneg_mean: aggr_accxneg_mean,
            accxneg_std: aggr_accxneg_std,
            accypos_mean: aggr_accypos_mean,
            accypos_std: aggr_accypos_std,
            accyneg_mean: aggr_accyneg_mean,
            accyneg_std: aggr_accyneg_std,
            
            accxposmax_mean: aggr_accxposmax_mean,
            accxposmax_std: aggr_accxposmax_std,
            accxnegmin_mean: aggr_accxnegmin_mean,
            accxnegmin_std: aggr_accxnegmin_std,
            accyposmax_mean: aggr_accyposmax_mean,
            accyposmax_std: aggr_accyposmax_std,
            accynegmin_mean: aggr_accynegmin_mean,
            accynegmin_std: aggr_accynegmin_std,
            
            speed_mean: aggr_speed_mean,
            speed_std: aggr_speed_std,
            speedmax_mean: aggr_speedmax_mean,
            speedmax_std: aggr_speedmax_std,
            speedviol_mean: aggr_speedviol_mean,
            speedviol_std: aggr_speedviol_std,
            
            duration_mean: aggr_duration_mean,
            duration_std: aggr_duration_std,
            length_mean: aggr_length_mean,
            length_std: aggr_length_std,
            fav_highway: aggr_fav_highway,
            fav_location: aggr_fav_location    
        };
        db.aggregations.insert(aggregation, function(err, doc) {
            res.json(doc);
        });
    });
});

// route: /api/aggregation, method: GET
// return all aggregationns in database
app.get('/api/aggregation', function (req, res) {
  console.log('I received a GET request on route /api/aggregation');
  db.aggregations.find(function (err, docs) {
    //console.log(docs);
    res.json(docs);
  });
});

// route /api/aggregation/id, method GET
// return single aggregation by id
app.get('/api/aggregation/:id', function (req, res) {
  var id = req.params.id;
  console.log('I received a GET request on route /api/aggregation/' + id);
  db.aggregations.findOne({_id: mongojs.ObjectId(id)}, function (err, doc) {
    res.json(doc);
  });
});

// route /api/aggregation/id, method DELETE
// delete a single aggregation in the collection (by id)
app.delete('/api/aggregation/:id', function (req, res) {
  var id = req.params.id;
  console.log('I received a DELETE request on route /api/aggregation/' + id);
  db.aggregations.remove({_id: mongojs.ObjectId(id)},{justOne: true}, function (err, doc) {
    res.json('The aggregation ' + id + ' has been deleted!');
  });
});


// start server on port 3000
app.listen(3000);
console.log("Server running on port 3000");