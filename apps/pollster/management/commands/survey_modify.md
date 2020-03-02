JSON for survey modification
----------

<> : Refer to a Type name
Enum[] : list of possible values
[<>] : Array of <type>

Global structure:

 "survey": <string>, # survey name to modify (shortname)
 "actions": [ <ActionType> ]  # List of actions
}

ActionType:
 "action": <string> # action name 'add_question', 'add_option'
 "params":  <ParamsQuestion> | <ParamsOption>
 
ParamsQuestion:
 "name": <string> # Question name
 "title": <strin> # "Question label",
 "description: <string> # Question description
 "type":  Enum["multiple-choice","single-choice"]
 "data_type": Enum["Numeric","Text"]
 "options": [<OptionType>]
 "open":  Enum["Numeric","Text"]
 "rules": [<ExclusiveRuleType>|<BaseRuleType>]  

ParamsOption:
 question: <string> # Question name to add the option to
 options: [<OptionWithAfterType>]

OptionType:
 title: <string> # Option label ("text" field)
 value: <string> # Value

OptionWithAfterType<OptionType>:
 after: <string> # Value of the option on which to add the new option after (only if addoption)

BaseRuleType:
  type: Enum["show","hide"]
  from: <string> # Question name for subject question (question trigger)
  options: "all"|<OptionSelectionType>

ExclusiveRuleType:
  type: "exclusive"
  options: [<string>] # List of option value to make exclusive to others

   
 