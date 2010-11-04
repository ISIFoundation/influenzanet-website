# 'Gold Standard' Questionnaires (Deliverable of Task 2) KULeuven
# 1) New user registration: intake questions

class IntakeQ1(d.Question):
  question = 'What is your gender?'
  type = 'options-single'
  options = ((0, 'Male'),
             (1, 'Female'), )
  
class IntakeQ2(d.Question):
  question = 'What is your birth month and birth year?'
  type = 'month-year'

class IntakeQ3(d.Question):
  question = 'What is your home postal code?'
  type = 'postcode'

class IntakeQ4(d.Question):
  question = 'What is your school/workplace postal code?'
  type = 'postcode'

class IntakeQ5(d.Question):
  question = """In your daily life, do you come into frequent contact with any 
  of the following? (Tick all that apply)"""
  type = 'options-multiple'
  options = ((0, 'Groups of children or teenagers'),
             (1, 'Groups of the elderly (>65 years of age)'),
             (2, 'Patients'),
             (3, """Crowds of people (more than 10 individuals on one and the
             same occasion)"""), )

class IntakeQ6(d.Question):
  question = """Not counting you, how many people in each of the following age
  groups live in your household?"""
  type = 'multiple-number'
  categories = ((0, '0-4 years'),
                (1, '5-18 years'),
                (2, '19-44 years'),
                (3, '45-64 years'),
                (4, '65+ years'), )

class IntakeQ6b(d.Question):
  question = """How many of ther children aged 0-4 in your household go to
  school or day-care?"""
  type = 'options-single'
  options = ((1, '1'),
             (2, '2'),
             (3, '3'),
             (4, '4'),
             (5, '5'),
             (99, 'more than 5'), )
  
class IntakeQ7(d.Question):
  question = 'What is your daily main means of transportation?'
  type = 'options-single'
  options = ((0, 'Walking'),
             (1, 'Bike'),
             (2, 'Motorbike/scooter'),
             # wording '(including taxi)' added to question following telco
             # 26-10-2010.
             (3, 'Car (including taxi)'),
             (4, 'Public transportation (Bus, train, ...'),
             (5, 'Other'), )

class IntakeQ7b(d.Question):
  question = """On a normal day, how much time do you spend on public transport
  (bus, train, underground)?"""
  type = 'options-single'
  options = ((0, 'No time at all'),
             (1, '0-30 minutes'),
             (2, '30 minutes - 1,5 hours'),
             (4, '1,5 hours - 4 hours'),
             (5, '>4 hours'), )

class IntakeQ8(d.Question):
  question = 'Were you vaccinated against swine flu last winter?'
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             (2, "I don't know"), )

class IntakeQ8b(d.Question):
  question = """When were you vaccinated against swine flu? Date of the first
  dose?"""
  type = 'date'

class IntakeQ8c(d.Question):
  question = 'If you received two doses: date of the second dose?'
  type = 'date'

class IntakeQ9(d.Question):
  question = """Did you receive seasonal flu vaccine last autumn/winter
  (i.e. 2009-2010)?"""
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             (2, "I don't know"), )

class IntakeQ10(d.Question):
  # word 'seasonal' added to question following telco 26-10-2010.
  question = 'Have you had a seasonal flu vaccine this season ({{ SEASON }})?'
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             (2, "I don't know"), )

class IntakeQ10b(d.Question):
  question = """When did you receive a flu vaccine this season ({{ SEASON }})?
  Date of the seasonal flu vaccination?"""
  type = 'date'

class IntakeQ10c(d.Question):
  question = """What were your reasons for getting a seasonal influenza
  vaccination this fall or winter season ({{ SEASON }})? (Tick all that apply)"""
  type = 'options-multiple'
  options = ((0, 'Because I belong to a risk group'),
             (1, """Because vaccination decreases the risk of me getting
             influenza"""),
             (2, """Because vaccination decreases the risk of spreading
             influenza to others"""),
             (3, """Because my general practitioner recommended influenza
             vaccination"""),
             (4, 'Because it was recommended in my workplace/school'),
             (5, """Because the vaccine was readily available and vaccine
             administration was convenient"""),
             (6, 'Because the vaccine was free'),
             (7, "Because I don't want to miss work/school"),
             (8, 'Because I believe that the vaccine is effective'),
             (9, 'Other reason(s)'), )
  
class IntakeQ10d(d.Question):
  question = """What are your reasons for NOT getting a flu vaccine this season
  ({{ SEASON }})? (Tick all that apply)"""
  type= 'options-multiple'
  options = ((0, 'I am still (planning to) get a vaccine'),
             (1, 'Because I don’t belong to a risk group'),
             (2, """Because it is better to build your own natural immunity
             against the flu"""),
             (3, 'Because I doubt that the influenza vaccine is effective'),
             (4, 'Because influenza is a minor illness'),
             (5, 'Because influenza vaccine can cause influenza'),
             (6, """Because I am worried that the vaccine is not safe or will
             cause illness or other adverse events"""),
             (7, 'Because the vaccine is not readily available to me'),
             (8, 'Because the vaccine is not free of charge'),
             (9, 'Because I dislike injections'),
             (10, 'No particular reason'),
             (11, 'Other reason(s)'), )

