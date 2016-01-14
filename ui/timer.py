from time import time


class Timer:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.difference = None

    def start(self):
        self.start_time = time()
        return self.start_time

    def end(self):
        self.end_time = time()
        self.difference = self.end_time - self.start_time
        return self.end_time

    def get_time_taken(self):
        if not self.difference:
            raise Exception('timer not initialized')
        return self.difference

    @staticmethod
    def _convert_to_text(value, name, plural_name=''):
        if len(plural_name) == 0:
            plural_name = '{}s'.format(name)

        if value > 1:
            return '{} {}'.format(value, plural_name)
        elif value == 1:
            return 'one {}'.format(name)

    def get_time_taken_pretty(self):
        time_taken = self.get_time_taken()

        hours, rest = divmod(time_taken, 3600)
        minutes, seconds = divmod(rest, 60)
        parts = [
            Timer._convert_to_text(hours, 'hour'),
            Timer._convert_to_text(minutes, 'minute'),
            Timer._convert_to_text(seconds, 'second')
        ]

        return ' '.join(parts)
