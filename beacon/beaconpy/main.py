# -*- coding: utf-8 -*-

import os, time
import config, data, poller, reporter, helpers

def main():
  """
  Main method of the beacon.
  """
  
  os.system('clear') # clear terminal screen
  try:
    
    # run calibration on startup
    #if config.calibrate_acc == True:
      #import calibration.accelerometer
      
      
      
    # init dispatching thread_acc
    thread_repdispatcher = reporter.ReportDispatcher(data.trip_dict, data.report_queue)
    # init + start poller threads
    thread_gps = poller.GpsPoller(config.tick_gpspoller, data.gps_dict) 
    thread_acc = poller.AccPoller(config.tick_gpspoller, data.acc_dict, config.acc_power_mgmt_1, config.acc_power_mgmt_2, config.acc_bus, config.acc_address, config.acc_addr_x, config.acc_addr_y, config.acc_addr_z, 0, 0, 0) 
    thread_gps.start() 
    thread_acc.start() 
    print 'Starte Sensoren ... Bitte warten.'
    
    # give threads some time to start up and pull first data (GPS in cold start can take up to 5secs)
    time.sleep(5) 
    
    # check if internet is avaible on the device
    if helpers.haveInternet():
      print '\nInternetverbindung ist AKTIV\n'
    else:
      print '\nInternetverbindung ist NICHT aktiv\n'
    
    # init + start reporting threads
    thread_repbuilder = reporter.ReportBuilder(config.tick_repbuilder, data.report_dict, data.gps_dict, data.acc_dict)
    thread_repbuilder.start()
    
    while True:
      # debug -- visualize most current data
      if config.output_console == True:
        os.system('clear') # clear terminal screen
        print
        print ' Zeit aktuell (UTC)            ' , helpers.ToIso(helpers.UtcNow())
        print '----------------------------------------------------------------'
        print
        print ' GPS Daten (NL-302U)'
        print '----------------------------------------------------------------'
        print '   Zeit letzter Fix (UTC)      ' , data.gps_dict['fixtime']
        print '   geogr. Breite (DDD)         ' , data.gps_dict['latitude']
        print '   geogr. Laenge (DDD)         ' , data.gps_dict['longitude']
        print '   Hoehe (m)                   ' , data.gps_dict['altitude']
        print '   Geschwindigkeit (m/s)       ' , data.gps_dict['speed']
        print '   Modus                       ' , data.gps_dict['mode']
        print '   Anzahl Satelliten           ' , data.gps_dict['satellites']
        print
        print ' Accelerometer Daten (MPU-6050)'
        print '----------------------------------------------------------------'
        print '   Beschl. X-Achse (m/s^2)     ' , data.acc_dict['axis_x']
        print '   Beschl. Y-Achse (m/s^2)     ' , data.acc_dict['axis_y']
        print '   Beschl. Z-Achse (m/s^2)     ' , data.acc_dict['axis_z']
        print 
        print '----------------------------------------------------------------'
        print ' Letzter Report:               ' , data.report_dict['time']
        print ' Reports in Warteschlange:     ' , data.report_queue.qsize()
        print         
      
      time.sleep(config.tick_visualization) 

  # kill threads with ctrl+c
  except (KeyboardInterrupt, SystemExit): 
    print "\nThreads werden beendet..."
    
    thread_gps.running = False
    thread_gps.join() 
    print "GpsPoller beendet!"
    
    thread_acc.running = False
    thread_acc.join() 
    print "AccPoller beendet!"
    
    thread_repbuilder.running = False
    thread_repbuilder.join() 
    print "ReportBuilder beendet!"
    print "\nErzeuge Bericht der Fahrt...!"
    
    # start dispatching thread
    thread_repdispatcher.start()
    thread_repdispatcher.join()
    print "Fahrtbericht erzeugt!"
    
  #except:
  #  print 'Etwas schreckliches ist passiert!'
    
  print "\nProgramm beendet."
        
if __name__ == '__main__':
  main()