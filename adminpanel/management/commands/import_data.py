from email import parser
import os
import csv
from collections import Counter


from django.core.management.base import BaseCommand
from SmartWaterTank.settings import BASE_DIR
from adminpanel.models import Building, Tank, Sensor, Reading, UserProfile
from django.conf import settings
from datetime import datetime  # update this


class Command(BaseCommand):
    help = 'Import data from CSV files into models'

    def handle(self, *args, **kwargs):
        base_dir = os.path.join(settings.BASE_DIR, 'static', 'csv files')
        self.stdout.write(f"Looking for CSV files in: {base_dir}")

        # Import buildings.csv
        try:
            
            with open(os.path.join(base_dir, 'buildings.csv'), newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        Building.objects.update_or_create(
                        building_id=row['building_id'],
                        defaults={
                            'building_name': row['building_name'],
                            'building_created_date': datetime.strptime(row['building_created_date'].strip(), "%m-%d-%Y").date() if '-' in row['building_created_date'] else datetime.strptime(row['building_created_date'].strip(), "%m/%d/%Y").date(),

                            'last_modified_date': datetime.strptime(row['last_modified_date'].strip(), "%m-%d-%Y %H:%M").replace(second=0) if '-' in row['last_modified_date'] else datetime.strptime(row['last_modified_date'].strip(), "%m/%d/%Y %H:%M").replace(second=0),

                        }
                    )
                    except Exception as e:
                         print(f"[ERROR] Row failed: {row} — {e}")
                self.stdout.write(self.style.SUCCESS('✅ Imported buildings.csv'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error importing buildings: {e}"))

        # Import tanks.csv (FIXED)
        from dateutil import parser  # <== Make sure to install this: pip install python-dateutil

# Import tanks.csv (FINAL VERSION)
        try:
            with open(os.path.join(base_dir, 'tanks.csv'), newline='') as csvfile:
              reader = csv.DictReader(csvfile)
              for row in reader:
                    try:
                        print(f"[DEBUG] Tank row: {row}")
                        print(f"[DEBUG] Trying to fetch user_id={row['user_id']} and building_id={row['building_id']}")

                        building = Building.objects.get(building_id=row['building_id'].strip())
                        user = UserProfile.objects.get(user_id=row['user_id'].strip())
                        created_date = parser.parse(row['tank_created_date'].strip())
                        modified_date = parser.parse(row['tank_last_modified_date'].strip())

                        Tank.objects.update_or_create(
                        tank_id=row['tank_id'].strip(),
                        defaults={
                        'user': user,
                        'building': building,
                        'capacity': float(row['capacity']),
                        'tank_created_date': created_date,
                        'tank_last_modified_date': modified_date,
                    }
                )
                    except Building.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"❌ Building '{row['building_id']}' not found for tank '{row['tank_id']}'"))
                    except UserProfile.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"❌ User '{row['user_id']}' not found for tank '{row['tank_id']}'"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Failed to import tank '{row}': {e}"))
            self.stdout.write(self.style.SUCCESS('✅ Imported tanks.csv'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error importing tanks.csv: {e}"))


        # Import sensors.csv
        try:
            with open(os.path.join(base_dir, 'sensors.csv'), newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        tank = Tank.objects.get(tank_id=row['tank_id'])
                        date_time = parser.parse(row['date_time'].strip())
                        modified_date = parser.parse(row['sensor_last_modified_date'].strip())

                        Sensor.objects.update_or_create(
                            sensor_id=row['sensor_id'],
                            defaults={
                                'tank': tank,
                                'date_time': date_time,
                                'sensor_last_modified_date': modified_date,
                            }
                        )
                    except Tank.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"❌ Tank '{row['tank_id']}' not found for sensor '{row['sensor_id']}'"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Failed to import sensor '{row}': {e}"))

            self.stdout.write(self.style.SUCCESS('✅ Imported sensors.csv'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error importing sensors.csv: {e}"))


                       # Import readings.csv
        try:
            with open(os.path.join(base_dir, 'readings.csv'), newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        sensor = Sensor.objects.get(sensor_id=row['sensor_id'])
                        modified_date = parser.parse(row['sensor_reading_last_modified_date'].strip())

                        Reading.objects.update_or_create(
                            reading_id=row['reading_id'],
                            defaults={
                                'sensor': sensor,
                                'reading': row['reading'],
                                'sensor_reading_last_modified_date': modified_date,
                            }
                        )
                    except Sensor.DoesNotExist:
                        self.stdout.write(self.style.ERROR(f"❌ Sensor '{row['sensor_id']}' not found for reading '{row['reading_id']}'"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"❌ Failed to import reading '{row}': {e}"))

                self.stdout.write(self.style.SUCCESS('✅ Imported readings.csv'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error importing readings.csv: {e}"))

