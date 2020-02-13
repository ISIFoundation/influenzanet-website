import warnings

from django.db import models, connection, transaction, IntegrityError, DatabaseError
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.core.validators import RegexValidator
from django.template import Template
from cms.models import CMSPlugin
from xml.etree import ElementTree
from math import pi,cos,sin,log,exp,atan
from . import dynamicmodels, json
from .db.utils import get_db_type, convert_query_paramstyle
import os, re, shutil, warnings, datetime, csv
from django.conf import settings

DEG_TO_RAD = pi/180
RAD_TO_DEG = 180/pi

try:
    import mapnik
    mapnik_version = 2
except ImportError:
        mapnik_version = None
        warnings.warn("No working version for library 'mapnik' found. Continuing without mapnik")

SURVEY_QUESTION_TITLE_SIZE = 4096


SURVEY_STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published'),
    ('UNPUBLISHED', 'Unpublished')
)

SURVEY_TRANSLATION_STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published')
)

CHART_STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published'),
)

QUESTION_TYPE_CHOICES = (
    ('builtin', 'Builtin'),
    ('text', 'Open Answer'),
    ('single-choice', 'Single Choice'),
    ('multiple-choice', 'Multiple Choice'),
    ('matrix-select', 'Matrix Select'),
    ('matrix-entry', 'Matrix Entry'),
)

CHART_SQLFILTER_CHOICES = (
    ('NONE', 'None'),
    ('USER', 'Current User'),
    ('PERSON', 'Current Person'),
)

IDENTIFIER_REGEX = r'^[a-zA-Z][a-zA-Z0-9_]*$'
IDENTIFIER_OPTION_REGEX = r'^[a-zA-Z0-9_]*$'

SURVEY_EXTRA_SQL = {
    'postgresql': {
        'weekly': [
            """DROP VIEW IF EXISTS pollster_health_status""",
            """CREATE VIEW pollster_health_status AS
               SELECT id as pollster_results_weekly_id,
                      case true
                          when "Q1_0"
                              then 'NO-SYMPTOMS'

                          when ("Q5" = 0 or "Q6b" = 0)
                           and ("Q1_1" or "Q1_2"  or "Q6d" = 3 or "Q6d" = 4 or "Q6d" = 5 or "Q1_11" or "Q1_8" or "Q1_9")
                           and ("Q1_5" or "Q1_6" or "Q1_7")
                              then 'ILI'

                          when
                            (
                                (not "Q1_1") and (not "Q1_2")
                                and (("Q6d" = 0) or ("Q6d" is null))
                                and ("Q1_3" or "Q1_4" or "Q1_14")
                                and ("Q11" = 2)
                            ) and (
                                case true when "Q1_17" then 1 else 0 end +
                                case true when "Q1_15" then 1 else 0 end +
                                case true when "Q1_16" then 1 else 0 end +
                                case true when "Q1_18" then 1 else 0 end >= 2
                            ) then 'ALLERGY-or-HAY-FEVER-and-GASTROINTESTINAL'

                          when (not "Q1_1") and (not "Q1_2")
                           and (("Q6d" = 0) or ("Q6d" is null))
                           and ("Q1_3" or "Q1_4" or "Q1_14")
                           and ("Q11" = 2)
                              then 'ALLERGY-or-HAY-FEVER'

                          when
                            (
                                case true when "Q1_3" then 1 else 0 end +
                                case true when "Q1_4" then 1 else 0 end +
                                case true when "Q1_6" then 1 else 0 end +
                                case true when "Q1_5" then 1 else 0 end >= 2
                                  -- note: common cold after all allergy-related branches
                            ) and (
                                case true when "Q1_17" then 1 else 0 end +
                                case true when "Q1_15" then 1 else 0 end +
                                case true when "Q1_16" then 1 else 0 end +
                                case true when "Q1_18" then 1 else 0 end >= 2
                            ) then 'COMMON-COLD-and-GASTROINTESTINAL'

                          when
                            case true when "Q1_3" then 1 else 0 end +
                            case true when "Q1_4" then 1 else 0 end +
                            case true when "Q1_6" then 1 else 0 end +
                            case true when "Q1_5" then 1 else 0 end >= 2
                              -- note: common cold after all allergy-related branches
                              then 'COMMON-COLD'

                          when
                            case true when "Q1_17" then 1 else 0 end +
                            case true when "Q1_15" then 1 else 0 end +
                            case true when "Q1_16" then 1 else 0 end +
                            case true when "Q1_18" then 1 else 0 end >= 2
                              then 'GASTROINTESTINAL'

                          else 'NON-SPECIFIC-SYMPTOMS'
                      end as status
                 FROM pollster_results_weekly"""
        ]
    },
    'sqlite': {
        'weekly': [
            """DROP VIEW IF EXISTS pollster_health_status""",
            """CREATE VIEW pollster_health_status AS
               SELECT id as pollster_results_weekly_id,
                      case 1
                          when Q1_0
                              then 'NO-SYMPTOMS'

                          when (Q5 = 0 or Q6b = 0)
                           and (Q1_1 or Q1_2  or Q6d = 3 or Q6d = 4 or Q6d = 5 or Q1_11 or Q1_8 or Q1_9)
                           and (Q1_5 or Q1_6 or Q1_7)
                              then 'ILI'

                          when
                            (
                                (not Q1_1) and (not Q1_2)
                                and ((Q6d = 0) or (Q6d is null))
                                and (Q1_3 or Q1_4 or Q1_14)
                                and (Q11 = 2)
                            ) and (
                                case true when Q1_17 then 1 else 0 end +
                                case true when Q1_15 then 1 else 0 end +
                                case true when Q1_16 then 1 else 0 end +
                                case true when Q1_18 then 1 else 0 end >= 2
                            ) then 'ALLERGY-or-HAY-FEVER-and-GASTROINTESTINAL'

                          when (not Q1_1) and (not Q1_2)
                           and ((Q6d = 0) or (Q6d is null))
                           and (Q1_3 or Q1_4 or Q1_14)
                           and (Q11 = 2)
                              then 'ALLERGY-or-HAY-FEVER'

                          when
                            (
                                case true when Q1_3 then 1 else 0 end +
                                case true when Q1_4 then 1 else 0 end +
                                case true when Q1_6 then 1 else 0 end +
                                case true when Q1_5 then 1 else 0 end >= 2
                                  -- note: common cold after all allergy-related branches
                            ) and (
                                case true when Q1_17 then 1 else 0 end +
                                case true when Q1_15 then 1 else 0 end +
                                case true when Q1_16 then 1 else 0 end +
                                case true when Q1_18 then 1 else 0 end >= 2
                            ) then 'COMMON-COLD-and-GASTROINTESTINAL'

                          when
                            case true when Q1_3 then 1 else 0 end +
                            case true when Q1_4 then 1 else 0 end +
                            case true when Q1_6 then 1 else 0 end +
                            case true when Q1_5 then 1 else 0 end >= 2
                              -- note: common cold after all allergy-related branches
                              then 'COMMON-COLD'

                          when
                            case true when Q1_17 then 1 else 0 end +
                            case true when Q1_15 then 1 else 0 end +
                            case true when Q1_16 then 1 else 0 end +
                            case true when Q1_18 then 1 else 0 end >= 2
                              then 'GASTROINTESTINAL'

                          else 'NON-SPECIFIC-SYMPTOMS'
                      end as status

                 FROM pollster_results_weekly"""
        ]
    }
}

