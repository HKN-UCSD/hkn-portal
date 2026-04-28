"""
Django management command to sync house data from Google Sheets.

This command reads from a Google Sheet with the following structure:
- Sheet 1: Summary with house totals, event names/dates, and points per event
- Sheets 2-6: One per house, with member names and points earned per event

Usage:
    python manage.py sync_house_sheet
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db import models
from django.utils import timezone
from django.conf import settings
from myapp.api.models.houses import House, HousePointRecord, HouseMembership
from myapp.api.models.users import CustomUser, Officer
from myapp.api.models.events import Event
import gspread
from google.oauth2.service_account import Credentials
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Sync house data from Google Sheets to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without updating database',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing house points before syncing',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        clear_points = options.get('clear', False)
        
        # Get credentials and sheet ID from environment
        creds_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH')
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        
        # If credentials path is relative, resolve it relative to Django's BASE_DIR
        if creds_path and not os.path.isabs(creds_path):
            creds_path = os.path.join(settings.BASE_DIR, creds_path)
        
        if not creds_path or not sheet_id:
            self.stdout.write(self.style.ERROR(
                'Missing configuration. Make sure these are set in your .env file:\n'
                '  GOOGLE_SHEETS_CREDENTIALS_PATH=credentials/service-account.json\n'
                '  GOOGLE_SHEET_ID=your_sheet_id_here\n\n'
                'See credentials/README.md for setup instructions.'
            ))
            return

        # Check if credentials file exists
        if not os.path.exists(creds_path):
            self.stdout.write(self.style.ERROR(
                f'Credentials file not found at: {creds_path}\n'
                'See credentials/README.md for setup instructions.'
            ))
            return

        self.stdout.write(self.style.SUCCESS('Connecting to Google Sheets...'))
        
        try:
            # Authenticate with Google Sheets
            scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            credentials = Credentials.from_service_account_file(creds_path, scopes=scopes)
            client = gspread.authorize(credentials)
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(sheet_id)
            
            self.stdout.write(self.style.SUCCESS(f'Connected to: {spreadsheet.title}'))
            self.stdout.write(self.style.SUCCESS(f'Found {len(spreadsheet.worksheets())} sheets\n'))
            
            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved\n'))
            
            # Clear existing points if requested
            if clear_points and not dry_run:
                self.stdout.write(self.style.WARNING('Clearing existing house data...'))
                HousePointRecord.objects.all().delete()
                HouseMembership.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('Cleared\n'))
            
            # Process all sheets
            with transaction.atomic():
                # Read summary sheet (first sheet) to get event dates
                event_dates = self.process_summary_sheet(spreadsheet.worksheets()[0], dry_run)
                
                # Define the 5 house names to look for
                house_names = ['Ohm', 'Ampere', 'Babbage', 'Volta', 'Wheatstone']
                
                # Clean up Assignment house if it exists in database
                if not dry_run:
                    assignment_house = House.objects.filter(name='Assignment').first()
                    if assignment_house:
                        self.stdout.write(self.style.WARNING('Removing "Assignment" from houses...'))
                        assignment_house.delete()
                
                # Read individual house sheets - look for specific house names
                for sheet in spreadsheet.worksheets():
                    # Explicitly skip Assignment sheet
                    if sheet.title.lower() == 'assignment':
                        self.stdout.write(self.style.WARNING(f'\nSkipping sheet: {sheet.title}'))
                        continue
                    
                    if sheet.title in house_names:
                        self.process_house_sheet(sheet, dry_run, event_dates)
                
                if dry_run:
                    self.stdout.write(self.style.WARNING('\nDry run complete - rolling back transaction'))
                    raise Exception("Dry run - rolling back")
                else:
                    self.stdout.write(self.style.SUCCESS('\nSync complete!'))
                    
        except Exception as e:
            if "Dry run" in str(e):
                # Expected exception for dry run
                pass
            else:
                self.stdout.write(self.style.ERROR(f'\nError during sync: {str(e)}'))
                import traceback
                self.stdout.write(self.style.ERROR(traceback.format_exc()))

    def process_summary_sheet(self, worksheet, dry_run):
        """Process the first sheet with house/event summaries and extract event dates"""
        self.stdout.write(self.style.WARNING(f'Processing summary sheet: {worksheet.title}'))
        
        # Get all values
        data = worksheet.get_all_values()
        if not data:
            self.stdout.write(self.style.WARNING('  No data found'))
            return {}
        
        # Display structure for debugging
        self.stdout.write(f'  Rows: {len(data)}, Columns: {len(data[0]) if data else 0}')
        
        # Parse event names (column B) and dates (column A)
        # Skip first 2 rows (headers/totals), then extract event info
        event_dates = {}
        for row_idx, row in enumerate(data[2:], start=3):
            if len(row) < 2:
                continue
            
            date_str = row[0].strip()  # Column A has dates
            event_name = row[1].strip()  # Column B has event names
            
            if not event_name or not date_str:
                continue
            
            # Try to parse the date
            try:
                # Handle date ranges by taking the first date
                if '~' in date_str:
                    date_str = date_str.split('~')[0].strip()
                elif '-' in date_str and '/' in date_str:
                    # Check if it's a date range like "1/13-1/16"
                    parts = date_str.split('-')
                    if len(parts) == 2 and '/' in parts[0]:
                        date_str = parts[0].strip()
                
                # Try common date formats
                from dateutil import parser
                event_date = parser.parse(date_str)
                # Make timezone-aware
                event_date = timezone.make_aware(event_date, timezone.get_current_timezone())
                event_dates[event_name] = event_date
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  Could not parse date "{date_str}" for event "{event_name}"'))
                continue
        
        self.stdout.write(self.style.SUCCESS(f'  Extracted {len(event_dates)} event dates'))
        return event_dates
        
    def process_house_sheet(self, worksheet, dry_run, event_dates=None):
        """Process an individual house sheet with member points"""
        self.stdout.write(self.style.WARNING(f'\nProcessing house sheet: {worksheet.title}'))
        
        if event_dates is None:
            event_dates = {}
        
        # Get all values
        data = worksheet.get_all_values()
        if not data or len(data) < 2:
            self.stdout.write(self.style.WARNING('  No data found'))
            return
        
        # Row 1 has member names (col 0 is empty, col 1 is "Total", col 2+ are members)
        headers = data[0]
        member_names = [name.strip() for name in headers[2:] if name.strip()]
        
        # Row 2 is a totals row - skip it
        # Rows 3+ have events (col 0 is event name, col 1 is total, col 2+ are member points)
        event_rows = data[2:]  # Skip row 1 (totals)
        
        self.stdout.write(f'  Members in sheet: {len(member_names)}')
        self.stdout.write(f'  Member names: {member_names[:5]}...' if len(member_names) > 5 else f'  Member names: {member_names}')
        self.stdout.write(f'  Events: {len(event_rows)}')
        
        # Get or create house
        house_name = worksheet.title
        house, created = House.objects.get_or_create(
            name=house_name,
            defaults={'description': f'{house_name} house', 'color': 'Blue'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'  Created house: {house_name}'))
        else:
            self.stdout.write(f'  Found existing house: {house_name}')
        
        # Clear existing point records and memberships for this house to rewrite from sheet
        if not dry_run:
            deleted_points = HousePointRecord.objects.filter(house=house).count()
            deleted_members = HouseMembership.objects.filter(house=house).count()
            HousePointRecord.objects.filter(house=house).delete()
            HouseMembership.objects.filter(house=house).delete()
            self.stdout.write(self.style.WARNING(
                f'  Cleared {deleted_members} existing members and {deleted_points} point records'
            ))
        
        # Process members and their points
        members_added = 0
        points_added = 0
        duplicates_found = []
        not_found = []
        
        for idx, member_name in enumerate(member_names):
            if not member_name:
                continue
            
            # Split name (could be "FirstName" or "FirstName LastName")
            name_parts = member_name.split()
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else None
            
            # Try to find officer by first name or preferred name (and last name if provided)
            # Get users who are officers
            officer_user_ids = Officer.objects.values_list('user_id', flat=True)
            officers = CustomUser.objects.filter(
                user_id__in=officer_user_ids
            ).filter(
                models.Q(first_name__iexact=first_name) | models.Q(preferred_name__iexact=first_name)
            )
            
            # If last name provided, filter by it too
            if last_name:
                officers = officers.filter(last_name__iexact=last_name)
            
            # Check results
            user = None
            if officers.count() == 0:
                not_found.append(member_name)
                # Create a basic user account for non-officers
                if not dry_run:
                    # Check if user already exists by name
                    existing_user = CustomUser.objects.filter(
                        first_name__iexact=first_name,
                        last_name__iexact=last_name if last_name else ''
                    ).first()
                    
                    if existing_user:
                        user = existing_user
                    else:
                        # Generate unique email
                        base_email = f"{first_name.lower()}.{last_name.lower() if last_name else 'unknown'}@housemember.hkn"
                        email = base_email
                        counter = 1
                        while CustomUser.objects.filter(email=email).exists():
                            email = f"{first_name.lower()}.{last_name.lower() if last_name else 'unknown'}{counter}@housemember.hkn"
                            counter += 1
                        
                        # Create the user account (UUID will be auto-generated)
                        user = CustomUser.objects.create(
                            first_name=first_name,
                            last_name=last_name or '',
                            preferred_name=first_name,
                            email=email
                        )
                else:
                    # In dry run, skip user creation but continue to count
                    pass
            elif officers.count() > 1:
                # If multiple matches, use first one and log it
                duplicates_found.append(f"{member_name} ({officers.count()} matches, using first)")
                user = officers.first()
            else:
                user = officers.first()
            
            # Add to house membership
            if user:
                membership, created = HouseMembership.objects.get_or_create(
                    user=user,
                    house=house
                )
                
                if created:
                    members_added += 1
            
            # Column index for this member's points (col 2 is first member, etc.)
            col_idx = idx + 2
            
            # Track points for this member
            member_points = 0
            
            # Process each event for this member
            for row_idx, row in enumerate(event_rows):
                if len(row) <= col_idx or not row[0]:
                    continue
                
                event_name = row[0].strip()
                if not event_name:  # Skip rows with no event name
                    continue
                    
                points_str = row[col_idx].strip() if col_idx < len(row) else ""
                
                # Parse points - treat empty as 0
                try:
                    points = float(points_str) if points_str else 0.0
                except ValueError:
                    continue
                
                # Create point record with event date if available
                if not dry_run:
                    description = event_name
                    # Look up the event date, default to now if not found
                    event_date = event_dates.get(event_name, timezone.now())
                    
                    HousePointRecord.objects.create(
                        house=house,
                        member=user,
                        points=points,
                        description=description,
                        added_by=None,
                        date_added=event_date
                    )
                
                member_points += 1
                points_added += 1
        
        # Report results
        if duplicates_found:
            self.stdout.write(self.style.ERROR(
                f'  DUPLICATES (add last names to sheet): {", ".join(duplicates_found)}'
            ))
        if not_found:
            self.stdout.write(self.style.WARNING(
                f'  Not found as officers: {", ".join(not_found)}'
            ))
        
        self.stdout.write(self.style.SUCCESS(
            f'  Added {members_added} new members, created {points_added} point records'
        ))
