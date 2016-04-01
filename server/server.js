// server.js 
// author: 			Daniel Grewe
// last change: 	17.03.2016 - 06:34


var express = require('express');
var app = express();
var mongojs = require('mongojs');
var db = mongojs('gps-iot', ['raw']);
var bodyParser = require('body-parser');

app.use(express.static(__dirname + '/public'));
app.use(bodyParser.json());

app.get('/gpsdata', function (req, res) {
  console.log('I received a GET request');

  db.raw.find(function (err, docs) {
    console.log(docs);
    res.json(docs);
  });
});

app.post('/gpsdata', function (req, res) {
  console.log(req.body);
  db.raw.insert(req.body, function(err, doc) {
    res.json(doc);
  });
});

app.delete('/gpsdata/:id', function (req, res) {
  var id = req.params.id;
  console.log(id);
  db.raw.remove({_id: mongojs.ObjectId(id)}, function (err, doc) {
    res.json(doc);
  });
});

app.get('/gpsdata/:id', function (req, res) {
  var id = req.params.id;
  console.log(id);
  db.raw.findOne({_id: mongojs.ObjectId(id)}, function (err, doc) {
    res.json(doc);
  });
});

app.put('/gpsdata/:id', function (req, res) {
  var id = req.params.id;
  console.log(req.body.name);
  db.raw.findAndModify({
    query: {_id: mongojs.ObjectId(id)},
    update: {$set: {name: req.body.name, email: req.body.email, number: req.body.number}},
    new: true}, function (err, doc) {
      res.json(doc);
    }
  );
});

app.listen(3000);
console.log("Server running on port 3000");