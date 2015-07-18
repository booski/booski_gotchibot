import time
import traceback

class Gotchi:
    def __init__(self):
        self.alive = True
        self.birth = int(time.time())
        self.complaints = ''
        self.attributes = dict(food = Attribute(2000, 0, 4000, True, True),
                               drink = Attribute(1000, 0, 6000, True, True),
                               attention = Attribute(750, 0, 750, False, False)
                               )


    def _react(self, message):
        parts = message.split(None, 1)
        
        if parts[0].startswith('_'):
            return "What??"

        try:
            if len(parts) > 1:
                args = parts[1].split()
                return getattr(self, parts[0])(args)
            else:
                return getattr(self, parts[0])()
            
        except AttributeError:
            print(traceback.format_exc())
            return "What?"


    def _tick(self):
        result = []
        for attr_id in self.attributes:
            attribute = self.attributes[attr_id]
            attribute._tick()
            
            status = attribute.status()
            output = ''
            if status == 'critlow':
                if attribute.lethal == True:
                    end = self._die()
                    output = "I've died from lack of {}. {}".format(attr_id, end)
                else:
                    output = "I'm completely starved for {}.".format(attr_id)
            
            elif status == 'low':
                output = "I want more {}.".format(attr_id)
            elif status == 'high':
                output = "You've given me too much {}.".format(attr_id)
            elif status == 'crithigh':
                if attribute.lethal == True:
                    end = self._die()
                    output = "I've died from too much {}. {}".format(attr_id, end)
                else:
                    output = "You've given me way too much {}.".format(attr_id)

            result.append(output)

        result = ' '.join(result)
        if result != self.complaints:
            self.complaints = result
            return result
        else:
            return None
        

    def _isalive(self):
        return self.alive


    def _increase_attr(self, attr_id, addition):
        self.attributes[attr_id].add(addition)

    
    def _reset_complaints(self):
        self.complaints = ''
        

    def _die(self):
        self.alive = False

        now = int(time.time())
        lifetime = now - self.birth
        seconds = lifetime % 60
        minutes = int(lifetime / 60) % 60
        hours = int(lifetime / 60 / 60) % 24
        days = int(lifetime / 60 / 60 / 24)
        
        return "I lived for {} days, {} hours, {} minutes and {} seconds.".format(days, hours, minutes, seconds)


    def feed(self):
        if self.attributes['attention'].status() == 'critlow':
            return "I'm too sad to eat."
        else:
            self._increase_attr('food', 800)
            return "Yum!"


    def water(self):
        self._increase_attr('drink', 400)
        return "Gulp!"


    def cuddle(self):
        current = self.attributes['attention']
        increment = 200
        if current.value + increment > current.max:
            increment = current.max - current.value

        self._increase_attr('attention', increment)
        return "Purr..."


    def kill(self):
        end = self._die()
        return "Why would you do that?? X.X {}".format(end)


class Attribute:
    def __init__(self, start, low, high, essential, warnhigh):
        if low > high or start < low or start > high:
            raise ValueError("The supplied values for 'start', 'low' or 'high' are not consistent")

        for i in [essential, warnhigh]:
            if type(i) is not bool:
                raise TypeError("The type of 'essential' and 'warnhigh' must be boolean")
            
        self.value = start
        self.min = low
        self.max = high
        self.warning = (self.max - self.min)/8
        self.lethal = essential
        self.warnhigh = warnhigh
        

    def _tick(self):
        if self.value > -500:
            self.value -= 1


    def add(self, addition):
        self.value += addition


    def status(self):
        if self.min > self.value:
            return 'critlow'
        elif  self.max < self.value:
            return 'crithigh'
        elif self.min + self.warning > self.value:
            return 'low'
        elif self.warnhigh and self.max - self.warning < self.value:
            return 'high'
        else:
            return 'ok'


