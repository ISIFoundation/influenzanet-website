# -*- coding: utf-8 -*-

from django.forms import Form, CharField, EmailField, ValidationError,TextInput, Textarea
from random import randint, choice

def create_captcha_value():
    v1 = randint(0, 9)
    v2 = randint(0, 9)
    op = choice(('+','-', '*'))
    value = {
     '+': lambda a,b: a+b,
     '-': lambda a,b: a-b,
     '*': lambda a,b: a*b
    }[op](v1,v2)
    label = '%d %s %d' % (v1,op,v2)
    #print '%s = %d' % (label, value)
    return (label, value)

class CaptchaField(CharField):

    def __init__(self):
        self.to_check = None
        CharField.__init__(self, required=True, widget=TextInput(attrs={'size':'3'}))

    def newValue(self):
        cc = create_captcha_value()
        self.label = cc[0]
        return cc[1]
    def setValue(self, value):
        self.to_check = int(value)

    def validate(self, value):
        CharField.validate(self, value)
        try:
            value = int(value)
        except:
            value = -1
        if(self.to_check is not None):
            print '%s vs %s' % (self.to_check, value)
            if self.to_check != value:
                raise ValidationError("Invalid captcha value")

class TellAFriendForm(Form):
    email = EmailField(required=True, help_text="Ce couriel ne sera pas conservé")
    subject = CharField(initial="Un ami vous conseille GrippeNet.fr", required=True, widget=TextInput(attrs={'size':'30'}))
    captcha = CaptchaField()

    def updateCaptcha(self):
        return self.fields['captcha'].newValue()

    def initCaptcha(self, value):
        self.fields['captcha'].setValue(value)