def _get_or_default(queryset, default=None):
    r = queryset[0:1]
    if r:
        return r[0]
    return default

def previous_season_data(shortname, user_id, global_id):
    cursor = connection.cursor()
    query = "select * from pollster_results_%s_previousdata where \"global_id\"='%s' and \"user\"='%s'" % (shortname, global_id, str(user_id))
    cursor.execute(query)
    res = cursor.fetchone()
    desc = cursor.description
    if res is not None:
        res = dict(zip([col[0] for col in desc], res))
        # Put a flag in the data
        res["_source_"] = "previousdata"
    return res


## Prefill strategy using previous season data
def prefill_previous_data(survey, user_id, global_id):
    """
    fetch data to prefill a user's survey looking first at the current data table and then to another
    table containing previous data for the user (for example from the last year data table)
    The only assumption made on this table are the keys global_id and user_id, and the table name
    """
    data = survey.get_last_participation_data(user_id, global_id)
    if data is not None:
        return data
    return previous_season_data(survey.shortname, user_id, global_id)

class Survey(models.Model):
    parent = models.ForeignKey('self', db_index=True, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, default='')
    shortname = models.SlugField(max_length=255, default='')
    version = models.SlugField(max_length=255, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default='DRAFT', choices=SURVEY_STATUS_CHOICES)
    prefill_method = models.CharField(max_length=255, blank=True, default="LAST")
    introduction = models.TextField(blank=True, default='')


    form = None
    translation_survey = None

    _standard_result_fields =[
        ('user', models.IntegerField(null=True, blank=True, verbose_name="User")),
        ('global_id', models.CharField(max_length=36, null=True, blank=True, verbose_name="Person")),
        ('channel', models.CharField(max_length=36, null=True, blank=True, verbose_name="Channel"))
    ]

    """
        Use survey cache allow to prefetch questions & options data for one survey
        and cache the result to avoid query deluge
    """
    _use_survey_cache = False
    _cache_questions = None
    _cache_model = None

    def set_caching(self, use_cache):
        self._use_survey_cache = use_cache

    def get_caching(self):
        return self._use_survey_cache

    @staticmethod
    def get_by_shortname(shortname):
        return Survey.objects.all().get(shortname=shortname, status="PUBLISHED")

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

    @property
    def is_draft(self):
        return self.status == 'DRAFT'

    @property
    def is_published(self):
        return self.status == 'PUBLISHED'

    @property
    def is_unpublished(self):
        return self.status == 'UNPUBLISHED'

    @property
    def is_editable(self):
        return self.is_draft or self.is_unpublished

    @property
    def questions(self):
        """
            Get questions of the survey,
        """
        if not self._use_survey_cache:
            return self._get_questions()
        if self._cache_questions is None:
            self._cache_questions = list(self._get_questions())
        return self._cache_questions

    def _prefetch_rules(self, q_dict):
        """
            Prefetch Rules for all the survey and return a dictionnary with all rules for each question (indexed by question_id)
        """
        ids = q_dict.keys()
        rr = Rule.objects.all().filter(subject_question__in=ids).select_related('rule_type')
        rules = {}
        for rule in rr:
            qid = rule.subject_question_id
            q = q_dict.get(qid)
            rule.subject_question = q
            oid = rule.object_question_id
            q = q_dict.get(oid)
            rule.object_question = q
            if not rules.has_key(qid):
                rules[qid] = []
            rules[qid].append(rule)
        return rules

    def _prefetch_options(self, q_dict):
        """
            Prefetch all options used in the Survey
            Return dictionnary of all options for each question
        """
        ids = q_dict.keys()
        oo = Option.objects.all().filter(question__in=ids).select_related('virtual_type')
        options = {}
        for option in oo:
            qid = option.question_id
            q = q_dict.get(qid)
            option.question = q
            if not options.has_key(qid):
                options[qid] = []
            options[qid].append(option)
        return options

    def _get_questions(self):
        """
        get questions list for this survey
        """
        questions = self.question_set.all().select_related('data_type', 'open_option_data_type')
        questions = list(questions) # actually get data
        if self._use_survey_cache:
            q_dict = dict( [(q.id,q) for q in questions])
            rules = self._prefetch_rules(q_dict)
            options = self._prefetch_options(q_dict)
        else:
            rules = None
            options = None
        for question in questions:
            # Propgagate caching policy
            question.set_caching(self._use_survey_cache)
            question.set_translation_survey(self.translation_survey)
            if rules is not None:
                r = rules.get(question.id)
                question.set_rules_cache(r)
            if options is not None:
                o = options.get(question.id)
                # Set whatever the result, as we assume we had fetch all options for ALL questions of this survey
                # If o is None, then an empty cache will be provided
                question.set_options_cache(o)
            if self.form is not None:
                question.set_form(self.form)
            yield question

    @property
    def translation(self):
        return self.translation_survey

    @models.permalink
    def get_absolute_url(self):
        return ('pollster_survey_edit', [str(self.id)])

    def __unicode__(self):
        return "Survey #%d %s" % (self.id, self.title)

    def get_table_name(self):
        if self.is_published and not self.shortname:
            raise RuntimeError('cannot generate tables for surveys with no shortname')
        return 'results_'+str(self.shortname)

    def get_last_participation_data(self, user_id, global_id):
        """
            get the last data available for a given user, in the current data table
        """
        model = self.as_model()
        participation = model.objects\
            .filter(user=user_id)\
            .filter(global_id = global_id)\
            .order_by('-timestamp')\
            .values()
        return _get_or_default(participation)

    def get_prefill_data(self, user_id, global_id):
        """
            get previous data for a user following the survey policy (prefill_method)
            'LAST' value fetch the last available data (in the current data table)
            other values should be a function name with the signature func(survey, user_id, global_id)

        """
        if self.prefill_method == '':
            return None

        if self.prefill_method == 'LAST':
            return self.get_last_participation_data(user_id, global_id)

        if self.prefill_method == 'prefill_previous_data':
            return prefill_previous_data(self, user_id, global_id)

        raise Exception("Prefill function %s does not exist" % self.prefill_method)

    def as_model(self):
        if self._use_survey_cache and self._cache_model:
            return self._cache_model
        fields = []
        fields.extend(Survey._standard_result_fields)
        for question in self.questions:
            fields += question.as_fields()
        model = dynamicmodels.create(self.get_table_name(), fields=dict(fields), app_label='pollster')
        if self._use_survey_cache:
            self._cache_model = model
        return model

    def as_form(self):
        model = self.as_model()
        questions = list(self.questions)
        def clean(self):
            for question in questions:
                if question.is_multiple_choice and question.is_mandatory:
                    valid = any([self.cleaned_data.get(d, False) for d in question.data_names])
                    if not valid:
                        self._errors[question.data_name] = self.error_class('At least one option should be selected')
            return self.cleaned_data
        form = dynamicmodels.to_form(model, {'clean': clean})

        for question in questions:
            if question.is_mandatory and question.data_name in form.base_fields:
                form.base_fields[question.data_name].required = True
        return form

    def set_form(self, form):
        self.form = form
        for question in self.questions:
            question.set_form(form)

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey

    def check(self):
        errors = []
        if not self.shortname:
            errors.append('Missing survey shortname')
        elif not re.match(IDENTIFIER_REGEX, self.shortname):
            errors.append('Invalid survey shortname "%s"' % (self.shortname,))
        for question in self.questions:
            errors.extend(question.check())
        return errors

    def publish(self):
        if self.is_published:
            return None
        errors = self.check()
        if errors:
            return errors
        # Unpublish other surveys with the same shortname.
        for o in Survey.objects.filter(shortname=self.shortname, status='PUBLISHED'):
            o.unpublish()
        self.status = 'PUBLISHED'
        model = self.as_model()
        table = model._meta.db_table
        if table in connection.introspection.table_names():
            now = datetime.datetime.now()
            backup = table+'_vx_'+format(now, '%Y%m%d%H%M%S')
            connection.cursor().execute('ALTER TABLE '+table+' RENAME TO '+backup)
        dynamicmodels.install(model)
        db = get_db_type(connection)
        for extra_sql in SURVEY_EXTRA_SQL[db].get(self.shortname, []):
            connection.cursor().execute(extra_sql)
        self.save()
        return None

    def unpublish(self):
        if not self.is_published:
            return
        table = self.as_model()._meta.db_table
        if table in connection.introspection.table_names():
            now = datetime.datetime.now()
            version = self.version or 0
            backup = table+'_v'+str(version)+'_'+format(now, '%Y%m%d%H%M%S')
            connection.cursor().execute('ALTER TABLE '+table+' RENAME TO '+backup)
        self.status = 'UNPUBLISHED'
        self.save()

    def write_csv(self, writer):
        model = self.as_model()
        fields = model._meta.fields
        headers = []
        for field in fields:
            name = field.verbose_name or field.name
            if type(name) is unicode:
                headers.append(name.encode('utf-8'))
            else:
                headers.append(str(name))
        writer.writerow(headers)
        for result in model.objects.all():
            row = []
            for field in fields:
                val = getattr(result, field.name)
                if callable(val):
                    val = val()
                if type(val) is unicode:
                    val = val.encode('utf-8')
                row.append(val)
            writer.writerow(row)

    @property
    def count_responses(self):
        model = self.as_model()
        return model.objects.count()

