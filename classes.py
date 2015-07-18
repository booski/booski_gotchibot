import time
import traceback

class Gotchi:
    def __init__(self):
        self.birth = int(time.time())
        self.lastcontact = self.birth

        self.alive = True
        self.awake = True
        self.complaints = ''
        self.active_attrs = dict(food = Attribute(2000, 0, 6000, True, True),
                                 drink = Attribute(1000, 0, 4000, True, True),
                                 attention = Attribute(3500, 0, 3500, False, False))
        self.sleep = Attribute(3000, 0, 3000, True, False)
        

    def _react(self, message):
        wokeup = self._wake()
        self.lastcontact = int(time.time())

        parts = message.split(None, 1)
        
        if parts[0].startswith('_'):
            return "What??"

        result = ''
        try:
            if len(parts) > 1:
                args = parts[1].split()
                result = getattr(self, parts[0])(args)
            else:
                result = getattr(self, parts[0])()
            
        except AttributeError:
            print(traceback.format_exc())
            result = "What?"
        
        return "{} {}".format(wokeup, result).strip()


    def _tick(self):
        result = []
        for attr_id in self.active_attrs:
            attribute = self.active_attrs[attr_id]
            attribute._tick()
        
            status = attribute.status()
            output = ''
            if status == 'critlow':
                if attribute.lethal == True:
                    output = "I've died from lack of {}. {}".format(attr_id, self._die())
                else:
                    output = "I'm completely starved for {}.".format(attr_id)
            
            elif status == 'low':
                output = "I want more {}.".format(attr_id)
            elif status == 'high':
                output = "You've given me too much {}.".format(attr_id)
            elif status == 'crithigh':
                if attribute.lethal == True:
                    output = "I've died from too much {}. {}".format(attr_id, self._die())
                else:
                    output = "You've given me way too much {}.".format(attr_id)

            result.append(output)

        result = ' '.join(result).strip()
        if result != '':
            if result != self.complaints:
                self.complaints = result
                return "{} {}".format(self._wake(), result).strip()

        else:
            if self.awake:
                self.sleep._tick()
                
                if self.sleep.status() == 'critlow':
                    return "I've died from lack of sleep. {}".format(self._die())
                
                elif self.sleep.status() == 'low':
                    if int(time.time()) - self.lastcontact > 120:
                        return self._sleep()
                    else:
                        result = "I'm tired"
                        if self.complaints != result:
                            self.complaints = result
                            return result

            else:
                self.sleep.add(1)

                if self.sleep.ismaxed():
                    return self._wake()

        return ''


    def _wake(self):
        if not self.awake:
            self.awake = True
            return "I've woken up."

        else:
            return ''


    def _sleep(self):
        if self.awake:
            self.awake = False
            return "I'm falling asleep."
        
        else:
            return ''


    def _isalive(self):
        return self.alive


    def _increase_attr(self, attr_id, addition):
        self.active_attrs[attr_id].add(addition)

    
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
        if self.active_attrs['attention'].status() == 'critlow':
            return "I'm too sad to eat."
        else:
            self._increase_attr('food', 800)
            return "Yum!"


    def water(self):
        self._increase_attr('drink', 400)
        return "Gulp!"


    def cuddle(self):
        current = self.active_attrs['attention']
        increment = 1000
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


    def ismaxed(self):
        if self.value >= self.max:
            return True
        else:
            return False


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


