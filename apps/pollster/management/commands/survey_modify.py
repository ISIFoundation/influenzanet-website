'''
Created on Mar 1, 2020

Modify a survey according to a json file describing each modifications


@author: clementturbelin
'''
from optparse import make_option
from django.core.management.base import BaseCommand
from apps.pollster import models
from django.utils import simplejson
from django.db import transaction
from django.db.models import Max


TYPES = dict(models.QUESTION_TYPE_CHOICES)
TYPE_SINGLE = 'single-choice'
TYPE_MULTIPLE = 'multiple-choice'
DATATYPE_NUMERIC = 'Numeric'
DATATYPE_TEXT = 'Text'
ACTIONS = ['add_question']

DATA_TYPES = [DATATYPE_NUMERIC, DATATYPE_TEXT]

RULES = dict((
 ('show', 'wok.pollster.rules.ShowQuestion'),    
 ('hide', 'wok.pollster.rules.HideQuestion'),  
 ('exclusive', 'wok.pollster.rules.Exclusive')
))

class Command(BaseCommand):
    help = 'Update a survey for with a json definition'
    option_list = BaseCommand.option_list + (
        make_option('-f', '--file', action='store', type="string",
                    dest='file',
                    help='json file with actions to make on survey'),
        make_option('-c', '--commit', action='store_true',  dest='commit', help='Validate changes (dont by default'),
    )

    def get_question(self, name):
        r = models.Question.objects.get(survey=self.survey, data_name=name)
        return(r)
    
    def get_datatype(self, name):
        r = models.QuestionDataType.objects.get(title=name)
        return(r)
    
    def get_ruletype(self, name):
        if not name in RULES:
            raise Exception("Uknown rule type '%s'" % (name, ))
        js = RULES.get(name)
        r = models.RuleType.objects.get(js_class=js)
        return r
    
    def handle(self, *args, **options):

        verbosity = int(options.get('verbosity'))

        commit = options.get('commit')
        json_file = options.get('file')

        if json_file is None:
            raise Exception("File not provided")

        update_def = simplejson.load(open(json_file, 'r'))
        
        if not 'survey' in update_def:
            raise '"survey" entry not defined in json file'
        
        self.survey = models.Survey.objects.get(shortname=update_def['survey']) 
        
        self.fields = {}
        
        print "Found Survey %d "  % (self.survey.id)
       
        if not 'actions' in update_def:
            raise '"Action" entry not defined in json file'
        
        actions = update_def['actions']
        
        commited = False
        with transaction.commit_manually():
            try:
                idx = 0
                for action in actions:
                    print "Action %d" % (idx, )
                    if(action['action'] == 'add_question'):
                        self.add_question(action)
                    if(action['action'] == 'add_option'):
                        self.add_option(action)
                    idx = idx + 1
            except Exception as e:
                transaction.rollback()
                raise    
            if commit:
                transaction.commit()
                commited = True
            else:
                transaction.rollback()
        
        if commited:
            print "Changed has been made on survey " + self.survey.shortname
        
        self.build_fields()
        
    def add_field(self, name, type):
        """
            Register field to modify data table
        """
        if name in self.fields:
            raise Exception("Field '%s' already exists" % (name)) 
         
        self.fields[name] = {'type': type}
       
    def build_fields(self):
        """
            Create SQL modification for data tables from fields
        """
        ff = []
        for name, r in self.fields.items():
            field_type = r['type']
            sql_type = '<Unknown>'
            if field_type == "bool":
                sql_type = "boolean NOT NULL"
            if field_type == DATATYPE_NUMERIC:
                sql_type = "integer"
            if field_type == DATATYPE_TEXT:
                sql_type = "text"
            ff.append('ADD COLUMN "' + name+'" '+ sql_type)        
        s = "ALTER TABLE pollster_results_weekly\n" + ",\n".join(ff)
        f = open(self.survey.shortname +'.sql', 'w')
        f.write(s)
        f.close()
        
        
    def add_option(self, action):
        p = action['params']
        if p is None:
            raise Exception("Params expected")
        name = p['question']
        question = self.get_question(name)
        
        print("Add option in " + self.str_question(question))
        
        max_ordinal = models.Option.objects.filter(question=question).aggregate(ordinal=Max('ordinal'))
        max_ordinal = max_ordinal['ordinal'] + 1
        
        xoptions = p['options']
        
        for xo in xoptions:
            o = models.Option()
            o.question = question
            o.text = xo['title']
            o.value = xo['value']
            o.is_open = False
            o.starts_hidden = False
            if 'after' in xo:
                after = xo['after']
                ordinal = self.redorder_options(question.options, after)
            else:
                ordinal = max_ordinal
                max_ordinal = max_ordinal + 1
            o.ordinal = ordinal
            o.save()
            
            if question.is_multiple_choice:
                self.add_field(o.data_name, type="bool")
            
            print(self.str_option(o))
    
    def redorder_options(self, options, after):
        ordinal = None
        for o in options:
            if o.value == after:
                ordinal = o.ordinal
        if ordinal is None:
            raise Exception("Unknown after value '%s'" % (after) )
        for o in options:
            if o.ordinal > ordinal:
                o.ordinal = ordinal + 2
                o.save()
        return ordinal + 1
        
    def add_question(self, action):    
        p = action['params']
        if p is None:
            raise Exception("Params expected")
        q = models.Question()
        name = p['name']
        if name is None:
            raise Exception("Name expected")
        
        ordinal = models.Question.objects.filter(survey=self.survey).aggregate(ordinal=Max('ordinal'))
        ordinal = ordinal['ordinal'] + 1
        
        q.data_name = name
        q.ordinal = ordinal
        q.title = p['title']
        if 'description' in p:
            q.description = p['description']
        
        q.survey = self.survey
        if 'hidden' in p:
            if not isinstance(p['hidden'], bool):
                raise Exception("Hidden must be boolean")
            q.starts_hidden = p["hidden"]
        else:
            q.starts_hidden = False
        q.regex = ''
        type = p['type']
        if not type in TYPES:
            raise Exception("Unknown type '%s'" % type)
        q.type = type
        data_type = p['data_type']
        dt = self.get_datatype(data_type)
        q.data_type = dt
        
        if 'open_type' in p:
            q.open_option_data_type = self.get_datatype(p['open_type'])
        
        q.save()
        
        if q.is_single_choice:
            self.add_field(q.data_name, data_type)
        
        print(" Adding " + self.str_question(q))
        options = {}
        if type == TYPE_SINGLE or type == TYPE_MULTIPLE:
            xoptions = p['options']
            option_ordinal = 0
            
            for xoption in xoptions:
                option_ordinal += 1
                option = models.Option()
                option.ordinal = option_ordinal
                option.question = q
                option.is_virtual = False
                virtual_type = ''
                option.virtual_inf =  ''
                option.virtual_sup = ''
                option.virtual_regex = ''
                option.text = xoption['title'] 
                option.value = xoption['value']
                option.is_open = False
                option.starts_hidden = False
                
                if 'open' in xoption:
                    option.is_open = True
                    if q.open_option_data_type is None:
                        raise Exception("Please set open option data type for this question")
                
                option.save()
                print "  + " + self.str_option(option)
                options[option.value] = option
                
                if q.is_multiple_choice:
                    self.add_field(option.data_name, 'bool')
                if option.is_open:
                    self.add_field(option.open_option_data_name, option.open_option_data_type)    
                
        if 'rules' in p:
            rules = p['rules']
            if not isinstance(rules, list) or not len(rules) > 0:
                raise Exception("Rules must be a list") 
            rid = 0
            for xr in rules:
                rule = models.Rule()
                subject_options = None
                object_options = None
                
                x_rule_type = xr['type']
                
                try:
                    rtype = self.get_ruletype(x_rule_type)
                    if x_rule_type == "exclusive":
                        subject_question = q
                        exclusive_options = xr['options']
                        subject_options = self.get_target_options(q, {'in': exclusive_options })
                        object_options = self.get_target_options(q, {'not': exclusive_options })
                    else:
                        subject_question = self.get_question(xr["from"])
                        if 'options' in xr:
                            subject_options = self.get_target_options(subject_question, xr['options'])
                except Exception as e:
                    e.message += "Error in rule %d : %s" % (rid, e.message)
                    raise
                rule.rule_type = rtype
                if 'sufficient' in xr:
                    rule.is_sufficient = xr['sufficient']
                else:
                    rule.is_sufficient = True
            
                rule.subject_question = subject_question
                rule.object_question = q
                rule.save()
                # Now update dependencies
                if subject_options is not None:
                    rule.subject_options = subject_options
                
                if object_options is not None:
                    rule.object_options = object_options
                
                
                print("   + " + self.str_rule(rule))
                rid = rid + 1
                
    def get_target_options(self, question, oo):           
        subject_options = None
        all_options = question.options
        if isinstance(oo, str) and oo == "all":
            subject_options = all_options
        if isinstance(oo, dict):
            values = None
            if 'not' in oo:
                values = oo['not']
                op = 'not'
            if 'in' in oo:
                values = oo['in']
                op = 'in'
            if not isinstance(values, list) or len(values) == 0:
                raise Exception("options values must be a list")
            subject_options = []
            for o in all_options:
                in_option = o.value in values
                if op == 'in' and in_option:
                    subject_options.append(o)
                if op == 'not' and not in_option:
                    subject_options.append(o)
        if subject_options is None:
            raise Exception("Unable to find option definitions")
        return subject_options
    def str_question(self, q):
        if q is None:
            return "Question<None>"
        s = "Q<%s, %s>" % (q.id, q.data_name)
        return s
    
    def str_option(self, option):
        return '<Option %s,%s,"%s">' % (option.id, option.value, option.text) 
    
    def str_options(self, options):
        if options is None:
            return '<None>'
        oo = []
        for o in options:
           oo.append(o.value)
        return '[' + ','.join(oo) + ']'
    
    def str_rule(self, rule):
        s = 'Rule<from ' + self.str_question(rule.subject_question) 
        if rule.subject_options is not None:
            oo = rule.subject_options.all()
            s += self.str_options(oo)
        s += ' target ' + self.str_question(rule.object_question)   
        if rule.object_options is not None:
            oo = rule.object_options.all()
            s += self.str_options(oo)
        s += ">"
        return s