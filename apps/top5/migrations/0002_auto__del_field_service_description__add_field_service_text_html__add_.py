# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Service.description'
        db.delete_column('Service', 'description')

        # Adding field 'Service.text_html'
        db.add_column('Service', 'text_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Adding field 'Service.score'
        db.add_column('Service', 'score', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Deleting field 'PartTemplate.colorfont'
        db.delete_column('PartTemplate', 'colorfont')

        # Deleting field 'PartTemplate.vertical_length'
        db.delete_column('PartTemplate', 'vertical_length')

        # Deleting field 'PartTemplate.color_text'
        db.delete_column('PartTemplate', 'color_text')

        # Adding field 'PartTemplate.order'
        db.add_column('PartTemplate', 'order', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, blank=True), keep_default=False)

        # Adding field 'PartTemplate.title_style'
        db.add_column('PartTemplate', 'title_style', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True), keep_default=False)

        # Adding field 'PartTemplate.width'
        db.add_column('PartTemplate', 'width', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Service.description'
        db.add_column('Service', 'description', self.gf('django.db.models.fields.TextField')(null=True, blank=True), keep_default=False)

        # Deleting field 'Service.text_html'
        db.delete_column('Service', 'text_html')

        # Deleting field 'Service.score'
        db.delete_column('Service', 'score')

        # Adding field 'PartTemplate.colorfont'
        db.add_column('PartTemplate', 'colorfont', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True), keep_default=False)

        # Adding field 'PartTemplate.vertical_length'
        db.add_column('PartTemplate', 'vertical_length', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True), keep_default=False)

        # Adding field 'PartTemplate.color_text'
        db.add_column('PartTemplate', 'color_text', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True), keep_default=False)

        # Deleting field 'PartTemplate.order'
        db.delete_column('PartTemplate', 'order')

        # Deleting field 'PartTemplate.title_style'
        db.delete_column('PartTemplate', 'title_style')

        # Deleting field 'PartTemplate.width'
        db.delete_column('PartTemplate', 'width')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'part_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'title_style': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'width': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'})
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
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['top5']
