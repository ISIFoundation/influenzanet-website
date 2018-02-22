# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'AnonymizeRequest.user'
        db.alter_column('sw_auth_anonymizerequest', 'user_id', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sw_auth.EpiworkUser'], unique=True))

        # Adding unique constraint on 'AnonymizeRequest', fields ['user']
        db.create_unique('sw_auth_anonymizerequest', ['user_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'AnonymizeRequest', fields ['user']
        db.delete_unique('sw_auth_anonymizerequest', ['user_id'])

        # Changing field 'AnonymizeRequest.user'
        db.alter_column('sw_auth_anonymizerequest', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sw_auth.EpiworkUser']))


    models = {
        'sw_auth.anonymizelog': {
            'Meta': {'object_name': 'AnonymizeLog'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sw_auth.EpiworkUser']"})
        },
        'sw_auth.anonymizerequest': {
            'Meta': {'object_name': 'AnonymizeRequest'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sw_auth.EpiworkUser']", 'unique': 'True'})
        },
        'sw_auth.epiworkuser': {
            'Meta': {'object_name': 'EpiworkUser'},
            'anonymize_warn': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'email_proposal': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'email_state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'login': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'token_activate': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'token_email': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True'}),
            'token_password': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'user': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'sw_auth.logintoken': {
            'Meta': {'object_name': 'LoginToken'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'next': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True'}),
            'usage_left': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sw_auth.EpiworkUser']"})
        }
    }

    complete_apps = ['sw_auth']