class RuleType(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
    js_class = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return "RuleType #%d %s" % (self.id, self.title)

class QuestionDataType(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
    db_type = models.CharField(max_length=255)
    css_class = models.CharField(max_length=255)
    js_class = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return "QuestionDataType #%d %s" % (self.id, self.title)

    def as_field_type(self, verbose_name=None, regex=None):
        import django.db.models
        import db.models
        field = eval(self.db_type)
        field.verbose_name = verbose_name
        if regex:
            field.validators.append(RegexValidator(regex=regex))
        return field

    @staticmethod
    def default_type():
        return QuestionDataType.objects.filter(title = 'Text')[0]

    @staticmethod
    def default_timestamp_type():
        return QuestionDataType.objects.filter(title = 'Timestamp')[0]

    @property
    def is_internal(self):
        return self.title == 'Timestamp'

class VirtualOptionType(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
    question_data_type = models.ForeignKey(QuestionDataType)
    js_class = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return "VirtualOptionType #%d %s for %s" % (self.id, self.title, self.question_data_type.title)

class Question(models.Model):
    survey = models.ForeignKey(Survey, db_index=True)
    starts_hidden = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=False)
    ordinal = models.IntegerField()
    title = models.TextField(max_length=SURVEY_QUESTION_TITLE_SIZE, blank=True, default='')
    description = models.TextField(blank=True, default='')
    type = models.CharField(max_length=255, choices=QUESTION_TYPE_CHOICES)
    data_type = models.ForeignKey(QuestionDataType)
    open_option_data_type = models.ForeignKey(QuestionDataType, related_name="questions_with_open_option", null=True, blank=True)
    data_name = models.CharField(max_length=255)
    visual = models.CharField(max_length=255, blank=True, default='')
    tags = models.TextField(blank=True, default='')
    regex = models.CharField(max_length=1023, blank=True, default='')
    error_message = models.TextField(blank=True, default='')

    form = None
    translation_survey = None
    translation_question = None

    # Define cache fields
    _use_survey_cache = False
    _cache_options = None
    _cache_rules = None
    _cache_rows = None
    _cache_columns = None

    def set_caching(self, use_cache):
        self._use_survey_cache = use_cache
        self._cache_rows = None
        self._cache_options = None
        self._cache_rules = None
        self._cache_columns = None

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

    @property
    def translated_description(self):
        if self.translation and self.translation.description:
            return self.translation.description
        return self.description

    @property
    def translated_error_message(self):
        if self.translation and self.translation.error_message:
            return self.translation.error_message
        return self.error_message


    @property
    def errors(self):
        if not self.form:
            return {}
        errors = [(data_name, self.form.errors[data_name]) for data_name in self.data_names if data_name in self.form.errors]
        if self.is_multiple_choice and self.data_name in self.form.errors:
            errors.append((self.data_name, self.form.errors[self.data_name]))
        return dict(errors)

    @property
    def rows(self):
        if self._use_survey_cache:
            if self._cache_rows is None:
                self._cache_rows = list(self._get_rows())
            return self._cache_rows
        return self._get_rows()

    def _get_rows(self):
        """
            get QuestionRow using generator
        """
        for row in self.row_set.all():
            row.set_translation_survey(self.translation_survey)
            yield row

    @property
    def columns(self):
        if self._use_survey_cache:
            if self._cache_columns is None:
                self._cache_columns = list(self._get_columns())
            return self._cache_columns
        return self._get_columns()

    def _get_columns(self):
        for column in self.column_set.all():
            column.set_translation_survey(self.translation_survey)
            yield column

    @property
    def rows_columns(self):
        for row in self.rows:
            yield (row, self._columns_for_row(row))

    def _columns_for_row(self, row):
        for column in self.columns:
            column.set_row(row)
            yield column

    @property
    def data_names(self):
        return [data_name for data_name, data_type in self.as_fields()]

    @property
    def options(self):
        if not self._use_survey_cache:
            return self._get_options()
        if self._cache_options is not None:
            return self._cache_options
        options = list(self._get_options())
        self._cache_options = options
        return options

    def set_options_cache(self, options):
        cache = []
        if options is not None:
            for option in options:
                if self.form is not None:
                    option.set_form(self.form)
                if self.translation_survey is not None:
                    option.set_translation_survey(self.translation_survey)
                cache.append(option)
        self._cache_options = cache

    def _get_options(self):
        for option in self.option_set.all().select_related('virtual_type'):
            if self.form is not None:
                option.set_form(self.form)
            option.set_translation_survey(self.translation_survey)
            yield option

    def set_rules_cache(self, rules):
        """
            Set cached rules for the question
        """
        if rules is None:
            self._cache_rules = []
        else:
            self._cache_rules = rules

    @property
    def rules(self):
        """
        Get the rules associated with this question
        """
        if self._use_survey_cache and self._cache_rules is not None:
            return self._cache_rules
        return self.subject_of_rules.all

    @property
    def translation(self):
        return self.translation_question

    @property
    def css_classes(self):
        c = ['question', 'question-'+self.type, self.data_type.css_class]
        if self.starts_hidden:
            c.append('starts-hidden')
        if self.is_mandatory:
            c.append('mandatory')
        if self.errors:
            c.append('error')
        return c

    @property
    def form_value(self):
        if not self.form:
            return ''
        return self.form.data.get(self.data_name, '')

    @property
    def is_builtin(self):
        return self.type == 'builtin'

    @property
    def is_text(self):
        return self.type == 'text'

    @property
    def is_single_choice(self):
        return self.type == 'single-choice'

    @property
    def is_multiple_choice(self):
        return self.type == 'multiple-choice'

    @property
    def is_matrix_select(self):
        return self.type == 'matrix-select'

    @property
    def is_matrix_entry(self):
        return self.type == 'matrix-entry'

    @property
    def is_visual_dropdown(self):
        return self.visual == 'dropdown'

    def __unicode__(self):
        return "Question #%d %s" % (self.id, self.title)

    class Meta:
        ordering = ['survey', 'ordinal']

    def data_name_for_row_column(self, row, column):
        return '%s_multi_row%d_col%d' % (self.data_name, row.ordinal, column.ordinal)

    def as_fields(self):
        fields = []
        if self.type == 'builtin':
            fields = [ (self.data_name, self.data_type.as_field_type(verbose_name=self.title)) ]
        elif self.type == 'text':
            fields = [ (self.data_name, self.data_type.as_field_type(verbose_name=self.title, regex=self.regex)) ]
        elif self.type == 'single-choice':
            open_option_data_type = self.open_option_data_type or self.data_type
            fields = [ (self.data_name, self.data_type.as_field_type(verbose_name=self.title)) ]
            for open_option in [o for o in self.options if o.is_open]:
                title_open = "%s: %s Open Answer" % (self.title, open_option.value)
                fields.append( (open_option.open_option_data_name, open_option_data_type.as_field_type(verbose_name=title_open)) )
        elif self.type == 'multiple-choice':
            fields = []
            for option in self.options:
                title = "%s: %s" % (self.title, option.value)
                fields.append( (option.data_name, models.BooleanField(verbose_name=title)) )
                if option.is_open:
                    title_open = "%s: %s Open Answer" % (self.title, option.value)
                    fields.append( (option.open_option_data_name, option.open_option_data_type.as_field_type(verbose_name=title_open)) )
        elif self.type in ('matrix-select', 'matrix-entry'):
            fields = []
            for row, columns in self.rows_columns:
                for column in columns:
                    r = row.title or ("row %d" % row.ordinal)
                    c = column.title or ("column %d" % column.ordinal)
                    title = "%s (%s, %s)" % (self.title, r, c)
                    fields.append( (column.data_name, self.data_type.as_field_type(verbose_name=title)) )
        else:
            raise NotImplementedError(self.type)
        return fields

    def set_form(self, form):
        self.form = form
        for option in self.options:
            option.set_form(form)

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            self.translation_question = translation_survey.translate_question(self)

    def check(self):
        errors = []
        if not self.data_name:
            errors.append('Missing data name for question "%s"' % (self.title, ))
        elif not re.match(IDENTIFIER_REGEX, self.data_name):
            errors.append('Invalid data name "%s" for question "%s"' % (self.data_name, self.title))
        values = {}
        for option in self.options:
            errors.extend(option.check())
            values[option.value] = values.get(option.value, 0) + 1
        if self.type == 'multiple-choice':
            dups = [val for val, count in values.items() if count > 1]
            for dup in dups:
                errors.append('Duplicated value %s in question %s' % (dup, self.title))
        return errors


class QuestionRow(models.Model):
    question = models.ForeignKey(Question, related_name="row_set", db_index=True)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, default='')

    translation_survey = None
    translation_row = None

    class Meta:
        ordering = ['question', 'ordinal']

    def __unicode__(self):
        return "QuestionRow #%d %s" % (self.id, self.title)

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

    @property
    def translation(self):
        return self.translation_row

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationquestionrow_set.all().filter(row=self)
            default = TranslationQuestionRow(translation = translation_survey, row=self)
            self.translation_row = _get_or_default(r, default)

class QuestionColumn(models.Model):
    question = models.ForeignKey(Question, related_name="column_set", db_index=True)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, default='')

    translation_survey = None
    translation_column = None
    row = None

    class Meta:
        ordering = ['question', 'ordinal']

    def __unicode__(self):
        return "QuestionColumn #%d %s" % (self.id, self.title)

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

    @property
    def translation(self):
        return self.translation_column

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationquestioncolumn_set.all().filter(column=self)
            default = TranslationQuestionColumn(translation = translation_survey, column=self)
            self.translation_column = _get_or_default(r, default)

    def set_row(self, row):
        self.row = row

    @property
    def options(self):
        for option in self.question.options:
            if option.row and option.row != self.row:
                continue
            if option.column and option.column != self:
                continue
            option.set_row_column(self.row, self)
            option.set_translation_survey(self.translation_survey)
            # TODO: We need a form to reset the selects to user's values.
            # option.set_form(self.form)
            yield option

    @property
    def data_name(self):
        if not self.row:
            raise NotImplementedError('use Question.rows_columns() to get the right data_name here')
        return self.question.data_name_for_row_column(self.row, self)

