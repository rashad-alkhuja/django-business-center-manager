# offices/migrations/0002_populate_offices.py

from django.db import migrations

# This is all your office data converted into a Python list
OFFICE_INITIAL_DATA = [
    {'no': 1, 'sqft': 109.79, 'rent': 71365}, {'no': 2, 'sqft': 92.57, 'rent': 60170},
    {'no': 3, 'sqft': 108.72, 'rent': 70665}, {'no': 4, 'sqft': 88.26, 'rent': 52958},
    {'no': 5, 'sqft': 88.26, 'rent': 52958}, {'no': 6, 'sqft': 88.26, 'rent': 52958},
    {'no': 7, 'sqft': 90.42, 'rent': 54250}, {'no': 8, 'sqft': 64.58, 'rent': 38750},
    {'no': 9, 'sqft': 64.58, 'rent': 38750}, {'no': 10, 'sqft': 64.58, 'rent': 38750},
    {'no': 11, 'sqft': 64.58, 'rent': 38750}, {'no': 12, 'sqft': 90.42, 'rent': 54250},
    {'no': 13, 'sqft': 90.42, 'rent': 54250}, {'no': 14, 'sqft': 166.84, 'rent': 108446},
    {'no': 15, 'sqft': 131.32, 'rent': 78792}, {'no': 16, 'sqft': 114.10, 'rent': 70740},
    {'no': 17, 'sqft': 206.67, 'rent': 134333}, {'no': 18, 'sqft': 55.97, 'rent': 33583},
    {'no': 19, 'sqft': 55.97, 'rent': 33583}, {'no': 20, 'sqft': 222.81, 'rent': 138142},
    {'no': 21, 'sqft': 217.43, 'rent': 141330}, {'no': 22, 'sqft': 60.28, 'rent': 36167},
    {'no': 23, 'sqft': 60.28, 'rent': 36167}, {'no': 24, 'sqft': 53.82, 'rent': 32292},
    {'no': 25, 'sqft': 53.82, 'rent': 32292}, {'no': 26, 'sqft': 67.81, 'rent': 44078},
    {'no': 27, 'sqft': 63.51, 'rent': 38104}, {'no': 28, 'sqft': 66.74, 'rent': 43379},
    {'no': 29, 'sqft': 63.51, 'rent': 38104}, {'no': 30, 'sqft': 64.58, 'rent': 38750},
    {'no': 31, 'sqft': 68.89, 'rent': 41333}, {'no': 32, 'sqft': 68.89, 'rent': 41333},
    {'no': 33, 'sqft': 67.81, 'rent': 40688}, {'no': 34, 'sqft': 55.97, 'rent': 33583},
    {'no': 35, 'sqft': 60.28, 'rent': 36167}, {'no': 36, 'sqft': 71.04, 'rent': 42625},
    {'no': 37, 'sqft': 64.58, 'rent': 38750}, {'no': 38, 'sqft': 71.04, 'rent': 42625},
    {'no': 39, 'sqft': 64.58, 'rent': 38750}, {'no': 41, 'sqft': 64.58, 'rent': 38750},
    {'no': 44, 'sqft': 59.20, 'rent': 36705}, {'no': 46, 'sqft': 100.10, 'rent': 62065},
    {'no': 47, 'sqft': 68.89, 'rent': 41333}, {'no': 48, 'sqft': 65.66, 'rent': 40709},
    {'no': 49, 'sqft': 69.97, 'rent': 41979}, {'no': 50, 'sqft': 67.81, 'rent': 40688},
    {'no': 51, 'sqft': 65.66, 'rent': 40709}, {'no': 52, 'sqft': 68.89, 'rent': 41333},
    {'no': 53, 'sqft': 64.58, 'rent': 40042}, {'no': 54, 'sqft': 68.89, 'rent': 41333},
    {'no': 55, 'sqft': 65.66, 'rent': 40709}, {'no': 56, 'sqft': 107.64, 'rent': 69965},
    {'no': 57, 'sqft': 66.74, 'rent': 43379}, {'no': 58, 'sqft': 64.58, 'rent': 41979},
    {'no': 61, 'sqft': 64.58, 'rent': 38750}, {'no': 62, 'sqft': 59.20, 'rent': 35521},
    {'no': 63, 'sqft': 134.55, 'rent': 83420}, {'no': 64, 'sqft': 59.20, 'rent': 35521},
    {'no': 67, 'sqft': 64.58, 'rent': 40042}, {'no': 68, 'sqft': 64.58, 'rent': 40042},
    {'no': 69, 'sqft': 78.58, 'rent': 48717}
]

# This is the function that will be executed when we run the migration
def populate_offices(apps, schema_editor):
    # We get the 'Office' model for this migration
    Office = apps.get_model('offices', 'Office')

    # We loop through our data list
    for item in OFFICE_INITIAL_DATA:
        # For each item, we create a new Office object in the database
        Office.objects.create(
            office_number=item['no'],
            size_sqft=item['sqft'],
            annual_rent=item['rent']
            # We don't need to set the status, it will use the 'available' default
        )

# This function would be used if we ever wanted to UN-do the migration
def delete_offices(apps, schema_editor):
    Office = apps.get_model('offices', 'Office')
    Office.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('offices', '0001_initial'),
    ]

    operations = [
        # This is the key part: we tell the migration to run our Python function
        migrations.RunPython(populate_offices, reverse_code=delete_offices),
    ]