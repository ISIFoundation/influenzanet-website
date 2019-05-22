# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Service'
        db.create_table('Service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('fullname', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('selected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('top5', ['Service'])

        # Adding model 'Ranking'
        db.create_table('RankingService', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('User', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('service_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['top5.Service'])),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('modif_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('temporary_rank', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True)),
            ('elserank', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
        ))
        db.send_create_signal('top5', ['Ranking'])

        # Adding model 'PartTemplate'
        db.create_table('PartTemplate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('part_name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('colorfont', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('color_text', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('vertical_length', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
        ))
        db.send_create_signal('top5', ['PartTemplate'])

        # Adding model 'Part'
        db.create_table('top5_part', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['top5.Service'])),
            ('part_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['top5.PartTemplate'])),
            ('text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('special_style', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
        ))
        db.send_create_signal('top5', ['Part'])


    def backwards(self, orm):
        
        # Deleting model 'Service'
        db.delete_table('Service')

        # Deleting model 'Ranking'
        db.delete_table('RankingService')

        # Deleting model 'PartTemplate'
        db.delete_table('PartTemplate')

        # Deleting model 'Part'
        db.delete_table('top5_part')


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
        'top5.part': {
            'Meta': {'object_name': 'Part'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['top5.PartTemplate']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['top5.Service']"}),
            'special_style': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'top5.parttemplate': {
            'Meta': {'object_name': 'PartTemplate', 'db_table': "'PartTemplate'"},
            'color_text': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'colorfont': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'part_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'vertical_length': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'})
        },
        'top5.ranking': {
            'Meta': {'object_name': 'Ranking', 'db_table': "'RankingService'"},
            'User': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'elserank': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modif_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'service_id': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['top5.Service']"}),
            'temporary_rank': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'})
        },
        'top5.service': {
            'Meta': {'object_name': 'Service', 'db_table': "'Service'"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['top5']