class IntakeQ11(d.Question):
  question = """Did you get an invitation from your doctor to receive flu
  vaccine this fall/winter season?"""
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             (2, "I don't know"), )

class IntakeQ12(d.Question):
  question = """Do you take medication for any of the following medical
  conditions?  (Tick all that apply)"""
  type = 'options-multiple'
  options = ((0, 'Yes, I am taking medication because of Asthma'),
             (1, 'Yes, I am taking medication because of Diabetes'),
             (2, """Yes, I am taking medication because of Lung disorder (COPD,
             emphysema, ...)"""),
             (3, 'Yes, I am taking medication because of a Heart disorder'),
             (4, 'Yes, I am taking medication because of a Kidney disorder'),
             (5, """Yes, I am taking medication because of an immunocompromised
             condition (e.g. splenectomy, organ transplant, aquired immune
             deficiency, cancer treatment)"""), )
  
class IntakeQ13(d.Question):
  question = 'Are you currently pregnant?'
  type = 'options-single'
  options = ((0, 'Yes'),
             (1, 'No'),
             (2, "I don't know"), )

class IntakeQ13b(d.Question):
  question = """If you are currently pregnant, in which trimester of the
  pregnancy are you?"""
  type = 'options-single'
  options = ((0, 'First trimester (week 1-12)'),
             (1, 'Second trimester (week 13-28)'),
             (2, 'Third trimester (week 29-delivery)'),
             (3, "I don't know"), )

class IntakeQ14(d.Question):
  question = 'Do you smoke?'
  type = 'options-single'
  options = ((0, 'No'),
             (1, 'Yes, less than 10 cigarettes a day'),
             (2, 'Yes, 10 cigarettes or more a day'),
             (3, 'Yes, but exclusively pipe or cigars'),
             (4, "I don't know"), )
  
class IntakeQ15(d.Question):
  question = """Do you have one of the following allergies that can cause
  respiratory symptoms? (Multiple answers possible)"""
  type = 'options-multiple'
  options = ((0, 'Pollen (hay fever)'),
             (1, 'House dust mite'),
             (2, 'Domestic animals/pets'),
             (3, """Other allergies that cause respiratory symptoms (e.g.
             sneezing, runny eyes)"""), )

class IntakeQ18(d.Question):
  question = """On average over the past 5 years, how many times per year did
  you have common colds or flu-like diseases?"""
  type = 'options-single'
  options = ((0, 'Never'),
             (1, 'One or two times a year'),
             (2, 'Between 3 and 5 times a year'),
             (3, 'Between 6 and 10 times a year'),
             (4, 'More than 10 times a year'), )

class IntakeQ16(d.Question):
  question = 'Do you follow a special diet?'
  type = 'options-single'
  options = ((0, 'No special diet'),
             (1, 'Vegetarian'),
             (2, 'Veganism'),
             (3, 'Low-calorie'),
             (4, 'Other'), )
  
class IntakeQ17(d.Question):
  question = 'Do you have pets at home? (Multiple answers possible)'
  type = 'options-multiple'
  options = ((0, 'No'),
             (1, 'Yes, one or more dogs'),
             (2, 'Yes, one or more cats'),
             (3, 'Yes, one or more birds'),
             (4, 'Yes, one ore more other animals'), )

class Survey(d.Survey):
    id = 'gold-standard-intake-0.1.0'
    rules = ( IntakeQ1,
              IntakeQ2,
              IntakeQ3,
              IntakeQ4,
              IntakeQ5,
              IntakeQ6,
              d.If(~d.Equal(IntakeQ6[0], 0)) ( IntakeQ6b ), # category 0 not 0
              IntakeQ7,
              IntakeQ7b,
              IntakeQ8,
              d.If(d.Equal(IntakeQ8, 0)) ( IntakeQ8b, IntakeQ8c ),
              IntakeQ9,
              IntakeQ10,

              d.If(d.Equal(IntakeQ10, 0)) ( IntakeQ10b, IntakeQ10c ),
              d.Else( IntakeQ10d ),

              IntakeQ11,
              IntakeQ12,
              IntakeQ13,
              d.If(d.Equal(IntakeQ13, 0)) ( IntakeQ13b ),
              IntakeQ14,
              IntakeQ15,
              IntakeQ18, # decided in telco 26-10-2010.
              IntakeQ16,
              IntakeQ17,
              )
