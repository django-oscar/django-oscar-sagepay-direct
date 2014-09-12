# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RequestResponse'
        db.create_table(u'oscar_sagepay_requestresponse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reference', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, blank=True)),
            ('protocol', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('tx_type', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('vendor', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('vendor_tx_code', self.gf('django.db.models.fields.CharField')(max_length=128, db_index=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=12, decimal_places=2, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=3, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=512, blank=True)),
            ('raw_request_json', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('request_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('status_detail', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tx_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, blank=True)),
            ('tx_auth_num', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
            ('security_key', self.gf('django.db.models.fields.CharField')(max_length=128, blank=True)),
            ('raw_response', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('response_datetime', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('related_tx_id', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=128, blank=True)),
        ))
        db.send_create_signal(u'oscar_sagepay', ['RequestResponse'])


    def backwards(self, orm):
        # Deleting model 'RequestResponse'
        db.delete_table(u'oscar_sagepay_requestresponse')


    models = {
        u'oscar_sagepay.requestresponse': {
            'Meta': {'ordering': "('-request_datetime',)", 'object_name': 'RequestResponse'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '12', 'decimal_places': '2', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '512', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'protocol': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'raw_request_json': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'raw_response': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'blank': 'True'}),
            'related_tx_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'blank': 'True'}),
            'request_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'response_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'security_key': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tx_auth_num': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'tx_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'blank': 'True'}),
            'tx_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'vendor': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'vendor_tx_code': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'})
        }
    }

    complete_apps = ['oscar_sagepay']