class Option(models.Model):
    question = models.ForeignKey(Question, db_index=True)
    clone = models.ForeignKey('self', db_index=True, blank=True, null=True)
    row = models.ForeignKey(QuestionRow, blank=True, null=True)
    column = models.ForeignKey(QuestionColumn, blank=True, null=True)
    is_virtual = models.BooleanField(default=False)
    is_open = models.BooleanField(default=False)
    starts_hidden = models.BooleanField(default=False)
    ordinal = models.IntegerField()
    text = models.CharField(max_length=4095, blank=True, default='')
    group = models.CharField(max_length=255, blank=True, default='')
    value = models.CharField(max_length=255, default='')
    description = models.TextField(blank=True, default='')

    virtual_type = models.ForeignKey(VirtualOptionType, blank=True, null=True)
    virtual_inf = models.CharField(max_length=255, blank=True, default='')
    virtual_sup = models.CharField(max_length=255, blank=True, default='')
    virtual_regex = models.CharField(max_length=255, blank=True, default='')

    form = None
    translation_survey = None
    translation_option = None
    current_row_column = (None, None)

    @property
    def translated_text(self):
        if self.translation and self.translation.text:
            return self.translation.text
        return self.text

    @property
    def translated_description(self):
        if self.translation and self.translation.description:
            return self.translation.description
        return self.description

    @property
    def data_name(self):
        if self.question.type in ('text', 'single-choice'):
            return self.question.data_name
        elif self.question.type == 'multiple-choice':
            return self.question.data_name+'_'+self.value
        elif self.question.type in ('matrix-select', 'matrix-entry'):
            row = self.row or self.current_row_column[0]
            column = self.column or self.current_row_column[1]
            return self.question.data_name_for_row_column(row, column)
        else:
            raise NotImplementedError(self.question.type)

    @property
    def translation(self):
        return self.translation_option

    @property
    def open_option_data_name(self):
        return self.question.data_name+'_'+self.value+'_open'

    @property
    def open_option_data_type(self):
        return self.question.open_option_data_type or self.question.data_type

    def __unicode__(self):
        return 'Option #%d %s' % (self.id, self.value)

    class Meta:
        ordering = ['question', 'ordinal']

    @property
    def form_value(self):
        if not self.form:
            return ''
        return self.form.data.get(self.data_name, '')

    @property
    def open_option_data_form_value(self):
        if not self.form:
            return ''
        return self.form.data.get(self.open_option_data_name, '')

    @property
    def form_is_checked(self):
        if self.question.type in ('text', 'single-choice'):
            return self.form_value == self.value
        elif self.question.type == 'multiple-choice':
            return bool(self.form_value)
        elif self.question.type in ('matrix-select', 'matrix-entry'):
            return self.form_value == self.value
        else:
            raise NotImplementedError(self.question.type)

    def set_form(self, form):
        self.form = form

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            self.translation_option = translation_survey.translate_option(self)

    def set_row_column(self, row, column):
        self.current_row_column = (row, column)

    def check(self):
        errors = []
        if self.is_virtual:
            if not self.virtual_inf and not self.virtual_sup and not self.virtual_regex:
                errors.append('Missing parameters for derived value in question "%s"' % (self.question.title, ))
        else:
            if not self.text:
                errors.append('Empty text for option in question "%s"' % (self.question.title, ))
            if not self.value:
                errors.append('Missing value for option "%s" in question "%s"' % (self.text, self.question.title))
            elif self.question.type == 'multiple-choice' and not re.match(IDENTIFIER_OPTION_REGEX, self.value):
                errors.append('Invalid value "%s" for option "%s" in question "%s"' % (self.value, self.text, self.question.title))
        return errors

