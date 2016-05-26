# Prototypical Development of a System for the Analysis of Driving Behaviour for Motor Vehicles
## The server - analysing sensor data

### Getting started
You need a mongoDB-database with the collections `trips` and `aggregations`.
Next insert the given test-data (`../probefahrten`) via HTTP-POST to `/api/beacon`.

Start the application: `node server.js`
The server will listen on port 3000.