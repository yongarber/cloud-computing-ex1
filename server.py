from flask import Flask, request
from datetime import datetime
import time

app = Flask(__name__)

plate = []
parkingLot = []
entry_timestamp = []
ticket_id = []
fmt = '%Y-%m-%d %H:%M:%S'

def cost(entry_timestamp): 
    d_now = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fmt)
    d_db = datetime.strptime(entry_timestamp.strftime("%Y-%m-%d %H:%M:%S"), fmt)

    # Convert to Unix timestamp
    d1_ts = time.mktime(d_now.timetuple())
    d2_ts = time.mktime(d_db.timetuple())

    # They are now in seconds, subtract and then divide by 60 to get minutes.
    minutes_in_parkingLot= int(d1_ts-d2_ts) / 60
    
    cost= (minutes_in_parkingLot // 15)*2.5
    return(minutes_in_parkingLot, cost)


@app.route('/entry', methods=['POST'])
def new_ticket():
    # if key doesn't exist, returns None
    plate_val = request.args.get('plate')
    parkingLot_val = request.args.get('parkingLot')

    now_timestamp = datetime.strptime(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), fmt)
    
    plate.append(plate_val)
    parkingLot.append(parkingLot_val)
    entry_timestamp.append(now_timestamp)
    ticket_id_val = len(plate)
    ticket_id.append(ticket_id_val)
        
    return '''
            The ticketId value is: {}'''.format(ticket_id_val)


@app.route('/exit', methods=['POST'])
def exit_ticket():
    ticketId = int(request.args.get('ticketId')) - 1
    plate_val_return = plate[ticketId]
    parkingLot_val_return = parkingLot[ticketId]
    entry_timestamp_val_return = entry_timestamp[ticketId]
    total_time_return,cost_val_return = cost(entry_timestamp_val_return)

    return '''
            The plate number value is: {}
            The parking lot id is: {}
            The total parked time in minutes is: {}
            The cost is: {}'''.format(plate_val_return, parkingLot_val_return, total_time_return, cost_val_return)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443)
    
