# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'MaskCohort.notification'
        db.delete_column('grippenet_maskcohort', 'notification')

        # Adding field 'MaskCohort.notification_count'
        db.add_column('grippenet_maskcohort', 'notification_count',
                      self.gf('django.db.models.fields.IntegerField')(default=1),
                      keep_default=False)

        # Adding field 'MaskCohort.last_notification'
        db.add_column('grippenet_maskcohort', 'last_notification',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'MaskCohort.notification'
        db.add_column('grippenet_maskcohort', 'notification',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'MaskCohort.notification_count'
        db.delete_column('grippenet_maskcohort', 'notification_count')

        # Deleting field 'MaskCohort.last_notification'
        db.delete_column('grippenet_maskcohort', 'last_notification')


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'grippenet.immunocohort': {
            'Meta': {'object_name': 'ImmunoCohort'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'change_channel': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'survey_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyUser']", 'unique': 'True', 'primary_key': 'True'})
        },
        'grippenet.maskcohort': {
            'Meta': {'object_name': 'MaskCohort'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'last_notification': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'notification_count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'survey_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyUser']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'grippenet.participation': {
            'Meta': {'object_name': 'Participation'},
            'first_season': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_season': ('django.db.models.fields.IntegerField', [], {}),
            'survey_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyUser']"})
        },
        'grippenet.pregnantcohort': {
            'Meta': {'object_name': 'PregnantCohort'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'change_channel': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_created': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_reminder': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reminder_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'survey_user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['survey.SurveyUser']"})
        },
        'survey.surveyuser': {
            'Meta': {'object_name': 'SurveyUser'},
            'avatar': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'global_id': ('django.db.models.fields.CharField', [], {'default': "'ef57803e-ae70-425c-810c-eafdf873956a'", 'unique': 'True', 'max_length': '36'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_participation_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        }
    }

    complete_apps = ['grippenet']