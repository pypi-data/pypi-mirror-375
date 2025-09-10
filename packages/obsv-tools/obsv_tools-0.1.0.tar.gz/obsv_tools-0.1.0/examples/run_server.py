import time

import obsv_tools.metrics.instrumentator


class Worker:
    def __init__(self):
        self.active = True

        self.instrumentator = obsv_tools.metrics.instrumentator.Instrumentator(
            server_port=8000,
            meter_name='my_app_metrics',
        )

        self.instrumentator.add_counter(
            name='my_counter',
            description='A simple counter',
        ).add_histogram(
            name='my_histogram',
            description='A simple histogram',
        )
    
    def run(
        self,
    ):
        while self.active:
            self.instrumentator.increment_counter(
                name='my_counter',
                attributes={'key': 'value'},
                amount=1,
            )
            self.instrumentator.record_histogram(
                name='my_histogram',
                attributes={'key': 'value'},
                amount=5.5,
            )

            print('Published metrics. Sleeping for 2 seconds...')
            time.sleep(2)
    
    def stop(
        self,
    ):
        self.active = False


def main():
    worker = Worker()

    try:
        worker.run()
    except KeyboardInterrupt:
        worker.stop()
        print('Shutting down...')


if __name__ == '__main__':
    main()