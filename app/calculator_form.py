from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField
from wtforms.validators import DataRequired, ValidationError, Optional
from datetime import datetime

# validation for form inputs
class Calculator_Form(FlaskForm):
    # this variable name needs to match with the input attribute name in the html file
    # you are NOT ALLOWED to change the field type, however, you can add more built-in validators and custom messages
    BatteryPackCapacity = StringField("Battery Pack Capacity", [DataRequired()])
    InitialCharge = StringField("Initial Charge", [DataRequired()])
    FinalCharge = StringField("Final Charge", [DataRequired()])
    StartDate = DateField("Start Date", [DataRequired("Data is missing or format is incorrect")], format='%d/%m/%Y')
    StartTime = TimeField("Start Time", [DataRequired("Data is missing or format is incorrect")], format='%H:%M')
    ChargerConfiguration = StringField("Charger Configuration", [DataRequired()])
    PostCode = StringField("Post Code", [DataRequired()])

    # use validate_ + field_name to activate the flask-wtforms built-in validator
    # this is an example for you
    def validate_BatteryPackCapacity(self, field):
        if field.data is None:
            raise ValidationError('Field data is none')
        elif field.data == '':
            raise ValueError("cannot fetch data")
        elif not self.isfloat(field.data):
            raise ValueError("Battery pack capacity must be a number")
        elif float(field.data) < 0.65 or float(field.data) > 100:
            raise ValueError("Battery pack capacity must be a number between 0.65 and 100.00")

    # validate initial charge here
    def validate_InitialCharge(self, field):
        # another example of how to compare initial charge with final charge
        # you may modify this part of the code
        if field.data is None:
            raise ValidationError('Field data is none')
        elif field.data == '':
            raise ValueError("cannot fetch data")
        elif not self.isfloat(field.data):
            raise ValueError("Initial charge must be a number")
        elif float(field.data) < 0 or float(field.data) > 100:
            raise ValueError("Initial charge must be a number between 0 and 100")
        elif float(field.data) > float(self.FinalCharge.data):
            raise ValueError("Initial charge cannot be more than final charge")

    # validate final charge here
    def validate_FinalCharge(self, field):
        if field.data is None:
            raise ValidationError('Field data is none')
        elif field.data == '':
            raise ValueError("cannot fetch data")
        elif not self.isfloat(field.data):
            raise ValueError("Final charge must be a number")
        elif float(field.data) < 0 or float(field.data) > 100:
            raise ValueError("Final charge must be a number between initial charge and 100")
        elif float(field.data) < float(self.InitialCharge.data):
            raise ValueError("Final charge cannot be less than initial charge")

    # validate start date here
    def validate_StartDate(self, field):
        year = str(field.data)[0:4]
        month = str(field.data)[5:7]
        day = str(field.data)[8:10]

        date_str = day + '-' + month + '-' + year
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')

        valid_date_str = '01-07-2008'
        valid_date_obj = datetime.strptime(valid_date_str, '%d-%m-%Y')

        if field.data is None:
            raise ValidationError('Field data is none')
        elif field.data == '':
            raise ValueError("cannot fetch data")
        elif date_obj < valid_date_obj:
            raise ValueError("Start date can only be after 1st July 2008")

    # validate start time here
    def validate_StartTime(self, field):
        if field.data is None:
            raise ValidationError('Field data is none')
        elif field.data == '':
            raise ValueError("cannot fetch data")

    # validate charger configuration here
    def validate_ChargerConfiguration(self, field):
        if field.data is None:
            raise ValidationError('Field data is none')
        elif field.data == '':
            raise ValueError("cannot fetch data")
        elif not field.data.isdigit():
            raise ValueError("Charger configuration must be an integer between 1 and 8")
        elif int(field.data) < 1 or int(field.data) > 9:
            raise ValueError("Charger configuration must be an integer between 1 and 8")

    # validate postcode here
    def validate_PostCode(self, field):
        if field.data is None:
            raise ValidationError('Field data is none')
        elif field.data == '':
            raise ValueError("cannot fetch data")
        elif not field.data.isdigit():
            raise ValueError("Postcode must be an integer between 200 and 9729")
        elif int(field.data) < 200 or int(field.data) > 9729:
            raise ValueError("Postcode must be an integer between 200 and 9729")

    # helper function to check if a value is a float
    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False
