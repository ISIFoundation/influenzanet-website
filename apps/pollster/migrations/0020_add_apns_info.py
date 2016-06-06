# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'NotifyToken.is_apns_invalid'
        db.add_column('pollster_notifytoken', 'is_apns_invalid',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'NotifyToken.last_apns_message_id'
        db.add_column('pollster_notifytoken', 'last_apns_message_id',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'NotifyToken.last_apns_failure'
        db.add_column('pollster_notifytoken', 'last_apns_failure',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'NotifyToken.last_apns_message_timestamp'
        db.add_column('pollster_notifytoken', 'last_apns_message_timestamp',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'NotifyToken.is_apns_invalid'
        db.delete_column('pollster_notifytoken', 'is_apns_invalid')

        # Deleting field 'NotifyToken.last_apns_message_id'
        db.delete_column('pollster_notifytoken', 'last_apns_message_id')

        # Deleting field 'NotifyToken.last_apns_failure'
        db.delete_column('pollster_notifytoken', 'last_apns_failure')

        # Deleting field 'NotifyToken.last_apns_message_timestamp'
        db.delete_column('pollster_notifytoken', 'last_apns_message_timestamp')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'pollster.chart': {
            'Meta': {'ordering': "['survey', 'shortname']", 'unique_together': "(('survey', 'shortname'),)", 'object_name': 'Chart'},
            'chartwrapper': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'geotable': ('django.db.models.fields.CharField', [], {'default': "'pollster_zip_codes'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'realtime': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'shortname': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'sqlfilter': ('django.db.models.fields.CharField', [], {'default': "'NONE'", 'max_length': '255'}),
            'sqlsource': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'DRAFT'", 'max_length': '255'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']"}),
            'template': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.ChartType']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'pollster.charttype': {
            'Meta': {'object_name': 'ChartType'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shortname': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'})
        },
        'pollster.notifytoken': {
            'Meta': {'object_name': 'NotifyToken'},
            'atoken': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_apns_invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_gcm_invalid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'itoken': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'last_apns_failure': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'last_apns_message_id': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'last_apns_message_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_gcm_failure': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'last_gcm_message_id': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'last_gcm_message_timestamp': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'pollster.option': {
            'Meta': {'ordering': "['question', 'ordinal']", 'object_name': 'Option'},
            'clone': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Option']", 'null': 'True', 'blank': 'True'}),
            'column': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionColumn']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_virtual': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Question']"}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionRow']", 'null': 'True', 'blank': 'True'}),
            'starts_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4095', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'virtual_inf': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'virtual_regex': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'virtual_sup': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'virtual_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.VirtualOptionType']", 'null': 'True', 'blank': 'True'})
        },
        'pollster.question': {
            'Meta': {'ordering': "['survey', 'ordinal']", 'object_name': 'Question'},
            'data_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionDataType']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'error_message': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_mandatory': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'open_option_data_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'questions_with_open_option'", 'null': 'True', 'to': "orm['pollster.QuestionDataType']"}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'regex': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1023', 'blank': 'True'}),
            'starts_hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']"}),
            'tags': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'visual': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.questioncolumn': {
            'Meta': {'ordering': "['question', 'ordinal']", 'object_name': 'QuestionColumn'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'column_set'", 'to': "orm['pollster.Question']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.questiondatatype': {
            'Meta': {'object_name': 'QuestionDataType'},
            'css_class': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'db_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'js_class': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.questionrow': {
            'Meta': {'ordering': "['question', 'ordinal']", 'object_name': 'QuestionRow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordinal': ('django.db.models.fields.IntegerField', [], {}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'row_set'", 'to': "orm['pollster.Question']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.rule': {
            'Meta': {'object_name': 'Rule'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_sufficient': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'object_options': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'object_of_rules'", 'symmetrical': 'False', 'to': "orm['pollster.Option']"}),
            'object_question': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'object_of_rules'", 'null': 'True', 'to': "orm['pollster.Question']"}),
            'rule_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.RuleType']"}),
            'subject_options': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'subject_of_rules'", 'symmetrical': 'False', 'to': "orm['pollster.Option']"}),
            'subject_question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subject_of_rules'", 'to': "orm['pollster.Question']"})
        },
        'pollster.ruletype': {
            'Meta': {'object_name': 'RuleType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'js_class': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.survey': {
            'Meta': {'object_name': 'Survey'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']", 'null': 'True', 'blank': 'True'}),
            'prefill_method': ('django.db.models.fields.CharField', [], {'default': "'LAST'", 'max_length': '255', 'blank': 'True'}),
            'shortname': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '255'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'DRAFT'", 'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.SlugField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.surveychartplugin': {
            'Meta': {'object_name': 'SurveyChartPlugin', 'db_table': "'cmsplugin_surveychartplugin'", '_ormbases': ['cms.CMSPlugin']},
            'chart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Chart']"}),
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'show_on_success': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'pollster.surveyplugin': {
            'Meta': {'object_name': 'SurveyPlugin', 'db_table': "'cmsplugin_surveyplugin'", '_ormbases': ['cms.CMSPlugin']},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'redirect_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4096', 'blank': 'True'}),
            'success_template': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']"})
        },
        'pollster.translationoption': {
            'Meta': {'ordering': "['translation', 'option']", 'unique_together': "(('translation', 'option'),)", 'object_name': 'TranslationOption'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'option': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Option']"}),
            'text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '4095', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationquestion': {
            'Meta': {'ordering': "['translation', 'question']", 'unique_together': "(('translation', 'question'),)", 'object_name': 'TranslationQuestion'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'error_message': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Question']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationquestioncolumn': {
            'Meta': {'ordering': "['translation', 'column']", 'unique_together': "(('translation', 'column'),)", 'object_name': 'TranslationQuestionColumn'},
            'column': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionColumn']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationquestionrow': {
            'Meta': {'ordering': "['translation', 'row']", 'unique_together': "(('translation', 'row'),)", 'object_name': 'TranslationQuestionRow'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionRow']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'translation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.TranslationSurvey']"})
        },
        'pollster.translationsurvey': {
            'Meta': {'ordering': "['survey', 'language']", 'unique_together': "(('survey', 'language'),)", 'object_name': 'TranslationSurvey'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'DRAFT'", 'max_length': '255'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.Survey']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'pollster.virtualoptiontype': {
            'Meta': {'object_name': 'VirtualOptionType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'js_class': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'question_data_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pollster.QuestionDataType']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['pollster']