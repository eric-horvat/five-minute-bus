from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from datetime import datetime
import requests
import config  # local settings file
from xml.etree import ElementTree as ET
from BeautifulSoup import BeautifulSoup as Soup


def get_time():
    from dateutil.tz import tzoffset
    from datetime import datetime
    now = datetime.now()
    return now.strftime("%Y-%m-%dT%H:%M:%S")


def request_rood_node():
    ''' Every request uses the same root node.
        May as well make it available for all '''
    root = Element('Siri')
    root.set('xmlns', 'http://www.siri.org.uk/siri')
    root.set('version', '2.0')
    root.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

    service_request = SubElement(root, 'ServiceRequest')

    timestamp = SubElement(service_request, 'RequestTimestamp')
    timestamp.text = get_time()

    requestor_ref = SubElement(service_request, 'RequestorRef')
    requestor_ref.text = config.NXTBUS_API
    return root, service_request


def stop_monitoring_request(bus_stop_id):
    from xml.etree.ElementTree import Element, SubElement, Comment, tostring 
    root, service_request = request_rood_node()

    stop_monitoring_request = SubElement(service_request, 'StopMonitoringRequest')
    stop_monitoring_request.set('version', '2.0')
    
    request_timestamp = SubElement(stop_monitoring_request, 'RequestTimestamp')
    request_timestamp.text = get_time()
    #preview_interval = SubElement(stop_monitoring_request, 'PreviewInterval')
    #preview_interval.text = 'PT30M'
    monitoring_ref = SubElement(stop_monitoring_request, 'MonitoringRef')
    monitoring_ref.text = str(bus_stop_id)
    return root

def tree_to_string(tree):
    return ET.tostring(tree, 'utf-8')

def assert_valid_response(response):
    status = response.find('servicedelivery').find('status').string
    assert(status == 'true')


def bus_arrival_times(bus_stop_id):
    response = None
    try:
        api_key = config.NXTBUS_API
        url = 'http://siri.nxtbus.act.gov.au:11000/{0}/sm/service.xml'.format(api_key)
        response = requests.get(url, data=tree_to_string(stop_monitoring_request(str(bus_stop_id))))
    except Exception as e:
        raise e
    response = Soup(response.content)
    assert_valid_response(response)
    stopmonitoringdelivery = response.find('servicedelivery')
    stopmonitoringdelivery = stopmonitoringdelivery.find('stopmonitoringdelivery')
    if stopmonitoringdelivery is None:
        return
    else:
        bus_arrival_times = {}
        for stopvisit in stopmonitoringdelivery.findAll('monitoredstopvisit'):
            vehiclejourney = stopvisit.find('monitoredvehiclejourney')
            busname = vehiclejourney.find('publishedlinename').string
            expected_departure_time = vehiclejourney.find('monitoredcall').find('expecteddeparturetime')
            if expected_departure_time:  # if the expected departure time is given
                expected_departure_time = expected_departure_time.string.split('+')[0]
                expected_departure_time = datetime.strptime(expected_departure_time, '%Y-%m-%dT%H:%M:%S')
                if busname in bus_arrival_times:
                    bus_arrival_times[busname].append(expected_departure_time)
                else:
                    bus_arrival_times[busname] = [expected_departure_time]
        return bus_arrival_times
