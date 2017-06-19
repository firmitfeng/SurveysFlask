# -*- coding: utf-8 -*-  

from wtforms import widgets, SelectMultipleField, RadioField

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class LabelRadioField(RadioField):
    pass
