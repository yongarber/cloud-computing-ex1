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
        
    # TODO- insert plate, parkingLot, and current_timestamp into DB with a new unique ID which will be returned as the TicketID.
    return '''
            <h1>The ticketId value is: {}</h1>'''.format(ticket_id_val)


@app.route('/exit', methods=['POST'])
def exit_ticket():
    ticketId = int(request.args.get('ticketId')) - 1
    #testing cost function
    plate_val_return = plate[ticketId]
    parkingLot_val_return = parkingLot[ticketId]
    entry_timestamp_val_return = entry_timestamp[ticketId]
    total_time_return,cost_val_return = cost(entry_timestamp_val_return)

    # TODO- insert plate and parkingLot into DB with a new unique ID which will be returned as the ticketId.
    return '''
            <h1>The plate number value is: {}</h1>
            <h1>The parking lot id is: {}</h1>
            <h1>The total parked time in minutes is: {}</h1>
            <h1>The cost is: {}</h1>'''.format(plate_val_return, parkingLot_val_return, total_time_return, cost_val_return)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443)
    