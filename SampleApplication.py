import AbstractApplication as Base
from time import sleep


class SampleApplication(Base.AbstractApplication):
    def __init__(self):
        super(SampleApplication, self).__init__(serverIP='192.168.0.105')

    def main(self):
        self.setLanguage('nl-NL')
        sleep(1)  # wait for the language to change
        self.sayAnimated('Hello, world!')
        sleep(3)  # wait for the robot to be done speaking (to see the relevant prints)
        self.doGesture('Enthusiastic_5')
        sleep(3)
        self.say('Volgende')
        self.doGesture('animations/Sit/BodyTalk/BodyTalk_1')
        sleep(3)

    def onRobotEvent(self, event):
        print(event)


# Run the application
sample = SampleApplication()
sample.main()
sample.stop()