class Rule(models.Model):
    rule_type = models.ForeignKey(RuleType)
    is_sufficient = models.BooleanField(default=True)
    subject_question = models.ForeignKey(Question, related_name='subject_of_rules', db_index=True)
    subject_options = models.ManyToManyField(Option, related_name='subject_of_rules', limit_choices_to = {'question': subject_question})
    object_question = models.ForeignKey(Question, related_name='object_of_rules', blank=True, null=True)
    object_options = models.ManyToManyField(Option, related_name='object_of_rules', limit_choices_to = {'question': object_question})

    _use_cache = False
    _cache_subject_options = None
    _cache_object_options = None

    def js_class(self):
        return self.rule_type.js_class

    def __unicode__(self):
        return 'Rule #%d' % (self.id)

    def get_subject_options(self):
        if not self._use_cache:
            return self.subject_options.all()
        if self._cache_subject_options is None:
            self._cache_subject_options = list(self.subject_options.all())
        return self._cache_subject_options

    def get_object_options(self):
        if not self._use_cache:
            return self.object_options.all()
        if self._cache_object_options is None:
            self._cache_object_options = list(self.object_options.all())
        return self._cache_object_options


# I18n models

class TranslationSurvey(models.Model):
    survey = models.ForeignKey(Survey, db_index=True)
    language = models.CharField(max_length=3, db_index=True)
    title = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=255, default='DRAFT', choices=SURVEY_TRANSLATION_STATUS_CHOICES)

    # Default
    _use_cache = False

    class Meta:
        verbose_name = 'Translation'
        ordering = ['survey', 'language']
        unique_together = ('survey', 'language')

    @models.permalink
    def get_absolute_url(self):
        return ('pollster_survey_translation_edit', [str(self.survey.id), self.language])

    def __unicode__(self):
        return "TranslationSurvey(%s) for %s" % (self.language, self.survey)

    def as_form(self, data=None):
        class TranslationSurveyForm(ModelForm):
            class Meta:
                model = TranslationSurvey
                fields = ['title', 'status']
        return TranslationSurveyForm(data, instance=self, prefix="survey")

    def prefetch_tranlations(self):
        self._use_cache = True
        self.prefetch_questions()
        self.prefetch_options()

    def prefetch_questions(self):
        qq = list(self.translationquestion_set.all())
        self._cache_questions = dict([(q.question_id, q) for q in qq])

    def prefetch_options(self):
        qq = list(self.translationoption_set.all())
        self._cache_options = dict([(q.option_id, q) for q in qq])

    def translate_option(self, option):
        if self._use_cache:
           r = self._cache_options.get(option.id)
           if r is None:
               return TranslationOption(translation = self, option=option)
           r.option = option
           return r
        else:
            r = self.translationoption_set.all().filter(option=option)
            default = TranslationOption(translation = self, option=option)
            return _get_or_default(r, default)

    def translate_question(self, question):
        if self._use_cache:
            r = self._cache_questions.get(question.id)
            if r is None:
                return TranslationQuestion(translation = self, question=question)
            r.question = question
            return r
        else:
            r = self.translationquestion_set.all().filter(question=question)
            default = TranslationQuestion(translation = self, question=question)
            return _get_or_default(r, default)

