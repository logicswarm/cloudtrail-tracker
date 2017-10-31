import boto3
import os, time
from to_dynamo import UseDynamoDB
from my_parser import Event
import Querys
import numpy as np

def chunks(l, porc=0.1):
    """Yield successive n-sized chunks from l."""

    percent = max(1,int(len(l) * porc))
    for i in range(0, len(l)+1, percent):
        if i + percent+1 >= len(l):
            yield l[i : ]
            return;
        else:
            yield l[i : i + percent]
        #last = i

def get_structure(path):
    res = []
    for (path,i,j) in os.walk(path):
        # print(path)
        # print(j)
        if len(j) > 0:
            aux = ["{0}\{1}".format(path,x) for x in j]
            res.extend(aux)
    return res


"""6 querys call"""
def querys(times_chunk):


    start_time = time.time()
    user_events = Querys.user_count_event('gmolto', 'DescribeMetricFilters', '2017-06-01T12:00:51Z', '2017-06-01T19:00:51Z')
    elapsed_time = time.time() - start_time
    print(user_events)
    print("      ---- > Time elapsed for user_count_event items %f " % elapsed_time)
    times_chunk[2] = (elapsed_time)

    start_time = time.time()
    user_events = Querys.used_services('alucloud171', '2017-06-01T12:00:51Z', '2017-06-01T19:00:51Z')
    elapsed_time = time.time() - start_time
    print(user_events)
    print("      ---- > Time elapsed for used_services items %f " % elapsed_time)
    times_chunk[3] = (elapsed_time)

    start_time = time.time()
    user_events = Querys.users_list()
    elapsed_time = time.time() - start_time
    print(user_events)
    print("      ---- > Time elapsed for users_list items %f " % elapsed_time)
    times_chunk[4] = (elapsed_time)

    start_time = time.time()
    user_events = Querys.top_users('2017-06-01T12:00:51Z', '2017-06-01T19:00:51Z')
    elapsed_time = time.time() - start_time
    print(user_events)
    print("      ---- > Time elapsed for top_users items %f " % elapsed_time)
    times_chunk[5] = (elapsed_time)


    start_time = time.time()
    user_events = Querys.actions_between_time('2016-06-01T12:00:51Z', '2018-06-01T19:00:51Z')
    elapsed_time = time.time() - start_time
    print(user_events)
    print("      ---- > Time elapsed for  actions_between_time (all events) %f " % elapsed_time)
    times_chunk[6] = (elapsed_time)

    start_time = time.time()
    user_events = Querys.actions_between_time('2016-06-01T12:00:51Z', '2018-06-01T19:00:51Z', event='DescribeInstanceStatus')
    elapsed_time = time.time() - start_time
    print(user_events)
    print("      ---- > Time elapsed for  actions_between_time (one event) %f " % elapsed_time)
    times_chunk[7] = (elapsed_time)

def save_array(data, path):

    with open(path, 'a') as outfile:
        outfile.write('#\n')
        for data_slice in data:
            [outfile.write(str(x)+" ") for x in data_slice]
            outfile.write('\n')

""" Save events from a dir ans calculate times"""
def analysis_events(path, table_name = 'EventoCloudTrail_230'):
    #Get all events from path
    events = get_structure(path)
    #split in equal parts (except last)

    #matrix for saves times
    save_times = []
    number_events = 0
    for l in chunks(events, 0.1):
        time_chunk = [None]*9
        #All times for chunck,
        #[NUMBER_EVENTS, T_Upload, user_events, user_events_service, user_list, top_users, act_between,times,
        #act_between_times_events, ALL]
        print("Uploading %d files " % len(l))
        start_time = time.time()

        for e in l: #e = events file

            event = Event(e)
            number_events = number_events + event.count_events()
            db = UseDynamoDB("prueba", verbose=False)
            db.guardar_evento(table_name, event)
        elapsed_time_upload = time.time() - start_time
        time_chunk[0] = number_events
        time_chunk[1] = elapsed_time_upload
        print("Time elapsed for upload %d events: %f " % (number_events, elapsed_time_upload))
        print(" - Calculating time for querys.. ")

        dinosaurs_time = time.time()
        try:
            querys(time_chunk)
        except Exception:
            print("Too many time, more read capacity is required!")
        elapsed_time_dinosaurs = time.time() - dinosaurs_time
        print("Time elapsed for all querys (%d number of items): %f " % (number_events, elapsed_time_dinosaurs))

        print(" -  Querys finished.. ")
        time_chunk[8] = (elapsed_time_dinosaurs)
        save_times.append(time_chunk)

    print("Saving array of times...")
    save_array(save_times, 'times/times')

def main():
    path = 'examples'
    analysis_events(path)
    # a = [[1, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0], [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8, 9], [9, 8, 7, 6, 5, 4, 3, 2, 1]]
    # save_array(a,'times/times')


if (__name__ == '__main__'):
    main()