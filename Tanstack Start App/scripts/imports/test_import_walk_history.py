import csv,io,json,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile
from import_walk_history import import_walks
class WalkImportTest(unittest.TestCase):
 def test_selected_fields_no_gps_and_idempotence(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);archive=root/'private.zip';out=root/'walks';table=io.StringIO();writer=csv.writer(table);writer.writerow(['Activity ID','Activity Type','Activity Date','Filename','Distance','Moving Time','Elapsed Time','Description'])
   writer.writerows([['1','Walk','Oct 14, 2026, 1:31:46 PM','activities/walk.gpx','1234.5','600','700','Private notes'],['2','Walk','Oct 15, 2026, 1:31:46 PM','','100','60','90','Private'],['3','Run','Oct 14, 2026, 1:31:46 PM','','1000','300','320','Run']])
   with ZipFile(archive,'w') as z:
    z.writestr('activities.csv',table.getvalue());z.writestr('activities/walk.gpx','<gpx><trk><trkseg><trkpt lat="40" lon="-75.3"><extensions><heartrate>120</heartrate></extensions></trkpt><trkpt lat="40.001" lon="-75.301"/></trkseg></trk></gpx>')
   summary=import_walks(archive,out);assert summary['walkRecords']==2;assert summary['mappedWalks']==1;assert summary['withoutGps']==1
   before={p.name:p.read_bytes() for p in out.iterdir()};import_walks(archive,out);assert before=={p.name:p.read_bytes() for p in out.iterdir()}
   content=''.join(p.read_text() for p in out.iterdir());assert 'Private notes' not in content;assert 'heartrate' not in content
   records=json.loads((out/'activities.json').read_text())['walks'];assert records[0]['distanceMeters']==1234.5;assert records[0]['date']=='2026-10-14T13:31:46Z'
if __name__=='__main__':unittest.main()