class TranslationQuestion(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True)
    question = models.ForeignKey(Question, db_index=True)
    title = models.CharField(max_length=SURVEY_QUESTION_TITLE_SIZE, blank=True, default='')
    description = models.TextField(blank=True, default='')
    error_message = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['translation', 'question']
        unique_together = ('translation', 'question')

    def __unicode__(self):
        return "TranslationQuestion(%s) for %s" % (self.translation.language, self.question)

    def as_form(self, data=None):
        class TranslationQuestionForm(ModelForm):
            class Meta:
                model = TranslationQuestion
                fields = ['title', 'description', 'error_message']
        return TranslationQuestionForm(data, instance=self, prefix="question_%s"%(self.id,))

class TranslationQuestionRow(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True)
    row = models.ForeignKey(QuestionRow, db_index=True)
    title = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['translation', 'row']
        unique_together = ('translation', 'row')

    def __unicode__(self):
        return "TranslationQuestionRow(%s) for %s" % (self.translation.language, self.row)

    def as_form(self, data=None):
        class TranslationRowForm(ModelForm):
            class Meta:
                model = TranslationQuestionRow
                fields = ['title']
        return TranslationRowForm(data, instance=self, prefix="row_%s"%(self.id,))

class TranslationQuestionColumn(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True)
    column = models.ForeignKey(QuestionColumn, db_index=True)
    title = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['translation', 'column']
        unique_together = ('translation', 'column')

    def __unicode__(self):
        return "TranslationQuestionColumn(%s) for %s" % (self.translation.language, self.column)

    def as_form(self, data=None):
        class TranslationColumnForm(ModelForm):
            class Meta:
                model = TranslationQuestionColumn
                fields = ['title']
        return TranslationColumnForm(data, instance=self, prefix="column_%s"%(self.id,))

class TranslationOption(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True)
    option = models.ForeignKey(Option, db_index=True)
    text = models.CharField(max_length=4095, blank=True, default='')
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['translation', 'option']
        unique_together = ('translation', 'option')

    def __unicode__(self):
        return "TranslationOption(%s) for %s" % (self.translation.language, self.option)

    def as_form(self, data=None):
        class TranslationOptionForm(ModelForm):
            class Meta:
                model = TranslationOption
                fields = ['text', 'description']
        return TranslationOptionForm(data, instance=self, prefix="option_%s"%(self.id,))

class ChartType(models.Model):
    shortname = models.SlugField(max_length=255, unique=True)
    description = models.CharField(max_length=255)

    def __unicode__(self):
        return self.description or self.shortname

