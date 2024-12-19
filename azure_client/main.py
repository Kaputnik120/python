from azure.eventhub import EventHubProducerClient, EventData

__EVENT_HUB_CONNECTION_STRING__ = 'Endpoint=sb://renkeventns.servicebus.windows.net/;SharedAccessKeyName=renkrddssend' \
                                  ';SharedAccessKey=+4imgBPyZQbnK286ECE/w19bd+2Nac0P2QiWcjLSjwY=;EntityPath=renkrdds '

__EVENT_HUB_NAME = 'renkrdds'


def main():
    print('Creating client')
    client = EventHubProducerClient.from_connection_string(__EVENT_HUB_CONNECTION_STRING__,
                                                           eventhub_name=__EVENT_HUB_NAME)

    print('Creating batch')
    event_data_batch = client.create_batch()
    can_add = True
    while can_add:
        try:
            print('Adding batch data')
            event_data_batch.add(EventData('Some RDDS Data'))
        except ValueError as ve:
            print('Finished adding batch data:')
            print(ve)
            can_add = False  # EventDataBatch object reaches max_size.

    with client:
        print('Sending batch')
        client.send_batch(event_data_batch)
        print('Batch sent')


if __name__ == '__main__':
    main()
