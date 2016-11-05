from django.forms import MultiWidget

from poll.fields import CustomInlineRadioSelect


class ScaleWidget(MultiWidget):
    def __init__(self, attrs=None):
        choices = [(i, i) for i in xrange(1, 6)]
        _widgets = [CustomInlineRadioSelect(attrs={"choice": [attrs["choices"][index]]}, choices=choices) for index in
                    xrange(len(attrs["choices"]))]
        self.widgets_len = len(_widgets)
        super(ScaleWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        return value.split(', ') if value else [None for i in xrange(self.widgets_len)]