class Chart(models.Model):
    survey = models.ForeignKey(Survey, db_index=True)
    type = models.ForeignKey(ChartType, db_index=True)
    shortname = models.SlugField(max_length=255)
    chartwrapper = models.TextField(blank=True, default='')
    sqlsource = models.TextField(blank=True, default='', verbose_name="SQL Source Query")
    sqlfilter = models.CharField(max_length=255, default='NONE', choices=CHART_SQLFILTER_CHOICES, verbose_name="Results Filter")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default='DRAFT', choices=CHART_STATUS_CHOICES)
    geotable = models.CharField(max_length=255, default='pollster_zip_codes', choices=settings.GEOMETRY_TABLES)
    hastitle = models.BooleanField(default=False)
    template = models.TextField(blank=True, default='')
    realtime = models.BooleanField(default=False)

    class Meta:
        ordering = ['survey', 'shortname']
        unique_together = ('survey', 'shortname')

    def __unicode__(self):
        return "Chart %s for %s" % (self.shortname, self.survey)

    @models.permalink
    def get_absolute_url(self):
        return ('pollster_survey_chart_edit', [str(self.survey.id), self.shortname])

    @property
    def is_draft(self):
        return self.status == 'DRAFT'

    @property
    def is_published(self):
        return self.status == 'PUBLISHED'

    @property
    def is_template(self):
        return self.type.shortname == 'template'

    @property
    def has_template(self):
        return self.template and True or False

    @property
    def has_data(self):
        if not self.sqlsource:
            return False
        else:
            return True

    def to_json(self, user_id, global_id):
        data = {}
        if self.type.shortname == "google-charts":
            data[ "chartType"] = "Table"
            if self.chartwrapper:
                data = json.loads(self.chartwrapper)
            descriptions, cells = self.load_data(user_id, global_id)
            cols = [{"id": desc[0], "label": desc[0], "type": "number"} for desc in descriptions]
            rows = [{"c": [{"v": v} for v in c]} for c in cells]
            data["dataTable"] = { "cols": cols, "rows": rows }

        elif self.type.shortname[:10] == "google-map":
            if self.chartwrapper:
                data["bounds"] = json.loads(self.chartwrapper)
            try:
                shortname = settings.POLLSTER_USER_PROFILE_SURVEY
                survey = Survey.objects.get(shortname=shortname, status='PUBLISHED')
                lpd = survey.get_last_participation_data(user_id, global_id)
                if lpd and hasattr(settings, 'POLLSTER_USER_ZIP_CODE_DATA_NAME'):
                    zip_code = lpd.get(settings.POLLSTER_USER_ZIP_CODE_DATA_NAME)
                    if zip_code is not None:
                        zip_code = str(zip_code).upper()
                    country = None
                    if hasattr(settings, 'POLLSTER_USER_COUNTRY_DATA_NAME'):
                        country = lpd.get(settings.POLLSTER_USER_COUNTRY_DATA_NAME)
                        if country is not None:
                            country = str(country).upper()
                    data["center"] = self.load_zip_coords(zip_code, country)
            except:
                pass

        return json.dumps(data)

    def get_map_click(self, lat, lng):
        result = {}
        skip_cols = ("ogc_fid", "color", "geometry")
        description, data = self.load_info(lat, lng)
        if data and len(data) > 0:
            for i in range(len(data[0])):
                if description[i][0] not in skip_cols:
                    result[description[i][0]] = str(data[0][i])
        return json.dumps(result)

    def get_map_tile(self, user_id, global_id, z, x, y):
        filename = self.get_map_tile_filename(z, x, y)
        if self.sqlfilter == "USER" and user_id:
            filename = filename + "_user_" + str(user_id)
        elif self.sqlfilter == "PERSON" and global_id:
            filename = filename + "_gid_" + global_id
        if not os.path.exists(filename):
            self.generate_map_tile(self.generate_mapnik_map(user_id, global_id), filename, z, x, y)
        return open(filename).read()

    def generate_map_tile(self, m, filename, z, x, y):
        # Code taken from OSM generate_tiles.py
        proj = GoogleProjection()
        mprj = mapnik.Projection(m.srs)

        p0 = (x * 256, (y + 1) * 256)
        p1 = ((x + 1) * 256, y * 256)
        l0 = proj.fromPixelToLL(p0, z);
        l1 = proj.fromPixelToLL(p1, z);
        c0 = mprj.forward(mapnik.Coord(l0[0], l0[1]))
        c1 = mprj.forward(mapnik.Coord(l1[0], l1[1]))

        if hasattr(mapnik,'mapnik_version') and mapnik.mapnik_version() >= 800:
            bbox = mapnik.Box2d(c0.x, c0.y, c1.x, c1.y)
        else:
            bbox = mapnik.Envelope(c0.x, c0.y, c1.x, c1.y)

        m.resize(256, 256)
        m.zoom_to_box(bbox)

        im = mapnik.Image(256, 256)
        mapnik.render(m, im)
        # See https://github.com/mapnik/mapnik/wiki/OutputFormats for output
        # formats and special parameters. The default here is 32 bit PNG with 8
        # bit per component and alpha channel.
        if mapnik_version == 2:
            im.save(str(filename), "png32")
        else:
            im.save(str(filename), "png")

    def generate_mapnik_map(self, user_id, global_id):
        m = mapnik.Map(256, 256)

        style = self.generate_mapnik_style(user_id, global_id)

        m.background = mapnik.Color("transparent")
        m.append_style("ZIP_CODES STYLE", style)
        m.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over"

        layer = mapnik.Layer('ZIP_CODES')
        layer.datasource = self.create_mapnik_datasource(user_id, global_id)
        layer.styles.append("ZIP_CODES STYLE")
        m.layers.append(layer)

        return m

    def generate_mapnik_style(self, user_id, global_id):
        style = mapnik.Style()
        for color in self.load_colors(user_id, global_id):
            # If the color can't be parsed, use red.
            try:
                c = mapnik.Color(str(color))
            except:
                c = mapnik.Color('#ff0000')
            line = mapnik.LineSymbolizer(c, 1.5)
            line.stroke.opacity = 0.7
            poly = mapnik.PolygonSymbolizer(c)
            poly.fill_opacity = 0.5
            rule = mapnik.Rule()
            rule.filter = mapnik.Filter(str("[color] = '%s'" % (color,)))
            rule.symbols.extend([poly,line])
            style.rules.append(rule)
        return style

    def create_mapnik_datasource(self, user_id, global_id):
        # First create the SQL query that is a join between pollster_zip_codes and
        # the chart query as created by the user; then create an appropriate datasource.

        if global_id and re.findall('[^0-9A-Za-z-]', global_id):
            raise Exception("invalid global_id "+global_id)

        table = """SELECT * FROM %s""" % (self.get_view_name(),)
        if self.sqlfilter == 'USER' :
            table += """ WHERE "user" = %d""" % (user_id,)
        elif self.sqlfilter == 'PERSON':
            table += """ WHERE "user" = %d AND global_id = '%s'""" % (user_id, global_id)
        table = "(" + table + ") AS ZIP_CODES"

        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
            filename = settings.DATABASES["default"]["NAME"]
            return mapnik.SQLite(file=filename, wkb_format="spatialite",
                geometry_field="geometry", estimate_extent=False, table=table)

        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
            name = settings.DATABASES["default"]["NAME"]
            host = settings.DATABASES["default"]["HOST"]
            port = settings.DATABASES["default"]["PORT"]
            username = settings.DATABASES["default"]["USER"]
            password = settings.DATABASES["default"]["PASSWORD"]
            return mapnik.PostGIS(host=host, port=port, user=username, password=password, dbname=name,
                geometry_field="geometry", estimate_extent=False, table=table, srid=4326)

    def get_map_tile_base(self):
        return "%s/_pollster_tile_cache/survey_%s/%s" % (settings.POLLSTER_CACHE_PATH, self.survey.id, self.shortname)

    def get_map_tile_filename(self, z, x, y):
        filename = "%s/%s/%s_%s" % (self.get_map_tile_base(), z, x, y)
        pathname = os.path.dirname(filename)
        if not os.path.exists(pathname):
            try:
                os.makedirs(pathname)
            except OSError:
                # Another thread created the directory in the meantime: just go on.
                pass
        return filename

    def clear_map_tile_cache(self):
        try:
            shutil.rmtree(self.get_map_tile_base())
        except:
            pass

    def get_table_name(self):
        return 'pollster_charts_'+str(self.survey.shortname)+'_'+str(self.shortname)

    def get_view_name(self):
        return self.get_table_name() + "_view"

    def update_table(self, verbose=False):
        table_query = self.sqlsource
        geo_table = self.geotable
        if table_query:
            table = self.get_table_name()
            view = self.get_view_name()

            if re.search(r'\bzip_code_country\b', table_query):
                view_query = """SELECT A.*, B.id AS OGC_FID, B.geometry
                                  FROM %s B, (SELECT * FROM %s) A
                                 WHERE upper(A.zip_code_key) = upper(B.zip_code_key)
                                   AND upper(A.zip_code_country) = upper(B.country)""" % (geo_table, table,)
            else:
                view_query = """SELECT A.*, B.id AS OGC_FID, B.geometry
                                  FROM %s B, (SELECT * FROM %s) A
                                 WHERE upper(A.zip_code_key) = upper(B.zip_code_key)""" % (geo_table, table,)
            cursor = connection.cursor()
            if verbose:
                print "droping  view %s" % (view,)
            cursor.execute("DROP VIEW IF EXISTS %s" % (view,))
            if verbose:
                print "droping  table %s" % (table,)
            cursor.execute("DROP TABLE IF EXISTS %s" % (table,))
            if not self.realtime:
                if verbose:
                    print "creating  table %s" % (table,)
                cursor.execute("CREATE TABLE %s AS %s" % (table, table_query))
                if self.type.shortname[:10] == "google-map":
                    if verbose:
                        print "creating  view %s" % (view, )
                    cursor.execute("CREATE VIEW %s AS %s" % (view, view_query))
                transaction.commit_unless_managed()
                if verbose:
                    print "clearing tile cache..."
                self.clear_map_tile_cache()
            return True
        return False

    def update_data(self):
        table_query = self.sqlsource
        if table_query and not self.realtime:
            table = self.get_table_name()
            cursor = connection.cursor()
            cursor.execute("DELETE FROM %s" % (table,))
            cursor.execute("INSERT INTO %s %s" % (table, table_query))
            transaction.commit_unless_managed()
            self.clear_map_tile_cache()
            return True
        return False

    def load_data(self, user_id, global_id):
        if not self.sqlsource:
            return ((('Error',),), (("SQL query is missing",),))
        if self.realtime:
            query = "SELECT * FROM (%s) A" % (self.sqlsource,)
        else:
            query = "SELECT * FROM %s" % (self.get_table_name(),)
        if self.sqlfilter == 'USER' :
            query += """ WHERE "user" = %(user_id)s"""
        elif self.sqlfilter == 'PERSON':
            query += """ WHERE "user" = %(user_id)s AND global_id = %(global_id)s"""
        params = { 'user_id': user_id, 'global_id': global_id }
        query = convert_query_paramstyle(connection, query, params)
        try:
            sid = transaction.savepoint()
            cursor = connection.cursor()
            cursor.execute(query, params)
            transaction.savepoint_commit(sid)
            return (cursor.description, cursor.fetchall())
        except DatabaseError, e:
            transaction.savepoint_rollback(sid)
            return ((('Error',),), ((str(e),),))

    def load_colors(self, user_id, global_id):
        if not self.sqlsource:
            return ((('Error',),), (("SQL query is missing",),))
        if self.realtime:
            query = "SELECT DISTINCT color FROM (%s) A" % (self.sqlsource,)
        else:
            query = "SELECT DISTINCT color FROM %s" % (self.get_table_name(),)
        if self.sqlfilter == 'USER' :
            query += """ WHERE "user" = %(user_id)s"""
        elif self.sqlfilter == 'PERSON':
            query += """ WHERE "user" = %(user_id)s AND global_id = %(global_id)s"""
        params = { 'user_id': user_id, 'global_id': global_id }
        query = convert_query_paramstyle(connection, query, params)
        try:
            sid = transaction.savepoint()
            cursor = connection.cursor()
            cursor.execute(query, params)
            transaction.savepoint_commit(sid)
            return [x[0] for x in cursor.fetchall()]
        except DatabaseError, e:
            transaction.savepoint_rollback(sid)
            # If the SQL query is wrong we just return 'red'. We don't try to pop
            # up a warning because this probably is an async Javascript call: the
            # query error should be shown by the map editor.
            return ['#ff0000']

    def load_info(self, lat, lng):
        view = self.get_view_name()
        if(self.hastitle):
            geotable = self.geotable
            query = "SELECT v.*, g.title as zip_title FROM %s as v left join %s g ON v.zip_code_key=g.zip_code_key WHERE ST_Contains(v.geometry, 'SRID=4326;POINT(%%s %%s)')" % (view,geotable,)
        else:
            query = "SELECT * FROM %s WHERE ST_Contains(geometry, 'SRID=4326;POINT(%%s %%s)')" % (view,)
        try:
            cursor = connection.cursor()
            cursor.execute(query, (lng, lat))
            return (cursor.description, cursor.fetchall())
        except DatabaseError, e:
            return (None, [])

    def load_zip_coords(self, zip_code_key, zip_code_country=None):
        geo_table = self.geotable
        if zip_code_country:
            query = """SELECT ST_Y(ST_Centroid(geometry)) AS lat, ST_X(ST_Centroid(geometry)) AS lng
                         FROM """ + geo_table + """ WHERE zip_code_key = %s AND country = %s"""
            args = (zip_code_key, zip_code_country)

        else:
            query = """SELECT ST_Y(ST_Centroid(geometry)) AS lat, ST_X(ST_Centroid(geometry)) AS lng
                         FROM """ + geo_table + """ WHERE zip_code_key = %s"""
            args = (zip_code_key,)
        try:
            cursor = connection.cursor()
            cursor.execute(query, args)
            data = cursor.fetchall()
            if len(data) > 0:
                return {"lat": data[0][0], "lng": data[0][1]}
            else:
                return {}
        except DatabaseError, e:
            return {}

    def get_template(self):
        return Template(self.template or "{% for row in rows %}{{ row }}<br/>{% endfor %}")

    def render(self, context):
        """Adds data to context and use it to render template."""
        template = self.get_template()
        if self.type.shortname == "template":
            if template:
                user_id = context["user_id"]
                global_id = context["global_id"]
                descriptions, cells = self.load_data(user_id, global_id)
                cols = [desc[0] for desc in descriptions]
                rows = [dict(zip(cols, cell)) for cell in cells]
                context.update({"cols": cols, "rows": rows})
                result = template.render(context)
                context.pop()
            return result
        else:
            if self.has_template:
                return template.render(context)

class GoogleProjection:
    def __init__(self, levels=25):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = 256
        for d in range(0,levels):
            e = c/2;
            self.Bc.append(c/360.0)
            self.Cc.append(c/(2 * pi))
            self.zc.append((e,e))
            self.Ac.append(c)
            c *= 2

    def fromLLtoPixel(self,ll,zoom):
         d = self.zc[zoom]
         e = round(d[0] + ll[0] * self.Bc[zoom])
         f = min(max(sin(DEG_TO_RAD * ll[1]),-0.9999),0.9999)
         g = round(d[1] + 0.5*log((1+f)/(1-f))*-self.Cc[zoom])
         return (e,g)

    def fromPixelToLL(self,px,zoom):
         e = self.zc[zoom]
         f = (px[0] - e[0])/self.Bc[zoom]
         g = (px[1] - e[1])/-self.Cc[zoom]
         h = RAD_TO_DEG * ( 2 * atan(exp(g)) - 0.5 * pi)
         return (f,h)

class SurveyChartPlugin(CMSPlugin):
    chart = models.ForeignKey(Chart)
    show_on_success = models.BooleanField(default=False, verbose_name="Show on submit", help_text="Show this chart only on successful submit of its survey.")

class SurveyPlugin(CMSPlugin):
    survey = models.ForeignKey(Survey, limit_choices_to={"status":"PUBLISHED"}, verbose_name="Survey")
    redirect_path = models.CharField(max_length=4096, blank=True, default='', verbose_name="Redirect to path")
    success_template = models.TextField(blank=True, default='', verbose_name="Success template")

    def get_template(self):
        return Template(self.success_template)

    def render(self, context):
        return self.get_template().render(context)

